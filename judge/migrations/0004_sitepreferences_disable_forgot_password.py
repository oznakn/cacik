# Generated by Django 2.1.13 on 2019-10-18 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0003_auto_20191018_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitepreferences',
            name='disable_forgot_password',
            field=models.BooleanField(default=False),
        ),
    ]
