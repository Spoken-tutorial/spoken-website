# -*- coding: utf-8 -*-
# Generated for AcademicDocument and salutation
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0058_auto_20260818_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicpaymentstatus',
            name='salutation',
            field=models.CharField(blank=True, choices=[('Principal', 'The Principal'), ('Vice Chancellor', 'The Vice Chancellor'), ('Director', 'The Director'), ('Headmaster', 'The Headmaster')], default='Principal', max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='AcademicDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type', models.CharField(choices=[('REC', 'Payment Receipt'), ('LOA', 'Letter of Association'), ('LOC', 'Annual Report (Certificate of Training)'), ('APP', 'Letter of Appreciation')], max_length=10)),
                ('reference_no', models.CharField(max_length=100, unique=True)),
                ('salutation', models.CharField(blank=True, max_length=50, null=True)),
                ('recipient_name', models.CharField(blank=True, max_length=255, null=True)),
                ('issued_date', models.DateField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('academic', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='academic_documents', to='events.AcademicCenter')),
                ('organiser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appreciation_documents', to='events.Organiser')),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='documents', to='events.AcademicPaymentStatus')),
            ],
            options={
                'verbose_name': 'Academic Document',
                'verbose_name_plural': 'Academic Documents',
            },
        ),
    ]
