# Generated by Django 2.0.7 on 2018-07-13 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('magnet_v030', '0007_remove_gene_ensembl'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.RenameField(
            model_name='gene',
            old_name='gene_name',
            new_name='gene_symbol',
        ),
        migrations.AddField(
            model_name='alias',
            name='gene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magnet_v030.Gene'),
        ),
    ]
