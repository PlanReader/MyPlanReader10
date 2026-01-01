"""
PDF Blueprint Parser
Extracts text, dimensions, and construction data from PDF blueprints
Uses PyMuPDF (fitz) for text extraction and Tesseract OCR for scanned images
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ParsedDimension:
    value: float
    unit: str
    raw_text: str
    confidence: float

@dataclass
class ParsedMaterial:
    name: str
    size: str
    quantity: int
    unit: str
    division: str
    notes: str

@dataclass
class BlueprintData:
    filename: str
    page_count: int
    total_sqft: float
    wall_linear_ft: float
    ceiling_sqft: float
    floor_sqft: float
    exterior_sqft: float
    roof_sqft: float
    num_doors: int
    num_windows: int
    num_stories: int
    foundation_type: str
    raw_text: str
    dimensions_found: List[Dict]
    materials_detected: List[Dict]

class BlueprintParser:
    """Parser for construction blueprint PDFs"""
    
    # Common dimension patterns in blueprints
    DIMENSION_PATTERNS = [
        r"(\d+)['\'][-\s]?(\d+)[\"″]?",  # 10'-6" or 10' 6"
        r"(\d+\.?\d*)\s*(ft|feet|foot|')",  # 10 ft or 10.5 feet
        r"(\d+\.?\d*)\s*(in|inch|inches|\")",  # 24 inches
        r"(\d+)x(\d+)",  # 4x8 (sheets, lumber)
        r"(\d+)['\']",  # 10'
        r"(\d+)[\"″]",  # 24"
    ]
    
    # Material keywords by division
    DIVISION_KEYWORDS = {
        "03": ["concrete", "footing", "slab", "foundation", "rebar", "reinforcing", "pour"],
        "04": ["cmu", "block", "masonry", "brick", "mortar", "grout", "stone"],
        "06": ["lumber", "wood", "framing", "stud", "joist", "rafter", "truss", "beam", 
               "header", "plate", "sheathing", "plywood", "osb", "lvl", "glulam",
               "2x4", "2x6", "2x8", "2x10", "2x12", "4x4", "6x6"],
        "07": ["roofing", "shingle", "insulation", "vapor barrier", "housewrap", 
               "waterproof", "flashing", "gutter", "soffit", "fascia", "siding"],
        "08": ["door", "window", "opening", "frame", "hardware", "glazing", "garage"],
        "09": ["drywall", "gypsum", "paint", "finish", "tile", "flooring", "carpet",
               "ceiling", "trim", "baseboard", "crown"]
    }
    
    # Lumber size patterns
    LUMBER_PATTERNS = [
        r"(2x4|2x6|2x8|2x10|2x12|4x4|4x6|6x6|1x4|1x6|1x8|1x10|1x12)",
        r"(\d+)\s*[xX]\s*(\d+)\s*(?:lumber|stud|joist|rafter|beam)",
    ]

    def __init__(self):
        self.zoom_factor = 2.0  # For OCR quality
    
    def parse_pdf(self, pdf_path: str) -> BlueprintData:
        """
        Parse a PDF blueprint and extract construction data
        Returns BlueprintData with extracted dimensions and materials
        """
        doc = fitz.open(pdf_path)
        
        all_text = ""
        dimensions_found = []
        materials_detected = []
        
        for page_num, page in enumerate(doc):
            # Try text extraction first (for searchable PDFs)
            page_text = page.get_text()
            
            # If minimal text found, use OCR
            if len(page_text.strip()) < 50:
                page_text = self._ocr_page(page)
            
            all_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            # Extract dimensions from this page
            page_dims = self._extract_dimensions(page_text)
            dimensions_found.extend(page_dims)
            
            # Detect materials mentioned
            page_materials = self._detect_materials(page_text)
            materials_detected.extend(page_materials)
        
        doc.close()
        
        # Calculate estimates based on extracted data
        estimates = self._calculate_estimates(dimensions_found, all_text, doc.page_count)
        
        return BlueprintData(
            filename=pdf_path.split("/")[-1],
            page_count=doc.page_count,
            total_sqft=estimates['total_sqft'],
            wall_linear_ft=estimates['wall_linear_ft'],
            ceiling_sqft=estimates['ceiling_sqft'],
            floor_sqft=estimates['floor_sqft'],
            exterior_sqft=estimates['exterior_sqft'],
            roof_sqft=estimates['roof_sqft'],
            num_doors=estimates['num_doors'],
            num_windows=estimates['num_windows'],
            num_stories=estimates['num_stories'],
            foundation_type=estimates['foundation_type'],
            raw_text=all_text[:5000],  # First 5000 chars
            dimensions_found=[asdict(d) for d in dimensions_found[:50]],  # Top 50
            materials_detected=materials_detected[:100]  # Top 100
        )
    
    def parse_pdf_bytes(self, pdf_bytes: bytes, filename: str = "uploaded.pdf") -> BlueprintData:
        """Parse PDF from bytes (for uploaded files)"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        all_text = ""
        dimensions_found = []
        materials_detected = []
        
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            
            if len(page_text.strip()) < 50:
                page_text = self._ocr_page(page)
            
            all_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            page_dims = self._extract_dimensions(page_text)
            dimensions_found.extend(page_dims)
            page_materials = self._detect_materials(page_text)
            materials_detected.extend(page_materials)
        
        page_count = doc.page_count
        doc.close()
        
        estimates = self._calculate_estimates(dimensions_found, all_text, page_count)
        
        return BlueprintData(
            filename=filename,
            page_count=page_count,
            total_sqft=estimates['total_sqft'],
            wall_linear_ft=estimates['wall_linear_ft'],
            ceiling_sqft=estimates['ceiling_sqft'],
            floor_sqft=estimates['floor_sqft'],
            exterior_sqft=estimates['exterior_sqft'],
            roof_sqft=estimates['roof_sqft'],
            num_doors=estimates['num_doors'],
            num_windows=estimates['num_windows'],
            num_stories=estimates['num_stories'],
            foundation_type=estimates['foundation_type'],
            raw_text=all_text[:5000],
            dimensions_found=[asdict(d) for d in dimensions_found[:50]],
            materials_detected=materials_detected[:100]
        )
    
    def _ocr_page(self, page) -> str:
        """Convert page to image and run OCR"""
        try:
            mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
    
    def _extract_dimensions(self, text: str) -> List[ParsedDimension]:
        """Extract dimensional values from text"""
        dimensions = []
        
        # Feet and inches pattern: 10'-6" or 10' 6"
        feet_inches = re.findall(r"(\d+)['\'][-\s]?(\d+)[\"″]?", text)
        for match in feet_inches:
            feet, inches = int(match[0]), int(match[1])
            total_ft = feet + (inches / 12)
            dimensions.append(ParsedDimension(
                value=total_ft,
                unit="ft",
                raw_text=f"{feet}'-{inches}\"",
                confidence=0.9
            ))
        
        # Feet only: 10' or 10 ft
        feet_only = re.findall(r"(\d+\.?\d*)\s*(?:ft|feet|foot|['\'])", text, re.IGNORECASE)
        for match in feet_only:
            dimensions.append(ParsedDimension(
                value=float(match),
                unit="ft",
                raw_text=f"{match} ft",
                confidence=0.85
            ))
        
        # Inches: 24" or 24 inches
        inches_only = re.findall(r"(\d+\.?\d*)\s*(?:in|inch|inches|[\"″])", text, re.IGNORECASE)
        for match in inches_only:
            dimensions.append(ParsedDimension(
                value=float(match) / 12,
                unit="ft",
                raw_text=f"{match} in",
                confidence=0.8
            ))
        
        return dimensions
    
    def _detect_materials(self, text: str) -> List[Dict]:
        """Detect material references in text"""
        materials = []
        text_lower = text.lower()
        
        for division, keywords in self.DIVISION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Try to find quantity near the keyword
                    pattern = rf"(\d+)\s*(?:pcs?|pieces?|sheets?|each|ea)?\s*(?:of\s+)?{keyword}"
                    matches = re.findall(pattern, text_lower)
                    
                    qty = int(matches[0]) if matches else 0
                    
                    materials.append({
                        "keyword": keyword,
                        "division": division,
                        "quantity_found": qty,
                        "context": self._get_context(text_lower, keyword)
                    })
        
        # Detect lumber sizes specifically
        lumber_matches = re.findall(r"(2x4|2x6|2x8|2x10|2x12|4x4|4x6|6x6|1x4|1x6|1x8)", text, re.IGNORECASE)
        for lumber in lumber_matches:
            materials.append({
                "keyword": lumber.lower(),
                "division": "06",
                "quantity_found": 0,
                "context": f"Lumber size: {lumber}"
            })
        
        return materials
    
    def _get_context(self, text: str, keyword: str, chars: int = 50) -> str:
        """Get text context around a keyword"""
        idx = text.find(keyword)
        if idx == -1:
            return ""
        start = max(0, idx - chars)
        end = min(len(text), idx + len(keyword) + chars)
        return text[start:end].replace("\n", " ")
    
    def _calculate_estimates(self, dimensions: List[ParsedDimension], text: str, page_count: int) -> Dict:
        """Calculate square footage and other estimates from extracted data"""
        text_lower = text.lower()
        
        # Extract large dimensions (likely room/building dimensions)
        large_dims = [d.value for d in dimensions if 8 <= d.value <= 200]
        
        # Estimate based on page count if dimensions not found
        if len(large_dims) >= 2:
            # Use largest dimensions as building footprint estimate
            large_dims.sort(reverse=True)
            estimated_sqft = large_dims[0] * large_dims[1]
        else:
            # Fallback: estimate based on page count (typical residential)
            estimated_sqft = page_count * 250  # ~250 sqft per page of plans
        
        # Cap at reasonable residential size
        estimated_sqft = min(estimated_sqft, 10000)
        estimated_sqft = max(estimated_sqft, 1000)
        
        # Calculate related dimensions
        # Assume roughly square building for perimeter
        side_length = math.sqrt(estimated_sqft)
        perimeter = side_length * 4
        
        # Stories detection
        stories = 1
        if "second floor" in text_lower or "2nd floor" in text_lower or "upper level" in text_lower:
            stories = 2
        if "third floor" in text_lower or "3rd floor" in text_lower:
            stories = 3
        
        # Wall height (default 8' per story)
        wall_height = 8 * stories
        
        # Door count
        door_matches = len(re.findall(r"door|entry|entrance|garage\s*door", text_lower))
        num_doors = max(door_matches, 3)  # Minimum 3 doors
        
        # Window count
        window_matches = len(re.findall(r"window|glazing|dh|sh|casement", text_lower))
        num_windows = max(window_matches, 6)  # Minimum 6 windows
        
        # Foundation type
        foundation = "slab"
        if "crawl" in text_lower:
            foundation = "crawlspace"
        elif "basement" in text_lower:
            foundation = "basement"
        elif "pier" in text_lower or "post" in text_lower:
            foundation = "pier_and_beam"
        
        return {
            "total_sqft": math.ceil(estimated_sqft),
            "wall_linear_ft": math.ceil(perimeter * stories),
            "ceiling_sqft": math.ceil(estimated_sqft),
            "floor_sqft": math.ceil(estimated_sqft),
            "exterior_sqft": math.ceil(perimeter * wall_height),
            "roof_sqft": math.ceil(estimated_sqft * 1.15),  # 15% for pitch
            "num_doors": num_doors,
            "num_windows": num_windows,
            "num_stories": stories,
            "foundation_type": foundation
        }


