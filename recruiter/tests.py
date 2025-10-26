from django.test import TestCase, Client
from django.contrib.auth.models import User
from profiles.models import Profile
from jobs.models import Job
from applications.models import Application


class KanbanTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='rec', password='pass')
		Profile.objects.create(user=self.user, user_type='recruiter')
		# create a job posted by recruiter
		self.job = Job.objects.create(title='Eng', company_name='Acme', posted_by=self.user)
		# create an applicant and application
		self.applicant = User.objects.create_user(username='cand', password='pw')
		self.app = Application.objects.create(applicant=self.applicant, job=self.job)

	def test_kanban_view_loads(self):
		self.client.login(username='rec', password='pass')
		resp = self.client.get(f'/recruiter/kanban/{self.job.id}/')
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Pipeline')
