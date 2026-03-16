from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Check user status and fix inactive users'

    def handle(self, *args, **options):
        self.stdout.write("Checking user status...")
        self.stdout.write("=" * 50)
        
        users = User.objects.all()
        
        if not users:
            self.stdout.write("No users found in database")
            return
        
        for user in users:
            self.stdout.write(f"\nUser: {user.username}")
            self.stdout.write(f"  Email: {user.email}")
            self.stdout.write(f"  Django User.is_active: {user.is_active}")
            self.stdout.write(f"  is_staff: {user.is_staff}")
            self.stdout.write(f"  is_superuser: {user.is_superuser}")
            
            # Check UserProfile
            try:
                profile = user.userprofile
                self.stdout.write(f"  UserProfile.is_active: {profile.is_active}")
                self.stdout.write(f"  Role: {profile.role}")
            except UserProfile.DoesNotExist:
                self.stdout.write("  No UserProfile found")
            
            status = "ACTIVE" if user.is_active else "INACTIVE"
            self.stdout.write(f"  Status: {status}")
        
        self.stdout.write("\n" + "=" * 50)
        
        # Create test user if needed
        if not User.objects.filter(username="testuser").exists():
            self.stdout.write("\nCreating test user...")
            user = User.objects.create_user(
                username="testuser",
                email="testuser@example.com",
                password="testpass123",
                is_active=True
            )
            
            # Create UserProfile
            from users.models import Role
            user_role, _ = Role.objects.get_or_create(name='User')
            
            UserProfile.objects.create(
                user=user,
                role=user_role,
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created test user 'testuser' with password 'testpass123'"))
        else:
            self.stdout.write("\nTest user 'testuser' already exists")
        
        # Fix any inactive users
        inactive_users = User.objects.filter(is_active=False)
        if inactive_users:
            self.stdout.write(f"\nFound {inactive_users.count()} inactive users, activating them...")
            for user in inactive_users:
                user.is_active = True
                user.save()
                
                # Also activate profile if exists
                try:
                    profile = user.userprofile
                    profile.is_active = True
                    profile.save()
                except UserProfile.DoesNotExist:
                    pass
                
                self.stdout.write(self.style.SUCCESS(f"Activated user '{user.username}'"))
        else:
            self.stdout.write("\nNo inactive users found")
