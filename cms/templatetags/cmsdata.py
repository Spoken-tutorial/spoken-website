# Third Party Stuff
from django import template
from django.conf import settings

# Spoken Tutorial Stuff
from cms.models import Block, Nav
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


def get_cms_subnavs(src_subnav):
    subnavs = src_subnav.all().filter(visible__exact=1).order_by('position')

    return subnavs


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


def combine_get_values(getValue, excludes=['page']):
    values = ''
    for k, v in getValue.iteritems():
        if k not in excludes:
            values += k + '=' + v + '&'
    return values

''' includes: will include include's values '''


def reset_get_values(getValue, includes=['page']):
    values = ''
    for k, v in getValue.iteritems():
        if k in includes:
            values += k + '=' + v + '&'
    return values

''' includes: will include include's values '''


def reset_get_value(getValue, exclude_key=None):
    values = ''
    for k, v in getValue.iteritems():
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
    except Exception as e:
        print(e)
        pass
    if token is None:
        token = csrf._get_new_csrf_key()
        try:
            request.META['CSRF_COOKIE'] = token
            request.META['CSRF_COOKIE_USED'] = True
        except Exception as e:
            print(e)
            pass
    return token


def paginator_page_cutter(page_range, current_page):
    page_count = len(page_range)
    if page_count <= 11:
        return page_range

    start_page = current_page - 5
    end_page = current_page + 5

    if current_page <= 11:
        if current_page < 6:
            start_page = 1
            end_page = 11
        else:
            tmp = current_page - 5
            start_page = tmp
            end_page = current_page + 5

    if page_count < end_page:
        end_page = page_count
        tmp = end_page - current_page
        start_page = start_page - (5 - tmp)

    return range(start_page, end_page + 1)


def get_analytics_code():
    context = {
        'analytics_data': settings.ANALYTICS_DATA
    }

    return context


def format_raw_data(raw_data):
    str_rows = raw_data.split('\n')
    formatted_data = ''
    for str_row in str_rows:
        if str_row:
            formatted_data += '<p>' + str_row + '</p>'
    return formatted_data

register.filter('format_raw_data', format_raw_data)
register.inclusion_tag('cms/templates/analytics_code.html')(get_analytics_code)
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
register.filter('paginator_page_cutter', paginator_page_cutter)
register.filter('get_cms_subnavs', get_cms_subnavs)
