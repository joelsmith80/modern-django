# Generated by Django 2.1.1 on 2018-09-30 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0002_rider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rider',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]