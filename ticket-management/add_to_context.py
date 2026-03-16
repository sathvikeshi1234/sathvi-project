# Add recent_payments to context dictionary

# Read the current file
with open('apps/superadmin/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add recent_payments to the context dictionary
content = content.replace(
        """        'expired_subscriptions': expired_subscriptions,
    })""",
        """        'expired_subscriptions': expired_subscriptions,
        'recent_payments': recent_payments,
    })"""
)

# Write back to file
with open('apps/superadmin/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added recent_payments to context dictionary")
