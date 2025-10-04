from django.contrib import admin
from .models import Profile, Skill, Education, WorkExperience, Project

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'headline', 'location', 'created_at']
    list_filter = ['user_type', 'profile_visibility', 'created_at']
    search_fields = ['user__username', 'user__email', 'headline', 'location']
    inlines = [SkillInline, EducationInline, WorkExperienceInline, ProjectInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type')
        }),
        ('Profile Details', {
            'fields': ('headline', 'bio', 'phone', 'location')
        }),
        ('Links', {
            'fields': ('linkedin_url', 'github_url', 'portfolio_url')
        }),
        ('Legacy Fields', {
            'fields': ('skills_text', 'projects_text'),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'show_contact_info', 'show_skills', 'show_education', 'show_experience', 'show_links')
        }),
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile', 'proficiency_level']
    list_filter = ['proficiency_level']
    search_fields = ['name', 'profile__user__username']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'institution', 'profile', 'start_date', 'end_date']
    list_filter = ['degree', 'start_date']
    search_fields = ['institution', 'degree', 'field_of_study', 'profile__user__username']

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'profile', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current', 'start_date']
    search_fields = ['position', 'company', 'profile__user__username']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'profile', 'start_date', 'end_date', 'is_featured']
    list_filter = ['is_featured', 'start_date']
    search_fields = ['title', 'description', 'technologies', 'profile__user__username']
