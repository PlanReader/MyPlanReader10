"""
AIA MasterFormat Divisions Data Model
Divisions 3, 4, 6, 7, 8, 9 for Construction Takeoffs
"""

# AIA MasterFormat Division Definitions
AIA_DIVISIONS = {
    "03": {
        "name": "Concrete",
        "description": "Cast-in-place concrete, precast concrete, cementitious decks",
        "subcategories": [
            {"code": "03 10 00", "name": "Concrete Forming and Accessories"},
            {"code": "03 20 00", "name": "Concrete Reinforcing"},
            {"code": "03 30 00", "name": "Cast-in-Place Concrete"},
            {"code": "03 40 00", "name": "Precast Concrete"},
            {"code": "03 50 00", "name": "Cast Decks and Underlayment"},
        ]
    },
    "04": {
        "name": "Masonry",
        "description": "Unit masonry, stone, masonry restoration",
        "subcategories": [
            {"code": "04 20 00", "name": "Unit Masonry"},
            {"code": "04 21 00", "name": "Clay Unit Masonry"},
            {"code": "04 22 00", "name": "Concrete Unit Masonry"},
            {"code": "04 40 00", "name": "Stone Assemblies"},
            {"code": "04 70 00", "name": "Manufactured Masonry"},
        ]
    },
    "06": {
        "name": "Wood, Plastics, and Composites",
        "description": "Rough carpentry, finish carpentry, architectural woodwork",
        "subcategories": [
            {"code": "06 10 00", "name": "Rough Carpentry"},
            {"code": "06 11 00", "name": "Wood Framing"},
            {"code": "06 12 00", "name": "Structural Panels"},
            {"code": "06 15 00", "name": "Wood Decking"},
            {"code": "06 17 00", "name": "Shop-Fabricated Structural Wood"},
            {"code": "06 20 00", "name": "Finish Carpentry"},
            {"code": "06 40 00", "name": "Architectural Woodwork"},
        ]
    },
    "07": {
        "name": "Thermal and Moisture Protection",
        "description": "Waterproofing, insulation, roofing, siding",
        "subcategories": [
            {"code": "07 10 00", "name": "Dampproofing and Waterproofing"},
            {"code": "07 20 00", "name": "Thermal Protection"},
            {"code": "07 21 00", "name": "Thermal Insulation"},
            {"code": "07 30 00", "name": "Steep Slope Roofing"},
            {"code": "07 40 00", "name": "Roofing and Siding Panels"},
            {"code": "07 46 00", "name": "Siding"},
            {"code": "07 50 00", "name": "Membrane Roofing"},
            {"code": "07 60 00", "name": "Flashing and Sheet Metal"},
            {"code": "07 90 00", "name": "Joint Protection"},
        ]
    },
    "08": {
        "name": "Openings",
        "description": "Doors, windows, entrances, storefronts, hardware",
        "subcategories": [
            {"code": "08 10 00", "name": "Doors and Frames"},
            {"code": "08 11 00", "name": "Metal Doors and Frames"},
            {"code": "08 14 00", "name": "Wood Doors"},
            {"code": "08 30 00", "name": "Specialty Doors and Frames"},
            {"code": "08 40 00", "name": "Entrances, Storefronts, and Curtain Walls"},
            {"code": "08 50 00", "name": "Windows"},
            {"code": "08 70 00", "name": "Hardware"},
            {"code": "08 80 00", "name": "Glazing"},
        ]
    },
    "09": {
        "name": "Finishes",
        "description": "Plaster, gypsum board, tile, flooring, painting",
        "subcategories": [
            {"code": "09 20 00", "name": "Plaster and Gypsum Board"},
            {"code": "09 21 00", "name": "Plaster and Gypsum Board Assemblies"},
            {"code": "09 22 00", "name": "Supports for Plaster and Gypsum Board"},
            {"code": "09 29 00", "name": "Gypsum Board"},
            {"code": "09 30 00", "name": "Tiling"},
            {"code": "09 50 00", "name": "Ceilings"},
            {"code": "09 60 00", "name": "Flooring"},
            {"code": "09 65 00", "name": "Resilient Flooring"},
            {"code": "09 68 00", "name": "Carpeting"},
            {"code": "09 90 00", "name": "Painting and Coating"},
        ]
    }
}

