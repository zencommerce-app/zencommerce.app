# Generated by Django 2.2.6 on 2019-11-12 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('man', '0020_auto_20191110_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etsylisting',
            name='when_made',
            field=models.CharField(blank=True, choices=[('made_to_order', 'Made To Order'), ('2010_2019', '2010 - 2019'), ('2000_2009', '2000 - 2009'), ('before_2000', 'Before 2000'), ('1990s', '1990s'), ('1980s', '1980s'), ('1970s', '1970s'), ('1960s', '1960s'), ('1950s', '1950s'), ('1940s', '1940s'), ('1930s', '1930s'), ('1920s', '1920s'), ('1910s', '1910s'), ('1900s', '1900 - 1909'), ('1800s', '1800s'), ('1700s', '1700s'), ('before_1700', 'Before 1700')], max_length=200),
        ),
        migrations.AlterField(
            model_name='etsylisting',
            name='who_made',
            field=models.CharField(blank=True, choices=[('i_did', 'I did'), ('collective', 'A member of my shop'), ('someone_else', 'Another company or person')], max_length=200),
        ),
    ]
