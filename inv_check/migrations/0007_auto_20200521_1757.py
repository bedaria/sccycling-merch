# Generated by Django 3.0.6 on 2020-05-22 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv_check', '0006_auto_20200521_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='date of order'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='date',
            field=models.DateField(auto_now_add=True, verbose_name='date of sale'),
        ),
    ]
