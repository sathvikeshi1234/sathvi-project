from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from superadmin.models import Subscription, Company


class Command(BaseCommand):
    help = 'Check and update expired subscriptions automatically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=0,
            help='Number of days before expiry to mark as expired (default: 0, already expired)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_before = options['days']
        today = timezone.now().date()
        expiry_date = today - timedelta(days=days_before)
        
        self.stdout.write(
            self.style.SUCCESS(f'=== Subscription Expiry Check - {today} ===')
        )
        self.stdout.write(f'Dry run: {dry_run}')
        self.stdout.write(f'Expiry date: {expiry_date}')
        self.stdout.write('')

        # Find subscriptions that should be marked as expired
        expired_subscriptions = Subscription.objects.filter(
            status__in=['active', 'trial'],
            end_date__lt=expiry_date
        ).select_related('company', 'plan')

        # Find companies whose plan_expiry_date has passed
        expired_companies = Company.objects.filter(
            plan_expiry_date__lt=expiry_date,
            is_active=True
        ).exclude(
            plan_expiry_date__isnull=True
        )

        total_updated = 0

        # Update expired subscriptions
        if expired_subscriptions.exists():
            self.stdout.write(
                self.style.WARNING(f'Found {expired_subscriptions.count()} expired subscriptions:')
            )
            
            for subscription in expired_subscriptions:
                days_expired = (today - subscription.end_date).days
                self.stdout.write(
                    f'  - {subscription.company.name} - {subscription.plan.name} '
                    f'(expired {days_expired} days ago)'
                )
                
                if not dry_run:
                    subscription.status = 'expired'
                    subscription.save(update_fields=['status'])
                    total_updated += 1
        else:
            self.stdout.write(self.style.SUCCESS('No expired subscriptions found'))

        # Update companies with expired plan_expiry_date
        if expired_companies.exists():
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(f'Found {expired_companies.count()} companies with expired plan dates:')
            )
            
            for company in expired_companies:
                days_expired = (today - company.plan_expiry_date).days
                self.stdout.write(
                    f'  - {company.name} (plan expired {days_expired} days ago)'
                )
                
                if not dry_run:
                    company.subscription_status = 'expired'
                    company.save(update_fields=['subscription_status'])
                    total_updated += 1
        else:
            self.stdout.write(self.style.SUCCESS('No companies with expired plan dates found'))

        # Update trial subscriptions that have ended
        trial_expired = Subscription.objects.filter(
            status='trial',
            end_date__lt=expiry_date
        ).select_related('company', 'plan')

        if trial_expired.exists():
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(f'Found {trial_expired.count()} expired trial subscriptions:')
            )
            
            for subscription in trial_expired:
                days_expired = (today - subscription.end_date).days
                self.stdout.write(
                    f'  - {subscription.company.name} - {subscription.plan.name} '
                    f'(trial expired {days_expired} days ago)'
                )
                
                if not dry_run:
                    subscription.status = 'expired'
                    subscription.save(update_fields=['status'])
                    total_updated += 1

        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would update {total_updated} records')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'SUCCESS: Updated {total_updated} records')
            )

        # Show current subscription status
        self.stdout.write('')
        self.stdout.write('=== Current Subscription Status ===')
        active_count = Subscription.objects.filter(status='active').count()
        trial_count = Subscription.objects.filter(status='trial').count()
        expired_count = Subscription.objects.filter(status='expired').count()
        cancelled_count = Subscription.objects.filter(status='cancelled').count()
        
        self.stdout.write(f'Active: {active_count}')
        self.stdout.write(f'Trial: {trial_count}')
        self.stdout.write(f'Expired: {expired_count}')
        self.stdout.write(f'Cancelled: {cancelled_count}')
        self.stdout.write(f'Total: {active_count + trial_count + expired_count + cancelled_count}')
