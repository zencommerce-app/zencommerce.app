# Generated by Django 2.2.6 on 2019-11-09 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('man', '0007_auto_20191109_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etsylisting',
            name='recipient',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
