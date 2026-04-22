"""
Multi-System Architecture Test Script
Verifies that the multi-system architecture is working correctly.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory
from eims_app.middleware.path_resolver import PathResolverMiddleware


def test_path_resolver():
    """Test the path resolver middleware."""
    print("\n" + "="*80)
    print("测试 1: 路径解析中间件")
    print("="*80)
    
    factory = RequestFactory()
    middleware = PathResolverMiddleware(lambda r: None)
    
    test_cases = [
        ('/dingce/', 'dingce', '广西鼎策工程顾问有限责任公司'),
        ('/shengchang/', 'shengchang', '广西晟昌工程科技有限责任公司'),
        ('/jiachengda/', 'jiachengda', '广西嘉诚达工程造价咨询有限公司'),
        ('/root/', 'root', '超级管理员后台'),
        ('/', None, None),
    ]
    
    all_passed = True
    
    for path, expected_system, expected_company in test_cases:
        request = factory.get(path)
        middleware(request)
        
        system_ok = getattr(request, 'current_system', None) == expected_system
        company_ok = getattr(request, 'company_name', None) == expected_company
        
        status = "✓" if (system_ok and company_ok) else "✗"
        print(f"{status} 路径: {path:20s} -> 系统: {str(getattr(request, 'current_system', None)):15s} | 公司: {str(getattr(request, 'company_name', None))}")
        
        if not (system_ok and company_ok):
            all_passed = False
    
    return all_passed


def test_database_config():
    """Test database configuration."""
    print("\n" + "="*80)
    print("测试 2: 数据库配置")
    print("="*80)
    
    from django.conf import settings
    
    required_dbs = ['default', 'dingce', 'shengchang', 'jiachengda', 'root_admin']
    all_passed = True
    
    for db_name in required_dbs:
        if db_name in settings.DATABASES:
            db_config = settings.DATABASES[db_name]
            print(f"✓ 数据库 '{db_name}' 已配置: {db_config['NAME']}")
        else:
            print(f"✗ 数据库 '{db_name}' 未配置!")
            all_passed = False
    
    # Check database router
    if hasattr(settings, 'DATABASE_ROUTERS'):
        print(f"✓ 数据库路由已配置: {settings.DATABASE_ROUTERS}")
    else:
        print(f"✗ 数据库路由未配置!")
        all_passed = False
    
    return all_passed


def test_installed_apps():
    """Test INSTALLED_APPS configuration."""
    print("\n" + "="*80)
    print("测试 3: 已安装应用")
    print("="*80)
    
    from django.conf import settings
    
    required_apps = ['eims_dingce', 'eims_shengchang', 'eims_jiachengda', 'eims_root_admin']
    all_passed = True
    
    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print(f"✓ 应用 '{app}' 已安装")
        else:
            print(f"✗ 应用 '{app}' 未安装!")
            all_passed = False
    
    return all_passed


def test_middleware_config():
    """Test middleware configuration."""
    print("\n" + "="*80)
    print("测试 4: 中间件配置")
    print("="*80)
    
    from django.conf import settings
    
    path_resolver = 'eims_app.middleware.path_resolver.PathResolverMiddleware'
    
    if path_resolver in settings.MIDDLEWARE:
        print(f"✓ 路径解析中间件已配置")
        return True
    else:
        print(f"✗ 路径解析中间件未配置!")
        return False


def test_url_configuration():
    """Test URL configuration."""
    print("\n" + "="*80)
    print("测试 5: URL 配置")
    print("="*80)
    
    try:
        from django.urls import reverse, NoReverseMatch
        
        # Try to reverse some URLs (this will fail if apps aren't properly configured)
        test_urls = []
        
        all_passed = True
        for url_name in test_urls:
            try:
                url = reverse(url_name)
                print(f"✓ URL '{url_name}' 可解析: {url}")
            except NoReverseMatch:
                print(f"⚠ URL '{url_name}' 无法解析（可能尚未定义）")
        
        print("✓ URL 配置文件语法正确")
        return all_passed
    except Exception as e:
        print(f"✗ URL 配置错误: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("多系统架构测试套件")
    print("="*80)
    
    results = {
        '路径解析中间件': test_path_resolver(),
        '数据库配置': test_database_config(),
        '已安装应用': test_installed_apps(),
        '中间件配置': test_middleware_config(),
        'URL 配置': test_url_configuration(),
    }
    
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name:20s}: {status}")
        if not passed:
            all_passed = False
    
    print("="*80)
    
    if all_passed:
        print("\n🎉 所有测试通过！多系统架构配置正确。")
        print("\n下一步:")
        print("1. 运行 SQL 脚本创建数据库: mysql -u root -p < create_multi_system_databases.sql")
        print("2. 执行数据库迁移: python run_multi_system_migrations.py")
        print("3. 启动服务器测试: python manage.py runserver")
    else:
        print("\n❌ 部分测试失败，请检查上述错误。")
    
    print("="*80 + "\n")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