# Standard lumber sizes sold at lumber yards (nominal sizes)
LUMBER_SIZES = {
    "dimensional": [
        {"nominal": "2x4", "actual": "1.5x3.5", "lengths": [8, 10, 12, 14, 16, 20]},
        {"nominal": "2x6", "actual": "1.5x5.5", "lengths": [8, 10, 12, 14, 16, 20]},
        {"nominal": "2x8", "actual": "1.5x7.25", "lengths": [8, 10, 12, 14, 16, 20]},
        {"nominal": "2x10", "actual": "1.5x9.25", "lengths": [8, 10, 12, 14, 16, 20]},
        {"nominal": "2x12", "actual": "1.5x11.25", "lengths": [8, 10, 12, 14, 16, 20]},
        {"nominal": "4x4", "actual": "3.5x3.5", "lengths": [8, 10, 12, 14, 16]},
        {"nominal": "4x6", "actual": "3.5x5.5", "lengths": [8, 10, 12, 14, 16]},
        {"nominal": "6x6", "actual": "5.5x5.5", "lengths": [8, 10, 12, 14, 16, 20]},
    ],
    "boards": [
        {"nominal": "1x4", "actual": "0.75x3.5", "lengths": [8, 10, 12, 14, 16]},
        {"nominal": "1x6", "actual": "0.75x5.5", "lengths": [8, 10, 12, 14, 16]},
        {"nominal": "1x8", "actual": "0.75x7.25", "lengths": [8, 10, 12, 14, 16]},
        {"nominal": "1x10", "actual": "0.75x9.25", "lengths": [8, 10, 12, 14, 16]},
        {"nominal": "1x12", "actual": "0.75x11.25", "lengths": [8, 10, 12, 14, 16]},
    ],
    "sheathing": [
        {"type": "plywood", "thickness": "1/2\"", "size": "4x8", "sqft": 32},
        {"type": "plywood", "thickness": "5/8\"", "size": "4x8", "sqft": 32},
        {"type": "plywood", "thickness": "3/4\"", "size": "4x8", "sqft": 32},
        {"type": "OSB", "thickness": "7/16\"", "size": "4x8", "sqft": 32},
        {"type": "OSB", "thickness": "1/2\"", "size": "4x8", "sqft": 32},
        {"type": "OSB", "thickness": "5/8\"", "size": "4x8", "sqft": 32},
    ]
}

# Fasteners commonly used in framing
FASTENERS = {
    "nails": [
        {"name": "16d Common Nails", "length": "3.5\"", "use": "Framing, structural connections", "unit": "lb"},
        {"name": "16d Sinker Nails", "length": "3.25\"", "use": "General framing", "unit": "lb"},
        {"name": "10d Common Nails", "length": "3\"", "use": "Sheathing, blocking", "unit": "lb"},
        {"name": "8d Common Nails", "length": "2.5\"", "use": "Sheathing, subfloor", "unit": "lb"},
        {"name": "8d Box Nails", "length": "2.5\"", "use": "Light framing", "unit": "lb"},
        {"name": "Roofing Nails 1.25\"", "length": "1.25\"", "use": "Roofing shingles", "unit": "lb"},
        {"name": "Roofing Nails 1.5\"", "length": "1.5\"", "use": "Roofing felt, shingles", "unit": "lb"},
    ],
    "screws": [
        {"name": "#8 x 2\" Wood Screws", "length": "2\"", "use": "Light duty connections", "unit": "box"},
        {"name": "#8 x 3\" Wood Screws", "length": "3\"", "use": "Deck boards, framing", "unit": "box"},
        {"name": "#10 x 3\" Structural Screws", "length": "3\"", "use": "Structural connections", "unit": "box"},
        {"name": "#10 x 4\" Structural Screws", "length": "4\"", "use": "Heavy structural", "unit": "box"},
        {"name": "GRK RSS 5/16 x 3\"", "length": "3\"", "use": "Structural, replaces lag bolts", "unit": "box"},
    ],
    "bolts": [
        {"name": "1/2\" x 6\" Carriage Bolt", "length": "6\"", "use": "Post connections", "unit": "each"},
        {"name": "1/2\" x 8\" Carriage Bolt", "length": "8\"", "use": "Beam connections", "unit": "each"},
        {"name": "5/8\" x 6\" Hex Bolt", "length": "6\"", "use": "Heavy structural", "unit": "each"},
        {"name": "1/2\" x 10\" Anchor Bolt", "length": "10\"", "use": "Sill plate to foundation", "unit": "each"},
        {"name": "5/8\" x 10\" J-Bolt", "length": "10\"", "use": "Foundation anchor", "unit": "each"},
    ]
}

