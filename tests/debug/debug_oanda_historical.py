#!/usr/bin/env python3
"""
Debug OANDA Historical Data
Test different parameters and timeframes to identify the issue
"""

import os
import json
from datetime import datetime, timedelta
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles


def debug_historical_data():
    """Debug historical data retrieval with different parameters"""

    api_token = "e8fdc63989baf7a54fa72f26afb775a4-4d8567bb9a2d4d0e17f7f0ba5f28db61"

    print("🔍 Debugging OANDA Historical Data")
    print("=" * 60)

    # Initialize API with live environment
    api = API(access_token=api_token, environment="live")

    # Test different scenarios
    test_cases = [
        {
            "name": "Recent 1-hour candles (count)",
            "params": {"count": 10, "granularity": "H1", "price": "M"},
        },
        {
            "name": "Recent 15-minute candles (count)",
            "params": {"count": 10, "granularity": "M15", "price": "M"},
        },
        {
            "name": "Specific date range (1 hour)",
            "params": {
                "from": "2025-01-20T00:00:00Z",
                "to": "2025-01-20T01:00:00Z",
                "granularity": "H1",
                "price": "M",
            },
        },
        {
            "name": "Specific date range (15 minutes)",
            "params": {
                "from": "2025-01-20T00:00:00Z",
                "to": "2025-01-20T01:00:00Z",
                "granularity": "M15",
                "price": "M",
            },
        },
        {
            "name": "Today's data (count)",
            "params": {"count": 24, "granularity": "H1", "price": "M"},
        },
        {
            "name": "Last week data (count)",
            "params": {"count": 168, "granularity": "H1", "price": "M"},
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print("-" * 40)

        try:
            request = InstrumentsCandles(
                instrument="EUR_USD", params=test_case["params"]
            )
            response = api.request(request)

            if "candles" in response:
                candles = response["candles"]
                print(f"✅ Success! Retrieved {len(candles)} candles")

                if candles:
                    # Show first and last candle details
                    first_candle = candles[0]
                    last_candle = candles[-1]

                    print(f"   First candle: {first_candle.get('time', 'N/A')}")
                    print(f"   Last candle: {last_candle.get('time', 'N/A')}")
                    print(
                        f"   First close: {first_candle.get('mid', {}).get('c', 'N/A')}"
                    )
                    print(
                        f"   Last close: {last_candle.get('mid', {}).get('c', 'N/A')}"
                    )

                    # Check if candles are complete
                    complete_candles = [c for c in candles if c.get("complete", False)]
                    print(
                        f"   Complete candles: {len(complete_candles)}/{len(candles)}"
                    )

            else:
                print(f"❌ No candles in response")
                print(f"   Response keys: {list(response.keys())}")
                print(f"   Full response: {json.dumps(response, indent=2)}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if hasattr(e, "response"):
                print(
                    f"   Response: {e.response.text if hasattr(e.response, 'text') else e.response}"
                )

    print("\n" + "=" * 60)
    print("🔍 Historical Data Debug Complete")


if __name__ == "__main__":
    debug_historical_data()
