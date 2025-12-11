#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔐 أداة تحديث بيانات الاعتماد - Update Credentials Tool

هذا الملف يساعدك على تحديث بيانات اتصال API
إذا كنت تواجه مشكلة INVALID_PASSWORD عند محاولة احضار المنتجات
"""

import os
import sys

def update_credentials():
    """تحديث بيانات الاعتماد في config.py"""
    
    print("\n" + "="*70)
    print("🔐 أداة تحديث بيانات الاعتماد API")
    print("="*70)
    
    print("""
📌 المتطلبات:
   أنت تحتاج إلى الحصول على هذه البيانات من Bitaqaty Business:
   
   1. Reseller Username (اسم المستخدم)
      مثال: business@example.com
   
   2. Secret Key (المفتاح السري)
      مثال: XXXXXXXXXXXXXXXXXXXX (16-32 حروف)
   
   3. Merchant ID (معرف التاجر)
      مثال: 123456 (رقم فقط)

⚠️  ملاحظة مهمة:
   - لا تشارك هذه البيانات مع أحد
   - احفظ هذا المفتاح في مكان آمن
   - لن نطلب منك هذه البيانات مرة أخرى
""")
    
    # قراءة البيانات الحالية
    try:
        from config import RESELLER_USERNAME, SECRET_KEY, MERCHANT_ID
        print(f"\n📌 البيانات الحالية:")
        print(f"   Reseller Username: {RESELLER_USERNAME}")
        print(f"   Merchant ID: {MERCHANT_ID}")
        print(f"   Secret Key: {'*' * len(SECRET_KEY)}")
    except:
        pass
    
    # اسأل المستخدم
    print("\n" + "-"*70)
    print("💬 إدخال البيانات الجديدة (اتركها فارغة للإبقاء على الحالية)")
    print("-"*70)
    
    # الحصول على البيانات من المستخدم
    new_username = input("\n📧 Reseller Username: ").strip()
    new_secret = input("🔑 Secret Key: ").strip()
    new_merchant = input("🏢 Merchant ID: ").strip()
    
    # إذا لم يدخل شيء، استخدم القيم الحالية
    if not new_username and not new_secret and not new_merchant:
        print("\n⏭️  تم الإلغاء - لم يتم تغيير أي شيء")
        return False
    
    # التحقق من الصحة
    if new_username and not ('@' in new_username or len(new_username) > 5):
        print("\n⚠️  اسم المستخدم يبدو غير صحيح (يجب أن يكون بريد إلكتروني أو نص طويل)")
        return False
    
    if new_secret and len(new_secret) < 10:
        print("\n⚠️  المفتاح السري قصير جداً (يجب أن يكون 10+ أحرف)")
        return False
    
    if new_merchant and not new_merchant.isdigit():
        print("\n⚠️  معرف التاجر يجب أن يكون أرقاماً فقط")
        return False
    
    # اقرأ ملف config.py الحالي
    config_path = 'config.py'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
    except Exception as e:
        print(f"\n❌ خطأ في قراءة ملف config.py: {e}")
        return False
    
    # استبدل القيم
    if new_username:
        config_content = config_content.replace(
            f'RESELLER_USERNAME = "{RESELLER_USERNAME}"',
            f'RESELLER_USERNAME = "{new_username}"'
        )
        print(f"✓ تم تحديث Reseller Username")
    
    if new_secret:
        config_content = config_content.replace(
            f'SECRET_KEY = "{SECRET_KEY}"',
            f'SECRET_KEY = "{new_secret}"'
        )
        print(f"✓ تم تحديث Secret Key")
    
    if new_merchant:
        config_content = config_content.replace(
            f'MERCHANT_ID = "{MERCHANT_ID}"',
            f'MERCHANT_ID = "{new_merchant}"'
        )
        print(f"✓ تم تحديث Merchant ID")
    
    # احفظ الملف المحدث
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"\n✅ تم حفظ البيانات الجديدة في {config_path}")
    except Exception as e:
        print(f"\n❌ خطأ في حفظ ملف config.py: {e}")
        return False
    
    # اختبر الاتصال بـ API
    print("\n" + "-"*70)
    print("🔍 اختبار الاتصال بـ API...")
    print("-"*70)
    
    # أعد استيراد config
    if 'config' in sys.modules:
        del sys.modules['config']
    
    try:
        from config import RESELLER_USERNAME, SECRET_KEY, MERCHANT_ID, get_check_balance_password
        from api_service import APIService
        
        response = APIService.check_balance()
        if APIService.is_success(response):
            print(f"\n✅ نجح الاتصال!")
            print(f"   الرصيد: {response.get('balance')} {response.get('currency')}")
            return True
        else:
            error = APIService.get_error_message(response)
            print(f"\n❌ فشل الاتصال:")
            print(f"   {error}")
            print(f"\n💡 تأكد من:")
            print(f"   • صحة بيانات الاعتماد")
            print(f"   • الاتصال بالإنترنت")
            print(f"   • أن API متاح حالياً")
            return False
    except Exception as e:
        print(f"\n❌ خطأ في الاتصال: {e}")
        return False

def main():
    """البرنامج الرئيسي"""
    
    try:
        success = update_credentials()
        
        if success:
            print("\n" + "="*70)
            print("✅ تم التحديث بنجاح!")
            print("="*70)
            print("""
الخطوات التالية:
   1. قم بتشغيل fetch_products.py لاحضار المنتجات:
      python fetch_products.py
   
   2. أو شغل التطبيق مباشرة:
      python app.py
   
   3. ثم افتح المتصفح على:
      http://localhost:5000
""")
            sys.exit(0)
        else:
            print("\n" + "="*70)
            print("⚠️  تم الإلغاء أو حدث خطأ")
            print("="*70)
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  تم الإلغاء من المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
