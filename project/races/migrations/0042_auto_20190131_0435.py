# Generated by Django 2.1.1 on 2019-01-31 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0041_auto_20190131_0434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roster',
            name='picks',
            field=models.ManyToManyField(to='races.Participation'),
        ),
    ]
