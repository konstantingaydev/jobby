# Jobby

Not tracking the sql database, so the job listings you add will be on your machine. You will also have to makemigrations when pulling.

# Migrating
python3 manage.py makemigrations
python3 manage.py migrate

# Start server
python3 manage.py runserver

# create superuser
python3 manage.py createsuperuser
  -input a user, email, password.
  
# Add jobs
Login to admin database by going to http://localhost:8000/admin
  -should be able to create 'jobs' (have improper attributes currently)
