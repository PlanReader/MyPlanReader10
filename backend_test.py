#!/usr/bin/env python3
"""
MyPlanReader Backend API Test Suite
Tests MongoDB connection fix and all API endpoints
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://planreader-3.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_test(test_name, status, details=""):
    """Log test results with colors"""
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    print(f"{color}[{status}]{Colors.ENDC} {test_name}")
    if details:
        print(f"    {details}")

def test_health_check():
    """Test 1: Health Check - GET /api/health"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                log_test("Health Check", "PASS", f"Status: {data.get('message')}")
                return True
            else:
                log_test("Health Check", "FAIL", f"Unexpected response: {data}")
                return False
        else:
            log_test("Health Check", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Health Check", "FAIL", f"Exception: {str(e)}")
        return False

def test_dashboard():
    """Test 2: Dashboard - GET /api/dashboard (requires DB access)"""
    try:
        response = requests.get(f"{API_BASE}/dashboard", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["total_tasks", "status_breakdown", "priority_breakdown", "completion_rate"]
            if all(field in data for field in required_fields):
                log_test("Dashboard DB Access", "PASS", f"Total tasks: {data.get('total_tasks')}, Completion rate: {data.get('completion_rate')}%")
                return True
            else:
                log_test("Dashboard DB Access", "FAIL", f"Missing required fields in response: {data}")
                return False
        else:
            log_test("Dashboard DB Access", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Dashboard DB Access", "FAIL", f"Exception: {str(e)}")
        return False

def test_pricing():
    """Test 3: Pricing - GET /api/pricing"""
    try:
        response = requests.get(f"{API_BASE}/pricing", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["base_trade", "add_ons", "max_pages", "currency"]
            if all(field in data for field in required_fields):
                base_price = data.get("base_trade", {}).get("price", 0)
                log_test("Pricing Configuration", "PASS", f"Base trade price: ${base_price}, Max pages: {data.get('max_pages')}")
                return True
            else:
                log_test("Pricing Configuration", "FAIL", f"Missing required fields in response: {data}")
                return False
        else:
            log_test("Pricing Configuration", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Pricing Configuration", "FAIL", f"Exception: {str(e)}")
        return False

def test_trades():
    """Test 4: Trades List - GET /api/trades"""
    try:
        response = requests.get(f"{API_BASE}/trades", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "trades" in data and isinstance(data["trades"], list):
                trades_count = len(data["trades"])
                log_test("Trades List", "PASS", f"Available trades: {trades_count} - {', '.join(data['trades'][:3])}...")
                return True
            else:
                log_test("Trades List", "FAIL", f"Invalid response format: {data}")
                return False
        else:
            log_test("Trades List", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Trades List", "FAIL", f"Exception: {str(e)}")
        return False

def test_user_signup():
    """Test 5a: User Signup - POST /api/auth/signup"""
    try:
        # Use realistic test data
        test_user = {
            "email": "contractor@myplanreader.com",
            "password": "SecurePass123!",
            "name": "John Contractor"
        }
        
        response = requests.post(f"{API_BASE}/auth/signup", json=test_user, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "user" in data:
                user_id = data["user"].get("id")
                log_test("User Signup", "PASS", f"User created with ID: {user_id}")
                return True, user_id, test_user
            else:
                log_test("User Signup", "FAIL", f"Invalid response format: {data}")
                return False, None, None
        elif response.status_code == 400 and "already registered" in response.text:
            # User already exists, try to sign in instead
            log_test("User Signup", "SKIP", "User already exists, will test signin")
            return "EXISTS", None, test_user
        else:
            log_test("User Signup", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False, None, None
    except Exception as e:
        log_test("User Signup", "FAIL", f"Exception: {str(e)}")
        return False, None, None

def test_user_signin(test_user):
    """Test 5b: User Signin - POST /api/auth/signin"""
    try:
        signin_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        response = requests.post(f"{API_BASE}/auth/signin", json=signin_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "user" in data:
                user_id = data["user"].get("id")
                log_test("User Signin", "PASS", f"User signed in with ID: {user_id}")
                return True, user_id
            else:
                log_test("User Signin", "FAIL", f"Invalid response format: {data}")
                return False, None
        else:
            log_test("User Signin", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        log_test("User Signin", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_user_projects(user_id):
    """Test 6: User Projects - GET /api/projects/{user_id}"""
    try:
        response = requests.get(f"{API_BASE}/projects/{user_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "projects" in data and isinstance(data["projects"], list):
                projects_count = len(data["projects"])
                log_test("User Projects", "PASS", f"User has {projects_count} projects")
                return True
            else:
                log_test("User Projects", "FAIL", f"Invalid response format: {data}")
                return False
        else:
            log_test("User Projects", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("User Projects", "FAIL", f"Exception: {str(e)}")
        return False

def test_stripe_config():
    """Test 7: Stripe Configuration - GET /api/stripe-config"""
    try:
        response = requests.get(f"{API_BASE}/stripe-config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "publishable_key" in data and data["publishable_key"].startswith("pk_"):
                log_test("Stripe Configuration", "PASS", f"Publishable key configured: {data['publishable_key'][:20]}...")
                return True
            else:
                log_test("Stripe Configuration", "FAIL", f"Invalid Stripe key format: {data}")
                return False
        else:
            log_test("Stripe Configuration", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Stripe Configuration", "FAIL", f"Exception: {str(e)}")
        return False

# ============================================
# NEW AIA DIVISION AND SIMPSON CATALOG TESTS
# ============================================

def test_aia_divisions():
    """Test 8: AIA Divisions - GET /api/aia-divisions"""
    try:
        response = requests.get(f"{API_BASE}/aia-divisions", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["divisions", "supported", "description"]
            if all(field in data for field in required_fields):
                divisions_count = len(data.get("divisions", {}))
                supported = data.get("supported", [])
                log_test("AIA Divisions", "PASS", f"Found {divisions_count} divisions, supported: {', '.join(supported)}")
                return True
            else:
                log_test("AIA Divisions", "FAIL", f"Missing required fields: {data}")
                return False
        else:
            log_test("AIA Divisions", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("AIA Divisions", "FAIL", f"Exception: {str(e)}")
        return False

def test_aia_division_detail():
    """Test 9: AIA Division Detail - GET /api/aia-divisions/06"""
    try:
        response = requests.get(f"{API_BASE}/aia-divisions/06", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["code", "name", "description"]
            if all(field in data for field in required_fields):
                log_test("AIA Division 06 Detail", "PASS", f"Division 06: {data.get('name')}")
                return True
            else:
                log_test("AIA Division 06 Detail", "FAIL", f"Missing required fields: {data}")
                return False
        else:
            log_test("AIA Division 06 Detail", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("AIA Division 06 Detail", "FAIL", f"Exception: {str(e)}")
        return False

def test_lumber_sizes():
    """Test 10: Lumber Sizes - GET /api/lumber-sizes"""
    try:
        response = requests.get(f"{API_BASE}/lumber-sizes", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "dimensional" in data and "boards" in data and "sheathing" in data:
                dimensional_count = len(data.get("dimensional", []))
                boards_count = len(data.get("boards", []))
                log_test("Lumber Sizes", "PASS", f"Found {dimensional_count} dimensional lumber sizes, {boards_count} board sizes")
                return True
            else:
                log_test("Lumber Sizes", "FAIL", f"Missing lumber categories: {data}")
                return False
        else:
            log_test("Lumber Sizes", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Lumber Sizes", "FAIL", f"Exception: {str(e)}")
        return False

def test_fasteners():
    """Test 11: Fasteners - GET /api/fasteners"""
    try:
        response = requests.get(f"{API_BASE}/fasteners", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "nails" in data and "screws" in data and "bolts" in data:
                nails_count = len(data.get("nails", {}))
                screws_count = len(data.get("screws", {}))
                log_test("Fasteners", "PASS", f"Found {nails_count} nail types, {screws_count} screw types")
                return True
            else:
                log_test("Fasteners", "FAIL", f"Missing fastener categories: {data}")
                return False
        else:
            log_test("Fasteners", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Fasteners", "FAIL", f"Exception: {str(e)}")
        return False

def test_concrete_anchors():
    """Test 12: Concrete Anchors - GET /api/concrete-anchors"""
    try:
        response = requests.get(f"{API_BASE}/concrete-anchors", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "anchors" in data and isinstance(data["anchors"], list):
                anchors_count = len(data.get("anchors", []))
                log_test("Concrete Anchors", "PASS", f"Found {anchors_count} anchor types")
                return True
            else:
                log_test("Concrete Anchors", "FAIL", f"Invalid anchor data format: {data}")
                return False
        else:
            log_test("Concrete Anchors", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Concrete Anchors", "FAIL", f"Exception: {str(e)}")
        return False

def test_simpson_catalog():
    """Test 13: Simpson Catalog - GET /api/simpson-catalog"""
    try:
        response = requests.get(f"{API_BASE}/simpson-catalog", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["connectors", "configurations", "total_products"]
            if all(field in data for field in required_fields):
                total_products = data.get("total_products", 0)
                connectors_count = len(data.get("connectors", {}))
                log_test("Simpson Catalog", "PASS", f"Found {total_products} total products in {connectors_count} categories")
                return True
            else:
                log_test("Simpson Catalog", "FAIL", f"Missing required fields: {data}")
                return False
        else:
            log_test("Simpson Catalog", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Simpson Catalog", "FAIL", f"Exception: {str(e)}")
        return False

def test_simpson_product_h25a():
    """Test 14: Simpson Product H2.5A - GET /api/simpson-product/H2.5A"""
    try:
        response = requests.get(f"{API_BASE}/simpson-product/H2.5A", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["model", "description", "uplift_load"]
            if all(field in data for field in required_fields):
                model = data.get("model")
                description = data.get("description")
                load = data.get("uplift_load")
                log_test("Simpson Product H2.5A", "PASS", f"Model: {model}, Load: {load}")
                return True
            else:
                log_test("Simpson Product H2.5A", "FAIL", f"Missing required fields: {data}")
                return False
        else:
            log_test("Simpson Product H2.5A", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Simpson Product H2.5A", "FAIL", f"Exception: {str(e)}")
        return False

def test_simpson_product_lus210():
    """Test 15: Simpson Product LUS210 - GET /api/simpson-product/LUS210"""
    try:
        response = requests.get(f"{API_BASE}/simpson-product/LUS210", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["model", "description", "load"]
            if all(field in data for field in required_fields):
                model = data.get("model")
                description = data.get("description")
                load = data.get("load")
                log_test("Simpson Product LUS210", "PASS", f"Model: {model}, Load: {load}")
                return True
            else:
                log_test("Simpson Product LUS210", "FAIL", f"Missing required fields: {data}")
                return False
        else:
            log_test("Simpson Product LUS210", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Simpson Product LUS210", "FAIL", f"Exception: {str(e)}")
        return False

def test_mitek_catalog():
    """Test 16: MiTek Catalog - GET /api/mitek-catalog"""
    try:
        response = requests.get(f"{API_BASE}/mitek-catalog", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and len(data) > 0:
                categories = list(data.keys())
                log_test("MiTek Catalog", "PASS", f"Found MiTek products in categories: {', '.join(categories[:3])}")
                return True
            else:
                log_test("MiTek Catalog", "FAIL", f"Empty or invalid catalog data: {data}")
                return False
        else:
            log_test("MiTek Catalog", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("MiTek Catalog", "FAIL", f"Exception: {str(e)}")
        return False

def test_manual_takeoff():
    """Test 17: Manual Takeoff - POST /api/manual-takeoff"""
    try:
        takeoff_data = {
            "total_sqft": 2400,
            "wall_linear_ft": 200,
            "num_stories": 1,
            "foundation_type": "slab",
            "num_doors": 8,
            "num_windows": 14
        }
        
        response = requests.post(f"{API_BASE}/manual-takeoff", json=takeoff_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "project_id", "takeoff"]
            if all(field in data for field in required_fields):
                project_id = data.get("project_id")
                takeoff = data.get("takeoff", {})
                materials_count = len(takeoff.get("materials", []))
                log_test("Manual Takeoff", "PASS", f"Created project {project_id} with {materials_count} material items")
                return True, project_id
            else:
                log_test("Manual Takeoff", "FAIL", f"Missing required fields: {data}")
                return False, None
        else:
            log_test("Manual Takeoff", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        log_test("Manual Takeoff", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_get_takeoff(project_id):
    """Test 18: Get Takeoff - GET /api/takeoff/{project_id}"""
    try:
        response = requests.get(f"{API_BASE}/takeoff/{project_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["project_id", "materials", "status"]
            if all(field in data for field in required_fields):
                materials_count = len(data.get("materials", []))
                status = data.get("status")
                log_test("Get Takeoff Results", "PASS", f"Retrieved {materials_count} materials, status: {status}")
                return True
            else:
                log_test("Get Takeoff Results", "FAIL", f"Missing required fields: {data}")
                return False
        else:
            log_test("Get Takeoff Results", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Get Takeoff Results", "FAIL", f"Exception: {str(e)}")
        return False

def test_division_materials():
    """Test 19-21: Division Materials - GET /api/materials/division-XX"""
    results = []
    
    # Test Division 06 - Wood & Composites
    try:
        response = requests.get(f"{API_BASE}/materials/division-06", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["division", "name", "lumber_sizes", "connectors", "fasteners"]
            if all(field in data for field in required_fields):
                lumber_sizes = data.get("lumber_sizes", {})
                dimensional_count = len(lumber_sizes.get("dimensional", []))
                connectors_count = len(data.get("connectors", {}))
                log_test("Division 06 Materials", "PASS", f"Wood & Composites: {dimensional_count} dimensional lumber, {connectors_count} connector categories")
                results.append(True)
            else:
                log_test("Division 06 Materials", "FAIL", f"Missing required fields: {data}")
                results.append(False)
        else:
            log_test("Division 06 Materials", "FAIL", f"HTTP {response.status_code}: {response.text}")
            results.append(False)
    except Exception as e:
        log_test("Division 06 Materials", "FAIL", f"Exception: {str(e)}")
        results.append(False)
    
    # Test Division 04 - Masonry
    try:
        response = requests.get(f"{API_BASE}/materials/division-04", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["division", "name", "materials"]
            if all(field in data for field in required_fields):
                materials_count = len(data.get("materials", {}))
                log_test("Division 04 Materials", "PASS", f"Masonry: {materials_count} material types")
                results.append(True)
            else:
                log_test("Division 04 Materials", "FAIL", f"Missing required fields: {data}")
                results.append(False)
        else:
            log_test("Division 04 Materials", "FAIL", f"HTTP {response.status_code}: {response.text}")
            results.append(False)
    except Exception as e:
        log_test("Division 04 Materials", "FAIL", f"Exception: {str(e)}")
        results.append(False)
    
    # Test Division 07 - Thermal/Moisture
    try:
        response = requests.get(f"{API_BASE}/materials/division-07", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["division", "name", "materials"]
            if all(field in data for field in required_fields):
                materials_count = len(data.get("materials", {}))
                log_test("Division 07 Materials", "PASS", f"Thermal/Moisture: {materials_count} material types")
                results.append(True)
            else:
                log_test("Division 07 Materials", "FAIL", f"Missing required fields: {data}")
                results.append(False)
        else:
            log_test("Division 07 Materials", "FAIL", f"HTTP {response.status_code}: {response.text}")
            results.append(False)
    except Exception as e:
        log_test("Division 07 Materials", "FAIL", f"Exception: {str(e)}")
        results.append(False)
    
    return results

# ============================================
# DIVISION 09 FIELD STANDARDS TESTS
# ============================================

def test_division_09_field_standards():
    """Test Division 09 Field Standards - Drywall, Paint, Stucco"""
    results = []
    
    # Test Division 09 Materials API
    try:
        response = requests.get(f"{API_BASE}/materials/division-09", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Check for drywall standards
            materials = data.get("materials", {})
            drywall_list = materials.get("drywall", [])
            drywall_accessories = materials.get("drywall_accessories", [])
            paint_list = materials.get("paint", [])
            
            # Verify drywall sqft per sheet = 32 (check first standard drywall sheet)
            drywall_found = False
            for drywall_item in drywall_list:
                if drywall_item.get("sqft") == 32 and "4x8" in drywall_item.get("size", ""):
                    log_test("Division 09 - Drywall Standards", "PASS", f"Drywall: {drywall_item.get('sqft')} sqft per sheet ✓")
                    drywall_found = True
                    break
            
            if not drywall_found:
                log_test("Division 09 - Drywall Standards", "FAIL", "Expected 32 sqft per 4x8 sheet not found")
            results.append(drywall_found)
            
            # Verify mud lbs per sqft = 0.05
            mud_found = False
            for accessory in drywall_accessories:
                if accessory.get("lbs_per_sqft") == 0.05:
                    log_test("Division 09 - Joint Compound Standards", "PASS", f"Joint compound: {accessory.get('lbs_per_sqft')} lbs per sqft ✓")
                    mud_found = True
                    break
            
            if not mud_found:
                log_test("Division 09 - Joint Compound Standards", "FAIL", "Expected 0.05 lbs per sqft not found")
            results.append(mud_found)
            
            # Verify paint coverage = 200 sqft/gallon
            paint_found = False
            for paint_item in paint_list:
                if paint_item.get("coverage") == 200:
                    log_test("Division 09 - Paint Standards", "PASS", f"Paint: {paint_item.get('coverage')} sqft per gallon ✓")
                    paint_found = True
                    break
            
            if not paint_found:
                log_test("Division 09 - Paint Standards", "FAIL", "Expected 200 sqft per gallon not found")
            results.append(paint_found)
                
        else:
            log_test("Division 09 Materials", "FAIL", f"HTTP {response.status_code}: {response.text}")
            results.extend([False, False, False])
    except Exception as e:
        log_test("Division 09 Materials", "FAIL", f"Exception: {str(e)}")
        results.extend([False, False, False])
    
    # Test Division 07 for Stucco Standards
    try:
        response = requests.get(f"{API_BASE}/materials/division-07", timeout=10)
        if response.status_code == 200:
            data = response.json()
            materials = data.get("materials", {})
            stucco_list = materials.get("stucco", [])
            
            # Verify stucco coverage = 22 sqft/bag
            stucco_found = False
            for stucco_item in stucco_list:
                if stucco_item.get("coverage") == 22 and "80lb bag" in stucco_item.get("unit", ""):
                    log_test("Division 07 - Stucco Standards", "PASS", f"Stucco: {stucco_item.get('coverage')} sqft per 80lb bag ✓")
                    stucco_found = True
                    break
            
            if not stucco_found:
                log_test("Division 07 - Stucco Standards", "FAIL", "Expected 22 sqft per 80lb bag not found")
            results.append(stucco_found)
        else:
            log_test("Division 07 - Stucco Standards", "FAIL", f"HTTP {response.status_code}: {response.text}")
            results.append(False)
    except Exception as e:
        log_test("Division 07 - Stucco Standards", "FAIL", f"Exception: {str(e)}")
        results.append(False)
    
    return results

def test_manual_takeoff_field_standards():
    """Test Manual Takeoff with Field Standards Verification"""
    try:
        takeoff_data = {
            "total_sqft": 2400,
            "wall_linear_ft": 200,
            "num_stories": 1,
            "foundation_type": "slab",
            "num_doors": 8,
            "num_windows": 14
        }
        
        response = requests.post(f"{API_BASE}/manual-takeoff", json=takeoff_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            takeoff = data.get("takeoff", {})
            materials = takeoff.get("materials", [])
            summary = takeoff.get("summary", "")
            
            results = []
            
            # Check for whole unit outputs
            drywall_found = False
            joint_compound_found = False
            paint_found = False
            stucco_found = False
            usa_construction_found = False
            
            for material in materials:
                description = material.get("description", "").lower()
                unit = material.get("unit", "").lower()
                quantity = material.get("quantity", 0)
                supplier_notes = material.get("supplier_notes", "")
                
                # Check drywall in whole sheets
                if "drywall" in description and "sheet" in unit:
                    if isinstance(quantity, int) and quantity > 0:
                        log_test("Manual Takeoff - Drywall Sheets", "PASS", f"Drywall: {quantity} whole sheets ✓")
                        drywall_found = True
                    else:
                        log_test("Manual Takeoff - Drywall Sheets", "FAIL", f"Drywall quantity not whole number: {quantity}")
                
                # Check joint compound in whole boxes
                if "joint compound" in description or "mud" in description:
                    if "50lb" in unit or "box" in unit:
                        if isinstance(quantity, int) and quantity > 0:
                            log_test("Manual Takeoff - Joint Compound Boxes", "PASS", f"Joint compound: {quantity} whole 50lb boxes ✓")
                            joint_compound_found = True
                        else:
                            log_test("Manual Takeoff - Joint Compound Boxes", "FAIL", f"Joint compound quantity not whole number: {quantity}")
                
                # Check paint in whole gallons
                if "paint" in description and "gallon" in unit:
                    if isinstance(quantity, int) and quantity > 0:
                        log_test("Manual Takeoff - Paint Gallons", "PASS", f"Paint: {quantity} whole gallons ✓")
                        paint_found = True
                    else:
                        log_test("Manual Takeoff - Paint Gallons", "FAIL", f"Paint quantity not whole number: {quantity}")
                
                # Check stucco in whole bags
                if "stucco" in description and ("80lb" in unit or "bag" in unit):
                    if isinstance(quantity, int) and quantity > 0:
                        log_test("Manual Takeoff - Stucco Bags", "PASS", f"Stucco: {quantity} whole 80lb bags ✓")
                        stucco_found = True
                    else:
                        log_test("Manual Takeoff - Stucco Bags", "FAIL", f"Stucco quantity not whole number: {quantity}")
                
                # Check USA Construction Inc. attribution
                if "USA Construction Inc." in supplier_notes:
                    usa_construction_found = True
            
            # Check summary attribution
            summary_attribution = "Verified Field Standards by USA Construction Inc." in summary
            if summary_attribution:
                log_test("Manual Takeoff - Summary Attribution", "PASS", "Summary contains USA Construction Inc. attribution ✓")
            else:
                log_test("Manual Takeoff - Summary Attribution", "FAIL", f"Missing attribution in summary: {summary}")
            
            # Check supplier notes attribution
            if usa_construction_found:
                log_test("Manual Takeoff - Supplier Attribution", "PASS", "Materials contain USA Construction Inc. attribution ✓")
            else:
                log_test("Manual Takeoff - Supplier Attribution", "FAIL", "Missing USA Construction Inc. in supplier notes")
            
            results = [drywall_found, joint_compound_found, paint_found, stucco_found, usa_construction_found, summary_attribution]
            
            project_id = data.get("project_id")
            return all(results), project_id
        else:
            log_test("Manual Takeoff Field Standards", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        log_test("Manual Takeoff Field Standards", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_session_security():
    """Test Session Security - POST /api/session/purge"""
    try:
        response = requests.post(f"{API_BASE}/session/purge", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["success", "message", "timeout_minutes"]
            if all(field in data for field in required_fields):
                success = data.get("success")
                timeout_minutes = data.get("timeout_minutes")
                message = data.get("message")
                
                if success and timeout_minutes == 10:
                    log_test("Session Security", "PASS", f"Session purge successful, 10-minute timeout confirmed ✓")
                    return True
                else:
                    log_test("Session Security", "FAIL", f"Unexpected response: success={success}, timeout={timeout_minutes}")
                    return False
            else:
                log_test("Session Security", "FAIL", f"Missing required fields: {data}")
                return False
        else:
            log_test("Session Security", "FAIL", f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Session Security", "FAIL", f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}MyPlanReader Backend API Test Suite{Colors.ENDC}")
    print(f"Testing against: {BACKEND_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health Check
    results.append(test_health_check())
    
    # Test 2: Dashboard (DB access)
    results.append(test_dashboard())
    
    # Test 3: Pricing
    results.append(test_pricing())
    
    # Test 4: Trades
    results.append(test_trades())
    
    # Test 5: User Authentication Flow
    signup_result, user_id, test_user = test_user_signup()
    if signup_result == "EXISTS":
        # User exists, test signin
        signin_result, user_id = test_user_signin({
            "email": "contractor@myplanreader.com",
            "password": "SecurePass123!"
        })
        results.append(signin_result)
    elif signup_result:
        # New user created, test signin
        signin_result, user_id = test_user_signin(test_user)
        results.append(True)  # Signup passed
        results.append(signin_result)
    else:
        results.append(False)  # Signup failed
        results.append(False)  # Skip signin
        user_id = None
    
    # Test 6: User Projects (requires user_id)
    if user_id:
        results.append(test_user_projects(user_id))
    else:
        log_test("User Projects", "SKIP", "No user_id available")
        results.append(False)
    
    # Test 7: Stripe Configuration
    results.append(test_stripe_config())
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== NEW AIA DIVISION & SIMPSON CATALOG TESTS ==={Colors.ENDC}")
    
    # Test 8: AIA Divisions
    results.append(test_aia_divisions())
    
    # Test 9: AIA Division Detail
    results.append(test_aia_division_detail())
    
    # Test 10: Lumber Sizes
    results.append(test_lumber_sizes())
    
    # Test 11: Fasteners
    results.append(test_fasteners())
    
    # Test 12: Concrete Anchors
    results.append(test_concrete_anchors())
    
    # Test 13: Simpson Catalog
    results.append(test_simpson_catalog())
    
    # Test 14: Simpson Product H2.5A
    results.append(test_simpson_product_h25a())
    
    # Test 15: Simpson Product LUS210
    results.append(test_simpson_product_lus210())
    
    # Test 16: MiTek Catalog
    results.append(test_mitek_catalog())
    
    # Test 17: Manual Takeoff
    takeoff_result, project_id = test_manual_takeoff()
    results.append(takeoff_result)
    
    # Test 18: Get Takeoff (requires project_id from manual takeoff)
    if project_id:
        results.append(test_get_takeoff(project_id))
    else:
        log_test("Get Takeoff Results", "SKIP", "No project_id available")
        results.append(False)
    
    # Test 19-21: Division Materials
    division_results = test_division_materials()
    results.extend(division_results)
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== DIVISION 09 FIELD STANDARDS TESTS ==={Colors.ENDC}")
    
    # Test Division 09 Field Standards
    field_standards_results = test_division_09_field_standards()
    results.extend(field_standards_results)
    
    # Test Manual Takeoff with Field Standards
    takeoff_standards_result, standards_project_id = test_manual_takeoff_field_standards()
    results.append(takeoff_standards_result)
    
    # Test Session Security
    results.append(test_session_security())
    
    # Summary
    print("=" * 60)
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"{Colors.BOLD}Test Summary:{Colors.ENDC}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.ENDC}/{total}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.ENDC}/{total}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All tests passed! Division 09 field standards and session security working correctly.{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some tests failed. Check the Division 09 field standards and session security endpoints.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())