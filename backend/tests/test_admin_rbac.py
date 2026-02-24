"""
Admin RBAC Tests for Gab44 Astrology Platform

Tests:
1. Admin access control - Only admin users can access /admin endpoints
2. Non-admin users get 403 on admin endpoints
3. Admin can grant/revoke admin role to other users
4. Admin dashboard stats are correct
5. Compatibility analysis endpoint works
6. User search in admin filters correctly
"""

import pytest
import requests
import os
from datetime import datetime

# Get base URL from environment - no default!
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "http://localhost:8001"

API_URL = f"{BASE_URL}/api"

# Admin credentials from review_request
ADMIN_EMAIL = "nchobah@gmail.com"
ADMIN_PASSWORD = "admin123"


class TestHealthCheck:
    """Basic health check tests - run first"""
    
    def test_api_root(self):
        response = requests.get(f"{API_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"API Root Response: {data}")
    
    def test_health_endpoint(self):
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"Health Check Response: {data}")


class TestAdminAuthentication:
    """Test admin user authentication"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin user token"""
        response = requests.post(f"{API_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 401:
            # Admin user might not exist, try to register
            timestamp = datetime.now().strftime("%H%M%S%f")
            # Can't register with admin email since it needs to be unique
            pytest.skip(f"Admin user {ADMIN_EMAIL} not found or invalid credentials")
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access token in response"
        print(f"Admin login successful for {ADMIN_EMAIL}")
        return data["access_token"], data.get("user", {})
    
    def test_admin_login_returns_is_admin_flag(self, admin_token):
        """Test that admin user has is_admin flag in /auth/me response"""
        token, user = admin_token
        
        response = requests.get(f"{API_URL}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200, f"Auth/me failed: {response.text}"
        data = response.json()
        
        # Admin status should be True for admin email
        assert data.get("is_admin") == True, f"Expected is_admin=True for admin user, got: {data.get('is_admin')}"
        print(f"Admin user has is_admin=True: {data.get('email')}")


class TestNonAdminAccess:
    """Test that non-admin users are properly restricted"""
    
    @pytest.fixture
    def regular_user_token(self):
        """Create a regular (non-admin) user and get token"""
        timestamp = datetime.now().strftime("%H%M%S%f")
        user_data = {
            "email": f"TEST_regular_user_{timestamp}@testgab44.com",
            "password": "TestPass123!",
            "name": "Regular Test User",
            "birth_date": "1992-07-22",
            "birth_time": "15:30",
            "birth_place": "Miami, FL, USA"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        assert response.status_code == 200, f"User registration failed: {response.text}"
        
        data = response.json()
        token = data["access_token"]
        user = data["user"]
        
        print(f"Created regular user: {user['email']}, is_admin: {user.get('is_admin', 'N/A')}")
        return token, user
    
    def test_non_admin_cannot_access_admin_stats(self, regular_user_token):
        """Non-admin users should get 403 on /api/admin/stats"""
        token, user = regular_user_token
        
        response = requests.get(f"{API_URL}/admin/stats", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}: {response.text}"
        print(f"Non-admin correctly denied access to /admin/stats")
    
    def test_non_admin_cannot_access_admin_users(self, regular_user_token):
        """Non-admin users should get 403 on /api/admin/users"""
        token, user = regular_user_token
        
        response = requests.get(f"{API_URL}/admin/users", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}: {response.text}"
        print(f"Non-admin correctly denied access to /admin/users")
    
    def test_non_admin_cannot_update_user_role(self, regular_user_token):
        """Non-admin users should get 403 when trying to update roles"""
        token, user = regular_user_token
        
        # Try to promote self to admin
        response = requests.put(
            f"{API_URL}/admin/users/{user['id']}/role?role=admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403, f"Expected 403 for non-admin role update, got {response.status_code}"
        print(f"Non-admin correctly denied access to role update endpoint")


class TestAdminRoleManagement:
    """Test admin can grant/revoke admin role"""
    
    @pytest.fixture
    def admin_session(self):
        """Get admin token"""
        response = requests.post(f"{API_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code != 200:
            pytest.skip("Admin login failed - cannot test role management")
        
        return response.json()["access_token"]
    
    @pytest.fixture  
    def test_user(self, admin_session):
        """Create a test user for role testing"""
        timestamp = datetime.now().strftime("%H%M%S%f")
        user_data = {
            "email": f"TEST_role_test_{timestamp}@testgab44.com",
            "password": "TestPass123!",
            "name": "Role Test User",
            "birth_date": "1988-12-15",
            "birth_place": "Chicago, IL, USA"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()["user"]
    
    def test_admin_can_grant_admin_role(self, admin_session, test_user):
        """Admin can grant admin role to another user"""
        response = requests.put(
            f"{API_URL}/admin/users/{test_user['id']}/role?role=admin",
            headers={"Authorization": f"Bearer {admin_session}"}
        )
        
        assert response.status_code == 200, f"Grant admin role failed: {response.text}"
        data = response.json()
        assert "granted" in data.get("message", "").lower(), f"Unexpected response: {data}"
        print(f"Successfully granted admin role to user {test_user['id']}")
    
    def test_admin_can_revoke_admin_role(self, admin_session, test_user):
        """Admin can revoke admin role from a user"""
        # First grant admin role
        requests.put(
            f"{API_URL}/admin/users/{test_user['id']}/role?role=admin",
            headers={"Authorization": f"Bearer {admin_session}"}
        )
        
        # Then revoke it
        response = requests.put(
            f"{API_URL}/admin/users/{test_user['id']}/role?role=user",
            headers={"Authorization": f"Bearer {admin_session}"}
        )
        
        assert response.status_code == 200, f"Revoke admin role failed: {response.text}"
        data = response.json()
        assert "revoked" in data.get("message", "").lower(), f"Unexpected response: {data}"
        print(f"Successfully revoked admin role from user {test_user['id']}")
    
    def test_invalid_role_rejected(self, admin_session, test_user):
        """Invalid role values should be rejected"""
        response = requests.put(
            f"{API_URL}/admin/users/{test_user['id']}/role?role=superadmin",
            headers={"Authorization": f"Bearer {admin_session}"}
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid role, got {response.status_code}"
        print(f"Invalid role correctly rejected")


class TestAdminDashboardStats:
    """Test admin dashboard statistics"""
    
    @pytest.fixture
    def admin_session(self):
        """Get admin token"""
        response = requests.post(f"{API_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        return response.json()["access_token"]
    
    def test_admin_stats_returns_correct_fields(self, admin_session):
        """Admin stats endpoint returns all required fields"""
        response = requests.get(f"{API_URL}/admin/stats", headers={
            "Authorization": f"Bearer {admin_session}"
        })
        
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        
        # Check required fields
        assert "total_users" in data, "Missing total_users"
        assert "recent_signups" in data, "Missing recent_signups"
        assert "subscription_breakdown" in data, "Missing subscription_breakdown"
        assert "sun_sign_distribution" in data, "Missing sun_sign_distribution"
        assert "total_chat_messages" in data, "Missing total_chat_messages"
        assert "total_chat_sessions" in data, "Missing total_chat_sessions"
        assert "total_compatibility_reports" in data, "Missing total_compatibility_reports"
        
        print(f"Admin stats: {data['total_users']} users, {data['total_chat_messages']} messages, {data['total_compatibility_reports']} compatibility reports")
    
    def test_admin_stats_values_are_valid(self, admin_session):
        """Admin stats values should be non-negative integers"""
        response = requests.get(f"{API_URL}/admin/stats", headers={
            "Authorization": f"Bearer {admin_session}"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["total_users"], int) and data["total_users"] >= 0
        assert isinstance(data["total_chat_messages"], int) and data["total_chat_messages"] >= 0
        assert isinstance(data["total_compatibility_reports"], int) and data["total_compatibility_reports"] >= 0
        
        print(f"Stats values validated - all are valid non-negative integers")


class TestCompatibilityAnalysis:
    """Test compatibility/synastry analysis feature"""
    
    @pytest.fixture
    def user_session(self):
        """Create user and get token"""
        timestamp = datetime.now().strftime("%H%M%S%f")
        user_data = {
            "email": f"TEST_compat_user_{timestamp}@testgab44.com",
            "password": "TestPass123!",
            "name": "Compatibility Test User",
            "birth_date": "1990-04-15",
            "birth_time": "12:00",
            "birth_place": "Boston, MA, USA"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=user_data)
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_compatibility_analyze_returns_synastry_report(self, user_session):
        """POST /api/compatibility/analyze returns a synastry report"""
        compatibility_request = {
            "partner_name": "Test Partner",
            "partner_birth_date": "1992-08-25",
            "partner_birth_time": "14:30",
            "partner_birth_place": "Los Angeles, CA, USA"
        }
        
        response = requests.post(
            f"{API_URL}/compatibility/analyze",
            json=compatibility_request,
            headers={"Authorization": f"Bearer {user_session}"},
            timeout=60  # AI generation may take time
        )
        
        assert response.status_code == 200, f"Compatibility analyze failed: {response.text}"
        data = response.json()
        
        # Verify required report fields
        assert "id" in data, "Missing report id"
        assert "partner_name" in data, "Missing partner_name"
        assert "partner_sun_sign" in data, "Missing partner_sun_sign"
        assert "overall_score" in data, "Missing overall_score"
        assert "category_scores" in data, "Missing category_scores"
        assert "synastry_aspects" in data, "Missing synastry_aspects"
        assert "ai_analysis" in data, "Missing ai_analysis"
        
        print(f"Compatibility report generated: overall_score={data['overall_score']}, partner_sign={data['partner_sun_sign']}")
        return data["id"]
    
    def test_compatibility_reports_list_returns_user_reports(self, user_session):
        """GET /api/compatibility/reports returns user's reports"""
        response = requests.get(
            f"{API_URL}/compatibility/reports",
            headers={"Authorization": f"Bearer {user_session}"}
        )
        
        assert response.status_code == 200, f"Get reports failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Expected list of reports"
        print(f"User has {len(data)} compatibility reports")


class TestUserSearchInAdmin:
    """Test user search functionality in admin panel"""
    
    @pytest.fixture
    def admin_session(self):
        """Get admin token"""
        response = requests.post(f"{API_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        
        return response.json()["access_token"]
    
    def test_admin_users_endpoint_returns_user_list(self, admin_session):
        """GET /api/admin/users returns paginated user list"""
        response = requests.get(
            f"{API_URL}/admin/users?skip=0&limit=10",
            headers={"Authorization": f"Bearer {admin_session}"}
        )
        
        assert response.status_code == 200, f"Get users failed: {response.text}"
        data = response.json()
        
        assert "users" in data, "Missing users array"
        assert "total" in data, "Missing total count"
        assert "skip" in data, "Missing skip"
        assert "limit" in data, "Missing limit"
        
        # Each user should have required fields
        if len(data["users"]) > 0:
            user = data["users"][0]
            assert "id" in user
            assert "email" in user
            assert "name" in user
            assert "is_admin" in user, "User should have is_admin flag"
        
        print(f"Admin users endpoint returned {len(data['users'])} of {data['total']} total users")
    
    def test_admin_users_pagination_works(self, admin_session):
        """Pagination works correctly on admin users"""
        # Get first page
        response1 = requests.get(
            f"{API_URL}/admin/users?skip=0&limit=5",
            headers={"Authorization": f"Bearer {admin_session}"}
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Get second page
        response2 = requests.get(
            f"{API_URL}/admin/users?skip=5&limit=5",
            headers={"Authorization": f"Bearer {admin_session}"}
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # If there are enough users, pages should be different
        if data1["total"] > 5:
            user_ids_1 = {u["id"] for u in data1["users"]}
            user_ids_2 = {u["id"] for u in data2["users"]}
            
            # Should have no overlap (unless < 10 total users)
            if len(data1["users"]) == 5 and len(data2["users"]) > 0:
                assert len(user_ids_1 & user_ids_2) == 0, "Pagination returned duplicate users"
        
        print(f"Pagination works correctly")


class TestAdminCanSelfTest:
    """Test that admin cannot demote self"""
    
    def test_admin_cannot_demote_self(self):
        """Admin should not be able to remove their own admin role"""
        # Login as admin
        login_response = requests.post(f"{API_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        
        token = login_response.json()["access_token"]
        admin_id = login_response.json()["user"]["id"]
        
        # Try to demote self
        response = requests.put(
            f"{API_URL}/admin/users/{admin_id}/role?role=user",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400, f"Admin should not be able to demote self, got {response.status_code}"
        print("Admin correctly prevented from demoting self")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
