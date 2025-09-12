import requests
import sys
from datetime import datetime, timedelta
import json

class TripPlannerAPITester:
    def __init__(self, base_url="https://voyage-assist-10.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - {name}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ FAILED - {name}")
                print(f"   Expected status: {expected_status}, got: {response.status_code}")
                print(f"   Response: {response.text[:500]}...")

            return success, response.json() if success and response.text else {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - {name} - Request timed out after {timeout}s")
            return False, {}
        except Exception as e:
            print(f"❌ FAILED - {name} - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        return self.run_test("Health Check", "GET", "", 200)

    def test_popular_destinations(self):
        """Test popular destinations endpoint"""
        success, response = self.run_test("Popular Destinations", "GET", "popular-destinations", 200)
        if success and 'destinations' in response:
            destinations = response['destinations']
            print(f"   Found {len(destinations)} destinations")
            if destinations:
                print(f"   Sample destination: {destinations[0]['name']} - {destinations[0]['country']}")
        return success

    def test_weather_endpoint(self, location="Paris"):
        """Test weather endpoint"""
        success, response = self.run_test(f"Weather for {location}", "GET", f"weather/{location}", 200, timeout=15)
        if success:
            print(f"   Weather: {response.get('temperature', 'N/A')}°C, {response.get('condition', 'N/A')}")
            print(f"   Forecast days: {len(response.get('forecast_days', []))}")
        return success

    def test_trip_search(self):
        """Test trip search with Paris"""
        # Calculate dates
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = datetime.now() + timedelta(days=2)
        
        search_data = {
            "destination": "Paris",
            "checkin_date": tomorrow.strftime("%Y-%m-%d"),
            "checkout_date": day_after.strftime("%Y-%m-%d"),
            "guests": 2,
            "budget_range": "mid"
        }
        
        print(f"   Search data: {search_data}")
        success, response = self.run_test("Trip Search - Paris", "POST", "search-trip", 200, data=search_data, timeout=45)
        
        if success:
            print(f"   Destination: {response.get('destination', 'N/A')}")
            print(f"   Hotels found: {len(response.get('best_hotels', []))}")
            print(f"   Weather location: {response.get('weather_info', {}).get('location', 'N/A')}")
            print(f"   AI suggestions length: {len(response.get('ai_suggestions', ''))}")
            print(f"   Estimated cost: ${response.get('estimated_total_cost', 'N/A')}")
            
            # Validate response structure
            required_fields = ['destination', 'best_hotels', 'weather_info', 'ai_suggestions', 'estimated_total_cost']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")
                
        return success

    def test_trip_search_different_budgets(self):
        """Test trip search with different budget ranges"""
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = datetime.now() + timedelta(days=2)
        
        budgets = ["low", "mid", "high"]
        all_passed = True
        
        for budget in budgets:
            search_data = {
                "destination": "Tokyo",
                "checkin_date": tomorrow.strftime("%Y-%m-%d"),
                "checkout_date": day_after.strftime("%Y-%m-%d"),
                "guests": 2,
                "budget_range": budget
            }
            
            success, response = self.run_test(f"Trip Search - {budget.title()} Budget", "POST", "search-trip", 200, data=search_data, timeout=30)
            if success:
                hotels = response.get('best_hotels', [])
                if hotels:
                    prices = [hotel['price_per_night'] for hotel in hotels]
                    print(f"   Hotel prices for {budget} budget: ${min(prices)}-${max(prices)}")
            
            all_passed = all_passed and success
            
        return all_passed

    def test_error_handling(self):
        """Test API error handling"""
        print(f"\n🔍 Testing Error Handling...")
        
        # Test invalid location for weather
        success1, _ = self.run_test("Weather - Invalid Location", "GET", "weather/InvalidLocationXYZ123", 404)
        
        # Test invalid trip search data
        invalid_data = {
            "destination": "",
            "checkin_date": "invalid-date",
            "checkout_date": "2024-01-01",
            "guests": -1,
            "budget_range": "invalid"
        }
        success2, _ = self.run_test("Trip Search - Invalid Data", "POST", "search-trip", 422, data=invalid_data)
        
        return success1 and success2

def main():
    print("🚀 Starting Trip Planner API Tests")
    print("=" * 50)
    
    tester = TripPlannerAPITester()
    
    # Run all tests
    tests = [
        tester.test_health_check,
        tester.test_popular_destinations,
        lambda: tester.test_weather_endpoint("Paris"),
        lambda: tester.test_weather_endpoint("Tokyo"),
        tester.test_trip_search,
        tester.test_trip_search_different_budgets,
        tester.test_error_handling,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "0%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())