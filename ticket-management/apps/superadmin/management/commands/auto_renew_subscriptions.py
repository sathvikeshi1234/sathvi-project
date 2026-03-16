from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from superadmin.models import Subscription, Payment
from decimal import Decimal


class Command(BaseCommand):
    help = 'Automatically process subscription renewals and billing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes',
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Process renewals due within X days (default: 7)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_ahead = options['days_ahead']
        today = timezone.now().date()
        due_date = today + timedelta(days=days_ahead)
        
        self.stdout.write(
            self.style.SUCCESS(f'=== Auto Renewal Processing - {today} ===')
        )
        self.stdout.write(f'Dry run: {dry_run}')
        self.stdout.write(f'Processing due dates up to: {due_date}')
        self.stdout.write('')

        # Find subscriptions due for renewal
        due_subscriptions = Subscription.objects.filter(
            status='active',
            auto_renew=True,
            next_billing_date__lte=due_date,
            next_billing_date__gte=today
        ).select_related('company', 'plan')

        total_processed = 0
        total_amount = Decimal('0.00')

        if due_subscriptions.exists():
            self.stdout.write(
                self.style.WARNING(f'Found {due_subscriptions.count()} subscriptions due for renewal:')
            )
            
            for subscription in due_subscriptions:
                days_until_billing = (subscription.next_billing_date - today).days
                self.stdout.write(
                    f'  - {subscription.company.name} - {subscription.plan.name} '
                    f'(${subscription.total_amount}) - Due in {days_until_billing} days'
                )
                
                if not dry_run:
                    # Create renewal payment
                    payment = Payment.objects.create(
                        subscription=subscription,
                        company=subscription.company,
                        amount=subscription.total_amount,
                        payment_method='auto_renewal',
                        payment_type='subscription',
                        status='completed',
                        payment_date=timezone.now(),
                        transaction_id=f'AUTO-{subscription.id}-{timezone.now().strftime("%Y%m%d%H%M")}',
                        invoice_number=f'INV-{subscription.id}-{timezone.now().strftime("%Y%m%d")}',
                        notes=f'Automatic renewal for {subscription.plan.name} subscription'
                    )
                    
                    # Update next billing date
                    subscription.update_next_billing_date()
                    
                    total_processed += 1
                    total_amount += subscription.total_amount
                    
                    self.stdout.write(
                        f'    ✓ Payment #{payment.id} created - ${payment.amount}'
                    )
        else:
            self.stdout.write(self.style.SUCCESS('No subscriptions due for renewal found'))

        # Find overdue subscriptions (billing date passed)
        overdue_subscriptions = Subscription.objects.filter(
            status='active',
            next_billing_date__lt=today
        ).select_related('company', 'plan')

        if overdue_subscriptions.exists():
            self.stdout.write('')
            self.stdout.write(
                self.style.ERROR(f'Found {overdue_subscriptions.count()} overdue subscriptions:')
            )
            
            for subscription in overdue_subscriptions:
                days_overdue = (today - subscription.next_billing_date).days
                self.stdout.write(
                    f'  - {subscription.company.name} - {subscription.plan.name} '
                    f'- Overdue by {days_overdue} days'
                )
                
                if not dry_run:
                    # Mark as suspended for non-payment
                    subscription.status = 'suspended'
                    subscription.save(update_fields=['status'])
                    
                    self.stdout.write(
                        f'    ⚠ Subscription marked as suspended'
                    )

        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would process {total_processed} renewals worth ${total_amount}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'SUCCESS: Processed {total_processed} renewals worth ${total_amount}')
            )
