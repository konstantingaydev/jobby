# Jobby

Not tracking the sql database, so the job listings you add will be on your machine. You will also have to makemigrations when pulling.

# Migrating
1.python3 manage.py makemigrations
2.python3 manage.py migrate

# Start server
1.python3 manage.py runserver

# create superuser
1.python3 manage.py createsuperuser
  -input a username, email, password.
  
# Add jobs
Login to admin database by going to http://localhost:8000/admin
  -should be able to create 'jobs' (have improper attributes currently)

# Recruiter features
After pulling these changes, create migrations and migrate to add candidate fields to profiles:

> python manage.py makemigrations accounts
> python manage.py migrate

Routes added:
- /accounts/recruiter/dashboard/  -> Recruiter dashboard (requires login & recruiter user_type)
- /accounts/recruiter/search/     -> Candidate search (search by skills, location, projects)

Profiles now include optional fields: skills, location, projects. Recruiters can search Job Seeker profiles using the dashboard.
