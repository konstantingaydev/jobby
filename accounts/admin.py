from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, Skill, Education, WorkExperience

# Define an inline admin descriptor for the Profile model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    list_filter = ('profile__user_type', 'is_staff', 'is_superuser', 'groups')

    @admin.display(ordering='profile__user_type', description='User Type')
    def user_type(self, obj):
        # Check if the user has a profile to avoid errors
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_type_display()
        return 'N/A'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register the new profile-related models
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile', 'proficiency_level')
    list_filter = ('proficiency_level',)
    search_fields = ('name', 'profile__user__username')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'profile', 'start_date', 'end_date')
    list_filter = ('degree', 'start_date')
    search_fields = ('degree', 'institution', 'profile__user__username')

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'profile', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date')
    search_fields = ('position', 'company', 'profile__user__username')
