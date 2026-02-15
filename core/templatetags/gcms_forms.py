"""Template tags for form rendering."""
from django import template

register = template.Library()


@register.filter
def is_checkbox(field):
    """Return True if the field's widget is a checkbox (safe when widget has no input_type)."""
    widget = field.field.widget
    return getattr(widget, 'input_type', None) == 'checkbox'
