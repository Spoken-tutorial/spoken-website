# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_auto_20170619_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='InductionInterest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('phonemob', models.CharField(max_length=20)),
                ('age', models.CharField(max_length=20, choices=[(b'', b'-----'), (b'below25', b'below 25'), (b'25to34', b'25 to 34'), (b'35to44', b'35 to 44'), (b'45to54', b'45 to 54'), (b'55to64', b'55 to 64'), (b'65andabove', b'65 and above')])),
                ('gender', models.CharField(max_length=10, choices=[(b'', b'-----'), (b'Male', b'Male'), (b'Female', b'Female')])),
                ('mother_tongue', models.CharField(max_length=100)),
                ('medium_of_studies', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'English', b'English'), (b'Other', b'Other')])),
                ('other_medium', models.CharField(max_length=100)),
                ('education', models.CharField(max_length=100, choices=[(b'', b'-----'), (b'3yeargraduatedegree(BABScB.Cometc)', b'3 year graduate degree (BA, BSc, B.Com, etc.)'), (b'Professionaldegree(BEBTechetc)', b'Professional degree (BE, B.Tech, etc.)'), (b'2yearMasters(MAMScMCometc)', b'2 year Masters (MA, MSc, MCom, etc.)'), (b'2yearprofessionalMasters(MEMTechMBAMPhiletc)', b'2 year professional Masters (ME, MTech, MBA, MPhil, etc.)'), (b'PhD', b'PhD'), (b'Other', b'Other')])),
                ('other_education', models.CharField(max_length=100)),
                ('specialisation', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Arts', b'Arts'), (b'Science', b'Science'), (b'Commerce', b'Commerce'), (b'EngineeringorComputerScience ', b'Engineering or Computer Science'), (b'Management', b'Management'), (b'Other', b'Other')])),
                ('other_specialisation', models.CharField(max_length=100)),
                ('designation', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Lecturer', b'Lecturer'), (b'AssistantProfessor', b'Assistant Professor'), (b'AssociateProfessor', b'Associate Professor'), (b'Professor', b'Professor'), (b'Other', b'Other')])),
                ('other_designation', models.CharField(max_length=100)),
                ('college', models.CharField(max_length=100)),
                ('college_address', models.CharField(max_length=500)),
                ('pincode', models.PositiveIntegerField()),
                ('experience_in_college', models.CharField(max_length=20, choices=[(b'', b'-----'), (b'Lessthan1year', b'Less than 1 year'), (b'Morethan1yearbutlessthan2years', b'More than 1 year, but less than 2 years'), (b'Morethan2yearsbutlessthan5years', b'More than 2 years but less than 5 years'), (b'Morethan5years', b'More than 5 years')])),
                ('bring_laptop', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('borrow_laptop', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('do_agree', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('no_objection', models.CharField(max_length=50, choices=[(b'', b'-----'), (b'Yes', b'Yes'), (b'No', b'No')])),
                ('other_comments', models.CharField(max_length=500)),
                ('city', models.ForeignKey(to='events.City', on_delete=models.deletion.PROTECT)),
                ('state', models.ForeignKey(to='events.State', on_delete=models.deletion.PROTECT)),
            ],
        ),
    ]
