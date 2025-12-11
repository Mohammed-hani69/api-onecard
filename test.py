"""
ملف الاختبار البسيط
يمكنك تشغيله للتحقق من عمل التطبيق
"""

import requests
import json
from config import (
    RESELLER_USERNAME, SECRET_KEY, MERCHANT_ID,
    get_check_balance_password, API_BASE_URL
)

# ==================== اختبار الاتصال بـ API ====================

def test_api_connection():
    """
    اختبر الاتصال بـ API والتحقق من البيانات
    """
    print("\n" + "="*50)
    print("اختبار الاتصال بـ API")
    print("="*50)
    
    # اختبر فحص الرصيد
    print("\n[1] اختبار فحص الرصيد...")
    try:
        url = f"{API_BASE_URL}/check-balance"
        data = {
            'resellerUsername': RESELLER_USERNAME,
            'password': get_check_balance_password()
        }
        
        response = requests.post(url, json=data, timeout=5)
        result = response.json()
        
        if result.get('status'):
            print(f"✓ النتيجة: الرصيد = {result.get('balance')} {result.get('currency')}")
            return True
        else:
            print(f"✗ الخطأ: {result.get('errorMessage')}")
            return False
            
    except Exception as e:
        print(f"✗ خطأ في الاتصال: {str(e)}")
        return False

def test_config():
    """
    تحقق من الإعدادات الأساسية
    """
    print("\n" + "="*50)
    print("فحص الإعدادات")
    print("="*50)
    
    checks = []
    
    # تحقق من اسم المستخدم
    if RESELLER_USERNAME:
        print(f"✓ اسم المستخدم: {RESELLER_USERNAME[:20]}...")
        checks.append(True)
    else:
        print("✗ اسم المستخدم غير محدد")
        checks.append(False)
    
    # تحقق من المفتاح السري
    if SECRET_KEY:
        print(f"✓ المفتاح السري: {len(SECRET_KEY)} حروف")
        checks.append(True)
    else:
        print("✗ المفتاح السري غير محدد")
        checks.append(False)
    
    # تحقق من معرف التاجر
    if MERCHANT_ID:
        print(f"✓ معرف التاجر: {MERCHANT_ID}")
        checks.append(True)
    else:
        print("✗ معرف التاجر غير محدد")
        checks.append(False)
    
    # تحقق من رابط API
    if API_BASE_URL:
        print(f"✓ رابط API: {API_BASE_URL}")
        checks.append(True)
    else:
        print("✗ رابط API غير محدد")
        checks.append(False)
    
    return all(checks)

def test_database():
    """
    تحقق من قاعدة البيانات
    """
    print("\n" + "="*50)
    print("فحص قاعدة البيانات")
    print("="*50)
    
    try:
        from app import app, db
        from models import Product, CartItem, Transaction, Balance
        
        with app.app_context():
            # عد الجداول
            products = Product.query.count()
            transactions = Transaction.query.count()
            
            print(f"✓ عدد المنتجات: {products}")
            print(f"✓ عدد المعاملات: {transactions}")
            
            # تحقق من وجود جداول
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['product', 'cart_item', 'transaction', 'balance']
            for table in required_tables:
                if table in tables:
                    print(f"✓ جدول {table} موجود")
                else:
                    print(f"✗ جدول {table} غير موجود")
            
            return True
            
    except Exception as e:
        print(f"✗ خطأ في قاعدة البيانات: {str(e)}")
        return False

def test_flask_app():
    """
    اختبر تطبيق Flask
    """
    print("\n" + "="*50)
    print("فحص تطبيق Flask")
    print("="*50)
    
    try:
        from app import app
        
        with app.test_client() as client:
            # اختبر الصفحة الرئيسية
            response = client.get('/')
            if response.status_code == 200:
                print("✓ الصفحة الرئيسية تعمل")
            else:
                print(f"✗ الصفحة الرئيسية: كود الخطأ {response.status_code}")
            
            # اختبر صفحة المنتجات
            response = client.get('/products')
            if response.status_code == 200:
                print("✓ صفحة المنتجات تعمل")
            else:
                print(f"✗ صفحة المنتجات: كود الخطأ {response.status_code}")
            
            # اختبر صفحة السلة
            response = client.get('/cart')
            if response.status_code == 200:
                print("✓ صفحة السلة تعمل")
            else:
                print(f"✗ صفحة السلة: كود الخطأ {response.status_code}")
            
            # اختبر صفحة المعاملات
            response = client.get('/transactions')
            if response.status_code == 200:
                print("✓ صفحة المعاملات تعمل")
            else:
                print(f"✗ صفحة المعاملات: كود الخطأ {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"✗ خطأ في تطبيق Flask: {str(e)}")
        return False

def main():
    """
    الدالة الرئيسية للاختبار
    """
    print("\n" + "="*50)
    print("اختبار شامل - OneCard API")
    print("="*50)
    
    results = []
    
    # اختبر الإعدادات
    results.append(("الإعدادات", test_config()))
    
    # اختبر قاعدة البيانات
    results.append(("قاعدة البيانات", test_database()))
    
    # اختبر تطبيق Flask
    results.append(("تطبيق Flask", test_flask_app()))
    
    # اختبر الاتصال بـ API
    results.append(("الاتصال بـ API", test_api_connection()))
    
    # عرض الملخص
    print("\n" + "="*50)
    print("ملخص الاختبار")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ نجح" if result else "✗ فشل"
        print(f"{name}: {status}")
    
    print(f"\nالنتيجة: {passed}/{total} اختبارات نجحت")
    
    if passed == total:
        print("\n✓ جميع الاختبارات نجحت! يمكنك تشغيل التطبيق الآن.")
    else:
        print("\n✗ بعض الاختبارات فشلت. تحقق من الأخطاء أعلاه.")
    
    return passed == total

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
