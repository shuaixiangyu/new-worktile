# Generated by Django 3.0.5 on 2020-04-30 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('worktile', '0006_auto_20200430_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=50, verbose_name='项目名称'),
        ),
        migrations.AlterField(
            model_name='sontask',
            name='manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sontask_manager', to='worktile.User', verbose_name='负责人'),
        ),
        migrations.AlterField(
            model_name='task',
            name='manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_manager', to='worktile.User', verbose_name='负责人'),
        ),
    ]
