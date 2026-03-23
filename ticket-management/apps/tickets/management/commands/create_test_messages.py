from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tickets.models import ChatMessage
import random

class Command(BaseCommand):
    help = 'Create test chat messages for testing clear chat functionality'

    def handle(self, *args, **options):
        # Get admin user (first staff user)
        try:
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin user found. Please create an admin user first.'))
                return
            
            # Get regular users (non-staff)
            regular_users = User.objects.filter(is_staff=False, is_superuser=False)
            if not regular_users.exists():
                self.stdout.write(self.style.ERROR('No regular users found. Please create some regular users first.'))
                return
            
            # Create test messages
            messages_created = 0
            test_messages = [
                "Hello! How can I help you today?",
                "I have a question about my ticket.",
                "Sure, I'd be happy to help you with that.",
                "Thank you for your assistance!",
                "Is there anything else I can help with?",
                "I need to update my profile information.",
                "No problem, I can guide you through that.",
                "Great! Let me know if you need anything else.",
            ]
            
            for user in regular_users[:3]:  # Create messages for first 3 users
                for i, message_text in enumerate(test_messages[:3]):  # 3 messages per user
                    # Alternate between admin sending and user sending
                    if i % 2 == 0:
                        ChatMessage.objects.create(
                            sender=admin_user,
                            recipient=user,
                            text=message_text
                        )
                    else:
                        ChatMessage.objects.create(
                            sender=user,
                            recipient=admin_user,
                            text=message_text
                        )
                    messages_created += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {messages_created} test chat messages')
            )
            
            # Show summary
            total_messages = ChatMessage.objects.count()
            self.stdout.write(f'Total chat messages in database: {total_messages}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test messages: {str(e)}'))
