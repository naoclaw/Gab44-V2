"""
Test file for Compatibility/Synastry feature endpoints
Tests:
- POST /api/compatibility/analyze - Create new compatibility report with AI analysis
- GET /api/compatibility/reports - Get user's compatibility reports list
- GET /api/compatibility/reports/{report_id} - Get specific report details
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
ADMIN_EMAIL = "nchobah@gmail.com"
ADMIN_PASSWORD = "admin123"


class TestAuthSetup:
    """Setup: Get authentication token for tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Auth headers for authenticated requests"""
        return {"Authorization": f"Bearer {auth_token}"}


class TestCompatibilityAnalysis(TestAuthSetup):
    """Tests for POST /api/compatibility/analyze endpoint"""
    
    def test_analyze_compatibility_success(self, auth_headers):
        """Test creating a new compatibility report with valid data"""
        # Use unique name to avoid confusion with existing reports
        test_data = {
            "partner_name": "TEST_Partner_Analysis",
            "partner_birth_date": "1995-07-15",
            "partner_birth_time": "14:30",
            "partner_birth_place": "New York, USA"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            json=test_data,
            headers=auth_headers
        )
        
        # Status assertion
        assert response.status_code == 200, f"Analyze failed: {response.text}"
        
        # Data structure assertions
        data = response.json()
        assert "id" in data, "Response missing 'id'"
        assert "user_id" in data, "Response missing 'user_id'"
        assert "partner_name" in data, "Response missing 'partner_name'"
        assert data["partner_name"] == test_data["partner_name"], "Partner name mismatch"
        assert "partner_birth_date" in data, "Response missing 'partner_birth_date'"
        assert "partner_sun_sign" in data, "Response missing 'partner_sun_sign'"
        assert data["partner_sun_sign"] == "Cancer", f"Expected Cancer, got {data['partner_sun_sign']}"  # July 15 = Cancer
        
        # Overall score assertions
        assert "overall_score" in data, "Response missing 'overall_score'"
        assert isinstance(data["overall_score"], (int, float)), "overall_score should be numeric"
        assert 0 <= data["overall_score"] <= 100, "overall_score should be 0-100"
        
        # Category scores assertions
        assert "category_scores" in data, "Response missing 'category_scores'"
        expected_categories = ["romantic", "emotional", "communication", "stability", "karmic"]
        for cat in expected_categories:
            assert cat in data["category_scores"], f"Missing category score: {cat}"
            assert isinstance(data["category_scores"][cat], (int, float)), f"category_scores[{cat}] should be numeric"
        
        # Synastry aspects assertions
        assert "synastry_aspects" in data, "Response missing 'synastry_aspects'"
        assert isinstance(data["synastry_aspects"], list), "synastry_aspects should be a list"
        
        # Strengths and challenges assertions
        assert "strengths" in data, "Response missing 'strengths'"
        assert "challenges" in data, "Response missing 'challenges'"
        assert isinstance(data["strengths"], list), "strengths should be a list"
        assert isinstance(data["challenges"], list), "challenges should be a list"
        
        # AI analysis assertion
        assert "ai_analysis" in data, "Response missing 'ai_analysis'"
        assert isinstance(data["ai_analysis"], str), "ai_analysis should be a string"
        assert len(data["ai_analysis"]) > 50, "ai_analysis seems too short"
        
        # Karmic themes assertion
        assert "karmic_themes" in data, "Response missing 'karmic_themes'"
        assert isinstance(data["karmic_themes"], list), "karmic_themes should be a list"
        
        # Created at assertion
        assert "created_at" in data, "Response missing 'created_at'"
        
        print(f"✅ Compatibility analysis created successfully: {data['id']}")
        print(f"   Partner: {data['partner_name']} ({data['partner_sun_sign']})")
        print(f"   Overall Score: {data['overall_score']}%")
        
        return data["id"]
    
    def test_analyze_missing_required_fields(self, auth_headers):
        """Test that missing required fields return proper error"""
        # Missing partner_name
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            json={
                "partner_birth_date": "1995-07-15",
                "partner_birth_place": "New York, USA"
            },
            headers=auth_headers
        )
        assert response.status_code == 422, "Should return 422 for missing partner_name"
        
        # Missing partner_birth_date
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            json={
                "partner_name": "Test Partner",
                "partner_birth_place": "New York, USA"
            },
            headers=auth_headers
        )
        assert response.status_code == 422, "Should return 422 for missing partner_birth_date"
        
        # Missing partner_birth_place
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            json={
                "partner_name": "Test Partner",
                "partner_birth_date": "1995-07-15"
            },
            headers=auth_headers
        )
        assert response.status_code == 422, "Should return 422 for missing partner_birth_place"
        
        print("✅ Validation correctly rejects missing required fields")
    
    def test_analyze_without_auth(self):
        """Test that analyze endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            json={
                "partner_name": "Test Partner",
                "partner_birth_date": "1995-07-15",
                "partner_birth_place": "New York, USA"
            }
        )
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("✅ Analyze endpoint correctly requires authentication")


