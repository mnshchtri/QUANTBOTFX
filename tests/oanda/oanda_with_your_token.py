#!/usr/bin/env python3
"""
OANDA Test with Your Token
Using the provided token with comprehensive error handling
"""

import requests
import json
import time
from datetime import datetime, timedelta


class OANDATester:
    """Test OANDA API with your token"""

    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def test_endpoint(self, url, description):
        """Test a specific endpoint"""
        print(f"\n📡 Testing: {description}")
        print(f"   URL: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print("   ✅ Success!")
                return True
            elif response.status_code == 401:
                print("   ❌ Unauthorized - Token issue")
                return False
            elif response.status_code == 403:
                print("   ❌ Forbidden - Permission issue")
                return False
            elif response.status_code == 404:
                print("   ❌ Not Found - Endpoint issue")
                return False
            elif response.status_code == 502:
                print("   ❌ Bad Gateway - OANDA server issue")
                return False
            elif response.status_code == 520:
                print("   ❌ Server Error - OANDA server issue")
                return False
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False

        except requests.exceptions.Timeout:
            print("   ❌ Timeout - Server not responding")
            return False
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection Error - Cannot reach server")
            return False
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False

    def test_all_endpoints(self):
        """Test all OANDA endpoints"""
        print("🔍 Comprehensive OANDA API Test")
        print("=" * 60)
        print(f"Token: {self.access_token[:10]}...{self.access_token[-10:]}")

        # Test both environments
        environments = [
            {
                "name": "fxTrade Practice",
                "base_url": "https://api-fxpractice.oanda.com",
            },
            {"name": "fxTrade Live", "base_url": "https://api-fxtrade.oanda.com"},
        ]

        results = {}

        for env in environments:
            print(f"\n🌐 Testing {env['name']}")
            print("-" * 40)

            base_url = env["base_url"]

            # Test different endpoints
            endpoints = [
                (f"{base_url}/v20/accounts", "Accounts List"),
                (f"{base_url}/v20/accounts", "Accounts (v20)"),
                (f"{base_url}/v1/accounts", "Accounts (v1)"),
                (
                    f"{base_url}/v20/instruments/EUR_USD/candles?count=5",
                    "Historical Data",
                ),
                (f"{base_url}/v20/prices?instruments=EUR_USD", "Live Prices"),
            ]

            env_results = []
            for url, desc in endpoints:
                success = self.test_endpoint(url, desc)
                env_results.append(success)
                time.sleep(1)  # Rate limiting

            results[env["name"]] = env_results

        return results

    def test_alternative_approaches(self):
        """Test alternative approaches"""
        print("\n🔍 Testing Alternative Approaches")
        print("=" * 40)

        # Test with different headers
        print("\n📋 Testing different header configurations...")

        headers_variations = [
            {"Authorization": f"Bearer {self.access_token}"},
            {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
            },
            {
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": "OANDA-API-Client",
            },
        ]

        test_url = "https://api-fxpractice.oanda.com/v20/accounts"

        for i, headers in enumerate(headers_variations, 1):
            print(f"\n   Test {i}: {list(headers.keys())}")
            try:
                response = requests.get(test_url, headers=headers, timeout=10)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Success with this header configuration!")
                    return headers
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

        return None


def main():
    """Main test function"""
    # Use the provided token
    access_token = "e8fdc63989baf7a54fa72f26afb775a4-4d8567bb9a2d4d0e17f7f0ba5f28db61"

    tester = OANDATester(access_token)

    # Test all endpoints
    results = tester.test_all_endpoints()

    # Test alternative approaches
    working_headers = tester.test_alternative_approaches()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    for env_name, env_results in results.items():
        success_count = sum(env_results)
        total_count = len(env_results)
        print(f"\n{env_name}:")
        print(f"   Success: {success_count}/{total_count} endpoints")

        if success_count > 0:
            print("   ✅ Some endpoints working")
        else:
            print("   ❌ All endpoints failing")

    if working_headers:
        print(f"\n✅ Found working header configuration: {list(working_headers.keys())}")
    else:
        print("\n❌ No working header configuration found")

    print("\n💡 Recommendations:")
    print("1. OANDA servers may be experiencing issues")
    print("2. Try again in 30-60 minutes")
    print("3. Consider using alternative data sources")
    print("4. Check OANDA status page for server issues")


if __name__ == "__main__":
    main()
