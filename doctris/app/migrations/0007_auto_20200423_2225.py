# Generated by Django 3.0.5 on 2020-04-23 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20200423_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
