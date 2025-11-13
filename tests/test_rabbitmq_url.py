#!/usr/bin/env python3
"""
Test script to verify RabbitMQ URL configuration works
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_url_parsing():
    """Test that pika can parse RabbitMQ URLs correctly"""
    print("=" * 60)
    print("Testing RabbitMQ URL Configuration")
    print("=" * 60)
    print()
    
    try:
        import pika
    except ImportError:
        print("❌ pika not installed. Run: pip install pika")
        return False
    
    # Test URL
    test_url = "amqps://sukxtmgv:UDNx7D0p9kdeeda4yNzwFQQfGAb5csQF@gorilla.lmq.cloudamqp.com/sukxtmgv"
    
    print(f"Testing URL parsing...")
    print(f"URL: {test_url[:50]}...")
    print()
    
    try:
        params = pika.URLParameters(test_url)
        print("✓ URL parsing successful!")
        print()
        print("Parsed parameters:")
        print(f"  - Host: {params.host}")
        print(f"  - Port: {params.port}")
        print(f"  - Virtual Host: {params.virtual_host}")
        print(f"  - SSL: {params.ssl_options is not None}")
        print(f"  - Heartbeat: {params.heartbeat}")
        print()
        
        # Test modifying parameters
        params.heartbeat = 600
        params.blocked_connection_timeout = 300
        print("✓ Parameter modification successful!")
        print(f"  - Updated Heartbeat: {params.heartbeat}")
        print(f"  - Blocked Timeout: {params.blocked_connection_timeout}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ URL parsing failed: {e}")
        return False

def test_config_loading():
    """Test that config loads URL correctly"""
    print("=" * 60)
    print("Testing Config Loading")
    print("=" * 60)
    print()
    
    # Set test environment variable
    os.environ['RABBITMQ_URL'] = "amqps://test:pass@example.com/vhost"
    os.environ['FLASK_ENV'] = "production"
    
    try:
        from api.config import config
        
        prod_config = config['production']
        
        print("✓ Config loaded successfully!")
        print()
        print("Configuration values:")
        print(f"  - RABBITMQ_URL: {prod_config.RABBITMQ_URL[:50] if prod_config.RABBITMQ_URL else 'Not set'}...")
        print(f"  - RABBITMQ_HOST (fallback): {prod_config.RABBITMQ_HOST}")
        print(f"  - RABBITMQ_PORT (fallback): {prod_config.RABBITMQ_PORT}")
        print(f"  - RABBITMQ_EXCHANGE: {prod_config.RABBITMQ_EXCHANGE}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_config():
    """Test fallback to individual variables"""
    print("=" * 60)
    print("Testing Fallback Configuration (No URL)")
    print("=" * 60)
    print()
    
    # Remove URL, set individual variables
    if 'RABBITMQ_URL' in os.environ:
        del os.environ['RABBITMQ_URL']
    
    os.environ['RABBITMQ_HOST'] = 'localhost'
    os.environ['RABBITMQ_PORT'] = '5672'
    os.environ['RABBITMQ_USER'] = 'guest'
    os.environ['RABBITMQ_PASSWORD'] = 'guest'
    
    try:
        # Reload config
        import importlib
        from api import config as config_module
        importlib.reload(config_module)
        
        from api.config import config
        prod_config = config['production']
        
        print("✓ Fallback config loaded successfully!")
        print()
        print("Configuration values:")
        print(f"  - RABBITMQ_URL: {prod_config.RABBITMQ_URL or 'Not set (using fallback)'}")
        print(f"  - RABBITMQ_HOST: {prod_config.RABBITMQ_HOST}")
        print(f"  - RABBITMQ_PORT: {prod_config.RABBITMQ_PORT}")
        print(f"  - RABBITMQ_USER: {prod_config.RABBITMQ_USER}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback config failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    results = []
    
    results.append(("URL Parsing", test_url_parsing()))
    results.append(("Config Loading", test_config_loading()))
    results.append(("Fallback Config", test_fallback_config()))
    
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print()
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("✓✓✓ All tests passed! ✓✓✓")
        print()
        print("Your RabbitMQ URL configuration is working correctly!")
        print()
        print("Usage:")
        print("  Set: RABBITMQ_URL=amqps://user:pass@host/vhost")
        print("  Run: python run.py")
        print()
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

