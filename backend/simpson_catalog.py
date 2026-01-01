"""
Simpson Strong-Tie Product Catalog
Comprehensive catalog of connectors, anchors, and hardware for construction takeoffs
"""

# Simpson Strong-Tie Framing Connectors
SIMPSON_CONNECTORS = {
    "hurricane_ties": [
        {
            "model": "H2.5A",
            "name": "Hurricane Tie",
            "description": "Single-sided hurricane/seismic tie for trusses and rafters",
            "use": "Secures roof trusses/rafters to top plate",
            "uplift_load": "505 lb",
            "fasteners": "10-10d x 1.5\" nails",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "H1",
            "name": "Hurricane Tie",
            "description": "Light-duty hurricane tie",
            "use": "Light truss/rafter to top plate",
            "uplift_load": "175 lb",
            "fasteners": "4-8d x 1.5\" nails",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "H10A",
            "name": "Hurricane Tie",
            "description": "Heavy-duty hurricane tie",
            "use": "Heavy truss/rafter to top plate",
            "uplift_load": "1070 lb",
            "fasteners": "14-10d x 1.5\" nails",
            "unit": "each",
            "pack_qty": 50
        },
        {
            "model": "LSTA",
            "name": "Lateral Stabilizer",
            "description": "Strap tie for lateral stability",
            "use": "Truss-to-truss or truss-to-wall",
            "load": "1545 lb",
            "fasteners": "varies by length",
            "lengths": ["9\"", "12\"", "15\"", "18\"", "21\"", "24\""],
            "unit": "each",
            "pack_qty": 50
        },
        {
            "model": "LSTI",
            "name": "Twist Strap",
            "description": "Light lateral strap with twist",
            "use": "Truss lateral bracing",
            "load": "810 lb",
            "fasteners": "10-8d nails",
            "unit": "each",
            "pack_qty": 100
        },
    ],
    "joist_hangers": [
        {
            "model": "LUS26",
            "name": "Face-Mount Joist Hanger 2x6",
            "description": "Standard face-mount hanger for 2x6",
            "use": "Joist to beam/header connection",
            "load": "790 lb",
            "fasteners": "10-10d x 1.5\" nails",
            "lumber": "2x6",
            "unit": "each",
            "pack_qty": 25
        },
        {
            "model": "LUS28",
            "name": "Face-Mount Joist Hanger 2x8",
            "description": "Standard face-mount hanger for 2x8",
            "use": "Joist to beam/header connection",
            "load": "1015 lb",
            "fasteners": "10-10d x 1.5\" nails",
            "lumber": "2x8",
            "unit": "each",
            "pack_qty": 25
        },
        {
            "model": "LUS210",
            "name": "Face-Mount Joist Hanger 2x10",
            "description": "Standard face-mount hanger for 2x10",
            "use": "Joist to beam/header connection",
            "load": "1290 lb",
            "fasteners": "10-10d x 1.5\" nails",
            "lumber": "2x10",
            "unit": "each",
            "pack_qty": 25
        },
        {
            "model": "LUS212",
            "name": "Face-Mount Joist Hanger 2x12",
            "description": "Standard face-mount hanger for 2x12",
            "use": "Joist to beam/header connection",
            "load": "1595 lb",
            "fasteners": "10-10d x 1.5\" nails",
            "lumber": "2x12",
            "unit": "each",
            "pack_qty": 25
        },
        {
            "model": "LU26",
            "name": "Top-Flange Joist Hanger 2x6",
            "description": "Top-flange hanger for 2x6",
            "use": "Joist to I-joist or beam",
            "load": "520 lb",
            "fasteners": "6-10d nails",
            "lumber": "2x6",
            "unit": "each",
            "pack_qty": 25
        },
        {
            "model": "HUS26",
            "name": "Heavy-Duty Joist Hanger 2x6",
            "description": "Heavy joist hanger for 2x6",
            "use": "Heavy-duty joist connection",
            "load": "1095 lb",
            "fasteners": "varies",
            "lumber": "2x6",
            "unit": "each",
            "pack_qty": 25
        },
    ],
    "angle_brackets": [
        {
            "model": "A35",
            "name": "Framing Angle",
            "description": "All-purpose framing angle",
            "use": "General framing connections, blocking, corners",
            "load": "1055 lb",
            "fasteners": "18-10d x 1.5\" nails",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "A34",
            "name": "Framing Angle",
            "description": "Standard framing angle",
            "use": "Light framing, nailer plates",
            "load": "555 lb",
            "fasteners": "10-10d nails",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "A21",
            "name": "Framing Angle",
            "description": "Light framing angle",
            "use": "Light-duty connections",
            "load": "340 lb",
            "fasteners": "8-8d nails",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "L50",
            "name": "Reinforcing Angle",
            "description": "Reinforcing L-angle",
            "use": "Beam/post connections",
            "load": "1760 lb",
            "fasteners": "14-10d nails",
            "unit": "each",
            "pack_qty": 50
        },
        {
            "model": "L70",
            "name": "Reinforcing Angle",
            "description": "Heavy reinforcing L-angle",
            "use": "Heavy-duty connections",
            "load": "2890 lb",
            "fasteners": "varies",
            "unit": "each",
            "pack_qty": 25
        },
    ],
    "post_bases": [
        {
            "model": "ABU44",
            "name": "Adjustable Post Base 4x4",
            "description": "Adjustable standoff post base",
            "use": "4x4 post to concrete",
            "load": "3770 lb",
            "fasteners": "4-10d nails + anchor",
            "post_size": "4x4",
            "unit": "each",
            "pack_qty": 10
        },
        {
            "model": "ABU66",
            "name": "Adjustable Post Base 6x6",
            "description": "Adjustable standoff post base",
            "use": "6x6 post to concrete",
            "load": "7615 lb",
            "fasteners": "varies + anchor",
            "post_size": "6x6",
            "unit": "each",
            "pack_qty": 10
        },
        {
            "model": "CB44",
            "name": "Column Base 4x4",
            "description": "Concealed post base",
            "use": "4x4 post to concrete (concealed)",
            "load": "2250 lb",
            "fasteners": "varies",
            "post_size": "4x4",
            "unit": "each",
            "pack_qty": 10
        },
        {
            "model": "PB44",
            "name": "Post Base 4x4",
            "description": "Standard post base",
            "use": "4x4 post to concrete",
            "load": "1795 lb",
            "fasteners": "4-16d nails",
            "post_size": "4x4",
            "unit": "each",
            "pack_qty": 25
        },
    ],
    "post_caps": [
        {
            "model": "BC4",
            "name": "Post Cap 4x4",
            "description": "Post to beam cap",
            "use": "4x4 post to beam",
            "load": "4560 lb",
            "fasteners": "8-16d nails",
            "post_size": "4x4",
            "unit": "each",
            "pack_qty": 25
        },
        {
            "model": "BC6",
            "name": "Post Cap 6x6",
            "description": "Post to beam cap",
            "use": "6x6 post to beam",
            "load": "7300 lb",
            "fasteners": "8-16d nails",
            "post_size": "6x6",
            "unit": "each",
            "pack_qty": 10
        },
        {
            "model": "AC4",
            "name": "Adjustable Post Cap 4x4",
            "description": "Adjustable post cap",
            "use": "4x4 post to beam (adjustable)",
            "load": "3905 lb",
            "fasteners": "8-16d nails",
            "post_size": "4x4",
            "unit": "each",
            "pack_qty": 25
        },
    ],
    "hold_downs": [
        {
            "model": "HDU2",
            "name": "Holdown",
            "description": "Pre-deflected holdown",
            "use": "Shear wall holdown",
            "load": "3075 lb",
            "fasteners": "SDS screws",
            "unit": "each",
            "pack_qty": 10
        },
        {
            "model": "HDU4",
            "name": "Holdown",
            "description": "Pre-deflected holdown",
            "use": "Heavy-duty shear wall",
            "load": "4565 lb",
            "fasteners": "SDS screws",
            "unit": "each",
            "pack_qty": 10
        },
        {
            "model": "HDU8",
            "name": "Holdown",
            "description": "Heavy pre-deflected holdown",
            "use": "Heavy shear wall",
            "load": "6525 lb",
            "fasteners": "SDS screws",
            "unit": "each",
            "pack_qty": 5
        },
        {
            "model": "PHD2",
            "name": "Purlin Hanger/Holdown",
            "description": "Multi-purpose holdown",
            "use": "Purlin or holdown",
            "load": "2895 lb",
            "fasteners": "8-16d nails",
            "unit": "each",
            "pack_qty": 25
        },
    ],
    "straps": [
        {
            "model": "LSTA12",
            "name": "Strap Tie 12\"",
            "description": "12\" strap tie",
            "use": "Truss bracing, general strapping",
            "load": "1545 lb",
            "fasteners": "10-10d nails",
            "length": "12\"",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "LSTA18",
            "name": "Strap Tie 18\"",
            "description": "18\" strap tie",
            "use": "Truss bracing, general strapping",
            "load": "1545 lb",
            "fasteners": "16-10d nails",
            "length": "18\"",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "LSTA24",
            "name": "Strap Tie 24\"",
            "description": "24\" strap tie",
            "use": "Truss bracing, general strapping",
            "load": "1545 lb",
            "fasteners": "20-10d nails",
            "length": "24\"",
            "unit": "each",
            "pack_qty": 50
        },
        {
            "model": "MST27",
            "name": "Medium Strap Tie 27\"",
            "description": "27\" medium strap",
            "use": "Wall plate splices",
            "load": "820 lb",
            "fasteners": "10-8d nails",
            "length": "27\"",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "MST37",
            "name": "Medium Strap Tie 37\"",
            "description": "37\" medium strap",
            "use": "Wall plate splices, rafters",
            "load": "820 lb",
            "fasteners": "14-8d nails",
            "length": "37\"",
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "ST22",
            "name": "Strap Tie Coil",
            "description": "22-gauge strap coil",
            "use": "Custom length strapping",
            "load": "varies",
            "width": "1.25\"",
            "length": "25ft roll",
            "unit": "roll",
            "pack_qty": 1
        },
    ],
    "beam_hangers": [
        {
            "model": "GLT4",
            "name": "Girder Tie",
            "description": "Beam to girder connection",
            "use": "LVL/Glulam to girder",
            "load": "1510 lb",
            "fasteners": "10-10d nails",
            "unit": "each",
            "pack_qty": 25
        },
        {
            "model": "HGU410",
            "name": "Heavy Glulam Hanger",
            "description": "Heavy beam hanger 4x10",
            "use": "Heavy beam connections",
            "load": "varies",
            "fasteners": "varies",
            "unit": "each",
            "pack_qty": 10
        },
    ],
    "miscellaneous": [
        {
            "model": "TP",
            "name": "Tie Plate",
            "description": "Flat tie plate",
            "use": "Wood-to-wood splices",
            "sizes": ["3x5", "5x7", "3x7", "5x5"],
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "MP",
            "name": "Mending Plate",
            "description": "Flat mending plate",
            "use": "Repairs, connections",
            "sizes": ["2x4", "3x6", "4x8"],
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "NS",
            "name": "Nail Stop/Plate",
            "description": "Protective nail plate",
            "use": "Protect pipes/wires in studs",
            "sizes": ["1.5x3", "1.5x5"],
            "unit": "each",
            "pack_qty": 100
        },
        {
            "model": "RTC2Z",
            "name": "Rigid Tie Connector",
            "description": "Rigid tie for roof framing",
            "use": "Ridge beam to rafter",
            "load": "500 lb",
            "fasteners": "8-8d nails",
            "unit": "each",
            "pack_qty": 50
        },
    ]
}

