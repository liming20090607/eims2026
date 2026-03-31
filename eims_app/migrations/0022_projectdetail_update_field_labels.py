# Generated manually to update field verbose_name labels

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eims_app', '0021_dynamicchoice'),
    ]

    operations = [
        # Update verbose_name for cumulative_payment
        migrations.AlterField(
            model_name='projectdetail',
            name='cumulative_payment',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=15,
                verbose_name='累计回款 (元)'
            ),
        ),
        # Update verbose_name for contract_balance
        migrations.AlterField(
            model_name='projectdetail',
            name='contract_balance',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=15,
                verbose_name='合同余额 (元)'
            ),
        ),
        # Update verbose_name for service_start_date
        migrations.AlterField(
            model_name='projectdetail',
            name='service_start_date',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='服务开始日期'
            ),
        ),
    ]
