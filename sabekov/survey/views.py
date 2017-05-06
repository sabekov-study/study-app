from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.urls import reverse


from .models import *
from .forms import *

@login_required
def index(request, checklist_id):
    if request.method == 'POST':
        cl_form = ChecklistForm(request.POST)
        if cl_form.is_valid():
            checklist = cl_form.cleaned_data.get('checklist')
            return HttpResponseRedirect(reverse('survey:site_overview', args=[checklist.id]))

    checklist = Checklist.objects.get(pk=checklist_id)
    site_list = list()
    for site in Site.objects.all():
        try:
            se = site.evaluations.get(
                checklist=checklist,
                tester=request.user,
            )
        except SiteEvaluation.DoesNotExist:
            se = None
        site_list.append((site, se))

    template = loader.get_template('survey/index.html')
    context = {
        'checklist': Checklist.objects.get(pk=checklist_id),
        'cl_form': ChecklistForm(
            initial={'checklist': checklist_id}
        ),
        'site_list': site_list,
    }
    return HttpResponse(template.render(context, request))

@login_required
def evaluate(request, checklist_id, site_id):
    s = Site.objects.get(pk=site_id)
    e, created = SiteEvaluation.objects.get_or_create(
        tester=request.user,
        site=Site.objects.get(pk=site_id),
        checklist=Checklist.objects.get(pk=checklist_id),
    )
    e.populate_answers() # Note: running on existing evaluations it adds potentially new questions

    if request.method == 'POST':
        eval_form = SiteEvaluationForm(request.POST, instance=e, prefix='GENERAL')
        if eval_form.is_valid() and eval_form.has_changed():
            eval_form.save()

        forms = e.generate_forms(data=request.POST)
        for ans, form in forms:
            form.full_clean()
        valid = all([ form.is_valid() for _, form in forms ])
        if valid:
            for ans, form in forms:
                if form.has_changed():
                    form.save()
    else:
        eval_form = SiteEvaluationForm(instance=e, prefix='GENERAL')
        forms = e.generate_forms()

    template = loader.get_template('survey/evaluate.html')
    context = {
            'evaluation' : e,
            'eval_form': eval_form,
            'forms' : forms,
            'filter' : AnswerFilterForm(),
    }
    return HttpResponse(template.render(context, request))
