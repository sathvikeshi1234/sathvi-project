from django.contrib import admin
from .models import Role, UserProfile
from django.contrib.auth.models import User

# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'department', 'is_active', 'user_is_active')
    search_fields = ('user__username', 'role__name')
    list_filter = ('role', 'is_active')
    
    def user_is_active(self, obj):
        return obj.user.is_active
    user_is_active.boolean = True
    user_is_active.short_description = 'User Active'
    
    def save_model(self, request, obj, form, change):
        # When saving profile, sync with user status
        if obj.user:
            # If profile is being activated, also activate user
            if obj.is_active and not obj.user.is_active:
                obj.user.is_active = True
                obj.user.save()
            # If profile is being deactivated, also deactivate user
            elif not obj.is_active and obj.user.is_active:
                obj.user.is_active = False
                obj.user.save()
        
        super().save_model(request, obj, form, change)


# Add custom User admin to sync profile status
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'profile_is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    def profile_is_active(self, obj):
        try:
            return obj.userprofile.is_active
        except UserProfile.DoesNotExist:
            return False
    profile_is_active.boolean = True
    profile_is_active.short_description = 'Profile Active'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # When saving user, sync with profile status
        try:
            profile = obj.userprofile
            # If user is being activated, also activate profile
            if obj.is_active and not profile.is_active:
                profile.is_active = True
                profile.save()
            # If user is being deactivated, also deactivate profile
            elif not obj.is_active and profile.is_active:
                profile.is_active = False
                profile.save()
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            from .models import Role
            user_role, _ = Role.objects.get_or_create(name='User')
            UserProfile.objects.create(
                user=obj,
                role=user_role,
                is_active=obj.is_active
            )

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)