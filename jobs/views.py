from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Job
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        jobs = Job.objects.filter(name__icontains=search_term)
    else:
        jobs = Job.objects.all()
    template_data = {}
    template_data['title'] = 'Jobs'
    template_data['jobs'] = jobs
    return render(request, 'jobs/index.html',
                  {'template_data': template_data})
def show(request, id):
    job = Job.objects.get(id=id)
    template_data = {}
    template_data['title'] = job.name
    template_data['job'] = job
    return render(request, 'jobs/show.html',
                  {'template_data': template_data})