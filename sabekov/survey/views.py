from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import *

@login_required
def index(request):
    template = loader.get_template('survey/index.html')
    context = {
        'site_list': Site.objects.all(),
    }
    return HttpResponse(template.render(context, request))

@login_required
def evaluate(request, site_id):
    s = Site.objects.get(pk=site_id)
    e, created = SiteEvaluation.objects.get_or_create(
        tester=request.user,
        site=Site.objects.get(pk=site_id),
        checklist=Checklist.objects.get(pk=10), # TODO proper handling of multiple checklists
    )
    if created:
        e.populate_answers()

    if request.method == 'POST':
        forms = e.generate_forms(data=request.POST)
        for ans, form in forms:
            form.full_clean()
        valid = all([ form.is_valid() for _, form in forms ])
        if valid:
            for ans, form in forms:
                form.save()
    else:
        forms = e.generate_forms()

    template = loader.get_template('survey/evaluate.html')
    context = {
            'evaluation' : e,
            'forms' : forms,
    }
    return HttpResponse(template.render(context, request))
