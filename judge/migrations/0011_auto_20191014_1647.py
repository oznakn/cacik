# Generated by Django 2.1.13 on 2019-10-14 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0010_auto_20191014_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='disable_social_share',
            field=models.BooleanField(default=False, help_text='Disable social share buttons on contest page', verbose_name='disable social share buttons'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='use_clarifications',
            field=models.BooleanField(default=True, help_text='Use clarification system instead of comments.', verbose_name='use clarification system'),
        ),
    ]
