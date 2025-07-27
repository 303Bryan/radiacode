#!/usr/bin/env python3
"""
Test script for Self-Contained Radiacode Home Assistant Integration

This script tests the self-contained Radiacode integration without requiring
external dependencies beyond the basic USB/Bluetooth libraries.
"""

import sys
import os
import json

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

def test_embedded_library():
    """Test the embedded Radiacode library."""
    print("🔧 Testing embedded Radiacode library...")
    
    try:
        # Test imports
        from custom_components.radiacode.radiacode_lib import RadiaCode
        print("   ✅ RadiaCode class imported")
        
        from custom_components.radiacode.radiacode_lib.types import (
            RealTimeData, RareData, Spectrum, AlarmLimits, DisplayDirection,
            DoseRateDB, Event, RawData, COMMAND, CTRL, VS, VSFR
        )
        print("   ✅ Types imported")
        
        from custom_components.radiacode.radiacode_lib.bytes_buffer import BytesBuffer
        print("   ✅ BytesBuffer imported")
        
        from custom_components.radiacode.radiacode_lib.transports.usb import Usb
        print("   ✅ USB transport imported")
        
        from custom_components.radiacode.radiacode_lib.transports.bluetooth import Bluetooth
        print("   ✅ Bluetooth transport imported")
        
        from custom_components.radiacode.radiacode_lib.decoders.databuf import decode_VS_DATA_BUF
        print("   ✅ Data buffer decoder imported")
        
        from custom_components.radiacode.radiacode_lib.decoders.spectrum import decode_RC_VS_SPECTRUM
        print("   ✅ Spectrum decoder imported")
        
        # Test BytesBuffer functionality
        test_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
        buffer = BytesBuffer(test_data)
        assert buffer.read_uint8() == 1
        assert buffer.read_uint16() == 0x0302
        print("   ✅ BytesBuffer functionality works")
        
        print("✅ Embedded library test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test embedded library: {e}")
        return False

def test_integration_components():
    """Test the integration components with embedded library."""
    print("\n🔧 Testing integration components with embedded library...")
    
    try:
        # Test imports
        from custom_components.radiacode.const import DOMAIN, PLATFORMS
        print("   ✅ Constants imported")
        
        from custom_components.radiacode.coordinator import RadiacodeCoordinator
        print("   ✅ Coordinator imported")
        
        from custom_components.radiacode.config_flow import RadiacodeConfigFlow
        print("   ✅ Config flow imported")
        
        # Test coordinator creation (without actual device connection)
        class MockHass:
            def __init__(self):
                self.data = {}
        
        hass = MockHass()
        coordinator = RadiacodeCoordinator(hass, None, None, "Test Device")
        print("   ✅ Coordinator created successfully")
        
        print("✅ Integration components test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test integration components: {e}")
        return False

def test_manifest_self_contained():
    """Test that the manifest reflects self-contained nature."""
    print("\n📋 Testing manifest for self-contained requirements...")
    
    try:
        with open('custom_components/radiacode/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        # Check that requirements don't include radiacode library
        if 'radiacode' in str(manifest.get('requirements', [])):
            print("   ❌ Manifest still references external radiacode library")
            return False
        
        # Check that it includes the basic dependencies
        requirements = manifest.get('requirements', [])
        if 'usb' not in str(requirements):
            print("   ⚠️  USB dependency not explicitly listed")
        
        print("   ✅ Manifest correctly reflects self-contained nature")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate manifest: {e}")
        return False

def test_file_structure_self_contained():
    """Test that all embedded library files exist."""
    print("\n📁 Testing embedded library file structure...")
    
    required_files = [
        'custom_components/radiacode/radiacode_lib/__init__.py',
        'custom_components/radiacode/radiacode_lib/types.py',
        'custom_components/radiacode/radiacode_lib/bytes_buffer.py',
        'custom_components/radiacode/radiacode_lib/radiacode.py',
        'custom_components/radiacode/radiacode_lib/transports/__init__.py',
        'custom_components/radiacode/radiacode_lib/transports/usb.py',
        'custom_components/radiacode/radiacode_lib/transports/bluetooth.py',
        'custom_components/radiacode/radiacode_lib/decoders/__init__.py',
        'custom_components/radiacode/radiacode_lib/decoders/databuf.py',
        'custom_components/radiacode/radiacode_lib/decoders/spectrum.py',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
        return False
    
    print("✅ All embedded library files exist")
    return True

def main():
    """Run all tests."""
    print("🧪 Self-Contained Radiacode Home Assistant Integration Test")
    print("=" * 70)
    
    tests = [
        ("Embedded Library", test_embedded_library),
        ("Integration Components", test_integration_components),
        ("Manifest Self-Contained", test_manifest_self_contained),
        ("File Structure Self-Contained", test_file_structure_self_contained),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The integration is now fully self-contained.")
        print("\n📝 Key improvements:")
        print("   ✅ No external radiacode library dependency")
        print("   ✅ All Radiacode functionality embedded")
        print("   ✅ Ready for immediate Home Assistant installation")
        print("   ✅ Supports both USB and Bluetooth connections")
        print("\n📋 Installation:")
        print("   1. Copy the custom_components/radiacode folder to your Home Assistant config directory")
        print("   2. Install basic dependencies if needed: pip install usb bluepy")
        print("   3. Restart Home Assistant")
        print("   4. Add the integration via Settings → Devices & Services → Integrations")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()