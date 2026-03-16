import os
import sys
import time
import schedule
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Schedule periodic subscription expiry checks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Check interval in minutes (default: 60)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        
        self.stdout.write(
            self.style.SUCCESS(f'=== Subscription Expiry Scheduler ===')
        )
        self.stdout.write(f'Checking every {interval} minutes')
        self.stdout.write('Press Ctrl+C to stop')
        self.stdout.write('')

        # Schedule the expiry check
        schedule.every(interval).minutes.do(
            lambda: execute_from_command_line(['manage.py', 'check_subscription_expiry'])
        )

        # Run once immediately
        self.stdout.write('Running initial check...')
        execute_from_command_line(['manage.py', 'check_subscription_expiry'])

        # Keep the scheduler running
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('Scheduler stopped by user'))
                break
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error in scheduler: {e}')
                )
                time.sleep(60)  # Wait before retrying
