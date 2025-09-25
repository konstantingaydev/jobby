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
