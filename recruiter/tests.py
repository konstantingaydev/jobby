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


class SavedSearchTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.recruiter = User.objects.create_user(username='recruiter', password='pass')
		# Profile is created via signal, just update it
		self.recruiter.profile.user_type = 'recruiter'
		self.recruiter.profile.save()

	def test_save_search(self):
		"""Test that a recruiter can save a search"""
		self.client.login(username='recruiter', password='pass')
		response = self.client.post('/recruiter/candidates/save/', {
			'name': 'Python Devs',
			'skills': 'Python, Django',
			'location': 'New York'
		})
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertTrue(data['success'])

		from .models import SavedSearch
		saved = SavedSearch.objects.get(recruiter=self.recruiter)
		self.assertEqual(saved.name, 'Python Devs')
		self.assertEqual(saved.skills, 'Python, Django')

	def test_apply_saved_search(self):
		"""Test that a saved search can be applied"""
		from .models import SavedSearch
		search = SavedSearch.objects.create(
			recruiter=self.recruiter,
			name='Test Search',
			skills='Java',
			location='Boston'
		)
		
		self.client.login(username='recruiter', password='pass')
		response = self.client.get(f'/recruiter/candidates/apply/{search.id}/')
		self.assertEqual(response.status_code, 302)  # Redirect
		self.assertIn('skills=Java', response.url)
		self.assertIn('location=Boston', response.url)

	def test_delete_saved_search(self):
		"""Test that a saved search can be deleted"""
		from .models import SavedSearch
		search = SavedSearch.objects.create(
			recruiter=self.recruiter,
			name='Test Search',
			skills='C++'
		)
		
		self.client.login(username='recruiter', password='pass')
		response = self.client.post(
			f'/recruiter/candidates/delete/{search.id}/',
			HTTP_X_REQUESTED_WITH='XMLHttpRequest'
		)
		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertTrue(data['success'])
		
		# Verify search was deleted
		self.assertEqual(SavedSearch.objects.filter(id=search.id).count(), 0)
