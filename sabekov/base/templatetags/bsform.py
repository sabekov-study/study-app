import re
import types

from django import template
from django.forms.widgets import Select

register = template.Library()
_whitespace_re = re.compile('^\s+$')


# Taken from django_widget_tweaks by Mikhail Korobov, MIT LICENSE.
# See  https://pypi.python.org/pypi/django-widget-tweaks/
# Modifications: Removed attr parameter and simplified.
def _process_field_attributes(field, process):
    # decorate field.as_widget method with updated attributes
    old_as_widget = field.as_widget

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        attrs = attrs or {}
        process(widget or self.field.widget, attrs)
        html = old_as_widget(widget, attrs, only_initial)
        self.as_widget = old_as_widget
        return html

    field.as_widget = types.MethodType(as_widget, field)
    return field


@register.filter('bsfield')
def bsfield(bound_field, extra_classes=None):
    css_classes = ['form-control']
    if extra_classes:
        css_classes += extra_classes.split()

    def process(widget, attrs):
        css_classes_str = ' '.join(css_classes)
        if 'class' not in attrs:
            attrs['class'] = css_classes_str
        else:
            attrs['class'] += ' ' + css_classes_str
    return _process_field_attributes(bound_field, process)


@register.filter('bsplaceholder')
def bsplaceholder(bound_field, placeholder):
    def process(widget, attrs):
        attrs['placeholder'] = placeholder
    return _process_field_attributes(bound_field, process)


@register.inclusion_tag('base/bserrors.html')
def bserrors(bound_field_or_form):
    return {
        'errors': bound_field_or_form.errors
    }


@register.simple_tag
def bserrorclass(bound_field_or_form):
    if getattr(bound_field_or_form, 'errors', False):
        return ' has-error'
    return ''


@register.tag
def bslabel(parser, token):
    nodelist = parser.parse(('endbslabel',))
    try:
        tag_name, field_varname = token.split_contents()
    except ValueError:
        raise ValueError('Missing field for bslabel tag.')
    parser.delete_first_token()
    return BSLabelNode(nodelist, field_varname)


class BSLabelNode(template.Node):
    def __init__(self, nodelist, field_varname):
        self.nodelist = nodelist
        self.field_varname = field_varname

    def render(self, context):
        content = self.nodelist.render(context)
        if self.field_varname not in context:
            field_name = 'unknown'
        else:
            field_name = context[self.field_varname].name
        label = '<label for="id_{field_name}" class="control-label">{content}</label>'
        return label.format(field_name=field_name, content=content)


@register.tag
def bshelp(parser, token):
    nodelist = parser.parse(('endbshelp',))
    parser.delete_first_token()
    return BSHelpNode(nodelist)


class BSHelpNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        if _whitespace_re.match(content):
            return ''
        return '<div class="form-text text-muted">{}</div>'.format(content)
