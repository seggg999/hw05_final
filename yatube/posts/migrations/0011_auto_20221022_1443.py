# Generated by Django 2.2.16 on 2022-10-22 11:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20221022_1345'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_booking',
        ),
    ]
