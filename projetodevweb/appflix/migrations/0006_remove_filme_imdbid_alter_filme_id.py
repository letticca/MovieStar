# Generated by Django 5.1.2 on 2024-10-18 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appflix', '0005_filme_poster'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filme',
            name='imdbID',
        ),
        migrations.AlterField(
            model_name='filme',
            name='id',
            field=models.CharField(max_length=15, primary_key=True, serialize=False, unique=True),
        ),
    ]
