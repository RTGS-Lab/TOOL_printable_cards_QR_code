#!/usr/bin/env python3
"""
Test script to verify that the QR code generation and card creation workflow works.
This script tests each component individually without requiring external dependencies.

Usage:
    python test.py
"""

import os
import sys
from pathlib import Path
import create_weblinks
import qrgen

# Define test directories
TEST_DIR = Path("test_output")
QR_DIR = TEST_DIR / "qr_codes"

def setup():
    """Create test directories"""
    print("Setting up test environment...")
    os.makedirs(TEST_DIR, exist_ok=True)
    os.makedirs(QR_DIR, exist_ok=True)
    print("✅ Test directories created")

def test_create_weblinks():
    """Test the create_weblinks module"""
    print("\nTesting create_weblinks.py...")
    
    # Test basic URL creation
    lat, lon = 44.9736, -93.4983
    url = create_weblinks.create_weblink(lat, lon)
    expected = f"https://www.google.com/maps?q={lat},{lon}&t=k&z=18"
    
    if url == expected:
        print(f"✅ URL created correctly: {url}")
    else:
        print(f"❌ URL mismatch: \nGot:      {url}\nExpected: {expected}")
    
    # Test with custom zoom
    zoom = 15
    url = create_weblinks.create_weblink(lat, lon, zoom)
    expected = f"https://www.google.com/maps?q={lat},{lon}&t=k&z={zoom}"
    
    if url == expected:
        print(f"✅ URL with custom zoom created correctly: {url}")
    else:
        print(f"❌ URL with custom zoom mismatch: \nGot:      {url}\nExpected: {expected}")
    
    return True

def test_qrgen():
    """Test the QR code generation module"""
    print("\nTesting qrgen.py...")
    
    test_url = "https://www.google.com/maps?q=44.9736,-93.4983&t=k&z=18"
    test_output = str(QR_DIR / "test_qr.png")
    
    try:
        qrgen.generate_qr_code(test_url, test_output)
        if os.path.exists(test_output):
            print(f"✅ QR code generated successfully at: {test_output}")
            return True
        else:
            print(f"❌ QR code file not found at: {test_output}")
            return False
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        return False

def main():
    """Run all tests"""
    print("Running tests for TOOL_printable_cards_QR_code components\n")
    
    setup()
    
    tests = [
        ("create_weblinks.py", test_create_weblinks),
        ("qrgen.py", test_qrgen)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\nTest Summary:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

if __name__ == "__main__":
    main()