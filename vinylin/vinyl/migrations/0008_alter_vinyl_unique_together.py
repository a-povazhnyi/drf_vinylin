# Generated by Django 3.2.13 on 2022-05-19 11:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinyl', '0007_auto_20220519_0820'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vinyl',
            unique_together={('vinyl_title', 'artist')},
        ),
    ]