# MiTek Products (Embedded Anchors and Connectors)
MITEK_PRODUCTS = {
    "truss_plates": [
        {
            "model": "MII-20",
            "name": "Metal Connector Plate",
            "description": "20-gauge truss plate",
            "use": "Truss manufacturing",
            "sizes": ["3x4", "3x6", "4x6", "4x8", "5x8", "6x8"],
            "unit": "each"
        },
        {
            "model": "MII-18",
            "name": "Metal Connector Plate Heavy",
            "description": "18-gauge truss plate",
            "use": "Heavy-duty truss connections",
            "sizes": ["4x6", "4x8", "6x8", "6x10"],
            "unit": "each"
        },
    ],
    "embedded_anchors": [
        {
            "model": "EZ Base",
            "name": "EZ Base Post Anchor",
            "description": "Cast-in-place post anchor",
            "use": "Post to concrete foundation",
            "sizes": ["4x4", "4x6", "6x6"],
            "unit": "each"
        },
        {
            "model": "WPA",
            "name": "Wedge Post Anchor",
            "description": "Retrofit post anchor",
            "use": "Post to existing concrete",
            "sizes": ["4x4", "6x6"],
            "unit": "each"
        },
        {
            "model": "HAB",
            "name": "Heavy Anchor Bolt",
            "description": "Heavy-duty anchor bolt",
            "use": "Sill plate to foundation",
            "diameters": ["1/2\"", "5/8\"", "3/4\""],
            "lengths": ["8\"", "10\"", "12\""],
            "unit": "each"
        },
    ],
    "hurricane_products": [
        {
            "model": "HCS",
            "name": "Hurricane Clip Single",
            "description": "Single-sided hurricane clip",
            "use": "Truss to top plate",
            "load": "500 lb",
            "unit": "each"
        },
        {
            "model": "HCD",
            "name": "Hurricane Clip Double",
            "description": "Double-sided hurricane clip",
            "use": "Heavy truss connection",
            "load": "800 lb",
            "unit": "each"
        },
        {
            "model": "TSB",
            "name": "Truss Stabilizer Brace",
            "description": "Temporary bracing system",
            "use": "Truss erection bracing",
            "unit": "each"
        },
    ],
    "hangers": [
        {
            "model": "JH26",
            "name": "Joist Hanger 2x6",
            "description": "Standard joist hanger",
            "use": "2x6 joist to beam",
            "load": "750 lb",
            "unit": "each"
        },
        {
            "model": "JH28",
            "name": "Joist Hanger 2x8",
            "description": "Standard joist hanger",
            "use": "2x8 joist to beam",
            "load": "950 lb",
            "unit": "each"
        },
        {
            "model": "JH210",
            "name": "Joist Hanger 2x10",
            "description": "Standard joist hanger",
            "use": "2x10 joist to beam",
            "load": "1200 lb",
            "unit": "each"
        },
    ]
}

