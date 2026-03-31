# Migration to add keywords and upload_person fields to Notice model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eims_app', '0026_smsverificationrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='keywords',
            field=models.CharField(blank=True, help_text='必填：用逗号或空格分隔的关键字', max_length=200, null=True, verbose_name='关键字'),
        ),
        migrations.AddField(
            model_name='notice',
            name='upload_person',
            field=models.CharField(blank=True, help_text='文件上传人员', max_length=50, null=True, verbose_name='上传人'),
        ),
        migrations.AlterField(
            model_name='notice',
            name='notice_title',
            field=models.CharField(help_text='必填：通知的标题', max_length=200, verbose_name='公告标题'),
        ),
    ]
