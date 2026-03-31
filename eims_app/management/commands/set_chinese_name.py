from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from eims_app.models.model_user import UserProfile

class Command(BaseCommand):
    help = '批量设置用户的中文姓名'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='CSV 文件路径，格式：用户名，中文姓名（例：zhangsan，张三）'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='单个用户名'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='对应的中文姓名'
        )

    def handle(self, *args, **options):
        # 方式 1: 从 CSV 文件批量导入
        if options['file']:
            self.import_from_csv(options['file'])
        
        # 方式 2: 设置单个用户
        elif options['username'] and options['name']:
            self.set_single_user(options['username'], options['name'])
        
        else:
            self.stdout.write(self.style.ERROR('请提供 --file 参数或同时提供 --username 和 --name 参数'))
            self.stdout.write(self.style.WARNING('\n使用示例:'))
            self.stdout.write('  # 批量导入:')
            self.stdout.write('  python manage.py set_chinese_name --file names.csv')
            self.stdout.write('\n  # 设置单个用户:')
            self.stdout.write('  python manage.py set_chinese_name --username zhangsan --name "张三"')

    def set_single_user(self, username, chinese_name):
        """设置单个用户的中文姓名"""
        try:
            user = User.objects.get(username=username)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.real_name = chinese_name
            profile.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ 已为用户 "{username}" 设置中文姓名：{chinese_name}')
            )
        except User.DoesNotExist:
            raise CommandError(f'用户 "{username}" 不存在')

    def import_from_csv(self, file_path):
        """从 CSV 文件批量导入"""
        import csv
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                
                success_count = 0
                error_count = 0
                
                for row in reader:
                    if len(row) < 2:
                        continue
                    
                    username = row[0].strip()
                    chinese_name = row[1].strip()
                    
                    if not username or not chinese_name:
                        continue
                    
                    try:
                        user = User.objects.get(username=username)
                        profile, created = UserProfile.objects.get_or_create(user=user)
                        profile.real_name = chinese_name
                        profile.save()
                        success_count += 1
                        
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ 创建并设置：{username} -> {chinese_name}')
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ 更新：{username} -> {chinese_name}')
                            )
                    except User.DoesNotExist:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ 用户不存在：{username}')
                        )
                
                self.stdout.write('\n' + '=' * 50)
                self.stdout.write(self.style.SUCCESS(f'完成！成功：{success_count} 条，失败：{error_count} 条'))
                
        except FileNotFoundError:
            raise CommandError(f'文件不存在：{file_path}')
        except Exception as e:
            raise CommandError(f'导入失败：{str(e)}')
