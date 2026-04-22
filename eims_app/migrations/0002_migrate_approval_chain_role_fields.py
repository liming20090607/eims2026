# Generated migration script to convert CharField to ForeignKey for approval chain roles
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eims_app', '0001_initial_clean'),
    ]

    operations = [
        # 使用原生 SQL 修改列类型
        migrations.RunSQL(
            sql=[
                # 先将旧列重命名
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_1_role level_1_role_old VARCHAR(50) NULL;",
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_2_role level_2_role_old VARCHAR(50) NULL;",
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_3_role level_3_role_old VARCHAR(50) NULL;",
                
                # 添加新的外键列
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_role_new INT NULL;",
                "ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level1_role FOREIGN KEY (level_1_role_new) REFERENCES eims_app_departmentrole(id);",
                
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_role_new INT NULL;",
                "ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level2_role FOREIGN KEY (level_2_role_new) REFERENCES eims_app_departmentrole(id);",
                
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_role_new INT NULL;",
                "ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level3_role FOREIGN KEY (level_3_role_new) REFERENCES eims_app_departmentrole(id);",
                
                # 删除旧列
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_1_role_old;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_2_role_old;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_3_role_old;",
                
                # 重命名新列为正式名称
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_1_role_new level_1_role INT NULL;",
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_2_role_new level_2_role INT NULL;",
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_3_role_new level_3_role INT NULL;",
            ],
            reverse_sql=[
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_role_old VARCHAR(50) NULL;",
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_role_old VARCHAR(50) NULL;",
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_role_old VARCHAR(50) NULL;",
                "ALTER TABLE eims_app_approvalchain DROP FOREIGN KEY fk_level1_role;",
                "ALTER TABLE eims_app_approvalchain DROP FOREIGN KEY fk_level2_role;",
                "ALTER TABLE eims_app_approvalchain DROP FOREIGN KEY fk_level3_role;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_1_role;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_2_role;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_3_role;",
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_1_role_old level_1_role VARCHAR(50) NULL;",
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_2_role_old level_2_role VARCHAR(50) NULL;",
                "ALTER TABLE eims_app_approvalchain CHANGE COLUMN level_3_role_old level_3_role VARCHAR(50) NULL;",
            ],
        ),
    ]
