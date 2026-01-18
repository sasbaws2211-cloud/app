import requests
import sys
import json
from datetime import datetime
from typing import Optional

class SusuFlowAPITester:
    def __init__(self, base_url="https://momogroup.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@test.com"
        self.test_user_phone = f"+233{datetime.now().strftime('%H%M%S')}000"
        self.test_user_name = "Test User"
        self.test_password = "TestPass123!"
        self.group_id = None
        self.invite_code = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
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
                    return success, response.json() if response.content else {}
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_user_registration(self):
        """Test user registration"""
        user_data = {
            "email": self.test_user_email,
            "phone": self.test_user_phone,
            "name": self.test_user_name,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            201,
            data=user_data
        )
        
        if success and 'id' in response:
            self.user_id = response['id']
            print(f"   User ID: {self.user_id}")
        
        return success

    def test_user_login(self):
        """Test user login and get token"""
        login_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token received: {self.token[:20]}...")
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_get_wallet(self):
        """Test getting user wallet"""
        success, response = self.run_test(
            "Get User Wallet",
            "GET",
            "wallet",
            200
        )
        
        if success:
            print(f"   Wallet Balance: GH¢ {response.get('balance', 0)}")
        
        return success

    def test_deposit_money(self):
        """Test deposit money to wallet"""
        deposit_data = {
            "amount": 100.0,
            "phone_number": self.test_user_phone,
            "provider": "MTN"
        }
        
        success, response = self.run_test(
            "Deposit Money",
            "POST",
            "wallet/deposit",
            200,
            data=deposit_data
        )
        
        if success:
            print(f"   Transaction ID: {response.get('id')}")
            print(f"   Status: {response.get('status')}")
        
        return success

    def test_withdraw_money(self):
        """Test withdraw money from wallet"""
        withdraw_data = {
            "amount": 20.0,
            "phone_number": self.test_user_phone,
            "provider": "MTN"
        }
        
        success, response = self.run_test(
            "Withdraw Money",
            "POST",
            "wallet/withdraw",
            200,
            data=withdraw_data
        )
        
        if success:
            print(f"   Transaction ID: {response.get('id')}")
            print(f"   Status: {response.get('status')}")
        
        return success

    def test_create_group(self):
        """Test creating a new group"""
        group_data = {
            "name": f"Test Group {datetime.now().strftime('%H%M%S')}",
            "description": "Test group for API testing",
            "contribution_amount": 50.0,
            "contribution_frequency": "monthly"
        }
        
        success, response = self.run_test(
            "Create Group",
            "POST",
            "groups",
            201,
            data=group_data
        )
        
        if success and 'id' in response:
            self.group_id = response['id']
            self.invite_code = response.get('invite_code')
            print(f"   Group ID: {self.group_id}")
            print(f"   Invite Code: {self.invite_code}")
        
        return success

    def test_get_user_groups(self):
        """Test getting user's groups"""
        success, response = self.run_test(
            "Get User Groups",
            "GET",
            "groups",
            200
        )
        
        if success:
            print(f"   Number of groups: {len(response)}")
        
        return success

    def test_get_group_detail(self):
        """Test getting specific group details"""
        if not self.group_id:
            print("❌ Skipping - No group ID available")
            return False
            
        success, response = self.run_test(
            "Get Group Detail",
            "GET",
            f"groups/{self.group_id}",
            200
        )
        
        if success:
            print(f"   Group Name: {response.get('name')}")
            print(f"   Invite Code: {response.get('invite_code')}")
        
        return success

    def test_contribute_to_group(self):
        """Test contributing to group"""
        if not self.group_id:
            print("❌ Skipping - No group ID available")
            return False
            
        contribution_data = {
            "group_id": self.group_id,
            "amount": 25.0
        }
        
        success, response = self.run_test(
            "Contribute to Group",
            "POST",
            f"groups/{self.group_id}/contribute",
            200,
            data=contribution_data
        )
        
        if success:
            print(f"   Contribution Amount: GH¢ {response.get('amount')}")
            print(f"   Status: {response.get('status')}")
        
        return success

    def test_get_group_transactions(self):
        """Test getting group transaction ledger"""
        if not self.group_id:
            print("❌ Skipping - No group ID available")
            return False
            
        success, response = self.run_test(
            "Get Group Transactions",
            "GET",
            f"groups/{self.group_id}/transactions",
            200
        )
        
        if success:
            print(f"   Number of transactions: {len(response)}")
        
        return success

    def test_get_user_transactions(self):
        """Test getting user's transaction history"""
        success, response = self.run_test(
            "Get User Transactions",
            "GET",
            "transactions",
            200
        )
        
        if success:
            print(f"   Number of transactions: {len(response)}")
        
        return success

    def test_get_group_messages(self):
        """Test getting group messages"""
        if not self.group_id:
            print("❌ Skipping - No group ID available")
            return False
            
        success, response = self.run_test(
            "Get Group Messages",
            "GET",
            f"groups/{self.group_id}/messages",
            200
        )
        
        if success:
            print(f"   Number of messages: {len(response)}")
        
        return success

    def test_join_group_with_invalid_code(self):
        """Test joining group with invalid invite code"""
        success, response = self.run_test(
            "Join Group (Invalid Code)",
            "POST",
            "groups/join/INVALID123",
            404
        )
        return success

def main():
    print("🚀 Starting SusuFlow API Testing...")
    print("=" * 60)
    
    tester = SusuFlowAPITester()
    
    # Test sequence
    test_results = []
    
    # Basic API tests
    test_results.append(("Root Endpoint", tester.test_root_endpoint()))
    
    # Authentication tests
    test_results.append(("User Registration", tester.test_user_registration()))
    test_results.append(("User Login", tester.test_user_login()))
    test_results.append(("Get Current User", tester.test_get_current_user()))
    
    # Wallet tests
    test_results.append(("Get Wallet", tester.test_get_wallet()))
    test_results.append(("Deposit Money", tester.test_deposit_money()))
    test_results.append(("Withdraw Money", tester.test_withdraw_money()))
    
    # Group tests
    test_results.append(("Create Group", tester.test_create_group()))
    test_results.append(("Get User Groups", tester.test_get_user_groups()))
    test_results.append(("Get Group Detail", tester.test_get_group_detail()))
    test_results.append(("Contribute to Group", tester.test_contribute_to_group()))
    test_results.append(("Get Group Transactions", tester.test_get_group_transactions()))
    
    # Transaction tests
    test_results.append(("Get User Transactions", tester.test_get_user_transactions()))
    
    # Chat tests
    test_results.append(("Get Group Messages", tester.test_get_group_messages()))
    
    # Error handling tests
    test_results.append(("Join Invalid Group", tester.test_join_group_with_invalid_code()))
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall: {tester.tests_passed}/{tester.tests_run} tests passed")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend API testing completed successfully!")
        return 0
    else:
        print("⚠️  Backend has significant issues that need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())