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
        checklist=Checklist.objects.get(is_active=True),
    )
    e.populate_answers() # Note: running on existing evaluations it adds potentially new questions

    if request.method == 'POST':
        eval_form = SiteEvaluationForm(request.POST, instance=e, prefix='GENERAL')
        if eval_form.is_valid():
            eval_form.save()

        forms = e.generate_forms(data=request.POST)
        for ans, form in forms:
            form.full_clean()
        valid = all([ form.is_valid() for _, form in forms ])
        if valid:
            for ans, form in forms:
                form.save()
    else:
        eval_form = SiteEvaluationForm(instance=e, prefix='GENERAL')
        forms = e.generate_forms()

    template = loader.get_template('survey/evaluate.html')
    context = {
            'evaluation' : e,
            'eval_form': eval_form,
            'forms' : forms,
    }
    return HttpResponse(template.render(context, request))
