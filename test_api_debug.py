"""
ملف لاختبار الاتصال بـ API والتحقق من المشاكل
"""

import requests
import json
import hashlib
from config import (
    API_BASE_URL, RESELLER_USERNAME, SECRET_KEY, MERCHANT_ID,
    get_check_balance_password, get_products_list_password
)

def test_check_balance():
    """اختبر فحص الرصيد"""
    print("\n" + "="*60)
    print("اختبار: فحص الرصيد")
    print("="*60)
    
    url = f"{API_BASE_URL}/check-balance"
    password = get_check_balance_password()
    
    print(f"URL: {url}")
    print(f"Username: {RESELLER_USERNAME}")
    print(f"Password: {password}")
    
    data = {
        'resellerUsername': RESELLER_USERNAME,
        'password': password
    }
    
    print(f"Request Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_products_list():
    """اختبر احضار قائمة المنتجات"""
    print("\n" + "="*60)
    print("اختبار: قائمة المنتجات")
    print("="*60)
    
    url = f"{API_BASE_URL}/detailed-products-list"
    password = get_products_list_password(MERCHANT_ID)
    
    print(f"URL: {url}")
    print(f"Username: {RESELLER_USERNAME}")
    print(f"MerchantId: {MERCHANT_ID}")
    print(f"Password: {password}")
    
    data = {
        'resellerUsername': RESELLER_USERNAME,
        'password': password,
        'merchantId': MERCHANT_ID
    }
    
    print(f"Request Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        resp_json = response.json()
        
        # اطبع جزء من الاستجابة
        if 'products' in resp_json:
            products_count = len(resp_json.get('products', []))
            print(f"Number of products: {products_count}")
            resp_json_copy = resp_json.copy()
            if 'products' in resp_json_copy and len(resp_json_copy['products']) > 2:
                resp_json_copy['products'] = resp_json_copy['products'][:2] + ['...']
            print(f"Response (partial): {json.dumps(resp_json_copy, indent=2, ensure_ascii=False)}")
        else:
            print(f"Response: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_products_list_empty_merchant():
    """اختبر احضار قائمة المنتجات مع merchantId فارغ"""
    print("\n" + "="*60)
    print("اختبار: قائمة المنتجات (merchantId فارغ)")
    print("="*60)
    
    url = f"{API_BASE_URL}/detailed-products-list"
    password = get_products_list_password('')
    
    print(f"URL: {url}")
    print(f"Username: {RESELLER_USERNAME}")
    print(f"MerchantId: (empty)")
    print(f"Password: {password}")
    
    data = {
        'resellerUsername': RESELLER_USERNAME,
        'password': password,
        'merchantId': ''
    }
    
    print(f"Request Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        resp_json = response.json()
        
        # اطبع جزء من الاستجابة
        if 'products' in resp_json:
            products_count = len(resp_json.get('products', []))
            print(f"Number of products: {products_count}")
            resp_json_copy = resp_json.copy()
            if 'products' in resp_json_copy and len(resp_json_copy['products']) > 2:
                resp_json_copy['products'] = resp_json_copy['products'][:2] + ['...']
            print(f"Response (partial): {json.dumps(resp_json_copy, indent=2, ensure_ascii=False)}")
        else:
            print(f"Response: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def verify_credentials():
    """التحقق من بيانات الاعتماد"""
    print("\n" + "="*60)
    print("التحقق من بيانات الاعتماد")
    print("="*60)
    
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Reseller Username: {RESELLER_USERNAME}")
    print(f"Secret Key: {SECRET_KEY}")
    print(f"Merchant ID: {MERCHANT_ID}")
    
    print("\nحسابات MD5:")
    print(f"  check_balance: {get_check_balance_password()}")
    print(f"  products_list: {get_products_list_password(MERCHANT_ID)}")

if __name__ == '__main__':
    verify_credentials()
    test_check_balance()
    test_products_list()
    test_products_list_empty_merchant()
