# Generated by Django 3.1.2 on 2021-06-28 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_shop', '0006_auto_20210628_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
