# Generated by Django 4.0.4 on 2022-06-16 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carcontrollerserver', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_name',
            field=models.CharField(default='', max_length=30),
        ),
    ]