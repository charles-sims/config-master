#!/usr/bin/env python3
"""
Test script for AI Platform Scanner
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from scanners.ai_platform_scanner import AIPlatformScanner

def test_scanner():
    """Test the AI Platform Scanner"""
    print("🔍 Testing AI Platform Scanner")

    # Test configuration without real API keys
    config = {
        'platforms': ['HubSpot'],
        'openai_api_key': None,  # Test without real keys first
        'exa_api_key': None,
        'firecrawl_api_key': None
    }

    scanner = AIPlatformScanner(config)

    print(f"Scanner can scan: {scanner.can_scan()}")

    if not scanner.can_scan():
        print("❌ Scanner cannot run without API keys")
        print("To test with real APIs, set these environment variables:")
        print("- OPENAI_API_KEY")
        print("- EXA_API_KEY")
        print("- FIRECRAWL_API_KEY")
        return

    print("🚀 Running AI Platform Scanner...")
    try:
        result = scanner.scan()
        print(f"✅ Scan completed successfully!")
        print(f"Target: {result.target}")
        print(f"Applications found: {len(result.applications)}")
        print(f"Errors: {len(result.errors)}")

        for app in result.applications:
            print(f"\n📱 Application: {app.name}")
            print(f"   Type: {app.type}")
            print(f"   Description: {app.description}")
            print(f"   Integrations: {len(app.integrations)}")

    except Exception as e:
        print(f"❌ Scanner failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scanner()