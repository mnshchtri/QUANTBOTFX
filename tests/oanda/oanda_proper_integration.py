#!/usr/bin/env python3
"""
Proper OANDA Integration
Following official OANDA v20 API documentation
"""

import requests
import json
import os
from datetime import datetime, timedelta

class OANDAv20Client:
    """OANDA v20 API Client following official documentation"""
    
    def __init__(self, access_token, account_id, environment="live"):
        """
        Initialize OANDA client
        
        Args:
            access_token: Your personal access token from HUB
            account_id: Your account ID from HUB (format: xxx-xxx-xxxxxxx-xxx)
            environment: "live" or "practice"
        """
        self.access_token = access_token
        self.account_id = account_id
        
        # Set correct URLs based on environment
        if environment == "live":
            self.base_url = "https://api-fxtrade.oanda.com/v20"
        else:
            self.base_url = "https://api-fxpractice.oanda.com/v20"
        
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_accounts(self):
        """Get account information"""
        url = f"{self.base_url}/accounts"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"📡 Accounts request - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
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
        url = f"{self.base_url}/accounts/{self.account_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"📡 Account details request - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                account = data.get('account', {})
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
        url = f"{self.base_url}/instruments/{instrument}/candles"
        
        params = {
            "count": count,
            "granularity": granularity,
            "price": "M"  # Midpoint prices
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            print(f"📡 Historical data request - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                candles = data.get('candles', [])
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

def test_oanda_integration():
    """Test OANDA integration with proper setup"""
    
    print("🔍 Testing OANDA v20 API Integration")
    print("=" * 60)
    print("Following official OANDA documentation guidelines")
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
            
            # Test 3: Get historical data
            print("\n📊 Step 3: Testing historical data...")
            instruments_to_test = ["EUR_USD", "GBP_USD", "USD_JPY"]
            
            for instrument in instruments_to_test:
                print(f"\n   Testing {instrument}...")
                candles = client.get_historical_data(instrument, count=10, granularity="H1")
                
                if candles:
                    print(f"   ✅ {instrument} data retrieved successfully")
                    break
                else:
                    print(f"   ❌ {instrument} failed, trying next...")
            
            print("\n🎉 OANDA integration test completed!")
            print("Your credentials are working correctly.")
            
        else:
            print("❌ Account details failed")
    else:
        print("❌ Account access failed")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your token is generated from HUB > Tools > API")
        print("2. Verify your account ID format: xxx-xxx-xxxxxxx-xxx")
        print("3. Ensure you're using the correct environment (live/practice)")
        print("4. Check if your account is properly set up in OANDA HUB")

def main():
    """Main function"""
    test_oanda_integration()

if __name__ == "__main__":
    main() 