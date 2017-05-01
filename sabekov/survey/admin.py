from django.contrib import admin

from .models import Question, AnswerOption, Catalog, Checklist, Site

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption

class QuestionInline(admin.TabularInline):
    model = Question
    fk_name = "catalog"

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnswerOptionInline,
    ]


class CatalogAdmin(admin.ModelAdmin):
    inlines = [
        QuestionInline,
    ]

admin.site.register(Checklist)
admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Site)
