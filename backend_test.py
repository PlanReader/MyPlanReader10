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
    
    # Summary
    print("=" * 60)
    passed = sum(1 for r in results if r is True)
    total = len(results)
    
    print(f"{Colors.BOLD}Test Summary:{Colors.ENDC}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.ENDC}/{total}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.ENDC}/{total}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All tests passed! MongoDB connection fix is working correctly.{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some tests failed. Check the MongoDB connection and API endpoints.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())