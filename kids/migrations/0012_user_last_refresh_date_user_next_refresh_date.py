# Generated by Django 4.0.5 on 2022-12-28 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kids', '0011_time_to_spend'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_refresh_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='next_refresh_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
