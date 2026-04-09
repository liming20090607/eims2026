from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from eims_app.models import Tenant, UserProfile


class Command(BaseCommand):
    help = '初始化多租户数据：创建三家公司并分配现有用户到默认公司'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要执行的操作，不实际修改数据'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('多租户数据初始化'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')
        
        # 1. 创建三家公司
        companies = [
            {
                'code': 'COMPANY_A',
                'name': '甲公司',
                'short_name': '甲',
                'contact_person': '甲公司联系人',
                'contact_phone': '',
                'contact_email': '',
                'address': '',
                'is_active': True,
                'remark': '默认租户公司'
            },
            {
                'code': 'COMPANY_B',
                'name': '乙公司',
                'short_name': '乙',
                'contact_person': '',
                'contact_phone': '',
                'contact_email': '',
                'address': '',
                'is_active': True,
                'remark': ''
            },
            {
                'code': 'COMPANY_C',
                'name': '丙公司',
                'short_name': '丙',
                'contact_person': '',
                'contact_phone': '',
                'contact_email': '',
                'address': '',
                'is_active': True,
                'remark': ''
            },
        ]
        
        self.stdout.write('步骤 1: 创建租户公司...')
        tenant_company_a = None
        
        for company in companies:
            if dry_run:
                self.stdout.write(f'  [DRY RUN] 将创建公司: {company["name"]} ({company["code"]})')
            else:
                tenant, created = Tenant.objects.get_or_create(
                    code=company['code'],
                    defaults=company
                )
                if created:
                    self.stdout.write(f'  ✅ 创建公司: {tenant.name} ({tenant.code})')
                else:
                    self.stdout.write(f'  ⏭️  公司已存在: {tenant.name} ({tenant.code})')
                
                # 保存第一个公司（甲公司）作为默认租户
                if company['code'] == 'COMPANY_A':
                    tenant_company_a = tenant
        
        self.stdout.write('')
        
        # 2. 统计现有用户
        User = get_user_model()
        total_users = User.objects.count()
        users_without_tenant = UserProfile.objects.filter(tenant__isnull=True).count()
        
        self.stdout.write(f'步骤 2: 统计用户数据...')
        self.stdout.write(f'  总用户数: {total_users}')
        self.stdout.write(f'  未分配租户的用户: {users_without_tenant}')
        self.stdout.write('')
        
        if not tenant_company_a:
            self.stdout.write(self.style.ERROR('❌ 错误: 找不到默认租户公司（甲公司）'))
            return
        
        # 3. 为所有未分配租户的用户分配默认租户
        if users_without_tenant > 0:
            self.stdout.write(f'步骤 3: 为未分配的用户分配默认租户（{tenant_company_a.name}）...')
            
            if dry_run:
                self.stdout.write(f'  [DRY RUN] 将为 {users_without_tenant} 个用户分配租户')
            else:
                # 更新所有 tenant 为 null 的 UserProfile
                updated_count = UserProfile.objects.filter(
                    tenant__isnull=True
                ).update(tenant=tenant_company_a)
                
                self.stdout.write(f'  ✅ 已为 {updated_count} 个用户分配默认租户')
            
            self.stdout.write('')
        
        # 4. 统计结果
        self.stdout.write('步骤 4: 统计结果...')
        for tenant in Tenant.objects.all():
            user_count = UserProfile.objects.filter(tenant=tenant).count()
            self.stdout.write(f'  {tenant.name}: {user_count} 个用户')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  这是试运行模式，没有实际修改数据'))
            self.stdout.write(self.style.WARNING('如需实际执行，请运行: python manage.py migrate_tenants'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ 多租户数据初始化完成！'))
            self.stdout.write(self.style.SUCCESS(f'默认租户: {tenant_company_a.name} ({tenant_company_a.code})'))
        
        self.stdout.write(self.style.SUCCESS('='*60))
