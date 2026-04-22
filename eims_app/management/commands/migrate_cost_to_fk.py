"""
造价咨询模块数据迁移脚本
将现有数据从字符串关联迁移到外键关联结构
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from eims_app.models import (
    CostProjectInfo,
    CostTaskPlan,
    CostTaskImplementation,
    CostReviewResult,
    CostPaymentStatus,
    CostProjectArchive,
    CostRemunerationDistribution
)


class Command(BaseCommand):
    help = '迁移造价咨询数据到外键关联结构'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要执行的操作，不实际修改数据',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  干运行模式 - 不会实际修改数据'))
        
        try:
            # 1. 统计现有数据
            self.stdout.write('\n📊 数据统计:')
            project_count = CostProjectInfo.objects.count()
            task_plan_count = CostTaskPlan.objects.count()
            task_impl_count = CostTaskImplementation.objects.count()
            review_count = CostReviewResult.objects.count()
            payment_count = CostPaymentStatus.objects.count()
            archive_count = CostProjectArchive.objects.count()
            remun_count = CostRemunerationDistribution.objects.count()
            
            self.stdout.write(f'  - 项目信息: {project_count} 条')
            self.stdout.write(f'  - 任务计划: {task_plan_count} 条')
            self.stdout.write(f'  - 任务实施: {task_impl_count} 条')
            self.stdout.write(f'  - 评审结果: {review_count} 条')
            self.stdout.write(f'  - 支付状态: {payment_count} 条')
            self.stdout.write(f'  - 项目归档: {archive_count} 条')
            self.stdout.write(f'  - 酬劳分配: {remun_count} 条')
            
            # 2. 构建项目编码映射
            self.stdout.write('\n🔍 构建项目映射...')
            project_map = {}
            for project in CostProjectInfo.objects.all():
                project_map[project.project_code] = project
            
            self.stdout.write(f'  ✓ 已加载 {len(project_map)} 个项目')
            
            # 3. 迁移各子模块数据
            migration_stats = {}
            
            # 3.1 迁移 CostTaskPlan
            self.stdout.write('\n🔄 迁移任务计划...')
            migrated = 0
            skipped = 0
            errors = 0
            
            for record in CostTaskPlan.objects.all():
                if not record.project and record.project_code:
                    if record.project_code in project_map:
                        if not dry_run:
                            record.project = project_map[record.project_code]
                            record.save(update_fields=['project'])
                        migrated += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠️  跳过: 项目编号 {record.project_code} 不存在于项目表中'
                            )
                        )
                        skipped += 1
                elif record.project:
                    skipped += 1  # 已有外键关联
                else:
                    errors += 1
            
            migration_stats['CostTaskPlan'] = {
                'migrated': migrated,
                'skipped': skipped,
                'errors': errors
            }
            self.stdout.write(
                f'  ✓ 迁移: {migrated}, 跳过: {skipped}, 错误: {errors}'
            )
            
            # 3.2 迁移 CostTaskImplementation
            self.stdout.write('\n🔄 迁移任务实施...')
            migrated = skipped = errors = 0
            
            for record in CostTaskImplementation.objects.all():
                if not record.project and record.project_code:
                    if record.project_code in project_map:
                        if not dry_run:
                            record.project = project_map[record.project_code]
                            record.save(update_fields=['project'])
                        migrated += 1
                    else:
                        skipped += 1
                elif record.project:
                    skipped += 1
                else:
                    errors += 1
            
            migration_stats['CostTaskImplementation'] = {
                'migrated': migrated,
                'skipped': skipped,
                'errors': errors
            }
            self.stdout.write(
                f'  ✓ 迁移: {migrated}, 跳过: {skipped}, 错误: {errors}'
            )
            
            # 3.3 迁移 CostReviewResult
            self.stdout.write('\n🔄 迁移评审结果...')
            migrated = skipped = errors = 0
            
            for record in CostReviewResult.objects.all():
                if not record.project and record.project_code:
                    if record.project_code in project_map:
                        if not dry_run:
                            record.project = project_map[record.project_code]
                            record.save(update_fields=['project'])
                        migrated += 1
                    else:
                        skipped += 1
                elif record.project:
                    skipped += 1
                else:
                    errors += 1
            
            migration_stats['CostReviewResult'] = {
                'migrated': migrated,
                'skipped': skipped,
                'errors': errors
            }
            self.stdout.write(
                f'  ✓ 迁移: {migrated}, 跳过: {skipped}, 错误: {errors}'
            )
            
            # 3.4 迁移 CostPaymentStatus
            self.stdout.write('\n🔄 迁移支付状态...')
            migrated = skipped = errors = 0
            
            for record in CostPaymentStatus.objects.all():
                if not record.project and record.project_code:
                    if record.project_code in project_map:
                        if not dry_run:
                            record.project = project_map[record.project_code]
                            record.save(update_fields=['project'])
                        migrated += 1
                    else:
                        skipped += 1
                elif record.project:
                    skipped += 1
                else:
                    errors += 1
            
            migration_stats['CostPaymentStatus'] = {
                'migrated': migrated,
                'skipped': skipped,
                'errors': errors
            }
            self.stdout.write(
                f'  ✓ 迁移: {migrated}, 跳过: {skipped}, 错误: {errors}'
            )
            
            # 3.5 迁移 CostProjectArchive
            self.stdout.write('\n🔄 迁移项目归档...')
            migrated = skipped = errors = 0
            
            for record in CostProjectArchive.objects.all():
                if not record.project and record.project_code:
                    if record.project_code in project_map:
                        if not dry_run:
                            record.project = project_map[record.project_code]
                            record.save(update_fields=['project'])
                        migrated += 1
                    else:
                        skipped += 1
                elif record.project:
                    skipped += 1
                else:
                    errors += 1
            
            migration_stats['CostProjectArchive'] = {
                'migrated': migrated,
                'skipped': skipped,
                'errors': errors
            }
            self.stdout.write(
                f'  ✓ 迁移: {migrated}, 跳过: {skipped}, 错误: {errors}'
            )
            
            # 3.6 迁移 CostRemunerationDistribution
            self.stdout.write('\n🔄 迁移酬劳分配...')
            migrated = skipped = errors = 0
            
            for record in CostRemunerationDistribution.objects.all():
                if not record.project and record.project_code:
                    if record.project_code in project_map:
                        if not dry_run:
                            record.project = project_map[record.project_code]
                            record.save(update_fields=['project'])
                        migrated += 1
                    else:
                        skipped += 1
                elif record.project:
                    skipped += 1
                else:
                    errors += 1
            
            migration_stats['CostRemunerationDistribution'] = {
                'migrated': migrated,
                'skipped': skipped,
                'errors': errors
            }
            self.stdout.write(
                f'  ✓ 迁移: {migrated}, 跳过: {skipped}, 错误: {errors}'
            )
            
            # 4. 输出总结
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('✅ 数据迁移完成！'))
            self.stdout.write('='*60)
            
            total_migrated = sum(stats['migrated'] for stats in migration_stats.values())
            total_skipped = sum(stats['skipped'] for stats in migration_stats.values())
            total_errors = sum(stats['errors'] for stats in migration_stats.values())
            
            self.stdout.write(f'\n总计:')
            self.stdout.write(f'  - 成功迁移: {total_migrated} 条记录')
            self.stdout.write(f'  - 跳过（已有外键或无项目编码）: {total_skipped} 条记录')
            self.stdout.write(f'  - 错误（项目不存在）: {total_errors} 条记录')
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️  这是干运行，未实际修改数据。'
                        '如需执行迁移，请移除 --dry-run 参数重新运行。'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✨ 所有数据已成功迁移到外键关联结构！'
                    )
                )
                
                if total_errors > 0:
                    self.stdout.write(
                        self.style.ERROR(
                            f'\n⚠️  警告: 有 {total_errors} 条记录因项目不存在而未能迁移。'
                            '请检查这些记录的项目编码是否正确。'
                        )
                    )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ 迁移失败: {str(e)}')
            )
            raise CommandError(f'数据迁移失败: {e}')
