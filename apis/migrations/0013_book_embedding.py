# Generated by Django 3.2 on 2024-08-15 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0012_remove_book_embedding'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='embedding',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
