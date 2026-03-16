# Subscription Scheduler and Management

This document explains the automated subscription management system implemented for the ticket system.

## Features Implemented

### 1. Background Job for Subscription Expiry Check

A Django management command automatically marks subscriptions as inactive when they expire:

**Command**: `python manage.py check_subscription_expiry`

**Features**:
- Automatically updates expired subscriptions (status changes from 'active'/'trial' to 'expired')
- Updates companies with expired plan_expiry_date
- Handles trial subscriptions that have ended
- Dry-run mode for testing
- Detailed logging of changes

**Usage**:
```bash
# Test without making changes
python manage.py check_subscription_expiry --dry-run

# Process expired subscriptions
python manage.py check_subscription_expiry

# Process subscriptions expiring within X days
python manage.py check_subscription_expiry --days 7
```

### 2. Automatic Renewal Processing

**Command**: `python manage.py auto_renew_subscriptions`

**Features**:
- Processes subscriptions due for renewal
- Creates automatic payments for subscriptions with auto_renew=True
- Handles overdue subscriptions (marks as suspended)
- Configurable look-ahead period

**Usage**:
```bash
# Test without making changes
python manage.py auto_renew_subscriptions --dry-run

# Process renewals due within 7 days (default)
python manage.py auto_renew_subscriptions

# Process renewals due within 14 days
python manage.py auto_renew_subscriptions --days-ahead 14
```

### 3. Continuous Scheduler

**Script**: `python scripts/scheduler/run_subscription_scheduler.py`

**Features**:
- Runs expiry check every hour
- Processes renewals daily at 2 AM
- Comprehensive logging to file and console
- Automatic restart on errors

**Usage**:
```bash
# Start the continuous scheduler
python scripts/scheduler/run_subscription_scheduler.py
```

### 4. Accept All/Reject All Buttons

Added to the subscriptions page for bulk operations:

**Accept All**: Activates all trial subscriptions
**Reject All**: Cancels all trial subscriptions

## Setup Instructions

### 1. Install Required Dependencies

The scheduler uses the `schedule` package. Install it:

```bash
pip install schedule
```

### 2. Set Up Cron Job (Recommended)

For production, set up a cron job to run the expiry check:

```bash
# Edit crontab
crontab -e

# Add this line to check every hour
0 * * * * cd /path/to/config22 && python manage.py check_subscription_expiry

# Add this line to process renewals daily at 2 AM
0 2 * * * cd /path/to/config22 && python manage.py auto_renew_subscriptions
```

### 3. Alternative: Use the Continuous Scheduler

If you prefer a Python-based scheduler:

```bash
# Run in the background
nohup python scripts/scheduler/run_subscription_scheduler.py > subscription_scheduler.log 2>&1 &
```

### 4. Windows Task Scheduler

For Windows environments:

1. Open Task Scheduler
2. Create a new task
3. Set trigger to run hourly/daily
4. Action: Start a program
   - Program: `python`
   - Arguments: `manage.py check_subscription_expiry`
   - Start in: `d:\config22`

## Database Schema

The system works with these models:

- **Subscription**: Contains `status`, `end_date`, `next_billing_date`, `auto_renew`
- **Company**: Contains `plan_expiry_date`, `subscription_status`
- **Payment**: Records all subscription payments and renewals

## Subscription Status Flow

```
trial → active → expired
  ↓       ↓       ↓
cancelled ← suspended ← cancelled
```

## Monitoring and Logs

- Command output shows detailed information about processed subscriptions
- Scheduler logs to `subscription_scheduler.log`
- Check Django admin for subscription status changes

## Testing

Test the system before deploying:

```bash
# Test expiry check
python manage.py check_subscription_expiry --dry-run

# Test renewal processing
python manage.py auto_renew_subscriptions --dry-run

# Verify current status
python manage.py check_subscription_expiry
```

## Security Notes

- Management commands require Django environment setup
- Bulk actions require SuperAdmin permissions
- All actions are logged for audit purposes
- CSRF protection enabled for web interface actions

## Troubleshooting

### Common Issues:

1. **Command not found**: Ensure you're in the project directory
2. **Permission denied**: Check Django settings and user permissions
3. **Database locked**: Ensure no long-running queries are blocking updates
4. **Scheduler stops**: Check logs for error messages and restart

### Debug Mode:

Run commands with verbose output:
```bash
python manage.py check_subscription_expiry --dry-run --verbosity=2
```
