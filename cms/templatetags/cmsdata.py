from django import template
from cms.models import Block, Nav, SubNav

register = template.Library()

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

register.inclusion_tag('cms/templates/cmsnav.html')(get_cms_nav)
register.inclusion_tag('cms/templates/cmsidebar.html')(get_cms_sidebar)
register.inclusion_tag('cms/templates/cmsfooter.html')(get_cms_footer)
register.inclusion_tag('cms/templates/cmsheader.html')(get_cms_header)

