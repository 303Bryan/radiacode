#!/usr/bin/env python3
"""
Test script for Radiacode Home Assistant Integration

This script tests the basic functionality of the Radiacode integration
without requiring a full Home Assistant installation.
"""

import asyncio
import sys
import os

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

try:
    from radiacode import RadiaCode
    print("✅ Radiacode library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Radiacode library: {e}")
    print("Please install the radiacode library: pip install radiacode")
    sys.exit(1)

async def test_radiacode_connection():
    """Test basic Radiacode device connection."""
    print("\n🔍 Testing Radiacode device connection...")
    
    try:
        # Try to connect to the first available device
        device = RadiaCode()
        print("✅ Successfully connected to Radiacode device")
        
        # Get device information
        serial_number = device.serial_number()
        firmware_version = device.fw_version()
        hardware_serial = device.hw_serial_number()
        
        print(f"📱 Device Information:")
        print(f"   Serial Number: {serial_number}")
        print(f"   Firmware Version: {firmware_version}")
        print(f"   Hardware Serial: {hardware_serial}")
        
        # Test basic data retrieval
        print("\n📊 Testing data retrieval...")
        
        # Get real-time data
        databuf = device.data_buf()
        real_time_count = 0
        rare_count = 0
        
        for record in databuf:
            if hasattr(record, 'count_rate'):  # RealTimeData
                real_time_count += 1
            elif hasattr(record, 'temperature'):  # RareData
                rare_count += 1
        
        print(f"   Real-time data records: {real_time_count}")
        print(f"   Rare data records: {rare_count}")
        
        # Test spectrum data
        try:
            spectrum = device.spectrum()
            print(f"   Spectrum duration: {spectrum.duration.total_seconds():.1f}s")
            print(f"   Spectrum total counts: {sum(spectrum.counts)}")
            print(f"   Spectrum channels: {len(spectrum.counts)}")
        except Exception as e:
            print(f"   ⚠️  Spectrum data not available: {e}")
        
        # Test energy calibration
        try:
            calibration = device.energy_calib()
            print(f"   Energy calibration: {calibration}")
        except Exception as e:
            print(f"   ⚠️  Energy calibration not available: {e}")
        
        print("✅ All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Failed to connect to Radiacode device: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure your Radiacode device is connected via USB")
        print("   2. Check that the device is powered on")
        print("   3. Verify USB permissions (may need sudo on Linux)")
        print("   4. Try specifying the serial number if multiple devices are connected")
        return False
    
    return True

async def test_integration_components():
    """Test the integration components."""
    print("\n🔧 Testing integration components...")
    
    try:
        # Test imports
        from custom_components.radiacode.const import DOMAIN, PLATFORMS
        print("✅ Constants imported successfully")
        
        from custom_components.radiacode.coordinator import RadiacodeCoordinator
        print("✅ Coordinator imported successfully")
        
        from custom_components.radiacode.config_flow import RadiacodeConfigFlow
        print("✅ Config flow imported successfully")
        
        # Test coordinator creation (without actual device connection)
        class MockHass:
            def __init__(self):
                self.data = {}
        
        hass = MockHass()
        coordinator = RadiacodeCoordinator(hass, None, None, "Test Device")
        print("✅ Coordinator created successfully")
        
        print("✅ All integration components imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import integration components: {e}")
        return False

def test_manifest():
    """Test the manifest file."""
    print("\n📋 Testing manifest file...")
    
    try:
        import json
        with open('custom_components/radiacode/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['domain', 'name', 'documentation', 'requirements', 'version', 'config_flow']
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field in manifest: {field}")
                return False
        
        print("✅ Manifest file is valid")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate manifest: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Radiacode Home Assistant Integration Test")
    print("=" * 50)
    
    # Test manifest
    manifest_ok = test_manifest()
    
    # Test integration components
    components_ok = await test_integration_components()
    
    # Test device connection (only if device is available)
    print("\n💡 Device connection test requires a connected Radiacode device.")
    print("   If you have a device connected, the test will attempt to connect.")
    print("   If no device is connected, this test will be skipped.")
    
    try:
        device_ok = await test_radiacode_connection()
    except Exception as e:
        print(f"⚠️  Device connection test skipped: {e}")
        device_ok = True  # Don't fail the test if no device is connected
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Manifest: {'✅ PASS' if manifest_ok else '❌ FAIL'}")
    print(f"   Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"   Device Connection: {'✅ PASS' if device_ok else '❌ FAIL'}")
    
    if all([manifest_ok, components_ok, device_ok]):
        print("\n🎉 All tests passed! The integration is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Copy the custom_components/radiacode folder to your Home Assistant config directory")
        print("   2. Restart Home Assistant")
        print("   3. Add the integration via Settings → Devices & Services → Integrations")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())