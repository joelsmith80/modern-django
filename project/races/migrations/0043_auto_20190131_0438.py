# Generated by Django 2.1.1 on 2019-01-31 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0042_auto_20190131_0435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roster',
            name='picks',
            field=models.ManyToManyField(blank=True, to='races.Participation'),
        ),
    ]
