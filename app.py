"""
تطبيق Flask الرئيسي
يحتوي على جميع الروتات والمعاملات الخاصة بالتطبيق
"""

from flask import Flask, render_template, request, jsonify, session, redirect
from models import db, Product, CartItem, Transaction, Balance
from api_service import APIService
from config import PRODUCT_CODES
import uuid
import os
from datetime import datetime

# ==================== إنشاء تطبيق Flask ====================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# ==================== تهيئة قاعدة البيانات ====================
db.init_app(app)

# إنشاء جداول قاعدة البيانات عند بدء التطبيق
with app.app_context():
    db.create_all()

# ==================== الروتات - الصفحات الرئيسية ====================

@app.route('/')
def home():
    """
    الصفحة الرئيسية للتطبيق
    تعرض الإحصائيات الأساسية والرصيد الحالي
    """
    # احضار الرصيد الحالي من قاعدة البيانات
    balance = Balance.query.first()
    if not balance:
        balance = Balance(balance=0.0)
        db.session.add(balance)
        db.session.commit()
    
    # احضار عدد المنتجات والمعاملات
    products_count = Product.query.count()
    transactions_count = Transaction.query.count()
    
    return render_template('index.html', 
                         balance=balance.balance,
                         products_count=products_count,
                         transactions_count=transactions_count)

@app.route('/products')
def products():
    """
    صفحة عرض المنتجات
    تعرض جميع المنتجات المتاحة مع معلومات التفاصيل
    """
    # احصل على معاملات البحث والتصفية
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # عمل استعلام قاعدة البيانات
    query = Product.query
    
    # تصفية بالبحث
    if search:
        query = query.filter(
            (Product.name_en.ilike(f'%{search}%')) |
            (Product.name_ar.ilike(f'%{search}%')) |
            (Product.product_id.ilike(f'%{search}%'))
        )
    
    # تصفية حسب الفئة
    if category:
        query = query.filter(Product.category_name_en.ilike(f'%{category}%'))
    
    # ترتيب حسب التوفر ثم الاسم
    products = query.filter(Product.available == True).paginate(page=page, per_page=12)
    
    # احضار الفئات الموجودة
    categories = db.session.query(Product.category_name_en).distinct().filter(
        Product.category_name_en != None
    ).all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('products.html', 
                         products=products,
                         categories=categories,
                         search=search,
                         selected_category=category)

@app.route('/cart')
def cart():
    """
    صفحة سلة التسوق
    تعرض جميع العناصر المضافة إلى السلة
    """
    # احصل على معرف الجلسة
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    # احضار عناصر السلة
    cart_items = CartItem.query.filter_by(session_id=session_id).all()
    
    # حساب المجموع
    total = sum(item.price * item.quantity for item in cart_items)
    
    return render_template('cart.html', 
                         cart_items=cart_items,
                         total=total,
                         items_count=len(cart_items))

@app.route('/checkout')
def checkout():
    """
    صفحة الدفع والتأكيد
    تسمح للمستخدم بمراجعة الطلب وتأكيده
    """
    # احصل على معرف الجلسة
    session_id = session.get('session_id')
    if not session_id:
        return redirect('/cart')
    
    # احضار عناصر السلة والرصيد
    cart_items = CartItem.query.filter_by(session_id=session_id).all()
    balance = Balance.query.first()
    
    if not cart_items:
        return redirect('/cart')
    
    total = sum(item.price * item.quantity for item in cart_items)
    
    return render_template('checkout.html',
                         cart_items=cart_items,
                         total=total,
                         balance=balance.balance if balance else 0)

@app.route('/transactions')
def transactions():
    """
    صفحة سجل المعاملات
    تعرض جميع المعاملات السابقة
    """
    # احضار المعاملات
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Transaction.query
    
    if status:
        query = query.filter_by(status=status)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('transactions.html', transactions=transactions, selected_status=status)

# ==================== API الروتات - عمليات البيانات ====================

