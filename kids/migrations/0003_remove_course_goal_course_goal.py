# Generated by Django 4.0.5 on 2022-12-02 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kids', '0002_aspect_kid_evaluation_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='goal',
        ),
        migrations.AddField(
            model_name='course',
            name='goal',
            field=models.ManyToManyField(blank=True, related_name='target', to='kids.aspect'),
        ),
    ]
