from django.db import models
from django.conf import settings
from applications.models import Application
from jobs.models import Job


class Stage(models.Model):
	"""A stage/column in a pipeline for a specific job."""
	job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='pipeline_stages')
	name = models.CharField(max_length=100)
	order = models.PositiveIntegerField(default=0)

	class Meta:
		unique_together = (('job', 'order'),)
		ordering = ['order']

	def __str__(self):
		return f"{self.job.title}: {self.name}"


class CandidateCard(models.Model):
	"""Represents an application placed in a stage column."""
	application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='kanban_card')
	stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='cards')
	order = models.PositiveIntegerField(default=0)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = (('stage', 'order'),)
		ordering = ['order']

	def __str__(self):
		return f"{self.application} in {self.stage.name} (#{self.order})"


class SavedSearch(models.Model):
	"""Saved candidate search criteria for a recruiter."""
	recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_searches')
	name = models.CharField(max_length=200, help_text="Name for this saved search")

	# Search criteria fields
	skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skills")
	location = models.CharField(max_length=255, blank=True, help_text="Location filter")
	projects = models.CharField(max_length=500, blank=True, help_text="Projects keywords")
	general_search = models.CharField(max_length=500, blank=True, help_text="General search query")

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		unique_together = (('recruiter', 'name'),)

	def __str__(self):
		return f"{self.name} ({self.recruiter.username})"

	def get_search_params(self):
		"""Return a dict of non-empty search parameters."""
		params = {}
		if self.skills:
			params['skills'] = self.skills
		if self.location:
			params['location'] = self.location
		if self.projects:
			params['projects'] = self.projects
		if self.general_search:
			params['search'] = self.general_search
		return params

	def get_criteria_display(self):
		"""Return a human-readable string of search criteria."""
		parts = []
		if self.skills:
			parts.append(f"Skills: {self.skills}")
		if self.location:
			parts.append(f"Location: {self.location}")
		if self.projects:
			parts.append(f"Projects: {self.projects}")
		if self.general_search:
			parts.append(f"Search: {self.general_search}")
		return " | ".join(parts) if parts else "No filters"
