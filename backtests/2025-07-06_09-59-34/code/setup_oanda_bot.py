#!/usr/bin/env python3
"""
Setup script for OANDA Trading Bot
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_oanda.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def create_env_file():
    """Create .env file template"""
    env_content = """# OANDA API Configuration
OANDA_ACCOUNT_ID=your_account_id_here
OANDA_API_KEY=your_api_key_here
OANDA_ENVIRONMENT=practice

# Trading Configuration
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("⚠️  Please update .env with your OANDA credentials")
    else:
        print("ℹ️  .env file already exists")

def validate_config():
    """Validate configuration"""
    config_file = Path("oanda_config.json")
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            print("✅ Configuration file validated")
            return True
        except json.JSONDecodeError:
            print("❌ Invalid configuration file")
            return False
    else:
        print("❌ Configuration file not found")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "data", "backups"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def main():
    """Main setup function"""
    print("🚀 Setting up OANDA Trading Bot...")
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create directories
    create_directories()
    
    # Create env file
    create_env_file()
    
    # Validate config
    validate_config()
    
    print("\n📋 Setup Complete!")
    print("\nNext steps:")
    print("1. Update .env file with your OANDA credentials")
    print("2. Update oanda_config.json with your settings")
    print("3. Run: python oanda_trading_bot.py")
    print("\nFor testing:")
    print("python test_oanda_connection.py")

if __name__ == "__main__":
    main() 