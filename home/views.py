from django.shortcuts import render
def index(request):
    template_data = {}
    template_data['title'] = 'Jobby'
    return render(request, 'home/index.html', {
        'template_data': template_data})
