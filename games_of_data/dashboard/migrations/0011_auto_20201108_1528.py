# Generated by Django 3.1.1 on 2020-11-08 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20201108_1421'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='id',
        ),
        migrations.AlterField(
            model_name='file',
            name='azur_file_name',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]