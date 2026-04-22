from django.core.management.base import BaseCommand
from eims_app.models import Employee


class Command(BaseCommand):
    help = '清除数据库中所有员工花名册数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='确认删除操作（必须提供此参数）',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                '\n警告：此操作将删除所有员工花名册数据！'
            ))
            self.stdout.write(self.style.WARNING(
                '请使用 --confirm 参数来确认删除操作。'
            ))
            self.stdout.write(self.style.WARNING(
                '例如：python manage.py clear_employees --confirm\n'
            ))
            return

        # 获取员工总数
        total_count = Employee.objects.count()
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('数据库中没有员工数据，无需删除。'))
            return

        # 显示统计信息
        self.stdout.write(self.style.WARNING(f'\n即将删除 {total_count} 条员工数据...'))
        
        # 执行删除
        deleted_count, _ = Employee.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ 成功删除 {deleted_count} 条员工数据！'
        ))
