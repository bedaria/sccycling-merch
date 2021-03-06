# Generated by Django 3.0.6 on 2020-05-20 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv_check', '0003_auto_20200519_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='count',
        ),
        migrations.AddField(
            model_name='sale',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='sale',
            name='ship',
            field=models.BooleanField(default=False, verbose_name='Does price include shipping?'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Receipt amount'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='size',
            field=models.CharField(choices=[('XXS', 'Xxs'), ('XS', 'Xs'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'Xl'), ('XXL', 'Xxl'), ('XXXL', 'Xxxl'), ('count', 'Cout')], max_length=5, verbose_name='Sold item size (if no size, select count'),
        ),
    ]