# Common Connector Configurations for Takeoffs
CONNECTOR_CONFIGURATIONS = {
    "roof_truss_package": {
        "name": "Roof Truss Connection Package",
        "description": "Standard connectors for residential roof trusses",
        "items": [
            {"model": "H2.5A", "qty_per_truss": 2, "note": "One each side of truss"},
            {"model": "LSTA12", "qty_per_4_trusses": 1, "note": "Lateral bracing"},
            {"model": "A35", "qty_per_truss": 1, "note": "Blocking connections"},
        ]
    },
    "floor_joist_package": {
        "name": "Floor Joist Connection Package",
        "description": "Standard connectors for floor joists",
        "items": [
            {"model": "LUS210", "qty_per_joist": 2, "note": "Each end of joist"},
            {"model": "A35", "qty_per_10_joists": 4, "note": "Blocking"},
        ]
    },
    "deck_post_package": {
        "name": "Deck Post Connection Package",
        "description": "Connectors for deck posts",
        "items": [
            {"model": "ABU44", "qty_per_post": 1, "note": "Post base"},
            {"model": "BC4", "qty_per_post": 1, "note": "Post cap"},
        ]
    },
    "shear_wall_package": {
        "name": "Shear Wall Connection Package",
        "description": "Holdowns and straps for shear walls",
        "items": [
            {"model": "HDU4", "qty_per_wall_end": 2, "note": "Each end of wall"},
            {"model": "MST37", "qty_per_wall": 4, "note": "Plate straps"},
        ]
    }
}

# Lookup function to get all Simpson products as flat list
def get_all_simpson_products():
    """Returns all Simpson products as a flat list for searching"""
    products = []
    for category, items in SIMPSON_CONNECTORS.items():
        for item in items:
            item['category'] = category
            products.append(item)
    return products

# Lookup function to get Simpson product by model
def get_simpson_by_model(model: str):
    """Look up a Simpson product by model number"""
    for category, items in SIMPSON_CONNECTORS.items():
        for item in items:
            if item['model'].upper() == model.upper():
                return {**item, 'category': category}
    return None

# Lookup function to get MiTek product by model
def get_mitek_by_model(model: str):
    """Look up a MiTek product by model number"""
    for category, items in MITEK_PRODUCTS.items():
        for item in items:
            if item['model'].upper() == model.upper():
                return {**item, 'category': category}
    return None
