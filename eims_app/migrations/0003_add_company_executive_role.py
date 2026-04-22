# Manual migration to add CompanyExecutiveRole model and executive fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eims_app', '0002_migrate_approval_chain_role_fields'),
    ]

    operations = [
        # Step 1: Create CompanyExecutiveRole table
        migrations.CreateModel(
            name='CompanyExecutiveRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='是否删除')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('executive_type', models.CharField(
                    choices=[
                        ('chairman', '董事长'),
                        ('general_manager', '总经理'),
                        ('deputy_general_manager', '副总经理'),
                        ('production_vp', '生产副总'),
                        ('business_vp', '经营副总'),
                        ('quality_vp', '质量副总'),
                        ('safety_vp', '安全副总'),
                        ('chief_engineer', '总工程师'),
                        ('chief_economist', '总经济师'),
                        ('cfo', '财务总监'),
                        ('hr_director', '人力资源总监'),
                        ('other', '其他高管'),
                    ],
                    max_length=30,
                    verbose_name='高管类型'
                )),
                ('role_name', models.CharField(help_text='如:董事长、总经理等', max_length=50, verbose_name='角色名称')),
                ('is_primary', models.BooleanField(default=True, help_text='同一类型只能有一个主要负责人', verbose_name='是否主要负责人')),
                ('description', models.TextField(blank=True, help_text='该职位的主要职责和权限', verbose_name='职责描述')),
                ('approval_authority', models.TextField(blank=True, help_text='可审批的业务类型和金额范围', verbose_name='审批权限')),
                ('order', models.IntegerField(default=0, help_text='数字越小优先级越高', verbose_name='排序顺序')),
                ('user', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='executive_roles', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '公司高管角色',
                'verbose_name_plural': '公司高管角色配置',
                'ordering': ['order', 'executive_type'],
            },
        ),
        
        # Step 2: Add indexes and unique constraint for CompanyExecutiveRole
        migrations.AddIndex(
            model_name='companyexecutiverole',
            index=models.Index(fields=['executive_type'], name='eims_app_co_executi_1d3482_idx'),
        ),
        migrations.AddIndex(
            model_name='companyexecutiverole',
            index=models.Index(fields=['is_primary'], name='eims_app_co_is_prim_86b0f6_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='companyexecutiverole',
            unique_together={('user', 'executive_type')},
        ),
        
        # Step 3: Update DepartmentRole role_type choices (just metadata update)
        migrations.AlterField(
            model_name='departmentrole',
            name='role_type',
            field=models.CharField(
                choices=[
                    ('manager', '部门经理'),
                    ('deputy', '部门副职'),
                    ('supervisor', '主管'),
                    ('member', '普通成员'),
                    ('assistant', '助理'),
                    ('specialist', '专员'),
                    ('consultant', '顾问'),
                    ('intern', '实习生')
                ],
                max_length=20,
                verbose_name='角色类型'
            ),
        ),
        
        # Step 4: Add approver_type fields if they don't exist (using RunSQL with error handling)
        migrations.RunSQL(
            sql=[
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_approver_type VARCHAR(20) NOT NULL DEFAULT 'department_role';",
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_approver_type VARCHAR(20) NOT NULL DEFAULT 'department_role';",
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_approver_type VARCHAR(20) NOT NULL DEFAULT 'department_role';",
            ],
            reverse_sql=[
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_1_approver_type;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_2_approver_type;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_3_approver_type;",
            ],
            state_operations=[
                migrations.AddField(
                    model_name='approvalchain',
                    name='level_1_approver_type',
                    field=models.CharField(choices=[('department_role', '部门角色'), ('executive_role', '公司高管')], default='department_role', max_length=20, verbose_name='一级审批人类型'),
                ),
                migrations.AddField(
                    model_name='approvalchain',
                    name='level_2_approver_type',
                    field=models.CharField(choices=[('department_role', '部门角色'), ('executive_role', '公司高管')], default='department_role', max_length=20, verbose_name='二级审批人类型'),
                ),
                migrations.AddField(
                    model_name='approvalchain',
                    name='level_3_approver_type',
                    field=models.CharField(choices=[('department_role', '部门角色'), ('executive_role', '公司高管')], default='department_role', max_length=20, verbose_name='三级审批人类型'),
                ),
            ],
        ),
        
        # Step 5: Add executive foreign key columns
        migrations.RunSQL(
            sql=[
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_1_executive_id INT NULL;",
                "ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level1_executive FOREIGN KEY (level_1_executive_id) REFERENCES eims_app_companyexecutiverole(id);",
                
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_2_executive_id INT NULL;",
                "ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level2_executive FOREIGN KEY (level_2_executive_id) REFERENCES eims_app_companyexecutiverole(id);",
                
                "ALTER TABLE eims_app_approvalchain ADD COLUMN level_3_executive_id INT NULL;",
                "ALTER TABLE eims_app_approvalchain ADD CONSTRAINT fk_level3_executive FOREIGN KEY (level_3_executive_id) REFERENCES eims_app_companyexecutiverole(id);",
            ],
            reverse_sql=[
                "ALTER TABLE eims_app_approvalchain DROP FOREIGN KEY fk_level1_executive;",
                "ALTER TABLE eims_app_approvalchain DROP FOREIGN KEY fk_level2_executive;",
                "ALTER TABLE eims_app_approvalchain DROP FOREIGN KEY fk_level3_executive;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_1_executive_id;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_2_executive_id;",
                "ALTER TABLE eims_app_approvalchain DROP COLUMN level_3_executive_id;",
            ],
            state_operations=[
                migrations.AddField(
                    model_name='approvalchain',
                    name='level_1_executive',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='level_1_chains', to='eims_app.companyexecutiverole', verbose_name='一级审批人(高管)'),
                ),
                migrations.AddField(
                    model_name='approvalchain',
                    name='level_2_executive',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='level_2_chains', to='eims_app.companyexecutiverole', verbose_name='二级审批人(高管)'),
                ),
                migrations.AddField(
                    model_name='approvalchain',
                    name='level_3_executive',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='level_3_chains', to='eims_app.companyexecutiverole', verbose_name='三级审批人(高管)'),
                ),
            ],
        ),
        
        # Step 6: Make level_1_department nullable
        migrations.RunSQL(
            sql=[
                "ALTER TABLE eims_app_approvalchain MODIFY COLUMN level_1_department_id BIGINT NULL;",
            ],
            reverse_sql=[
                "ALTER TABLE eims_app_approvalchain MODIFY COLUMN level_1_department_id BIGINT NOT NULL;",
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='approvalchain',
                    name='level_1_department',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='level_1_approvals', to='eims_app.department', verbose_name='一级审批部门'),
                ),
            ],
        ),
    ]
