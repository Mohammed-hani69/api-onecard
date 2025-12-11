"""
ملف خدمة API - يحتوي على جميع وظائف التواصل مع API الخارجي
"""

import requests
import json
from config import (
    API_BASE_URL, RESELLER_USERNAME, SECRET_KEY, MERCHANT_ID,
    get_check_balance_password, get_product_password, 
    get_purchase_password, get_bill_inquire_password, get_topup_password
)

class APIService:
    """
    فئة للتواصل مع API الخارجي
    تحتوي على جميع الوظائف اللازمة
    """
    
    @staticmethod
    def _make_request(endpoint, data):
        """
        وظيفة داخلية للقيام برطلب HTTP إلى API
        
        Args:
            endpoint: اسم الـ endpoint (مثل: check-balance)
            data: البيانات المراد إرسالها في الطلب
            
        Returns:
            dict: البيانات المستجابة من الـ API أو رسالة خطأ
        """
        try:
            url = f"{API_BASE_URL}/{endpoint}"
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': False,
                'errorCode': '999',
                'errorMessage': 'خطأ في الاتصال',
                'errorDesc': str(e)
            }
    
    # ==================== فحص الرصيد ====================
    @staticmethod
    def check_balance():
        """
        احضار رصيد الحساب الحالي من API
        
        معادلة كلمة المرور: MD5(resellerUsername + secretKey)
        
        Returns:
            dict: استجابة API تحتوي على الرصيد والعملة
        """
        data = {
            'resellerUsername': RESELLER_USERNAME,
            'password': get_check_balance_password()
        }
        return APIService._make_request('check-balance', data)
    
    # ==================== احضار قائمة المنتجات ====================
    @staticmethod
    def get_detailed_products_list():
        """
        احضار قائمة شاملة بجميع المنتجات المتاحة مع تفاصيلها
        
        معادلة كلمة المرور: MD5(resellerUsername + merchantId + secretKey)
        
        Returns:
            dict: استجابة API تحتوي على قائمة المنتجات
        """
        import hashlib
        password = f"{RESELLER_USERNAME}{MERCHANT_ID}{SECRET_KEY}"
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        data = {
            'resellerUsername': RESELLER_USERNAME,
            'password': password_hash,
            'merchantId': MERCHANT_ID
        }
        return APIService._make_request('detailed-products-list', data)
    
    # ==================== احضار معلومات منتج محدد ====================
    @staticmethod
    def get_product_details(product_id):
        """
        احضار معلومات تفصيلية عن منتج معين
        
        معادلة كلمة المرور: MD5(resellerUsername + productId + secretKey)
        
        Args:
            product_id: معرف المنتج
            
        Returns:
            dict: استجابة API تحتوي على تفاصيل المنتج
        """
        data = {
            'resellerUsername': RESELLER_USERNAME,
            'password': get_product_password(product_id),
            'productID': product_id
        }
        return APIService._make_request('product-detailed-info', data)
    
    # ==================== استعلام الفاتورة ====================
    @staticmethod
    def bill_inquire(product_id, input_parameters):
        """
        الاستعلام عن تفاصيل الفاتورة قبل السداد
        
        معادلة كلمة المرور: MD5(resellerUsername + productId + secretKey)
        
        Args:
            product_id: معرف المنتج
            input_parameters: dict بمعاملات الاستعلام (مثل رقم العميل)
            
        Returns:
            dict: استجابة API تحتوي على تفاصيل الفاتورة
        """
        data = {
            'resellerUsername': RESELLER_USERNAME,
            'password': get_bill_inquire_password(product_id),
            'productId': product_id,
            'inputParameters': input_parameters
        }
        return APIService._make_request('service-bill-inquire', data)
    
    # ==================== حساب سعر الشحن ====================
    @staticmethod
    def calculate_topup_amount(product_id, amount):
        """
        حساب سعر الشحن النهائي قبل الشراء
        
        معادلة كلمة المرور: MD5(resellerUsername + productId + secretKey)
        
        Args:
            product_id: معرف المنتج
            amount: المبلغ المراد شحنه
            
        Returns:
            dict: استجابة API تحتوي على السعر النهائي
        """
        data = {
            'resellerUsername': RESELLER_USERNAME,
            'password': get_topup_password(product_id),
            'productId': product_id,
            'amount': amount
        }
        return APIService._make_request('calculate-topup-amount', data)
    
    # ==================== عملية الشراء والسداد ====================
    @staticmethod
    def make_purchase(reseller_ref_number, product_id=None, inquire_ref_number=None, 
                     input_parameters=None, terminal_id=None):
        """
        إجراء عملية شراء/سداد فاتورة
        
        معادلة كلمة المرور: MD5(resellerUsername + resellerRefNumber + secretKey)
        
        Args:
            reseller_ref_number: رقم مرجعي فريد للطلب
            product_id: معرف المنتج (للمنتجات التي لا تتطلب استعلام)
            inquire_ref_number: رقم الاستعلام (للفواتير)
            input_parameters: معاملات الإدخال (للشحن والدفع)
            terminal_id: معرف الجهاز (اختياري)
            
        Returns:
            dict: استجابة API تحتوي على حالة الشراء
        """
        data = {
            'resellerUsername': RESELLER_USERNAME,
            'password': get_purchase_password(reseller_ref_number),
            'resellerRefNumber': reseller_ref_number
        }
        
        # أضيف المعاملات الشرطية
        if inquire_ref_number:
            data['inquireReferenceNumber'] = inquire_ref_number
        
        if product_id:
            data['productId'] = product_id
        
        if input_parameters:
            data['inputParameters'] = input_parameters
        
        if terminal_id:
            data['terminalID'] = terminal_id
        
        return APIService._make_request('service-bill-pay', data)
    
    # ==================== دوال مساعدة ====================
    @staticmethod
    def is_success(response):
        """
        فحص ما إذا كانت الاستجابة ناجحة
        
        Args:
            response: استجابة API
            
        Returns:
            bool: True إذا كانت العملية ناجحة
        """
        return response.get('status', False) == True
    
    @staticmethod
    def get_error_message(response):
        """
        احضار رسالة الخطأ من الاستجابة
        
        Args:
            response: استجابة API
            
        Returns:
            str: رسالة الخطأ
        """
        error_code = response.get('errorCode', 'unknown')
        error_message = response.get('errorMessage', 'حدث خطأ غير معروف')
        return f"({error_code}) {error_message}"
