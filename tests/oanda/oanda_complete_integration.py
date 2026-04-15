#!/usr/bin/env python3
"""
Complete OANDA Integration
REST v20 API + Streaming API following official documentation
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta


class OANDAv20Client:
    """Complete OANDA v20 API Client"""

    def __init__(self, access_token, account_id, environment="practice"):
        """
        Initialize OANDA client

        Args:
            access_token: Your personal access token from HUB
            account_id: Your account ID from HUB (format: xxx-xxx-xxxxxxx-xxx)
            environment: "live" or "practice"
        """
        self.access_token = access_token
        self.account_id = account_id
        self.environment = environment

        # Set correct URLs based on environment
        if environment == "live":
            self.rest_url = "https://api-fxtrade.oanda.com"
            self.stream_url = "https://stream-fxtrade.oanda.com"
        else:
            self.rest_url = "https://api-fxpractice.oanda.com"
            self.stream_url = "https://stream-fxpractice.oanda.com"

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def get_accounts(self):
        """Get account information"""
        url = f"{self.rest_url}/v20/accounts"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"📡 Accounts request - Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                print(f"✅ Found {len(accounts)} accounts")
                for account in accounts:
                    print(f"   Account ID: {account.get('id')}")
                    print(f"   Currency: {account.get('currency')}")
                    print(f"   Balance: {account.get('balance')}")
                return accounts
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None

    def get_account_details(self):
        """Get specific account details"""
        url = f"{self.rest_url}/v20/accounts/{self.account_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"📡 Account details request - Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                account = data.get("account", {})
                print(f"✅ Account details retrieved")
                print(f"   ID: {account.get('id')}")
                print(f"   Currency: {account.get('currency')}")
                print(f"   Balance: {account.get('balance')}")
                print(f"   Margin Rate: {account.get('marginRate')}")
                return account
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None

    def get_historical_data(self, instrument, count=100, granularity="H1"):
        """
        Get historical candle data

        Args:
            instrument: Currency pair (e.g., "EUR_USD")
            count: Number of candles to retrieve
            granularity: Timeframe (S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1, H2, H3, H4, H6, H8, H12, D, W, M)
        """
        url = f"{self.rest_url}/v20/instruments/{instrument}/candles"

        params = {
            "count": count,
            "granularity": granularity,
            "price": "M",  # Midpoint prices
        }

        try:
            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            print(f"📡 Historical data request - Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                candles = data.get("candles", [])
                print(f"✅ Retrieved {len(candles)} candles for {instrument}")

                if candles:
                    latest = candles[-1]
                    print(f"   Latest time: {latest.get('time')}")
                    print(f"   Latest close: {latest.get('mid', {}).get('c')}")

                return candles
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None

    def get_live_prices(self, instruments):
        """
        Get real-time prices

        Args:
            instruments: List of instruments (e.g., ["EUR_USD", "GBP_USD"])
        """
        url = f"{self.rest_url}/v20/prices"

        params = {"instruments": ",".join(instruments)}

        try:
            response = requests.get(
                url, headers=self.headers, params=params, timeout=10
            )
            print(f"📡 Live prices request - Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                prices = data.get("prices", [])
                print(f"✅ Retrieved {len(prices)} live prices")

                for price in prices:
                    instrument = price.get("instrument")
                    bid = price.get("bids", [{}])[0].get("price")
                    ask = price.get("asks", [{}])[0].get("price")
                    print(f"   {instrument}: Bid={bid}, Ask={ask}")

                return prices
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None

    def get_instruments(self):
        """Get available instruments"""
        url = f"{self.rest_url}/v20/accounts/{self.account_id}/instruments"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"📡 Instruments request - Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                instruments = data.get("instruments", [])
                print(f"✅ Found {len(instruments)} instruments")

                # Show first 10 instruments
                for i, instrument in enumerate(instruments[:10]):
                    print(
                        f"   {i+1}. {instrument.get('name')} ({instrument.get('type')})"
                    )

                return instruments
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None


def test_complete_integration():
    """Test complete OANDA integration"""

    print("🔍 Complete OANDA v20 API Integration Test")
    print("=" * 60)
    print("Testing REST API endpoints following official documentation")
    print()

    # Get credentials from user
    print("📋 Please provide your OANDA credentials:")
    print("(Get these from OANDA HUB > Tools > API)")
    print()

    access_token = input("Enter your Personal Access Token: ").strip()
    account_id = input("Enter your Account ID (xxx-xxx-xxxxxxx-xxx): ").strip()
    environment = input("Enter environment (live/practice): ").strip().lower()

    if not access_token or not account_id:
        print("❌ Missing required credentials")
        return

    print(f"\n🔧 Testing with:")
    print(f"   Environment: {environment}")
    print(f"   Account ID: {account_id}")
    print(f"   Token: {access_token[:10]}...{access_token[-10:]}")
    print()

    # Initialize client
    client = OANDAv20Client(access_token, account_id, environment)

    # Test 1: Get accounts
    print("📊 Step 1: Testing account access...")
    accounts = client.get_accounts()

    if accounts:
        print("✅ Account access successful!")

        # Test 2: Get account details
        print("\n📊 Step 2: Testing account details...")
        account_details = client.get_account_details()

        if account_details:
            print("✅ Account details successful!")

            # Test 3: Get available instruments
            print("\n📊 Step 3: Testing instruments...")
            instruments = client.get_instruments()

            if instruments:
                print("✅ Instruments retrieved successfully!")

                # Test 4: Get historical data
                print("\n📊 Step 4: Testing historical data...")
                test_instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]

                for instrument in test_instruments:
                    print(f"\n   Testing {instrument}...")
                    candles = client.get_historical_data(
                        instrument, count=10, granularity="H1"
                    )

                    if candles:
                        print(
                            f"   ✅ {instrument} historical data retrieved successfully"
                        )
                        break
                    else:
                        print(f"   ❌ {instrument} failed, trying next...")

                # Test 5: Get live prices
                print("\n📊 Step 5: Testing live prices...")
                live_prices = client.get_live_prices(["EUR_USD", "GBP_USD"])

                if live_prices:
                    print("✅ Live prices retrieved successfully!")

                print("\n🎉 Complete OANDA integration test completed!")
                print("Your credentials are working correctly.")
                print("\n📈 Ready to implement trading strategies!")

            else:
                print("❌ Instruments failed")
        else:
            print("❌ Account details failed")
    else:
        print("❌ Account access failed")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your token is generated from HUB > Tools > API")
        print("2. Verify your account ID format: xxx-xxx-xxxxxxx-xxx")
        print("3. Ensure you're using the correct environment (live/practice)")
        print("4. Check if your account is properly set up in OANDA HUB")
        print("5. Verify your account has proper permissions")


def main():
    """Main function"""
    test_complete_integration()


if __name__ == "__main__":
    main()
