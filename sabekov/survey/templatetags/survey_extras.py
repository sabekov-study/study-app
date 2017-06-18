from django import template

register = template.Library()

@register.filter
def calc_irr(site, checklist):
    return site.calc_inter_rater_relyability(checklist)

