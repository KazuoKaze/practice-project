# Generated by Django 5.0.9 on 2024-09-16 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('subsrciptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptions',
            name='permisssions',
            field=models.ManyToManyField(limit_choices_to={'codebnname__in': ['advanced', 'pro', 'basic'], 'content_type__app_label': 'subscriptions'}, to='auth.permission'),
        ),
    ]
