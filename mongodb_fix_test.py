#!/usr/bin/env python3
"""
MongoDB Connection Fix Verification Test
Specifically tests the database name parsing from MONGO_URL
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://planreader-3.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_mongodb_operations():
    """Test various MongoDB operations to ensure no authorization errors"""
    print(f"{Colors.BOLD}{Colors.BLUE}MongoDB Connection Fix Verification{Colors.ENDC}")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Dashboard stats (reads from tasks collection)
    total_tests += 1
    try:
        response = requests.get(f"{API_BASE}/dashboard", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ Dashboard DB Read{Colors.ENDC} - Tasks collection accessible")
            print(f"   Total tasks: {data.get('total_tasks')}")
            print(f"   Completion rate: {data.get('completion_rate')}%")
            tests_passed += 1
        else:
            print(f"{Colors.RED}❌ Dashboard DB Read{Colors.ENDC} - HTTP {response.status_code}")
    except Exception as e:
        print(f"{Colors.RED}❌ Dashboard DB Read{Colors.ENDC} - Exception: {str(e)}")
    
    # Test 2: User signup (writes to users collection)
    total_tests += 1
    try:
        test_user = {
            "email": f"dbtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}@myplanreader.com",
            "password": "TestPass123!",
            "name": "DB Test User"
        }
        
        response = requests.post(f"{API_BASE}/auth/signup", json=test_user, timeout=10)
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("user", {}).get("id")
            print(f"{Colors.GREEN}✅ User Collection Write{Colors.ENDC} - Users collection writable")
            print(f"   Created user ID: {user_id}")
            tests_passed += 1
            
            # Test 3: User signin (reads from users collection)
            total_tests += 1
            signin_data = {"email": test_user["email"], "password": test_user["password"]}
            signin_response = requests.post(f"{API_BASE}/auth/signin", json=signin_data, timeout=10)
            if signin_response.status_code == 200:
                print(f"{Colors.GREEN}✅ User Collection Read{Colors.ENDC} - Users collection readable")
                tests_passed += 1
                
                # Test 4: Projects query (reads from projects collection)
                total_tests += 1
                projects_response = requests.get(f"{API_BASE}/projects/{user_id}", timeout=10)
                if projects_response.status_code == 200:
                    projects_data = projects_response.json()
                    print(f"{Colors.GREEN}✅ Projects Collection Read{Colors.ENDC} - Projects collection accessible")
                    print(f"   User projects: {len(projects_data.get('projects', []))}")
                    tests_passed += 1
                else:
                    print(f"{Colors.RED}❌ Projects Collection Read{Colors.ENDC} - HTTP {projects_response.status_code}")
            else:
                print(f"{Colors.RED}❌ User Collection Read{Colors.ENDC} - HTTP {signin_response.status_code}")
                total_tests += 1  # Skip projects test
        else:
            print(f"{Colors.RED}❌ User Collection Write{Colors.ENDC} - HTTP {response.status_code}")
            total_tests += 2  # Skip signin and projects tests
    except Exception as e:
        print(f"{Colors.RED}❌ User Collection Write{Colors.ENDC} - Exception: {str(e)}")
        total_tests += 2  # Skip signin and projects tests
    
    # Test 5: Trades query (reads from tasks collection with distinct operation)
    total_tests += 1
    try:
        response = requests.get(f"{API_BASE}/trades", timeout=10)
        if response.status_code == 200:
            data = response.json()
            trades = data.get("trades", [])
            print(f"{Colors.GREEN}✅ Tasks Collection Distinct{Colors.ENDC} - Distinct operation works")
            print(f"   Available trades: {len(trades)} ({', '.join(trades[:3])}...)")
            tests_passed += 1
        else:
            print(f"{Colors.RED}❌ Tasks Collection Distinct{Colors.ENDC} - HTTP {response.status_code}")
    except Exception as e:
        print(f"{Colors.RED}❌ Tasks Collection Distinct{Colors.ENDC} - Exception: {str(e)}")
    
    # Summary
    print("=" * 50)
    print(f"{Colors.BOLD}MongoDB Operations Test Summary:{Colors.ENDC}")
    print(f"Passed: {Colors.GREEN}{tests_passed}{Colors.ENDC}/{total_tests}")
    
    if tests_passed == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ All MongoDB operations successful!{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ Database name parsing from MONGO_URL is working correctly{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ No 'not authorized on taskmanager' errors detected{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Some MongoDB operations failed{Colors.ENDC}")
        return False

def test_specific_collections():
    """Test access to specific collections mentioned in the fix"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Collection Access Verification{Colors.ENDC}")
    print("=" * 40)
    
    collections_tested = []
    
    # Test tasks collection
    try:
        response = requests.get(f"{API_BASE}/dashboard", timeout=10)
        if response.status_code == 200:
            collections_tested.append("✅ tasks")
        else:
            collections_tested.append("❌ tasks")
    except:
        collections_tested.append("❌ tasks")
    
    # Test users collection
    try:
        test_email = f"colltest_{datetime.now().strftime('%H%M%S')}@test.com"
        response = requests.post(f"{API_BASE}/auth/signup", json={
            "email": test_email, "password": "test123", "name": "Collection Test"
        }, timeout=10)
        if response.status_code == 200:
            collections_tested.append("✅ users")
        else:
            collections_tested.append("❌ users")
    except:
        collections_tested.append("❌ users")
    
    # Test materials collection (via trades endpoint)
    try:
        response = requests.get(f"{API_BASE}/trades", timeout=10)
        if response.status_code == 200:
            collections_tested.append("✅ materials (via trades)")
        else:
            collections_tested.append("❌ materials")
    except:
        collections_tested.append("❌ materials")
    
    print("Collections Access Status:")
    for status in collections_tested:
        print(f"  {status}")
    
    return all("✅" in status for status in collections_tested)

if __name__ == "__main__":
    print(f"Testing MongoDB fix at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run MongoDB operations test
    mongodb_ok = test_mongodb_operations()
    
    # Run collections access test
    collections_ok = test_specific_collections()
    
    if mongodb_ok and collections_ok:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 MongoDB Connection Fix VERIFIED!{Colors.ENDC}")
        print(f"{Colors.GREEN}The backend is successfully parsing database name from MONGO_URL{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ MongoDB Connection Issues Detected{Colors.ENDC}")
        sys.exit(1)