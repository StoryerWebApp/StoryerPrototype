# Generated by Django 4.1.1 on 2022-10-25 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storyer', '0012_assignment_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='group',
        ),
    ]
