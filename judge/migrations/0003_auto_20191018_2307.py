# Generated by Django 2.1.13 on 2019-10-18 23:07

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0002_auto_20191014_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitepreferences',
            name='disable_registration',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='contestparticipation',
            name='frozen_format_data',
            field=jsonfield.fields.JSONField(blank=True, null=True, verbose_name='frozen contest format specific data'),
        ),
    ]
