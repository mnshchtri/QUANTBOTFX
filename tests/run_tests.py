#!/usr/bin/env python3
"""
Test Runner for QuantBotForex
Run tests from any category easily
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


class TestRunner:
    """Run tests from different categories"""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.categories = {
            "oanda": self.test_dir / "oanda",
            "alternative": self.test_dir / "alternative_data",
            "strategies": self.test_dir / "strategies",
            "debug": self.test_dir / "debug",
        }

    def list_tests(self, category=None):
        """List available tests"""
        if category and category in self.categories:
            test_path = self.categories[category]
            if test_path.exists():
                print(f"\n📁 Tests in {category}:")
                for test_file in test_path.glob("*.py"):
                    print(f"   - {test_file.name}")
            else:
                print(f"❌ Category '{category}' not found")
        else:
            print("\n📁 Available test categories:")
            for cat, path in self.categories.items():
                if path.exists():
                    test_count = len(list(path.glob("*.py")))
                    print(f"   - {cat}: {test_count} tests")
                else:
                    print(f"   - {cat}: No tests found")

    def run_test(self, category, test_name=None):
        """Run a specific test or all tests in a category"""
        if category not in self.categories:
            print(f"❌ Unknown category: {category}")
            return False

        test_path = self.categories[category]
        if not test_path.exists():
            print(f"❌ Category directory not found: {test_path}")
            return False

        if test_name:
            # Run specific test
            test_file = test_path / test_name
            if not test_file.exists():
                print(f"❌ Test file not found: {test_file}")
                return False

            print(f"\n🚀 Running: {category}/{test_name}")
            print("=" * 50)
            return self._execute_test(test_file)
        else:
            # Run all tests in category
            test_files = list(test_path.glob("*.py"))
            if not test_files:
                print(f"❌ No test files found in {category}")
                return False

            print(f"\n🚀 Running all tests in {category}")
            print("=" * 50)

            results = []
            for test_file in test_files:
                print(f"\n📋 Running: {test_file.name}")
                print("-" * 30)
                success = self._execute_test(test_file)
                results.append((test_file.name, success))

            # Summary
            print(f"\n📊 Results for {category}:")
            print("=" * 30)
            passed = sum(1 for _, success in results if success)
            total = len(results)
            print(f"Passed: {passed}/{total}")

            for test_name, success in results:
                status = "✅" if success else "❌"
                print(f"{status} {test_name}")

            return passed == total

    def _execute_test(self, test_file):
        """Execute a single test file"""
        try:
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=test_file.parent,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"Errors: {result.stderr}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("⏰ Test timed out after 60 seconds")
            return False
        except Exception as e:
            print(f"❌ Error running test: {e}")
            return False

    def run_quick_check(self):
        """Run a quick check of all systems"""
        print("🔍 Quick System Check")
        print("=" * 30)

        checks = [
            ("OANDA Connection", "tests/oanda/oanda_with_your_token.py"),
            ("Alternative Data", "tests/alternative_data/test_alternative_data.py"),
            ("Strategy Test", "tests/strategies/forex_strategy_working.py"),
        ]

        for check_name, test_path in checks:
            print(f"\n📋 {check_name}:")
            test_file = Path(test_path)
            if test_file.exists():
                success = self._execute_test(test_file)
                status = "✅" if success else "❌"
                print(f"{status} {check_name}")
            else:
                print(f"❌ Test file not found: {test_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run QuantBotForex tests")
    parser.add_argument(
        "action", choices=["list", "run", "quick"], help="Action to perform"
    )
    parser.add_argument(
        "--category",
        "-c",
        choices=["oanda", "alternative", "strategies", "debug"],
        help="Test category",
    )
    parser.add_argument("--test", "-t", help="Specific test file name")

    args = parser.parse_args()

    runner = TestRunner()

    if args.action == "list":
        runner.list_tests(args.category)

    elif args.action == "run":
        if not args.category:
            print("❌ Please specify a category with --category")
            return
        runner.run_test(args.category, args.test)

    elif args.action == "quick":
        runner.run_quick_check()


if __name__ == "__main__":
    main()
