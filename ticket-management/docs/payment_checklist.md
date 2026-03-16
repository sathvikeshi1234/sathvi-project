# Payment System Troubleshooting Checklist

## ✅ Fixed Issues
- [x] Payment records are now created in `payment_success` function
- [x] Added `razorpay_key` to template context
- [x] Added `subscription` object to template context  
- [x] Fixed User model field errors (subscription_active, requires_payment)
- [x] Enhanced frontend feedback with payment details

## 🔍 Potential Remaining Issues

### 1. Razorpay Configuration
- [ ] Razorpay key is test key (`rzp_test_1DP5mmOlF5G5ag`) - need production key
- [ ] Currency set to INR but amounts might need conversion
- [ ] Company name and subscription details must be valid

### 2. Template Context Issues
- [ ] `subscription.total_amount` might be None or invalid
- [ ] `subscription.company.name` might be None
- [ ] `subscription.id` might be missing

### 3. Frontend JavaScript Issues
- [ ] Bootstrap modal might not be loaded
- [ ] CSRF token might be missing
- [ ] Fetch API call might fail due to CORS or headers

### 4. Backend Issues
- [ ] Company lookup by `f'{user.username} Company'` might not find company
- [ ] Subscription might not exist for the company
- [ ] Payment creation might fail due to validation errors

## 🧪 Testing Steps

### Step 1: Check Template Context
```python
# In admin_dashboard view, add debug prints
print(f"Subscription: {subscription}")
print(f"Subscription ID: {subscription.id if subscription else None}")
print(f"Subscription Amount: {subscription.total_amount if subscription else None}")
```

### Step 2: Check Frontend Console
Open browser dev tools and check for:
- JavaScript errors
- Network requests to `/superadmin/payment-success/`
- Razorpay modal loading

### Step 3: Test Payment Success Endpoint
```python
# Test the payment_success endpoint directly
import requests
import json

response = requests.post('/superadmin/payment-success/', 
    json={
        'razorpay_payment_id': 'test_12345',
        'subscription_id': 1
    },
    headers={'Content-Type': 'application/json'})
print(response.json())
```

## 🚀 Quick Fixes

### Fix 1: Add Debug Information
Add this to admin_dashboard view:
```python
if show_payment_modal and subscription:
    print(f"DEBUG: Subscription found: {subscription.id}")
    print(f"DEBUG: Subscription amount: {subscription.total_amount}")
    print(f"DEBUG: Company: {subscription.company.name}")
else:
    print(f"DEBUG: No subscription found. show_payment_modal: {show_payment_modal}")
```

### Fix 2: Handle Missing Subscription
In payment_success function, add better error handling:
```python
if not target_subscription:
    print(f"DEBUG: No subscription found for user: {user.username}")
    return JsonResponse({'status': 'error', 'message': f'No subscription found. Companies checked: {[c.name for c in companies]}'}), status=404
```

### Fix 3: Add Frontend Debug
In admin_payment_modal.html, add console logs:
```javascript
console.log('DEBUG: Subscription data:', {{ subscription|safe }});
console.log('DEBUG: Razorpay key:', '{{ razorpay_key }}');
```

## 📋 What to Check Next

1. **Browser Console**: Look for JavaScript errors
2. **Network Tab**: Check if payment-success request is being sent
3. **Server Logs**: Look for payment_success function output
4. **Database**: Verify Payment records are being created
5. **Template Rendering**: Check if modal variables are populated

## 🔧 Common Issues and Solutions

### Issue: "subscription is not defined"
**Solution**: Ensure subscription object is passed to template context

### Issue: "razorpay_key is not defined"  
**Solution**: Add razorpay_key to all view contexts that include the modal

### Issue: Payment modal not showing
**Solution**: Check show_payment_modal logic and session flags

### Issue: Payment success but no record created
**Solution**: Check payment_success function for errors and company lookup

### Issue: Super Admin can't see transactions
**Solution**: Verify Payment objects are created and check all_transactions page