@app.route('/api/products/fetch', methods=['POST'])
def fetch_products():
    """
    روت لاحضار المنتجات من API الخارجي
    يقوم بجلب المنتجات وتخزينها في قاعدة البيانات
    
    Returns:
        JSON: حالة العملية ورسالة التأكيد
    """
    try:
        # احضار المنتجات من API
        response = APIService.get_detailed_products_list()
        
        if not APIService.is_success(response):
            return jsonify({
                'success': False,
                'message': APIService.get_error_message(response)
            }), 400
        
        # معالجة المنتجات المحضرة
        products_data = response.get('products', [])
        added_count = 0
        updated_count = 0
        
        for product_data in products_data:
            product_id = product_data.get('productID')
            
            # تحقق من أن المنتج في قائمتنا المطلوبة
            if product_id not in PRODUCT_CODES:
                continue
            
            # ابحث عن المنتج الموجود
            product = Product.query.filter_by(product_id=product_id).first()
            
            if product:
                # تحديث المنتج الموجود
                product.name_ar = product_data.get('nameAr')
                product.name_en = product_data.get('nameEn', '')
                product.merchant_id = product_data.get('merchantid')
                product.merchant_name_ar = product_data.get('merchantNameAr')
                product.merchant_name_en = product_data.get('merchantNameEn')
                product.category_name_ar = product_data.get('categoryNameAr')
                product.category_name_en = product_data.get('categoryNameEn')
                product.cost_price_before_vat = product_data.get('costPriceBeforeVat')
                product.cost_price_vat_amount = product_data.get('costPriceVatAmount')
                product.cost_price_after_vat = product_data.get('costPriceAfterVat')
                product.recommended_retail_price_before_vat = product_data.get('recommendedRetailPriceBeforeVat')
                product.recommended_retail_price_vat_amount = product_data.get('recommendedRetailPriceVatAmount')
                product.recommended_retail_price_after_vat = product_data.get('recommendedRetailPriceAfterVat')
                product.currency = product_data.get('currency')
                product.available = product_data.get('available', True)
                product.image = product_data.get('image')
                product.how_to_use_ar = product_data.get('howToUseAr')
                product.how_to_use_en = product_data.get('howToUseEn')
                product.vat_type = product_data.get('vatType')
                product.vat_percentage = product_data.get('vatPercentage')
                product.face_value = product_data.get('faceValue')
                product.inquiry_required = product_data.get('inquiryRequired', False)
                product.dynamic_form_list = product_data.get('dynamicFormList')
                updated_count += 1
            else:
                # إضافة منتج جديد
                product = Product(
                    product_id=product_id,
                    name_ar=product_data.get('nameAr'),
                    name_en=product_data.get('nameEn', ''),
                    merchant_id=product_data.get('merchantid'),
                    merchant_name_ar=product_data.get('merchantNameAr'),
                    merchant_name_en=product_data.get('merchantNameEn'),
                    category_name_ar=product_data.get('categoryNameAr'),
                    category_name_en=product_data.get('categoryNameEn'),
                    cost_price_before_vat=product_data.get('costPriceBeforeVat'),
                    cost_price_vat_amount=product_data.get('costPriceVatAmount'),
                    cost_price_after_vat=product_data.get('costPriceAfterVat'),
                    recommended_retail_price_before_vat=product_data.get('recommendedRetailPriceBeforeVat'),
                    recommended_retail_price_vat_amount=product_data.get('recommendedRetailPriceVatAmount'),
                    recommended_retail_price_after_vat=product_data.get('recommendedRetailPriceAfterVat'),
                    currency=product_data.get('currency'),
                    available=product_data.get('available', True),
                    image=product_data.get('image'),
                    how_to_use_ar=product_data.get('howToUseAr'),
                    how_to_use_en=product_data.get('howToUseEn'),
                    vat_type=product_data.get('vatType'),
                    vat_percentage=product_data.get('vatPercentage'),
                    face_value=product_data.get('faceValue'),
                    inquiry_required=product_data.get('inquiryRequired', False),
                    dynamic_form_list=product_data.get('dynamicFormList')
                )
                db.session.add(product)
                added_count += 1
        
        # احفظ التغييرات
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'تم إضافة {added_count} منتج جديد وتحديث {updated_count} منتج',
            'added': added_count,
            'updated': updated_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@app.route('/api/balance/check', methods=['GET'])
