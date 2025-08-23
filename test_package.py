#!/usr/bin/env python3
"""
Test script to verify the gcs_browser package installation and functionality
"""

def test_imports():
    """Test if the package can be imported"""
    print("🧪 Testing package imports...")
    
    try:
        import gcs_browser
        print(f"   ✅ gcs_browser v{gcs_browser.__version__}")
    except ImportError as e:
        print(f"   ❌ gcs_browser: {e}")
        return False
    
    try:
        from gcs_browser import GCSBrowser, GCSItem
        print("   ✅ Core classes imported")
    except ImportError as e:
        print(f"   ❌ Core classes: {e}")
        return False
    
    try:
        from gcs_browser.utils import detect_download_tools
        print("   ✅ Utility functions imported")
    except ImportError as e:
        print(f"   ❌ Utility functions: {e}")
        return False
    
    return True


def test_tools():
    """Test tool detection"""
    print("\n🛠️  Testing tool detection...")
    
    try:
        from gcs_browser.utils import detect_download_tools
        tools = detect_download_tools()
        
        for tool, available in tools.items():
            status = "✅" if available else "❌"
            print(f"   {status} {tool}")
        
        return True
    except Exception as e:
        print(f"   ❌ Tool detection failed: {e}")
        return False


def test_gcs_connection():
    """Test basic GCS connection"""
    print("\n🌐 Testing GCS connection...")
    
    try:
        from gcs_browser import GCSBrowser
        
        browser = GCSBrowser()
        success = browser.connect(use_anonymous=True)
        
        if success:
            print("   ✅ Successfully connected to GCS (anonymous)")
            
            # Test listing a known public bucket
            items = browser.list_items("nmfs_odp_pifsc", "")
            if items:
                print(f"   ✅ Found {len(items)} items in nmfs_odp_pifsc bucket")
                print(f"      First few items:")
                for item in items[:3]:
                    print(f"        - {item.type}: {item.name}")
            else:
                print("   ⚠️  No items found (bucket might be empty or access restricted)")
            
            return True
        else:
            print("   ❌ Failed to connect to GCS")
            return False
            
    except Exception as e:
        print(f"   ❌ GCS connection test failed: {e}")
        return False


def test_cli_entry_point():
    """Test CLI entry point"""
    print("\n🖥️  Testing CLI entry point...")
    
    try:
        import subprocess
        import sys
        
        # Test if the CLI entry point exists
        result = subprocess.run([sys.executable, '-m', 'gcs_browser.cli', '--help'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ CLI entry point working")
            return True
        else:
            print(f"   ❌ CLI failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ CLI test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🎯 GCS Browser Package Test")
    print("=" * 50)
    
    tests = [
        ("Package Import", test_imports),
        ("Tool Detection", test_tools),
        ("GCS Connection", test_gcs_connection),
        ("CLI Entry Point", test_cli_entry_point),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * (len(test_name) + 4))
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
    
    print(f"\n🎉 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Package is ready to use.")
        print("\n📖 Next steps:")
        print("   CLI: gcs-browser --help")
        print("   Web: gcs-browser-web")
        print("   Python: from gcs_browser import GCSBrowser")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
