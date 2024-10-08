# Generated by Django 3.2 on 2024-08-15 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0004_auto_20240815_0326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='gender',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='id',
            field=models.CharField(max_length=500, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='book',
            name='id',
            field=models.CharField(max_length=500, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(max_length=130, unique=True),
        ),
    ]
