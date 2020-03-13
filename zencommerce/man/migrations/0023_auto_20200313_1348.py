# Generated by Django 2.2.10 on 2020-03-13 13:48

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('man', '0022_auto_20200313_1155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='etsylisting',
            name='can_write_inventory',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='category_id',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='category_path',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='category_path_ids',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='featured_rank',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='item_dimensions_unit',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='item_height',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='item_length',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='item_weight',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='item_weight_unit',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='item_width',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='shop_section_id',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='state_tsz',
        ),
        migrations.RemoveField(
            model_name='etsylisting',
            name='suggested_taxonomy_id',
        ),
        migrations.AddField(
            model_name='etsylisting',
            name='listing_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='etsyreceipt',
            name='receipt_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='etsytransaction',
            name='transaction_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=''),
        ),
    ]