class MaterialCalculator:
    """Calculate material quantities based on parsed blueprint data"""
    
    def __init__(self):
        pass
    
    def calculate_division_06_framing(self, data: BlueprintData) -> List[Dict]:
        """
        Calculate Division 6 - Wood Framing materials
        Returns supplier-ready material list with all quantities rounded UP
        """
        materials = []
        order_line = 1
        
        # Wall framing calculations
        wall_sqft = data.wall_linear_ft * 8  # 8' walls
        
        # 2x4 Studs (16" OC = 0.75 studs per linear ft + 10% waste)
        stud_count = math.ceil(data.wall_linear_ft * 0.75 * 1.1)
        materials.append({
            "order_line": order_line,
            "description": "2x4x96 (8') Studs",
            "lumber_size": "2x4",
            "quantity": stud_count,
            "length": "8'",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 11 00",
            "supplier_notes": "SPF #2 or better. For wall framing @ 16\" OC"
        })
        order_line += 1
        
        # Top/Bottom Plates (2 top + 1 bottom = 3 per wall run)
        plate_lf = data.wall_linear_ft * 3
        plates_10ft = math.ceil(plate_lf / 10 * 1.1)
        materials.append({
            "order_line": order_line,
            "description": "2x4x10 Top/Bottom Plates",
            "lumber_size": "2x4",
            "quantity": plates_10ft,
            "length": "10'",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 11 00",
            "supplier_notes": "Bottom plates at exterior walls must be pressure treated"
        })
        order_line += 1
        
        # Headers (assume 1 per door/window, 2x6 for standard)
        header_count = (data.num_doors + data.num_windows)
        materials.append({
            "order_line": order_line,
            "description": "2x6x8 Window/Door Headers",
            "lumber_size": "2x6",
            "quantity": math.ceil(header_count * 2),  # Double headers
            "length": "8'",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 11 00",
            "supplier_notes": "Header framing for doors and windows"
        })
        order_line += 1
        
        # 2x8 for larger headers/beams
        materials.append({
            "order_line": order_line,
            "description": "2x8x10 Beams/Large Headers",
            "lumber_size": "2x8",
            "quantity": math.ceil(header_count * 0.5),
            "length": "10'",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 11 00",
            "supplier_notes": "Large window/door headers, garage headers"
        })
        order_line += 1
        
        # Floor joists (if multi-story or raised floor)
        if data.num_stories > 1 or data.foundation_type == "crawlspace":
            joist_count = math.ceil(data.floor_sqft / 16 * 0.75 * 1.1)  # 16" OC
            materials.append({
                "order_line": order_line,
                "description": "2x10x12 Floor Joists",
                "lumber_size": "2x10",
                "quantity": joist_count,
                "length": "12'",
                "unit": "Each",
                "division": "06",
                "subcategory": "06 11 00",
                "supplier_notes": "Floor framing @ 16\" OC. Verify span tables."
            })
            order_line += 1
            
            # Rim joists
            rim_joist_lf = math.ceil(math.sqrt(data.floor_sqft) * 4)
            materials.append({
                "order_line": order_line,
                "description": "2x10x16 Rim Joists",
                "lumber_size": "2x10",
                "quantity": math.ceil(rim_joist_lf / 16 * 1.1),
                "length": "16'",
                "unit": "Each",
                "division": "06",
                "subcategory": "06 11 00",
                "supplier_notes": "Band/rim joist at floor perimeter"
            })
            order_line += 1
        
        # Roof framing (if trusses not specified, calculate rafters)
        rafter_count = math.ceil(data.roof_sqft / 24)  # Simplified
        materials.append({
            "order_line": order_line,
            "description": "2x6x16 Rafters/Ceiling Joists",
            "lumber_size": "2x6",
            "quantity": rafter_count,
            "length": "16'",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 11 00",
            "supplier_notes": "Roof/ceiling framing. Verify if trusses specified instead."
        })
        order_line += 1
        
        # Ridge beam
        ridge_length = math.ceil(math.sqrt(data.floor_sqft))
        materials.append({
            "order_line": order_line,
            "description": "2x12x16 Ridge Beam",
            "lumber_size": "2x12",
            "quantity": math.ceil(ridge_length / 16),
            "length": "16'",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 11 00",
            "supplier_notes": "Ridge beam for conventional roof framing"
        })
        order_line += 1
        
        # Wall sheathing
        wall_sheets = math.ceil(data.exterior_sqft / 32 * 1.1)  # 4x8 = 32 sqft
        materials.append({
            "order_line": order_line,
            "description": "7/16\" OSB Wall Sheathing 4x8",
            "lumber_size": "4x8",
            "quantity": wall_sheets,
            "length": "8'",
            "unit": "Sheet",
            "division": "06",
            "subcategory": "06 12 00",
            "supplier_notes": "7/16\" OSB structural sheathing"
        })
        order_line += 1
        
        # Roof sheathing
        roof_sheets = math.ceil(data.roof_sqft / 32 * 1.1)
        materials.append({
            "order_line": order_line,
            "description": "5/8\" Plywood Roof Sheathing 4x8",
            "lumber_size": "4x8",
            "quantity": roof_sheets,
            "length": "8'",
            "unit": "Sheet",
            "division": "06",
            "subcategory": "06 12 00",
            "supplier_notes": "5/8\" CDX plywood, 32 sqft per sheet"
        })
        order_line += 1
        
        # Subfloor (if applicable)
        if data.num_stories > 1 or data.foundation_type in ["crawlspace", "basement"]:
            subfloor_sheets = math.ceil(data.floor_sqft / 32 * 1.05)
            materials.append({
                "order_line": order_line,
                "description": "3/4\" T&G Plywood Subfloor 4x8",
                "lumber_size": "4x8",
                "quantity": subfloor_sheets,
                "length": "8'",
                "unit": "Sheet",
                "division": "06",
                "subcategory": "06 12 00",
                "supplier_notes": "3/4\" tongue & groove subfloor plywood"
            })
            order_line += 1
        
        return materials
    
    def calculate_connectors(self, data: BlueprintData) -> List[Dict]:
        """Calculate Simpson Strong-Tie and hardware requirements"""
        materials = []
        order_line = 100  # Start connectors at 100
        
        # Hurricane ties (2 per truss/rafter)
        truss_count = math.ceil(data.roof_sqft / 32)  # Estimate trusses
        materials.append({
            "order_line": order_line,
            "description": "Simpson H2.5A Hurricane Ties",
            "lumber_size": "N/A",
            "quantity": math.ceil(truss_count * 2),
            "length": "N/A",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Secures trusses to top plate. 2 per truss."
        })
        order_line += 1
        
        # Lateral bracing straps
        materials.append({
            "order_line": order_line,
            "description": "Simpson LSTA12 Truss Bracing Straps",
            "lumber_size": "N/A",
            "quantity": math.ceil(truss_count / 4),
            "length": "12\"",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Lateral bracing at truss webs and purlins"
        })
        order_line += 1
        
        # Angle connectors
        angle_count = math.ceil(data.wall_linear_ft / 8)  # One per 8 LF
        materials.append({
            "order_line": order_line,
            "description": "Simpson A35 Framing Angles",
            "lumber_size": "N/A",
            "quantity": angle_count,
            "length": "N/A",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Blocking and corner connections"
        })
        order_line += 1
        
        # Joist hangers (if floor framing)
        if data.num_stories > 1 or data.foundation_type == "crawlspace":
            joist_count = math.ceil(data.floor_sqft / 16 * 0.75)
            materials.append({
                "order_line": order_line,
                "description": "Simpson LUS210 Joist Hangers 2x10",
                "lumber_size": "2x10",
                "quantity": math.ceil(joist_count * 2),
                "length": "N/A",
                "unit": "Each",
                "division": "06",
                "subcategory": "06 05 23",
                "supplier_notes": "Face-mount joist hangers, each end of joist"
            })
            order_line += 1
        
        # Post bases (for porch/deck if detected)
        post_count = max(4, math.ceil(data.total_sqft / 500))
        materials.append({
            "order_line": order_line,
            "description": "Simpson ABU44 Adjustable Post Base 4x4",
            "lumber_size": "4x4",
            "quantity": post_count,
            "length": "N/A",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Standoff post base for 4x4 posts to concrete"
        })
        order_line += 1
        
        # Strap ties for wall plates
        strap_count = math.ceil(data.wall_linear_ft / 20)
        materials.append({
            "order_line": order_line,
            "description": "Simpson MST37 Strap Ties",
            "lumber_size": "N/A",
            "quantity": strap_count,
            "length": "37\"",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Wall plate splices and rafter ties"
        })
        order_line += 1
        
        return materials
    
    def calculate_fasteners(self, data: BlueprintData) -> List[Dict]:
        """Calculate fastener requirements"""
        materials = []
        order_line = 200  # Start fasteners at 200
        
        # 16d framing nails (1 lb per 50 sqft of framing)
        nails_16d = math.ceil(data.total_sqft / 50)
        materials.append({
            "order_line": order_line,
            "description": "16d Common Nails (3.5\")",
            "lumber_size": "N/A",
            "quantity": nails_16d,
            "length": "3.5\"",
            "unit": "lb",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Framing nails for structural connections"
        })
        order_line += 1
        
        # 10d nails for sheathing
        nails_10d = math.ceil((data.roof_sqft + data.exterior_sqft) / 100)
        materials.append({
            "order_line": order_line,
            "description": "10d Common Nails (3\")",
            "lumber_size": "N/A",
            "quantity": nails_10d,
            "length": "3\"",
            "unit": "lb",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Sheathing and blocking nails"
        })
        order_line += 1
        
        # 8d nails for subfloor/light work
        nails_8d = math.ceil(data.floor_sqft / 100)
        materials.append({
            "order_line": order_line,
            "description": "8d Common Nails (2.5\")",
            "lumber_size": "N/A",
            "quantity": nails_8d,
            "length": "2.5\"",
            "unit": "lb",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Subfloor and light framing"
        })
        order_line += 1
        
        # Connector nails (10d x 1.5" for Simpson hardware)
        connector_nails = math.ceil(data.total_sqft / 100)
        materials.append({
            "order_line": order_line,
            "description": "10d x 1.5\" Connector Nails",
            "lumber_size": "N/A",
            "quantity": connector_nails,
            "length": "1.5\"",
            "unit": "lb",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "For Simpson Strong-Tie connectors"
        })
        order_line += 1
        
        return materials
    
    def calculate_anchors(self, data: BlueprintData) -> List[Dict]:
        """Calculate anchor requirements"""
        materials = []
        order_line = 300  # Start anchors at 300
        
        # Foundation anchor bolts (1 per 4 LF of sill plate)
        perimeter = math.sqrt(data.total_sqft) * 4
        anchor_bolts = math.ceil(perimeter / 4)
        materials.append({
            "order_line": order_line,
            "description": "1/2\" x 10\" J-Bolts (Foundation Anchors)",
            "lumber_size": "N/A",
            "quantity": anchor_bolts,
            "length": "10\"",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Embed in concrete, sill plate anchors @ 4' OC max"
        })
        order_line += 1
        
        # Wedge anchors for retrofit/ledger
        wedge_count = math.ceil(perimeter / 16)
        materials.append({
            "order_line": order_line,
            "description": "Wedge Anchor 1/2\" x 5.5\"",
            "lumber_size": "N/A",
            "quantity": wedge_count,
            "length": "5.5\"",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Ledger board and retrofit anchor connections"
        })
        order_line += 1
        
        # Tapcons for misc concrete connections
        tapcon_count = math.ceil(data.total_sqft / 200)
        materials.append({
            "order_line": order_line,
            "description": "Tapcon 1/4\" x 2.75\" Concrete Screws",
            "lumber_size": "N/A",
            "quantity": math.ceil(tapcon_count) * 25,  # Box of 25
            "length": "2.75\"",
            "unit": "Each",
            "division": "06",
            "subcategory": "06 05 23",
            "supplier_notes": "Concrete/block connections, box of 25"
        })
        order_line += 1
        
        return materials
    
    def generate_full_takeoff(self, data: BlueprintData) -> Dict:
        """Generate complete supplier-ready material takeoff"""
        framing = self.calculate_division_06_framing(data)
        connectors = self.calculate_connectors(data)
        fasteners = self.calculate_fasteners(data)
        anchors = self.calculate_anchors(data)
        
        all_materials = framing + connectors + fasteners + anchors
        
        return {
            "project_info": {
                "filename": data.filename,
                "page_count": data.page_count,
                "total_sqft": data.total_sqft,
                "wall_linear_ft": data.wall_linear_ft,
                "stories": data.num_stories,
                "foundation": data.foundation_type,
                "doors": data.num_doors,
                "windows": data.num_windows
            },
            "materials": all_materials,
            "summary": {
                "total_line_items": len(all_materials),
                "divisions_included": ["06 - Wood, Plastics, Composites"],
                "note": "All quantities rounded UP to whole numbers for supplier ordering"
            }
        }
