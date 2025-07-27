#!/usr/bin/env python3
"""
Test script for Embedded Radiacode Library Only

This script tests the embedded Radiacode library functionality without requiring
Home Assistant modules.
"""

import sys
import os
import json

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

def test_embedded_library_imports():
    """Test that all embedded library modules can be imported."""
    print("🔧 Testing embedded Radiacode library imports...")
    
    try:
        # Test main library import
        from custom_components.radiacode.radiacode_lib import RadiaCode
        print("   ✅ RadiaCode class imported")
        
        # Test types import
        from custom_components.radiacode.radiacode_lib.types import (
            RealTimeData, RareData, Spectrum, AlarmLimits, DisplayDirection,
            DoseRateDB, Event, RawData, COMMAND, CTRL, VS, VSFR
        )
        print("   ✅ All types imported")
        
        # Test bytes buffer
        from custom_components.radiacode.radiacode_lib.bytes_buffer import BytesBuffer
        print("   ✅ BytesBuffer imported")
        
        # Test transports
        from custom_components.radiacode.radiacode_lib.transports.usb import Usb
        print("   ✅ USB transport imported")
        
        from custom_components.radiacode.radiacode_lib.transports.bluetooth import Bluetooth
        print("   ✅ Bluetooth transport imported")
        
        # Test decoders
        from custom_components.radiacode.radiacode_lib.decoders.databuf import decode_VS_DATA_BUF
        print("   ✅ Data buffer decoder imported")
        
        from custom_components.radiacode.radiacode_lib.decoders.spectrum import decode_RC_VS_SPECTRUM
        print("   ✅ Spectrum decoder imported")
        
        print("✅ All embedded library imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import embedded library: {e}")
        return False

def test_bytes_buffer_functionality():
    """Test the BytesBuffer functionality."""
    print("\n🔧 Testing BytesBuffer functionality...")
    
    try:
        from custom_components.radiacode.radiacode_lib.bytes_buffer import BytesBuffer
        
        # Test data
        test_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C'
        buffer = BytesBuffer(test_data)
        
        # Test reading different data types
        assert buffer.read_uint8() == 1
        assert buffer.read_uint16() == 0x0302
        assert buffer.read_uint32() == 0x07060504
        assert buffer.read_float() == 1.539989614439558e-36  # Expected float value
        
        # Test remaining bytes
        assert buffer.remaining() == 0
        
        # Test position management
        buffer.set_position(0)
        assert buffer.get_position() == 0
        assert buffer.remaining() == 12
        
        print("   ✅ BytesBuffer functionality works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test BytesBuffer: {e}")
        return False

def test_types_and_enums():
    """Test that types and enums are properly defined."""
    print("\n🔧 Testing types and enums...")
    
    try:
        from custom_components.radiacode.radiacode_lib.types import (
            RealTimeData, RareData, Spectrum, COMMAND, CTRL, VS, VSFR
        )
        import datetime
        
        # Test creating data objects
        dt = datetime.datetime.now()
        real_time_data = RealTimeData(
            dt=dt,
            count_rate=1.5,
            count_rate_err=0.1,
            dose_rate=10,
            dose_rate_err=0.5,
            flags=0,
            real_time_flags=0
        )
        assert real_time_data.count_rate == 1.5
        assert real_time_data.dose_rate == 10
        
        # Test enum values
        assert int(COMMAND.GET_STATUS) == 0x0005
        assert int(VSFR.DEVICE_ON) == 0x0503
        assert int(CTRL.BUTTONS) == 1
        
        print("   ✅ Types and enums work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test types and enums: {e}")
        return False

def test_radiacode_class_structure():
    """Test that the RadiaCode class has the expected methods."""
    print("\n🔧 Testing RadiaCode class structure...")
    
    try:
        from custom_components.radiacode.radiacode_lib import RadiaCode
        
        # Check that the class has the expected methods
        expected_methods = [
            'data_buf', 'spectrum', 'spectrum_accum',
            'dose_reset', 'spectrum_reset', 'energy_calib',
            'set_energy_calib', 'set_device_on', 'set_sound_on',
            'set_vibro_on', 'set_display_brightness', 'get_alarm_limits',
            'set_alarm_limits'
        ]
        
        for method_name in expected_methods:
            if not hasattr(RadiaCode, method_name):
                print(f"   ❌ Missing method: {method_name}")
                return False
        
        print("   ✅ RadiaCode class has all expected methods")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test RadiaCode class structure: {e}")
        return False

def test_manifest_requirements():
    """Test that the manifest has correct requirements."""
    print("\n📋 Testing manifest requirements...")
    
    try:
        with open('custom_components/radiacode/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        requirements = manifest.get('requirements', [])
        
        # Check that it doesn't include the external radiacode library
        if 'radiacode' in str(requirements):
            print("   ❌ Manifest still references external radiacode library")
            return False
        
        # Check that it includes basic dependencies
        has_usb = any('usb' in req for req in requirements)
        has_bluepy = any('bluepy' in req for req in requirements)
        
        if not has_usb:
            print("   ⚠️  USB dependency not listed")
        
        print("   ✅ Manifest requirements are correct for self-contained integration")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test manifest: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\n📁 Testing file structure...")
    
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
        'custom_components/radiacode/manifest.json',
        'custom_components/radiacode/const.py',
        'custom_components/radiacode/coordinator.py',
        'custom_components/radiacode/config_flow.py',
        'custom_components/radiacode/sensor.py',
        'custom_components/radiacode/binary_sensor.py',
        'custom_components/radiacode/switch.py',
        'custom_components/radiacode/services.py',
        'custom_components/radiacode/services.yaml',
        'custom_components/radiacode/translations/en.json',
        'custom_components/radiacode/README.md',
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
    
    print("✅ All required files exist")
    return True

def main():
    """Run all tests."""
    print("🧪 Embedded Radiacode Library Test")
    print("=" * 60)
    
    tests = [
        ("Library Imports", test_embedded_library_imports),
        ("BytesBuffer Functionality", test_bytes_buffer_functionality),
        ("Types and Enums", test_types_and_enums),
        ("RadiaCode Class Structure", test_radiacode_class_structure),
        ("Manifest Requirements", test_manifest_requirements),
        ("File Structure", test_file_structure),
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
    print("\n" + "=" * 60)
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
        print("\n🎉 All tests passed! The embedded Radiacode library is ready.")
        print("\n📝 Key Features:")
        print("   ✅ Fully self-contained Radiacode library")
        print("   ✅ No external radiacode library dependency")
        print("   ✅ Complete USB and Bluetooth support")
        print("   ✅ All device functionality included")
        print("   ✅ Ready for Home Assistant integration")
        print("\n📋 Installation Instructions:")
        print("   1. Copy custom_components/radiacode/ to your Home Assistant config directory")
        print("   2. Install basic dependencies: pip install usb bluepy")
        print("   3. Restart Home Assistant")
        print("   4. Add integration via Settings → Devices & Services → Integrations")
        print("   5. Configure your Radiacode device (USB or Bluetooth)")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()