# Concrete anchors
CONCRETE_ANCHORS = [
    {"name": "Wedge Anchor 1/2\" x 4\"", "type": "wedge", "diameter": "1/2\"", "length": "4\"", "use": "Concrete, sill plates"},
    {"name": "Wedge Anchor 1/2\" x 5.5\"", "type": "wedge", "diameter": "1/2\"", "length": "5.5\"", "use": "Concrete, ledger boards"},
    {"name": "Wedge Anchor 5/8\" x 6\"", "type": "wedge", "diameter": "5/8\"", "length": "6\"", "use": "Heavy duty concrete"},
    {"name": "Sleeve Anchor 3/8\" x 3\"", "type": "sleeve", "diameter": "3/8\"", "length": "3\"", "use": "Block, brick"},
    {"name": "Sleeve Anchor 1/2\" x 4\"", "type": "sleeve", "diameter": "1/2\"", "length": "4\"", "use": "Block, brick"},
    {"name": "Tapcon 3/16\" x 1.75\"", "type": "tapcon", "diameter": "3/16\"", "length": "1.75\"", "use": "Light duty concrete/block"},
    {"name": "Tapcon 1/4\" x 2.75\"", "type": "tapcon", "diameter": "1/4\"", "length": "2.75\"", "use": "Medium duty concrete/block"},
    {"name": "Tapcon 1/4\" x 4\"", "type": "tapcon", "diameter": "1/4\"", "length": "4\"", "use": "Heavy duty concrete/block"},
    {"name": "Drop-In Anchor 3/8\"", "type": "drop-in", "diameter": "3/8\"", "use": "Overhead concrete"},
    {"name": "Drop-In Anchor 1/2\"", "type": "drop-in", "diameter": "1/2\"", "use": "Overhead concrete"},
]

# Division 4 - Masonry materials
MASONRY_MATERIALS = {
    "cmu_blocks": [
        {"name": "8x8x16 Standard CMU", "size": "8x8x16", "sqft_coverage": 1.125, "unit": "block"},
        {"name": "8x8x16 Lightweight CMU", "size": "8x8x16", "sqft_coverage": 1.125, "unit": "block"},
        {"name": "8x8x16 Split-Face CMU", "size": "8x8x16", "sqft_coverage": 1.125, "unit": "block"},
        {"name": "4x8x16 Half CMU", "size": "4x8x16", "sqft_coverage": 1.125, "unit": "block"},
        {"name": "12x8x16 CMU", "size": "12x8x16", "sqft_coverage": 1.125, "unit": "block"},
    ],
    "mortar": [
        {"name": "Type S Mortar Mix", "coverage": "36 blocks per bag", "unit": "80lb bag"},
        {"name": "Type N Mortar Mix", "coverage": "36 blocks per bag", "unit": "80lb bag"},
        {"name": "Portland Cement", "use": "Mix with sand", "unit": "94lb bag"},
        {"name": "Masonry Sand", "use": "Mortar mix", "unit": "cubic yard"},
    ],
    "reinforcement": [
        {"name": "#4 Rebar (1/2\")", "use": "Vertical cells, bond beams", "unit": "20ft stick"},
        {"name": "#5 Rebar (5/8\")", "use": "Bond beams, lintels", "unit": "20ft stick"},
        {"name": "Ladder Wire Reinforcement", "use": "Horizontal bed joints", "unit": "10ft stick"},
        {"name": "Truss Wire Reinforcement", "use": "Horizontal bed joints", "unit": "10ft stick"},
    ],
    "accessories": [
        {"name": "Wall Ties", "use": "Veneer to backup", "unit": "box of 100"},
        {"name": "Control Joint Material", "use": "Movement joints", "unit": "10ft length"},
        {"name": "Flashing", "use": "Water management", "unit": "roll"},
    ]
}

# Division 7 - Thermal and Moisture Protection
# ============================================
# VERIFIED FIELD STANDARDS BY USA CONSTRUCTION INC.
# These calculations are based on 40 years of industry experience
# ============================================

