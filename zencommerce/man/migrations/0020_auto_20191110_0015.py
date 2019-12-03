# Generated by Django 2.2.6 on 2019-11-10 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('man', '0019_etsytransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etsytransaction',
            name='paid_tsz',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='etsytransaction',
            name='shipped_tsz',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]