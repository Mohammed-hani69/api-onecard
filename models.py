"""
ملف النماذج - يحتوي على بنية البيانات المستخدمة في التطبيق
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

# ==================== نموذج المنتج ====================
class Product(db.Model):
    """
    نموذج لتخزين معلومات المنتجات المحضرة من API
    """
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(255), unique=True, nullable=False)
    name_ar = db.Column(db.String(255), nullable=True)
    name_en = db.Column(db.String(255), nullable=False)
    merchant_id = db.Column(db.String(100), nullable=True)
    merchant_name_ar = db.Column(db.String(255), nullable=True)
    merchant_name_en = db.Column(db.String(255), nullable=True)
    category_name_ar = db.Column(db.String(255), nullable=True)
    category_name_en = db.Column(db.String(255), nullable=True)
    
    # الأسعار
    face_value = db.Column(db.Float, nullable=True)
    cost_price_before_vat = db.Column(db.Float, nullable=True)
    cost_price_vat_amount = db.Column(db.Float, nullable=True)
    cost_price_after_vat = db.Column(db.Float, nullable=True)
    recommended_retail_price_before_vat = db.Column(db.Float, nullable=True)
    recommended_retail_price_vat_amount = db.Column(db.Float, nullable=True)
    recommended_retail_price_after_vat = db.Column(db.Float, nullable=True)
    
    # معلومات إضافية
    currency = db.Column(db.String(10), nullable=True)
    available = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(500), nullable=True)
    how_to_use_ar = db.Column(db.Text, nullable=True)
    how_to_use_en = db.Column(db.Text, nullable=True)
    vat_type = db.Column(db.String(10), nullable=True)
    vat_percentage = db.Column(db.Float, nullable=True)
    
    # معلومات الفورم الديناميكي
    inquiry_required = db.Column(db.Boolean, default=False)
    dynamic_form_list = db.Column(db.JSON, nullable=True)
    
    # بيانات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product {self.product_id}: {self.name_en}>"
    
    def to_dict(self):
        """تحويل المنتج إلى قاموس"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'merchant_name_en': self.merchant_name_en,
            'merchant_name_ar': self.merchant_name_ar,
            'category_name_en': self.category_name_en,
            'category_name_ar': self.category_name_ar,
            'face_value': self.face_value,
            'cost_price_after_vat': self.cost_price_after_vat,
            'recommended_retail_price_after_vat': self.recommended_retail_price_after_vat,
            'currency': self.currency,
            'available': self.available,
            'image': self.image,
            'how_to_use_ar': self.how_to_use_ar,
            'how_to_use_en': self.how_to_use_en,
        }

# ==================== نموذج عنصر السلة ====================
class CartItem(db.Model):
    """
    نموذج لتخزين عناصر سلة التسوق
    """
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.String(255), db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='cart_items')
    
    def __repr__(self):
        return f"<CartItem {self.product_id} x{self.quantity}>"
    
    def to_dict(self):
        """تحويل عنصر السلة إلى قاموس"""
        return {
            'id': self.id,
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'price': self.price,
            'total': self.price * self.quantity,
        }

# ==================== نموذج المعاملة ====================
class Transaction(db.Model):
    """
    نموذج لتخزين سجل المعاملات والشراء
    """
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, default=lambda: str(uuid.uuid4()))
    
    # معلومات المنتج
    product_id = db.Column(db.String(255), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    
    # معلومات الشراء
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # حالة المعاملة
    status = db.Column(db.String(50), default='pending')  # pending, success, failed
    error_code = db.Column(db.String(100), nullable=True)
    error_message = db.Column(db.String(500), nullable=True)
    
    # معلومات الاستجابة من API
    response_data = db.Column(db.JSON, nullable=True)
    
    # بيانات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transaction {self.transaction_id}: {self.status}>"
    
    def to_dict(self):
        """تحويل المعاملة إلى قاموس"""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'status': self.status,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

# ==================== نموذج الرصيد ====================
class Balance(db.Model):
    """
    نموذج لتخزين معلومات الرصيد الحالي
    """
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='SAR')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Balance {self.balance} {self.currency}>"
    
    def to_dict(self):
        """تحويل الرصيد إلى قاموس"""
        return {
            'balance': self.balance,
            'currency': self.currency,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
        }