THERMAL_MOISTURE_MATERIALS = {
    "insulation": [
        {"name": "R-13 Fiberglass Batt 3.5\"", "r_value": 13, "thickness": "3.5\"", "coverage": "40 sqft/bag", "use": "2x4 walls"},
        {"name": "R-19 Fiberglass Batt 6.25\"", "r_value": 19, "thickness": "6.25\"", "coverage": "48 sqft/bag", "use": "2x6 walls"},
        {"name": "R-30 Fiberglass Batt 10\"", "r_value": 30, "thickness": "10\"", "coverage": "31 sqft/bag", "use": "Attic floors"},
        {"name": "R-38 Fiberglass Batt 12\"", "r_value": 38, "thickness": "12\"", "coverage": "24 sqft/bag", "use": "Attic"},
        {"name": "Rigid Foam XPS 1\"", "r_value": 5, "thickness": "1\"", "coverage": "32 sqft/sheet", "use": "Foundation"},
        {"name": "Rigid Foam XPS 2\"", "r_value": 10, "thickness": "2\"", "coverage": "32 sqft/sheet", "use": "Foundation, exterior"},
        {"name": "Spray Foam Open Cell", "r_value": "3.7/inch", "use": "Walls, attic", "unit": "board foot"},
        {"name": "Spray Foam Closed Cell", "r_value": "6.5/inch", "use": "Foundation, roof", "unit": "board foot"},
    ],
    "housewrap": [
        {"name": "Tyvek HomeWrap", "coverage": "150 sqft/roll", "unit": "roll"},
        {"name": "Tyvek CommercialWrap", "coverage": "150 sqft/roll", "unit": "roll"},
        {"name": "ZIP System Tape", "use": "Seam sealing", "unit": "roll"},
    ],
    "roofing": [
        {"name": "Asphalt Shingles 3-Tab", "coverage": "33 sqft/bundle", "unit": "bundle"},
        {"name": "Architectural Shingles", "coverage": "33 sqft/bundle", "unit": "bundle"},
        {"name": "Roofing Felt #15", "coverage": "400 sqft/roll", "unit": "roll"},
        {"name": "Roofing Felt #30", "coverage": "200 sqft/roll", "unit": "roll"},
        {"name": "Ice & Water Shield", "coverage": "67 sqft/roll", "unit": "roll"},
        {"name": "Drip Edge Metal", "length": "10ft", "unit": "piece"},
        {"name": "Ridge Vent", "length": "4ft", "unit": "piece"},
    ],
    "siding": [
        {"name": "Vinyl Siding", "coverage": "100 sqft/carton", "unit": "carton"},
        {"name": "Fiber Cement Siding (Hardie)", "coverage": "varies", "unit": "piece"},
        {"name": "LP SmartSide Siding", "coverage": "varies", "unit": "piece"},
    ],
    # Verified Field Standards: Stucco scratch/brown coat at 22 sq ft per 80lb bag
    "stucco": [
        {"name": "Stucco Base Coat (Scratch/Brown) 80lb", "coverage": 22, "unit": "80lb bag", "note": "Verified Field Standard"},
        {"name": "Stucco Finish Coat 80lb", "coverage": 30, "unit": "80lb bag"},
        {"name": "Metal Lath 2.5lb Diamond", "coverage": 2.78, "unit": "sheet", "size": "27\"x96\""},
        {"name": "Stucco Wire 17ga Self-Furring", "coverage": 2.78, "unit": "sheet"},
        {"name": "Weep Screed 10ft", "length": 10, "unit": "piece"},
        {"name": "Corner Aid 10ft", "length": 10, "unit": "piece"},
        {"name": "Casing Bead 10ft", "length": 10, "unit": "piece"},
    ]
}


# Division 8 - Openings
OPENINGS_MATERIALS = {
    "doors": [
        {"name": "Prehung Interior Door 2/0 x 6/8", "size": "24\"x80\"", "type": "interior", "unit": "each"},
        {"name": "Prehung Interior Door 2/6 x 6/8", "size": "30\"x80\"", "type": "interior", "unit": "each"},
        {"name": "Prehung Interior Door 2/8 x 6/8", "size": "32\"x80\"", "type": "interior", "unit": "each"},
        {"name": "Prehung Interior Door 3/0 x 6/8", "size": "36\"x80\"", "type": "interior", "unit": "each"},
        {"name": "Prehung Exterior Door 3/0 x 6/8", "size": "36\"x80\"", "type": "exterior", "unit": "each"},
        {"name": "Sliding Glass Door 6/0 x 6/8", "size": "72\"x80\"", "type": "exterior", "unit": "each"},
        {"name": "Garage Door 16x7", "size": "16'x7'", "type": "garage", "unit": "each"},
        {"name": "Garage Door 9x7", "size": "9'x7'", "type": "garage", "unit": "each"},
    ],
    "windows": [
        {"name": "Single Hung Window 2/0 x 3/0", "size": "24\"x36\"", "type": "single hung", "unit": "each"},
        {"name": "Single Hung Window 3/0 x 4/0", "size": "36\"x48\"", "type": "single hung", "unit": "each"},
        {"name": "Single Hung Window 3/0 x 5/0", "size": "36\"x60\"", "type": "single hung", "unit": "each"},
        {"name": "Double Hung Window 3/0 x 4/0", "size": "36\"x48\"", "type": "double hung", "unit": "each"},
        {"name": "Casement Window 2/0 x 3/0", "size": "24\"x36\"", "type": "casement", "unit": "each"},
        {"name": "Picture Window 4/0 x 5/0", "size": "48\"x60\"", "type": "fixed", "unit": "each"},
    ],
    "hardware": [
        {"name": "Interior Door Knob Set", "type": "passage", "unit": "set"},
        {"name": "Privacy Door Knob Set", "type": "privacy", "unit": "set"},
        {"name": "Entry Door Handleset", "type": "entry", "unit": "set"},
        {"name": "Deadbolt Lock", "type": "security", "unit": "each"},
        {"name": "Door Hinges 3.5\"", "type": "hinge", "unit": "pair"},
        {"name": "Door Stop", "type": "stop", "unit": "each"},
    ]
}

