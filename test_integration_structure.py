#!/usr/bin/env python3
"""
Test script for Radiacode Home Assistant Integration Structure

This script tests the basic structure and components of the Radiacode integration
without requiring the actual radiacode library or device.
"""

import sys
import os
import json

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

def test_file_structure():
    """Test that all required files exist."""
    print("📁 Testing file structure...")
    
    required_files = [
        'custom_components/radiacode/__init__.py',
        'custom_components/radiacode/const.py',
        'custom_components/radiacode/coordinator.py',
        'custom_components/radiacode/config_flow.py',
        'custom_components/radiacode/sensor.py',
        'custom_components/radiacode/binary_sensor.py',
        'custom_components/radiacode/switch.py',
        'custom_components/radiacode/services.py',
        'custom_components/radiacode/services.yaml',
        'custom_components/radiacode/manifest.json',
        'custom_components/radiacode/README.md',
        'custom_components/radiacode/translations/en.json',
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

def test_manifest():
    """Test the manifest file."""
    print("\n📋 Testing manifest file...")
    
    try:
        with open('custom_components/radiacode/manifest.json', 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['domain', 'name', 'documentation', 'requirements', 'version', 'config_flow']
        missing_fields = []
        
        for field in required_fields:
            if field not in manifest:
                missing_fields.append(field)
            else:
                print(f"   ✅ {field}: {manifest[field]}")
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {missing_fields}")
            return False
        
        # Check that domain matches
        if manifest['domain'] != 'radiacode':
            print(f"   ❌ Domain mismatch: expected 'radiacode', got '{manifest['domain']}'")
            return False
        
        print("✅ Manifest file is valid")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate manifest: {e}")
        return False

def test_services_yaml():
    """Test the services.yaml file."""
    print("\n🔧 Testing services.yaml file...")
    
    try:
        with open('custom_components/radiacode/services.yaml', 'r') as f:
            content = f.read()
        
        # Check for required services
        required_services = [
            'radiacode_reset_dose',
            'radiacode_reset_spectrum',
            'radiacode_set_display_brightness',
            'radiacode_get_spectrum',
            'radiacode_get_energy_calibration',
            'radiacode_set_energy_calibration',
        ]
        
        missing_services = []
        for service in required_services:
            if service in content:
                print(f"   ✅ {service}")
            else:
                missing_services.append(service)
        
        if missing_services:
            print(f"   ❌ Missing services: {missing_services}")
            return False
        
        print("✅ Services.yaml file is valid")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate services.yaml: {e}")
        return False

def test_translations():
    """Test the translations file."""
    print("\n🌐 Testing translations file...")
    
    try:
        with open('custom_components/radiacode/translations/en.json', 'r') as f:
            translations = json.load(f)
        
        # Check for required sections
        required_sections = ['config', 'entity', 'services']
        missing_sections = []
        
        for section in required_sections:
            if section in translations:
                print(f"   ✅ {section}")
            else:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"   ❌ Missing sections: {missing_sections}")
            return False
        
        print("✅ Translations file is valid")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate translations: {e}")
        return False

def test_python_imports():
    """Test that Python modules can be imported."""
    print("\n🐍 Testing Python imports...")
    
    try:
        # Test basic imports
        from custom_components.radiacode.const import DOMAIN, PLATFORMS
        print("   ✅ Constants imported")
        
        from custom_components.radiacode.coordinator import RadiacodeCoordinator
        print("   ✅ Coordinator imported")
        
        from custom_components.radiacode.config_flow import RadiacodeConfigFlow
        print("   ✅ Config flow imported")
        
        from custom_components.radiacode.sensor import async_setup_entry as sensor_setup
        print("   ✅ Sensor module imported")
        
        from custom_components.radiacode.binary_sensor import async_setup_entry as binary_sensor_setup
        print("   ✅ Binary sensor module imported")
        
        from custom_components.radiacode.switch import async_setup_entry as switch_setup
        print("   ✅ Switch module imported")
        
        from custom_components.radiacode.services import async_setup_services
        print("   ✅ Services module imported")
        
        print("✅ All Python modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import modules: {e}")
        return False

def test_coordinator_structure():
    """Test the coordinator class structure."""
    print("\n🔧 Testing coordinator structure...")
    
    try:
        from custom_components.radiacode.coordinator import RadiacodeCoordinator
        
        # Create a mock coordinator (without actual device connection)
        class MockHass:
            def __init__(self):
                self.data = {}
        
        hass = MockHass()
        coordinator = RadiacodeCoordinator(hass, None, None, "Test Device")
        
        # Check that required methods exist
        required_methods = [
            'async_connect',
            'async_shutdown',
            'async_set_device_power',
            'async_set_sound',
            'async_set_vibration',
            'async_set_display_brightness',
            'async_reset_dose',
            'async_reset_spectrum',
            'async_get_spectrum',
            'async_get_energy_calibration',
            'async_set_energy_calibration',
        ]
        
        missing_methods = []
        for method in required_methods:
            if hasattr(coordinator, method):
                print(f"   ✅ {method}")
            else:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"   ❌ Missing methods: {missing_methods}")
            return False
        
        print("✅ Coordinator structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Failed to test coordinator: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Radiacode Home Assistant Integration Structure Test")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Manifest", test_manifest),
        ("Services YAML", test_services_yaml),
        ("Translations", test_translations),
        ("Python Imports", test_python_imports),
        ("Coordinator Structure", test_coordinator_structure),
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
        print("\n🎉 All tests passed! The integration structure is ready.")
        print("\n📝 Next steps:")
        print("   1. Install the radiacode library: pip install radiacode")
        print("   2. Copy the custom_components/radiacode folder to your Home Assistant config directory")
        print("   3. Restart Home Assistant")
        print("   4. Add the integration via Settings → Devices & Services → Integrations")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()