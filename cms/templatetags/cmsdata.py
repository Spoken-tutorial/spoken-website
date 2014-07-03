from django import template
from cms.models import Block, Nav, SubNav
from cms.sortable import *

register = template.Library()

def len_cutter(srting, limit):
    return srting[:limit] + (srting[limit:] and '..')
    
def get_cms_sidebar():
    block = Block.objects.all().filter(block_location_id=3, visible__exact=1).order_by('position')
    context = {
        'blocks': block
    }

    return context

def get_cms_nav():
    nav = Nav.objects.all().filter(visible__exact=1).order_by('position')
    context = {
        'navs': nav
    }

    return context

@register.filter
def sort_by(queryset, order):
    return queryset.filter(visible__exact=1).order_by('position')

def get_cms_footer():
    block = Block.objects.all().filter(block_location_id=2, visible__exact=1).order_by('position')
    context = {
        'blocks': block
    }

    return context

def get_cms_header():
    block = Block.objects.all().filter(block_location_id=1, visible__exact=1).order_by('position')
    context = {
        'blocks': block
    }

    return context

''' excludes: will exclude excludes's values '''
def combine_get_values(getValue, excludes = ['page']):
    values = ''
    for k,v in getValue.iteritems():
        if k not in excludes:
            values += k+'='+v+'&'
    return values

''' includes: will include include's values '''
def reset_get_values(getValue, includes = ['page']):
    values = ''
    for k,v in getValue.iteritems():
        if k in includes:
            values += k+'='+v+'&'
    return values

''' includes: will include include's values '''
def reset_get_value(getValue, exclude_key = None):
    values = ''
    for k,v in getValue.iteritems():
        if k != exclude_key:
            if values:
                values += '&'
            values += k + '=' + v
    return values

def get_or_create_csrf_token(request):
    from django.middleware import csrf
    token = None
    try:
        token = request.META.get('CSRF_COOKIE', None)
    except Exception, e:
        print e
        pass
    if token is None:
        token = csrf._get_new_csrf_key()
        try:
            request.META['CSRF_COOKIE'] = token
            request.META['CSRF_COOKIE_USED'] = True
        except Exception, e:
            print e
            pass
    print token
    return token
    
register.filter('len_cutter', len_cutter)
register.inclusion_tag('cms/templates/sortable_header.html')(get_sortable_header)
register.inclusion_tag('cms/templates/cmsnav.html')(get_cms_nav)
register.inclusion_tag('cms/templates/cmsidebar.html')(get_cms_sidebar)
register.inclusion_tag('cms/templates/cmsfooter.html')(get_cms_footer)
register.inclusion_tag('cms/templates/cmsheader.html')(get_cms_header)
register.filter('combine_get_values', combine_get_values)
register.filter('reset_get_values', reset_get_values)
register.filter('reset_get_value', reset_get_value)
register.filter('get_or_create_csrf_token', get_or_create_csrf_token)
