# Generated by Django 4.0.4 on 2022-06-20 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carcontrollerserver', '0004_alter_game_game_name_alter_game_game_tag_appuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_name',
            field=models.CharField(max_length=30),
        ),
    ]