from django.shortcuts import render
import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.template.defaultfilters import slugify
from django.db.models.loading import get_model
from django.db.models import ForeignKey
from events.views import *

def get_fk_model(model, fieldname):
    '''returns None if not foreignkey, otherswise the relevant model'''
    field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
    print field_object, model, direct, m2m
    if not m2m and direct and isinstance(field_object, ForeignKey):
        return field_object.rel.to
    return None

def get_m2m_model_value(obj, field):
    return ", ".join([s.__unicode__() for s in getattr(obj, field).all()])

def get_all_field_names(obj):
    fields = []
    for field in obj._meta.fields:
        fields.append(field.name)
    return fields.sort()

def get_all_field_names(model):
    fields = []
    model_fields = model._meta.fields
    for field in model_fields:
        fields.append(field.name)
    return fields

def export(qs, fields=None):
    model = qs.model
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    writer = csv.writer(response, delimiter=';')
    # Write headers to CSV file
    human_readable_headers = []
    if fields:
        headers = fields
        for field in headers:
            human_readable_headers.append(field.replace('_', ' ').title())
    else:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
            human_readable_headers.append(field.name.replace('_', ' ').title())
    writer.writerow(human_readable_headers)
    # Write data to CSV file
    for obj in qs:
        row = []
        for field in headers:
            if field in headers:
                val = None
                field_object, model, direct, m2m = obj._meta.get_field_by_name(field)
                if m2m:
                    val = get_m2m_model_value(obj, field)
                elif not m2m and direct and isinstance(field_object, ForeignKey):
                    val = getattr(obj, field)
                else:
                    val = getattr(obj, field)
                if callable(val):
                    val = val()
                row.append(val)
        writer.writerow(row)
    # Return CSV file to browser as download
    return response

def export_csv(request, model_name="None", app_label="None", queryset=None, fields=None, list_display=True):
    """
    Put the following line in your urls.py BEFORE your admin include
    (r'^admin/(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/csv/', 'util.csv_view.admin_list_export'),
    """
    #if not request.user.is_staff:
    #    return HttpResponseForbidden()
    if not queryset:
        model = get_model(app_label, model_name)
        queryset = model.objects.all()
        filters = dict()
        for key, value in request.GET.items():
            if key not in ('ot', 'o') and value:
                if '_0' in key:
                    key = key.split('_0')
                    filters[key[0] + '__gte'] = str(value)
                elif '_1' in key:
                    key = key.split('_1')
                    filters[key[0] + '__lte'] = str(value)
                else:
                    filters[str(key)] = str(value)
        
        #print "*****************"
        #print filters
        #print "*****************"
        if len(filters):
            queryset = queryset.filter(**filters)
    if not fields:
        if list_display and len(queryset.model._meta.fields) > 1:
            fields = get_all_field_names(model)
        else:
            fields = None
    return export(queryset, fields)
    """
    Create your own change_list.html for your admin view and put something like this in it:
    {% block object-tools %}
    <ul class="object-tools">
        <li><a href="csv/{%if request.GET%}?{{request.GET.urlencode}}{%endif%}" class="addlink">Export to CSV</a></li>
    {% if has_add_permission %}
        <li><a href="add/{% if is_popup %}?_popup=1{% endif %}" class="addlink">{% blocktrans with cl.opts.verbose_name|escape as name %}Add {{ name }}{% endblocktrans %}</a></li>
    {% endif %}
    </ul>
    {% endblock %}
    """

def report_filter(request, model_name="None", app_label="None", queryset=None, fields=None, list_display=True):
    model = get_model(app_label, model_name)
    fields = get_all_field_names(model)
    if request.POST:
        fields = None
        fields = request.POST.getlist('column_name')
        return export_csv(request, model_name = model_name, app_label= app_label, queryset = queryset, fields = fields, list_display=True)
    context = {'fields' : fields }
    context.update(csrf(request))
    return render(request, 'reports/templates/index.html', context)
