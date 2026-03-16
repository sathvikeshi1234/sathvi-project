# Add recent payments to subscriptions view context

import re

# Read the current file
with open('apps/superadmin/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the context update section and add recent payments
pattern = r"('monthly_revenue': monthly_revenue,\s*'mrr': mrr,\s*})"
replacement = r"""'monthly_revenue': monthly_revenue,
        'mrr': mrr,
        
        # Recent payments for the transactions section
        recent_payments = Payment.objects.select_related('company', 'subscription__plan').order_by('-payment_date')[:5],
    })"""

# Apply the replacement
new_content = re.sub(pattern, replacement, content)

# Write back to file
with open('apps/superadmin/views.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Added recent_payments to subscriptions view context")
