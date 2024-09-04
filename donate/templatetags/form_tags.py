# # donate/templatetags/form_tags.py
# from django import template

# register = template.Library()

# @register.filter(name='add_class')
# def add_class(field, css_class):
#     return field.as_widget(attrs={"class": css_class})


from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_classes):
    existing_classes = value.field.widget.attrs.get('class', '')
    all_classes = f'{existing_classes} {css_classes}'.strip()
    return value.as_widget(attrs={"class": all_classes})
