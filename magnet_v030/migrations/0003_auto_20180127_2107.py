# Generated by Django 2.0.1 on 2018-01-28 03:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('magnet_v030', '0002_auto_20180127_2059'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cluster',
            options={'ordering': ['cluster_number']},
        ),
    ]
