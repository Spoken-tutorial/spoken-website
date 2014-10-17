# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Test.use_exam_app'
        db.add_column(u'events_test', 'use_exam_app',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'FossMdlCourses.examquestionpaper'
        db.add_column(u'events_fossmdlcourses', 'examquestionpaper',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.QuestionPaper'], null=True),
                      keep_default=False)

        # Adding field 'FossMdlCourses.use_exam_app'
        db.add_column(u'events_fossmdlcourses', 'use_exam_app',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'TestAttendance.user'
        db.add_column(u'events_testattendance', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True),
                      keep_default=False)

        # Adding field 'TestAttendance.examquestionpaper'
        db.add_column(u'events_testattendance', 'examquestionpaper',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exam.QuestionPaper'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Test.use_exam_app'
        db.delete_column(u'events_test', 'use_exam_app')

        # Deleting field 'FossMdlCourses.examquestionpaper'
        db.delete_column(u'events_fossmdlcourses', 'examquestionpaper_id')

        # Deleting field 'FossMdlCourses.use_exam_app'
        db.delete_column(u'events_fossmdlcourses', 'use_exam_app')

        # Deleting field 'TestAttendance.user'
        db.delete_column(u'events_testattendance', 'user_id')

        # Deleting field 'TestAttendance.examquestionpaper'
        db.delete_column(u'events_testattendance', 'examquestionpaper_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'creation.fosscategory': {
            'Meta': {'ordering': "('foss',)", 'object_name': 'FossCategory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'foss': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'max_length': '2'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'creation.language': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Language'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.academiccenter': {
            'Meta': {'object_name': 'AcademicCenter'},
            'academic_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.City']"}),
            'contact_person': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.District']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.InstituteCategory']"}),
            'institution_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'institution_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.InstituteType']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Location']", 'null': 'True'}),
            'pincode': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rating': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'remarks': ('django.db.models.fields.TextField', [], {}),
            'resource_center': ('django.db.models.fields.BooleanField', [], {}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.State']"}),
            'status': ('django.db.models.fields.BooleanField', [], {}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.University']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.city': {
            'Meta': {'unique_together': "(('name', 'state'),)", 'object_name': 'City'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.State']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'events.course': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'Course'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.department': {
            'Meta': {'object_name': 'Department'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.district': {
            'Meta': {'unique_together': "(('state', 'code', 'name'),)", 'object_name': 'District'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.State']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'events.eventsnotification': {
            'Meta': {'object_name': 'EventsNotification'},
            'academic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AcademicCenter']"}),
            'category': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'categoryid': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'role': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.fossmdlcourses': {
            'Meta': {'object_name': 'FossMdlCourses'},
            'examquestionpaper': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.QuestionPaper']", 'null': 'True'}),
            'foss': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['creation.FossCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdlcourse_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mdlquiz_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'use_exam_app': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'events.institutecategory': {
            'Meta': {'object_name': 'InstituteCategory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.institutetype': {
            'Meta': {'unique_together': "(('name',),)", 'object_name': 'InstituteType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.invigilator': {
            'Meta': {'object_name': 'Invigilator'},
            'academic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AcademicCenter']"}),
            'appoved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invigilator_approved_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'events.location': {
            'Meta': {'unique_together': "(('name', 'district', 'pincode'),)", 'object_name': 'Location'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.District']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pincode': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.organiser': {
            'Meta': {'object_name': 'Organiser'},
            'academic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AcademicCenter']", 'null': 'True', 'blank': 'True'}),
            'appoved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organiser_approved_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'organiser'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'events.permission': {
            'Meta': {'object_name': 'Permission'},
            'assigned_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_assigned_by'", 'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_district'", 'null': 'True', 'to': u"orm['events.District']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institute': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_district'", 'null': 'True', 'to': u"orm['events.AcademicCenter']"}),
            'institute_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_institution_type'", 'null': 'True', 'to': u"orm['events.InstituteType']"}),
            'permissiontype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.PermissionType']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_state'", 'to': u"orm['events.State']"}),
            'university': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_iniversity'", 'null': 'True', 'to': u"orm['events.University']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_user'", 'to': u"orm['auth.User']"})
        },
        u'events.permissiontype': {
            'Meta': {'object_name': 'PermissionType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.resourceperson': {
            'Meta': {'unique_together': "(('user', 'state'),)", 'object_name': 'ResourcePerson'},
            'assigned_by': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.State']"}),
            'status': ('django.db.models.fields.BooleanField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.state': {
            'Meta': {'unique_together': "(('code', 'name'),)", 'object_name': 'State'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_map_area': ('django.db.models.fields.TextField', [], {}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '4', 'blank': 'True'}),
            'longtitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '4', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'resource_person'", 'symmetrical': 'False', 'through': u"orm['events.ResourcePerson']", 'to': u"orm['auth.User']"})
        },
        u'events.test': {
            'Meta': {'unique_together': "(('organiser', 'academic', 'foss', 'tdate', 'ttime'),)", 'object_name': 'Test'},
            'academic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AcademicCenter']"}),
            'appoved_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'test_approved_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['events.Department']", 'symmetrical': 'False'}),
            'foss': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['creation.FossCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invigilator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'test_invigilator'", 'null': 'True', 'to': u"orm['events.Invigilator']"}),
            'organiser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'test_organiser'", 'to': u"orm['events.Organiser']"}),
            'participant_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'tdate': ('django.db.models.fields.DateField', [], {}),
            'test_category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'test_category'", 'to': u"orm['events.TestCategory']"}),
            'test_code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'training': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Training']", 'null': 'True'}),
            'ttime': ('django.db.models.fields.TimeField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_exam_app': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'events.testattendance': {
            'Meta': {'object_name': 'TestAttendance'},
            'count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'examquestionpaper': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.QuestionPaper']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdlattempt_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'mdlcourse_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'mdlquiz_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'mdluser_firstname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'mdluser_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'mdluser_lastname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Test']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'events.testcategory': {
            'Meta': {'object_name': 'TestCategory'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'events.testimonials': {
            'Meta': {'object_name': 'Testimonials'},
            'actual_content': ('django.db.models.fields.TextField', [], {}),
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'testimonial_approved_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minified_content': ('django.db.models.fields.TextField', [], {}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'source_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'source_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'testimonial_created_by'", 'to': u"orm['auth.User']"}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'events.testlog': {
            'Meta': {'object_name': 'TestLog'},
            'academic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AcademicCenter']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Test']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.training': {
            'Meta': {'unique_together': "(('organiser', 'academic', 'foss', 'trdate', 'trtime'),)", 'object_name': 'Training'},
            'academic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AcademicCenter']"}),
            'appoved_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'training_approved_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Course']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['events.Department']", 'symmetrical': 'False'}),
            'extra_fields': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['events.TrainingExtraFields']", 'unique': 'True', 'null': 'True'}),
            'foss': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['creation.FossCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['creation.Language']"}),
            'organiser': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Organiser']"}),
            'participant_counts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'skype': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'training_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'training_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'trdate': ('django.db.models.fields.DateField', [], {}),
            'trtime': ('django.db.models.fields.TimeField', [], {}),
            'trusted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.trainingattendance': {
            'Meta': {'unique_together': "(('training', 'mdluser_id'),)", 'object_name': 'TrainingAttendance'},
            'count': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mdluser_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'training': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Training']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.trainingextrafields': {
            'Meta': {'object_name': 'TrainingExtraFields'},
            'approximate_hour': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'future_training': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_tutorial_useful': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'online_test': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'paper_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'recommend_to_others': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'events.trainingfeedback': {
            'Meta': {'unique_together': "(('training', 'mdluser_id'),)", 'object_name': 'TrainingFeedback'},
            'answered_questions': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'apply_information': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'appropriate_example': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'assignment': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'audio_quality': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'clarity': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'computers_lab': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'content': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'executed_workshop': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'faciliate_learning': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'if_apply_information_yes': ('django.db.models.fields.TextField', [], {}),
            'instruction_sheet': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'interested_helping': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'interesting': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'knowledge_about_software': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'mdluser_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'motivate_learners': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'other_comments': ('django.db.models.fields.TextField', [], {}),
            'other_weakness': ('django.db.models.fields.TextField', [], {}),
            'pace_of_tutorial': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'provide_clear_explanation': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'rate_workshop': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'reason_why': ('django.db.models.fields.TextField', [], {}),
            'recommend_workshop': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'sequence': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'setup_learning': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'time_management': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'training': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Training']"}),
            'tutorial_language': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'video_quality': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'weakness_narration': ('django.db.models.fields.BooleanField', [], {}),
            'weakness_understand': ('django.db.models.fields.BooleanField', [], {}),
            'weakness_workshop': ('django.db.models.fields.BooleanField', [], {}),
            'workshop_improved': ('django.db.models.fields.TextField', [], {}),
            'workshop_learnt': ('django.db.models.fields.TextField', [], {}),
            'workshop_orgainsation': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'events.traininglivefeedback': {
            'Meta': {'unique_together': "(('training', 'email'),)", 'object_name': 'TrainingLiveFeedback'},
            'answered_questions': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'apply_information': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'appropriate_example': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'assignment': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'audio_quality': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'clarity': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'computers_lab': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'content': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'executed_workshop': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'faciliate_learning': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'if_apply_information_yes': ('django.db.models.fields.TextField', [], {}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'instruction_sheet': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'interested_helping': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'interesting': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'knowledge_about_software': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'motivate_learners': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'other_comments': ('django.db.models.fields.TextField', [], {}),
            'other_weakness': ('django.db.models.fields.TextField', [], {}),
            'pace_of_tutorial': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'provide_clear_explanation': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'rate_workshop': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'reason_why': ('django.db.models.fields.TextField', [], {}),
            'recommend_workshop': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'sequence': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'setup_learning': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'time_management': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'training': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Training']"}),
            'tutorial_language': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'video_quality': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'weakness_narration': ('django.db.models.fields.BooleanField', [], {}),
            'weakness_understand': ('django.db.models.fields.BooleanField', [], {}),
            'weakness_workshop': ('django.db.models.fields.BooleanField', [], {}),
            'workshop_improved': ('django.db.models.fields.TextField', [], {}),
            'workshop_learnt': ('django.db.models.fields.TextField', [], {}),
            'workshop_orgainsation': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'events.traininglog': {
            'Meta': {'object_name': 'TrainingLog'},
            'academic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.AcademicCenter']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'training': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Training']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.university': {
            'Meta': {'unique_together': "(('name', 'state'),)", 'object_name': 'University'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.State']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'exam.question': {
            'Meta': {'object_name': 'Question'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'options': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'snippet': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'test': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '24'})
        },
        u'exam.questionpaper': {
            'Meta': {'object_name': 'QuestionPaper'},
            'fixed_questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['exam.Question']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quiz': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Quiz']"}),
            'random_questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['exam.QuestionSet']", 'symmetrical': 'False'}),
            'shuffle_questions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'total_marks': ('django.db.models.fields.FloatField', [], {})
        },
        u'exam.questionset': {
            'Meta': {'object_name': 'QuestionSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marks': ('django.db.models.fields.FloatField', [], {}),
            'num_questions': ('django.db.models.fields.IntegerField', [], {}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['exam.Question']", 'symmetrical': 'False'})
        },
        u'exam.quiz': {
            'Meta': {'object_name': 'Quiz'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'attempts_allowed': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'pass_criteria': ('django.db.models.fields.FloatField', [], {'default': '40'}),
            'prerequisite': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exam.Quiz']", 'null': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'time_between_attempts': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['events']