# Division 9 - Finishes
# ============================================
# VERIFIED FIELD STANDARDS BY USA CONSTRUCTION INC.
# These calculations are based on 40 years of industry experience
# ============================================

FINISHES_MATERIALS = {
    "drywall": [
        {"name": "Drywall 1/2\" 4x8", "size": "4x8", "thickness": "1/2\"", "sqft": 32, "unit": "sheet"},
        {"name": "Drywall 1/2\" 4x10", "size": "4x10", "thickness": "1/2\"", "sqft": 40, "unit": "sheet"},
        {"name": "Drywall 1/2\" 4x12", "size": "4x12", "thickness": "1/2\"", "sqft": 48, "unit": "sheet"},
        {"name": "Drywall 5/8\" 4x8 (Fire-Rated)", "size": "4x8", "thickness": "5/8\"", "sqft": 32, "unit": "sheet"},
        {"name": "Moisture Resistant Drywall 1/2\"", "size": "4x8", "thickness": "1/2\"", "sqft": 32, "unit": "sheet"},
        {"name": "Cement Board 1/2\" 3x5", "size": "3x5", "thickness": "1/2\"", "sqft": 15, "unit": "sheet"},
    ],
    "drywall_accessories": [
        {"name": "Joint Compound 50lb Box", "coverage": "1000 sqft/box", "unit": "50lb box", "lbs_per_sqft": 0.05},
        {"name": "Paper Drywall Tape", "length": "500ft", "unit": "roll"},
        {"name": "Mesh Drywall Tape", "length": "300ft", "unit": "roll"},
        {"name": "Corner Bead Metal", "length": "8ft", "unit": "piece"},
        {"name": "Corner Bead Vinyl", "length": "10ft", "unit": "piece"},
        {"name": "Drywall Screws 1.25\"", "unit": "lb"},
        {"name": "Drywall Screws 1.625\"", "unit": "lb"},
    ],
    "paint": [
        # Verified Field Standards: 200 sq ft per gallon for 2 coats (100 sq ft effective per coat)
        {"name": "Interior Primer", "coverage": 200, "unit": "gallon", "coats": 1},
        {"name": "Interior Latex Paint (Flat)", "coverage": 200, "unit": "gallon", "coats": 2},
        {"name": "Interior Latex Paint (Eggshell)", "coverage": 200, "unit": "gallon", "coats": 2},
        {"name": "Interior Latex Paint (Satin)", "coverage": 200, "unit": "gallon", "coats": 2},
        {"name": "Interior Latex Paint (Semi-Gloss)", "coverage": 200, "unit": "gallon", "coats": 2},
        {"name": "Exterior Primer", "coverage": 200, "unit": "gallon", "coats": 1},
        {"name": "Exterior Latex Paint", "coverage": 200, "unit": "gallon", "coats": 2},
    ],
    "flooring": [
        {"name": "Underlayment Plywood 1/4\"", "size": "4x8", "sqft": 32, "unit": "sheet"},
        {"name": "LVP Flooring", "coverage": "varies", "unit": "sqft"},
        {"name": "Carpet", "coverage": "varies", "unit": "sqyd"},
        {"name": "Carpet Pad", "coverage": "varies", "unit": "sqyd"},
        {"name": "Tile Backer Board", "size": "3x5", "sqft": 15, "unit": "sheet"},
    ]
}
