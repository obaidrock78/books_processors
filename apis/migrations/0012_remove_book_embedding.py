# Generated by Django 3.2 on 2024-08-15 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0011_alter_book_embedding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='embedding',
        ),
    ]
