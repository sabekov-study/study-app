from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import *

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption

class QuestionInline(admin.TabularInline):
    model = Question
    fk_name = "catalog"

class CatalogInline(admin.TabularInline):
    model = Catalog
    fk_name = "checklist"

class QuestionAdmin(SimpleHistoryAdmin):
    inlines = [
        AnswerOptionInline,
    ]


class CatalogAdmin(admin.ModelAdmin):
    inlines = [
        QuestionInline,
    ]

class ChecklistAdmin(admin.ModelAdmin):
    inlines = [
        CatalogInline,
    ]

class SiteSynonymInline(admin.TabularInline):
    model = SiteSynonym

class SiteAdmin(admin.ModelAdmin):
    inlines = [
        SiteSynonymInline,
    ]

class ListingIssueInline(admin.TabularInline):
    model = ListingIssue

class ListingAdmin(admin.ModelAdmin):
    inlines = [
        ListingIssueInline,
    ]

admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Listing, ListingAdmin)
