# Custom migration to recreate Job table with correct structure
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0001_initial'),
    ]

    operations = [
        # Drop the old table
        migrations.RunSQL(
            "DROP TABLE IF EXISTS jobs_job;",
            reverse_sql="-- Cannot reverse drop table"
        ),
        
        # Recreate the table with correct structure
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(default='', help_text='Job title', max_length=255)),
                ('company_name', models.CharField(default='', help_text='Company name', max_length=255)),
                ('location', models.CharField(default='', help_text='Job location', max_length=255)),
                ('salary_min', models.IntegerField(blank=True, help_text='Minimum salary', null=True)),
                ('salary_max', models.IntegerField(blank=True, help_text='Maximum salary', null=True)),
                ('employment_type', models.CharField(choices=[('full-time', 'Full Time'), ('part-time', 'Part Time'), ('contract', 'Contract'), ('internship', 'Internship'), ('remote', 'Remote')], default='full-time', max_length=20)),
                ('experience_level', models.CharField(choices=[('entry', 'Entry Level'), ('mid', 'Mid Level'), ('senior', 'Senior Level'), ('executive', 'Executive')], default='entry', max_length=20)),
                ('description', models.TextField(default='', help_text='Job description and requirements')),
                ('requirements', models.TextField(default='', help_text='Required skills and qualifications')),
                ('benefits', models.TextField(blank=True, help_text='Benefits and perks')),
                ('image', models.ImageField(blank=True, null=True, upload_to='job_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, help_text='Whether the job posting is active')),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posted_jobs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]