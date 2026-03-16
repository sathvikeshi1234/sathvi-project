#!/usr/bin/env python
"""
Subscription Scheduler Runner
This script runs the subscription expiry check and renewal processing automatically.
"""

import os
import sys
from pathlib import Path
import django
import time
import schedule
import logging
from datetime import datetime

# Setup Django
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("subscription_scheduler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def run_expiry_check():
    """Run subscription expiry check"""
    logger.info("Running subscription expiry check...")
    try:
        from django.core.management import execute_from_command_line

        execute_from_command_line(["manage.py", "check_subscription_expiry"])
        logger.info("Expiry check completed successfully")
    except Exception as e:
        logger.error(f"Error in expiry check: {e}")


def run_renewal_processing():
    """Run subscription renewal processing"""
    logger.info("Running renewal processing...")
    try:
        from django.core.management import execute_from_command_line

        execute_from_command_line(["manage.py", "auto_renew_subscriptions"])
        logger.info("Renewal processing completed successfully")
    except Exception as e:
        logger.error(f"Error in renewal processing: {e}")


def main():
    """Main scheduler function"""
    logger.info("=== Subscription Scheduler Started ===")

    # Schedule tasks
    schedule.every().hour.do(run_expiry_check)  # Check expiry every hour
    schedule.every().day.at("02:00").do(
        run_renewal_processing
    )  # Process renewals daily at 2 AM

    # Run once immediately on startup
    logger.info("Running initial checks...")
    run_expiry_check()
    run_renewal_processing()

    logger.info("Scheduler running. Press Ctrl+C to stop.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("=== Subscription Scheduler Stopped ===")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        time.sleep(300)  # Wait 5 minutes before retrying


if __name__ == "__main__":
    main()
