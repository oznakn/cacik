# Generated by Django 2.2.6 on 2019-10-28 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0002_auto_20191020_1628'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contest',
            options={'permissions': (('see_private_contest', 'See private contests'), ('edit_own_contest', 'Edit own contests'), ('edit_all_contest', 'Edit all contests'), ('clone_contest', 'Clone contest'), ('contest_rating', 'Rate contests'), ('contest_access_code', 'Contest access codes'), ('create_private_contest', 'Create private contests'), ('share_contest_message', 'Share contest wide message')), 'verbose_name': 'contest', 'verbose_name_plural': 'contests'},
        ),
        migrations.AddField(
            model_name='sitepreferences',
            name='disable_organizations',
            field=models.BooleanField(default=False),
        ),
    ]