def check_balance():
    """
    روت للتحقق من الرصيد الحالي من API
    يحدث الرصيد في قاعدة البيانات
    
    Returns:
        JSON: معلومات الرصيد الحالي
    """
    try:
        # احصل على الرصيد من API
        response = APIService.check_balance()
        
        if not APIService.is_success(response):
            # إذا فشل، أرجع الرصيد الموجود في قاعدة البيانات
            balance = Balance.query.first()
            if balance:
                return jsonify({
                    'success': True,
                    'balance': balance.balance,
                    'currency': balance.currency
                }), 200
            return jsonify({
                'success': False,
                'message': APIService.get_error_message(response)
            }), 400
        
        # احدث الرصيد في قاعدة البيانات
        balance = Balance.query.first()
        if not balance:
            balance = Balance()
            db.session.add(balance)
        
        balance.balance = response.get('balance', 0)
        balance.currency = response.get('currency', 'SAR')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'balance': balance.balance,
            'currency': balance.currency
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """
    روت لإضافة منتج إلى سلة التسوق
    
    Body:
        product_id: معرف المنتج
        quantity: الكمية (اختياري، الافتراضي: 1)
    
    Returns:
        JSON: حالة العملية
    """
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # احصل على معرف الجلسة
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # احضار المنتج
        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            return jsonify({'success': False, 'message': 'المنتج غير موجود'}), 404
        
        # التحقق من توفر المنتج
        if not product.available:
            return jsonify({'success': False, 'message': 'المنتج غير متاح'}), 400
        
        # تحقق من المنتج في السلة
        cart_item = CartItem.query.filter_by(
            session_id=session_id,
            product_id=product_id
        ).first()
        
        price = product.recommended_retail_price_after_vat or product.cost_price_after_vat or 0
        
        if cart_item:
            # زد الكمية
            cart_item.quantity += quantity
        else:
            # أضيف عنصر جديد
            cart_item = CartItem(
                session_id=session_id,
                product_id=product_id,
                quantity=quantity,
                price=price
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تمت إضافة المنتج إلى السلة',
            'cart_count': CartItem.query.filter_by(session_id=session_id).count()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

@app.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    """
    روت لحذف منتج من سلة التسوق
    
    Args:
        item_id: معرف عنصر السلة
    
    Returns:
        JSON: حالة العملية
    """
    try:
        session_id = session.get('session_id')
        cart_item = CartItem.query.filter_by(id=item_id, session_id=session_id).first()
        
        if not cart_item:
            return jsonify({'success': False, 'message': 'العنصر غير موجود'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف العنصر من السلة'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'}), 500

@app.route('/api/purchase', methods=['POST'])
def make_purchase():
    """
    روت لإجراء عملية شراء
    يقوم بمعالجة الشراء من خلال API
    
    Body:
        reseller_ref_number: رقم مرجعي فريد (اختياري)
    
    Returns:
        JSON: حالة العملية ومعلومات الشراء
    """
    try:
        data = request.get_json()
        session_id = session.get('session_id')
        
        # احضار عناصر السلة
        cart_items = CartItem.query.filter_by(session_id=session_id).all()
        
        if not cart_items:
            return jsonify({
                'success': False,
                'message': 'السلة فارغة'
            }), 400
        
        # معالجة كل عنصر في السلة
        transactions_created = []
        for item in cart_items:
            # توليد رقم مرجعي فريد
            reseller_ref_number = data.get('reseller_ref_number', str(uuid.uuid4()))
            
            # إنشاء معاملة
            transaction = Transaction(
                product_id=item.product_id,
                product_name=item.product.name_ar or item.product.name_en,
                quantity=item.quantity,
                unit_price=item.price,
                total_price=item.price * item.quantity,
                status='pending'
            )
            db.session.add(transaction)
            db.session.flush()  # احفظ لاحضار المعرف
            
            # حاول الشراء من خلال API
            purchase_response = APIService.make_purchase(
                reseller_ref_number=reseller_ref_number,
                product_id=item.product_id,
                input_parameters={}
            )
            
            if APIService.is_success(purchase_response):
                transaction.status = 'success'
                transaction.response_data = purchase_response
            else:
                transaction.status = 'failed'
                transaction.error_code = purchase_response.get('errorCode')
                transaction.error_message = purchase_response.get('errorMessage')
                transaction.response_data = purchase_response
            
            db.session.commit()
            transactions_created.append(transaction.to_dict())
            
            # احذف العنصر من السلة
            db.session.delete(item)
        
        db.session.commit()
        
        # احدث الرصيد
        balance_response = APIService.check_balance()
        if APIService.is_success(balance_response):
            balance = Balance.query.first()
            if not balance:
                balance = Balance()
                db.session.add(balance)
            balance.balance = balance_response.get('balance')
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تمت عملية الشراء',
            'transactions': transactions_created
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

@app.route('/api/product/<product_id>', methods=['GET'])
def get_product_info(product_id):
    """
    روت لاحضار معلومات منتج محدد
    
    Args:
        product_id: معرف المنتج
    
    Returns:
        JSON: معلومات المنتج
    """
    try:
        # احضار من قاعدة البيانات أولاً
        product = Product.query.filter_by(product_id=product_id).first()
        
        if product:
            return jsonify({
                'success': True,
                'product': product.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'المنتج غير موجود'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطأ: {str(e)}'
        }), 500

# ==================== معالجة الأخطاء ====================

@app.errorhandler(404)
def not_found(error):
    """معالج خطأ 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """معالج خطأ 500"""
    return render_template('500.html'), 500

# ==================== تشغيل التطبيق ====================

if __name__ == '__main__':
    # قم بإنشاء المجلدات إذا لم تكن موجودة
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # شغل التطبيق
    app.run(debug=True, host='0.0.0.0', port=5000)