class TestCompatibilityReports(TestAuthSetup):
    """Tests for GET /api/compatibility/reports endpoint"""
    
    def test_get_reports_list(self, auth_headers):
        """Test getting the list of compatibility reports"""
        response = requests.get(
            f"{BASE_URL}/api/compatibility/reports",
            headers=auth_headers
        )
        
        # Status assertion
        assert response.status_code == 200, f"Get reports failed: {response.text}"
        
        # Data structure assertions
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            # Check structure of first report
            report = data[0]
            assert "id" in report, "Report missing 'id'"
            assert "partner_name" in report, "Report missing 'partner_name'"
            assert "partner_sun_sign" in report, "Report missing 'partner_sun_sign'"
            assert "overall_score" in report, "Report missing 'overall_score'"
            assert "created_at" in report, "Report missing 'created_at'"
            
            print(f"✅ Found {len(data)} compatibility reports")
            for r in data[:3]:  # Print first 3
                print(f"   - {r['partner_name']} ({r['partner_sun_sign']}): {r['overall_score']}%")
        else:
            print("✅ Reports list returned (empty)")
        
        return data
    
    def test_get_reports_without_auth(self):
        """Test that reports endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/compatibility/reports")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("✅ Reports endpoint correctly requires authentication")


class TestCompatibilityReportDetail(TestAuthSetup):
    """Tests for GET /api/compatibility/reports/{report_id} endpoint"""
    
    def test_get_report_detail(self, auth_headers):
        """Test getting a specific report by ID"""
        # First get the list to find a report ID
        list_response = requests.get(
            f"{BASE_URL}/api/compatibility/reports",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        reports = list_response.json()
        
        if len(reports) == 0:
            pytest.skip("No reports available to test detail view")
        
        report_id = reports[0]["id"]
        
        # Get the detail
        response = requests.get(
            f"{BASE_URL}/api/compatibility/reports/{report_id}",
            headers=auth_headers
        )
        
        # Status assertion
        assert response.status_code == 200, f"Get report detail failed: {response.text}"
        
        # Data structure assertions (same as analyze but from persistence)
        data = response.json()
        assert data["id"] == report_id, "Report ID mismatch"
        assert "partner_name" in data, "Detail missing 'partner_name'"
        assert "overall_score" in data, "Detail missing 'overall_score'"
        assert "category_scores" in data, "Detail missing 'category_scores'"
        assert "synastry_aspects" in data, "Detail missing 'synastry_aspects'"
        assert "strengths" in data, "Detail missing 'strengths'"
        assert "challenges" in data, "Detail missing 'challenges'"
        assert "ai_analysis" in data, "Detail missing 'ai_analysis'"
        
        print(f"✅ Report detail retrieved successfully: {report_id}")
        print(f"   Partner: {data['partner_name']}")
        print(f"   AI Analysis length: {len(data['ai_analysis'])} chars")
    
    def test_get_nonexistent_report(self, auth_headers):
        """Test getting a report that doesn't exist returns 404"""
        fake_id = "nonexistent-report-id-12345"
        response = requests.get(
            f"{BASE_URL}/api/compatibility/reports/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Correctly returns 404 for nonexistent report")
    
    def test_get_report_detail_without_auth(self):
        """Test that report detail endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/compatibility/reports/some-id")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("✅ Report detail endpoint correctly requires authentication")


class TestSunSignCalculation:
    """Tests to verify sun sign calculation for various birth dates"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['access_token']}"}
    
    @pytest.mark.parametrize("birth_date,expected_sign", [
        ("1990-03-25", "Aries"),      # March 25 = Aries
        ("1990-04-22", "Taurus"),     # April 22 = Taurus
        ("1990-06-15", "Gemini"),     # June 15 = Gemini
        ("1990-07-10", "Cancer"),     # July 10 = Cancer
        ("1990-08-15", "Leo"),        # August 15 = Leo
        ("1990-09-10", "Virgo"),      # September 10 = Virgo
        ("1990-10-05", "Libra"),      # October 5 = Libra
        ("1990-11-10", "Scorpio"),    # November 10 = Scorpio
        ("1990-12-05", "Sagittarius"),# December 5 = Sagittarius
        ("1990-01-05", "Capricorn"),  # January 5 = Capricorn
        ("1990-02-05", "Aquarius"),   # February 5 = Aquarius
        ("1990-03-05", "Pisces"),     # March 5 = Pisces
    ])
    def test_sun_sign_calculation(self, auth_headers, birth_date, expected_sign):
        """Test that partner sun sign is calculated correctly"""
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            json={
                "partner_name": f"TEST_Sign_{expected_sign}",
                "partner_birth_date": birth_date,
                "partner_birth_place": "Test City"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Analyze failed for {birth_date}"
        data = response.json()
        assert data["partner_sun_sign"] == expected_sign, f"Expected {expected_sign} for {birth_date}, got {data['partner_sun_sign']}"
        print(f"✅ {birth_date} → {expected_sign} (correct)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
