from __future__ import unicode_literals, print_function

# Standard Library
import csv
import datetime

# Third Party Stuff
from django.conf import settings
from django.db.models import ForeignKey
from django.db.models.loading import get_model
from django.http import HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import slugify

# Spoken Tutorial Stuff
from creation.views import *
from events.views import *


def get_fk_model(model, fieldname):
    '''returns None if not foreignkey, otherswise the relevant model'''
    field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
    print(field_object, model, direct, m2m)
    if not m2m and direct and isinstance(field_object, ForeignKey):
        return field_object.rel.to
    return None


def get_m2m_model_value(obj, field):
    return ", ".join([s.__unicode__() for s in getattr(obj, field).all()])


# def get_all_field_names(obj):
#     fields = []
#     for field in obj._meta.fields:
#         fields.append(field.name)
#     return fields.sort()

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
    # if not request.user.is_staff:
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
        <li><a href="add/{% if is_popup %}?_popup=1{% endif %}" class="addlink">
            {% blocktrans with cl.opts.verbose_name|escape as name %}Add {{ name }}{% endblocktrans %}</a></li>
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
        return export_csv(request, model_name=model_name, app_label=app_label,
                          queryset=queryset, fields=fields, list_display=True)
    context = {'fields': fields}
    context.update(csrf(request))
    return render(request, 'reports/templates/index.html', context)


def elibrary(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="E-library-data.csv"'

    writer = csv.writer(response)
    writer.writerow(['FileNamewithExtension',
                     'dc.contributor.author',
                     'dc.contributor.illustrator',
                     'dc.creator',
                     'dc.contributor.editor',
                     'dc.date.created',
                     'dc.date.copyright',
                     'dc.date.accessioned',
                     'dc.date.available',
                     'dc.identifier.uri',
                     'dc.identifier.isbn',
                     'dc.identifier.issn',
                     'dc.identifier.citation',
                     'dc.description.abstract',
                     'dc.description.tableofcontents',
                     'dc.format.extent',
                     'dc.format.mimetype',
                     'dc.language.iso',
                     'dc.relation.ispartof',
                     'dc.relation.ispartofseries',
                     'dc.relation.haspart',
                     'dc.source',
                     'dc.subject',
                     'dc.subject.ddc',
                     'dc.subject.lcc',
                     'dc.title',
                     'dc.title.alternative',
                     'dc.publisher',
                     'dc.type',
                     'dcterms.educationLevel',
                     'dc.subject.pedagogicobjective',
                     'dc.coverage.board',
                     'dc.format.typicallearningtime',
                     'dc.format.difficultylevel',
                     'dc.type.typeoflearningmaterial',
                     'dc.creator.researcher',
                     'dc.subject.authorkeyword',
                     'dc.contributor.advisor',
                     'dc.publisher.place',
                     'dc.publisher.institution',
                     'dc.date.awarded',
                     'dc.type.degree',
                     'dc.publisher.department',
                     'dc.rights.uri',
                     'dc.rights.rightsholder'])
    trs = TutorialResource.objects.filter(
        Q(status=1) | Q(status=2), language__name='English').all().order_by('tutorial_detail__foss__foss')
    education_level = '"Class-XI;Class-XII;Under Graduate;Post Graduate"'
    edu_board = '"CBSE;ICSE;State Board;University"'
    domain_reviewer = "Nancy Varkey"
    for tr in trs:
        tr.outline = filter(lambda x: x in string.printable, tr.outline)
        keywords = filter(lambda x: x in string.printable, tr.common_content.keyword)
        tr.common_content.keyword = '"' + keywords.replace(',', ';') + '"'
        user_name = find_tutorial_user(tr)
        publish_date = formated_publish_date(tr)
        duration, filesize = video_duration_with_filesize(tr)
        vdurwithsize = '"' + str(duration) + ";" + str(filesize) + '"'
        tutorial_duration = time_plus_ten_min(tr, duration)
        tlevel = get_level(tr)
        videourl = "http://spoken-tutorial.org/watch/" + tr.tutorial_detail.foss.foss + "/" + \
                   tr.tutorial_detail.tutorial + "/" + tr.language.name
        writer.writerow([tr.video, user_name, domain_reviewer, 'NMEICT', '', tr.created, '', '', publish_date,
                         videourl, '', '', '', tr.outline, '', vdurwithsize, 'video/ogg', tr.language.name, '',
                         tr.tutorial_detail.foss.foss, '', '', tr.common_content.keyword, '', '',
                         tr.tutorial_detail.tutorial, '', '', 'Video', education_level, '', edu_board,
                         tutorial_duration, tlevel, 'Audio-Video Lecture/Tutorial', '', '', '', '', '', '', '', '',
                         'CC BY SA', 'NMEICT'])
    return response


def find_tutorial_user(tr):
    if tr.tutorial_detail.foss.foss == "Python" or tr.tutorial_detail.foss.foss == "Python Old Version":
        return "FOSSEE Ptyhon Team"
    elif tr.tutorial_detail.foss.foss == "Scilab":
        return "FOSSEE Scilab Team"
    file_path = settings.MEDIA_ROOT + "Tutorial-user-name-modification-Sheet5.csv"
    if tr.video_user.username == 'pravin1389':
        with open(file_path, 'rbU') as csvfile:
            csvdata = csv.reader(csvfile, delimiter=',', quotechar='|')
            print(tr.tutorial_detail.foss.foss, ",", tr.tutorial_detail.tutorial)
            for row in csvdata:
                try:
                    if row[1] == tr.tutorial_detail.foss.foss and \
                       row[0] == tr.tutorial_detail.tutorial and not row[8] == tr.video_user.username:
                        user = User.objects.get(username=row[8])
                        if user.first_name:
                            return user.first_name + " " + user.last_name
                        else:
                            return user.username
                except Exception as e:
                    print(e, " => ", row[8])
    if tr.video_user.first_name:
        return str(tr.video_user.first_name) + " " + str(tr.video_user.last_name)
    return str(tr.video_user.username)


def formated_publish_date(tr):
    print(tr.id)
    try:
        pt = PublishTutorialLog.objects.filter(tutorial_resource_id=tr.id).last()
        return pt.created
    except:
        return tr.updated


def video_duration_with_filesize(tr):
    video_path = settings.MEDIA_ROOT + "videos/" + \
        str(tr.tutorial_detail.foss_id) + "/" + str(tr.tutorial_detail_id) + "/" + tr.video
    video_info = get_video_info(video_path)
    return video_info['duration'], video_info['size']


def get_level(tr):
    level = {
        'Basic': 'Easy',
        'Intermediate': 'Medium',
        'Advanced': 'Difficult'
    }
    return level[tr.tutorial_detail.level.level]


def time_plus_ten_min(tr, vtime):
    try:
        delta = datetime.timedelta(minutes=10)
        vtime = datetime.datetime.strptime(vtime, '%H:%M:%S') + delta
        return vtime.strftime("%H:%M:%S")
    except:
        pass
    return "00:00:00"
