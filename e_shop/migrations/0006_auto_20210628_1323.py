# Generated by Django 3.1.2 on 2021-06-28 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('e_shop', '0005_auto_20210628_1320'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='id_user',
            new_name='user',
        ),
    ]
