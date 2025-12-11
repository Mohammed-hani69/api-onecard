/**
 * ملف JavaScript الرئيسي
 * يحتوي على جميع الوظائف المساعدة والعمليات الأساسية
 */

// ==================== دالة لعرض الإخطارات ====================
/**
 * عرض رسالة إخطار للمستخدم
 * @param {string} message - النص المراد عرضه
 * @param {string} type - نوع الرسالة (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // إنشاء عنصر div للإخطار
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // إضافة أنماط الإخطار
    const style = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        color: white;
        font-weight: bold;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    notification.style.cssText = style;
    
    // تحديد لون الإخطار حسب النوع
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#4CAF50';
            break;
        case 'error':
            notification.style.backgroundColor = '#f44336';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ff9800';
            break;
        default:
            notification.style.backgroundColor = '#2196F3';
    }
    
    // أضيف الإخطار إلى الصفحة
    document.body.appendChild(notification);
    
    // احذف الإخطار بعد 3 ثوان
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ==================== دالة تحديث عدد السلة ====================
/**
 * تحديث عدد العناصر في شريط التنقل (رقم السلة)
 * لاحضار عدد العناصر من localStorage
 */
function updateCartCount() {
    // احضار عدد العناصر من localStorage
    const cartCount = localStorage.getItem('cartCount') || 0;
    
    // تحديث جميع عناصر cartCount في الصفحة
    const countElements = document.querySelectorAll('#cartCount');
    countElements.forEach(el => {
        el.textContent = cartCount;
    });
}

// ==================== دالة إضافة منتج إلى السلة ====================
/**
 * إضافة منتج إلى سلة التسوق
 * @param {string} productId - معرف المنتج
 * @param {string} productName - اسم المنتج (للعرض)
 * @param {number} quantity - الكمية (اختياري، الافتراضي: 1)
 */
function addToCart(productId, productName, quantity = 1) {
    // إرسال طلب POST إلى الخادم
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // تحديث عدد السلة
            localStorage.setItem('cartCount', data.cart_count);
            updateCartCount();
            
            // عرض رسالة نجاح
            showNotification(`تمت إضافة ${productName} إلى السلة`, 'success');
        } else {
            // عرض رسالة خطأ
            showNotification('خطأ: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('حدث خطأ في الاتصال', 'error');
    });
}

// ==================== دالة حذف منتج من السلة ====================
/**
 * حذف منتج من سلة التسوق
 * @param {number} itemId - معرف عنصر السلة
 */
function removeFromCart(itemId) {
    // تأكيد من المستخدم
    if (!confirm('هل أنت متأكد من حذف هذا العنصر؟')) {
        return;
    }
    
    // إرسال طلب DELETE إلى الخادم
    fetch(`/api/cart/remove/${itemId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // إزالة الصف من الجدول بحركة
            const row = document.getElementById(`row-${itemId}`);
            if (row) {
                row.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => {
                    row.remove();
                    // إعادة تحميل الصفحة بعد الحذف
                    location.reload();
                }, 300);
            }
            
            showNotification('تم حذف العنصر', 'success');
        } else {
            showNotification('خطأ: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('حدث خطأ في الاتصال', 'error');
    });
}

// ==================== دالة تحديث الرصيد ====================
/**
 * احضار الرصيد الحالي من API وتحديثه
 */
function checkBalance() {
    // عرض رسالة جاري التحميل
    showNotification('جاري تحديث الرصيد...', 'info');
    
    // إرسال طلب GET إلى الخادم
    fetch('/api/balance/check', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // تحديث عنصر الرصيد في الصفحة
            const balanceElements = document.querySelectorAll('#balance');
            balanceElements.forEach(el => {
                el.textContent = parseFloat(data.balance).toFixed(2) + ' ر.س';
            });
            
            showNotification('تم تحديث الرصيد بنجاح', 'success');
        } else {
            showNotification('خطأ: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('حدث خطأ في الاتصال', 'error');
    });
}

// ==================== دالة تحديث قائمة المنتجات ====================
/**
 * احضار المنتجات من API الخارجي وتخزينها في قاعدة البيانات
 */
function fetchProducts() {
    // عرض رسالة جاري التحميل
    const btn = event.target;
    const originalText = btn.textContent;
    btn.textContent = '⏳ جاري التحميل...';
    btn.disabled = true;
    
    // إرسال طلب POST إلى الخادم
    fetch('/api/products/fetch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        // استرجاع حالة الزر
        btn.textContent = originalText;
        btn.disabled = false;
        
        if (data.success) {
            // عرض رسالة النجاح مع الإحصائيات
            showNotification(
                `✓ ${data.message}\nتم إضافة: ${data.added}, تم تحديث: ${data.updated}`,
                'success'
            );
            
            // إعادة تحميل الصفحة بعد ثانيتين
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            showNotification('خطأ: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btn.textContent = originalText;
        btn.disabled = false;
        showNotification('حدث خطأ في الاتصال', 'error');
    });
}

// ==================== إضافة الرسوم المتحركة ====================
/**
 * CSS للرسوم المتحركة
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== معالجات الأحداث ====================

/**
 * عند تحميل الصفحة
 */
document.addEventListener('DOMContentLoaded', () => {
    // تحديث عدد السلة من localStorage
    updateCartCount();
    
    // إذا كانت هناك بيانات في النموذج، احفظها تلقائياً
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('change', () => {
            // يمكن إضافة حفظ تلقائي هنا إذا لزم الأمر
        });
    });
});

/**
 * معالجة إغلاق الصفحة - احفظ البيانات المهمة
 */
window.addEventListener('beforeunload', () => {
    // يمكن إضافة حفظ البيانات هنا إذا لزم الأمر
});

// ==================== دوال مساعدة إضافية ====================

/**
 * تنسيق الأرقام بصيغة نقدية
 * @param {number} value - القيمة المراد تنسيقها
 * @param {string} currency - رمز العملة (SAR, USD, إلخ)
 * @returns {string} القيمة المنسقة
 */
function formatCurrency(value, currency = 'SAR') {
    return parseFloat(value).toFixed(2) + ' ' + currency;
}

/**
 * التحقق من صحة البريد الإلكتروني
 * @param {string} email - البريد الإلكتروني
 * @returns {boolean} True إذا كان صحيحاً
 */
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * التحقق من صحة الهاتف
 * @param {string} phone - رقم الهاتف
 * @returns {boolean} True إذا كان صحيحاً
 */
function validatePhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
    return phoneRegex.test(phone);
}

/**
 * الحصول على معامل URL
 * @param {string} paramName - اسم المعامل
 * @returns {string|null} قيمة المعامل أو null
 */
function getUrlParam(paramName) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(paramName);
}

/**
 * تأخير التنفيذ (للاستخدام مع async/await)
 * @param {number} ms - الوقت بالميلي ثانية
 * @returns {Promise}
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

console.log('✓ تم تحميل ملف JavaScript بنجاح');
