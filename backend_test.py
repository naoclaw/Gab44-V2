import requests
import sys
import json
from datetime import datetime

class Gab44APITester:
    def __init__(self, base_url="https://gab44-redesign.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n=== HEALTH CHECK TESTS ===")
        self.run_test("API Root", "GET", "", 200)
        self.run_test("Health Check", "GET", "health", 200)

    def test_auth_flow(self):
        """Test authentication flow"""
        print("\n=== AUTHENTICATION TESTS ===")
        
        # Test user registration
        timestamp = datetime.now().strftime("%H%M%S")
        test_user_data = {
            "email": f"test_user_{timestamp}@gab44test.com",
            "password": "TestPass123!",
            "name": "Test User",
            "birth_date": "1990-06-15",
            "birth_time": "14:30",
            "birth_place": "New York, NY, USA",
            "birth_latitude": 40.7128,
            "birth_longitude": -74.0060
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Token obtained: {self.token[:20]}...")
            
            # Test login with same credentials
            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
            
            success, login_response = self.run_test(
                "User Login",
                "POST",
                "auth/login",
                200,
                data=login_data
            )
            
            # Test get current user
            self.run_test(
                "Get Current User",
                "GET",
                "auth/me",
                200
            )
            
            return True
        else:
            print("❌ Registration failed, skipping auth-dependent tests")
            return False

    def test_chat_functionality(self):
        """Test AI chat functionality"""
        print("\n=== CHAT FUNCTIONALITY TESTS ===")
        
        if not self.token:
            print("❌ No auth token, skipping chat tests")
            return
        
        # Test sending a chat message
        chat_data = {
            "message": "Hello, can you tell me about my sun sign?",
            "session_id": None
        }
        
        success, response = self.run_test(
            "Send Chat Message",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        
        if success and 'session_id' in response:
            session_id = response['session_id']
            print(f"   Session ID: {session_id}")
            
            # Test getting chat history
            self.run_test(
                "Get Chat History",
                "GET",
                f"chat/history/{session_id}",
                200
            )
            
            # Test getting chat sessions
            self.run_test(
                "Get Chat Sessions",
                "GET",
                "chat/sessions",
                200
            )

    def test_chart_functionality(self):
        """Test birth chart functionality"""
        print("\n=== BIRTH CHART TESTS ===")
        
        if not self.token:
            print("❌ No auth token, skipping chart tests")
            return
        
        # Test getting user's birth chart
        self.run_test(
            "Get Birth Chart",
            "GET",
            "chart/me",
            200
        )

    def test_transits_functionality(self):
        """Test transits functionality"""
        print("\n=== TRANSITS TESTS ===")
        
        if not self.token:
            print("❌ No auth token, skipping transits tests")
            return
        
        # Test getting upcoming transits
        self.run_test(
            "Get Upcoming Transits",
            "GET",
            "transits/upcoming",
            200
        )

    def test_guidance_functionality(self):
        """Test daily guidance functionality"""
        print("\n=== DAILY GUIDANCE TESTS ===")
        
        if not self.token:
            print("❌ No auth token, skipping guidance tests")
            return
        
        # Test getting daily guidance
        self.run_test(
            "Get Daily Guidance",
            "GET",
            "guidance/daily",
            200
        )

    def test_pricing_info(self):
        """Test pricing information"""
        print("\n=== PRICING TESTS ===")
        
        # Test getting pricing plans (should work without auth)
        self.run_test(
            "Get Pricing Plans",
            "GET",
            "pricing",
            200
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Gab44 API Tests...")
        print(f"Testing against: {self.base_url}")
        
        # Basic health checks
        self.test_health_check()
        
        # Authentication flow
        auth_success = self.test_auth_flow()
        
        if auth_success:
            # Test authenticated endpoints
            self.test_chat_functionality()
            self.test_chart_functionality()
            self.test_transits_functionality()
            self.test_guidance_functionality()
        
        # Test public endpoints
        self.test_pricing_info()
        
        # Print summary
        print(f"\n📊 TEST SUMMARY")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = Gab44APITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())