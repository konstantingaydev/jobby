import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import Profile, Skill, Education, WorkExperience, Project

def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="profile_summary_report.csv"'},
    )
    writer = csv.writer(response)

    # add headers here
    writer.writerow([
        'Username', 'Email', 'User Type', 'Headline', 'Location', 'Date Joined', 
        'Skills', 'Education', 'Work History', 'Projects'
    ])

    queryset = queryset.select_related('user').prefetch_related(
        'skills', 'education', 'work_experience', 'projects'
    )

    for profile in queryset:
        # a single string, e.g., "Python; Django"
        skills = "; ".join([s.name for s in profile.skills.all()])
        education = "; ".join([f"{e.degree} at {e.institution}" for e in profile.education.all()])
        work = "; ".join([w.position for w in profile.work_experience.all()])
        projects = "; ".join([p.title for p in profile.projects.all()])

        writer.writerow([
            profile.user.username,
            profile.user.email,
            profile.get_user_type_display(),
            profile.headline,
            profile.location,
            profile.user.date_joined,
            skills,
            education,
            work,
            projects
        ])

    return response

export_as_csv.short_description = "Export Selected Profiles as CSV"

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
    
    actions = [export_as_csv]

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
