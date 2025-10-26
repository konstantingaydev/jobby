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
