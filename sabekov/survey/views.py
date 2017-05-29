from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


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

        forms = e.get_forms(data=request.POST)
        valid = True
        for _, formlist in forms:
            for _, form in formlist:
                form.full_clean()
                valid = valid and form.is_valid()
        if valid:
            for _, formlist in forms:
                for _, form in formlist:
                    if form.has_changed():
                        form.save()
    else:
        eval_form = SiteEvaluationForm(instance=e, prefix='GENERAL')
        forms = e.get_forms()

    template = loader.get_template('survey/evaluate.html')
    context = {
            'evaluation' : e,
            'eval_form': eval_form,
            'forms' : forms,
            'filter' : AnswerFilterForm(),
    }
    return HttpResponse(template.render(context, request))


class SummaryListView(PermissionRequiredMixin, ListView):
    permission_required = 'survey.can_review'
    model = SiteEvaluation
    template_name = 'survey/summary.html'
    context_object_name = 'evaluations'

    def get_queryset(self):
        self.checklist = get_object_or_404(Checklist, pk=self.kwargs['checklist_id'])
        return self.checklist.evaluations.order_by('site', 'tester__username')

    def get_context_data(self, **kwargs):
        context = super(SummaryListView, self).get_context_data(**kwargs)
        context['checklist'] = self.checklist
        return context


class SummaryByUserListView(SummaryListView):
    template_name = 'survey/summary-by-user.html'

    def get_queryset(self):
        self.checklist = get_object_or_404(Checklist, pk=self.kwargs['checklist_id'])
        return self.checklist.evaluations.order_by('tester__username', 'site')


class CompareListView(PermissionRequiredMixin, ListView):
    permission_required = 'survey.can_review'
    model = AnswerChoice
    template_name = 'survey/compare.html'
    context_object_name = 'answers'

    def get_queryset(self):
        self.checklist = get_object_or_404(Checklist, pk=self.kwargs['checklist_id'])
        self.site = get_object_or_404(Site, pk=self.kwargs['site_id'])
        return AnswerChoice.objects.ordered_by_label(self.checklist,
            evaluation__site=self.site)

    def get_context_data(self, **kwargs):
        context = super(CompareListView, self).get_context_data(**kwargs)
        context['checklist'] = self.checklist
        context['site'] = self.site
        return context


class ReviewDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'survey.can_review'
    model = SiteEvaluation
    pk_url_kwarg = 'eval_id'
    template_name = 'survey/review.html'
    context_object_name = 'eval'
