import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from eims_app.models import Personnel, ProjectDetail

print('=== Personnel Table (sample) ===')
personnel_list = Personnel.objects.filter(is_deleted=False)[:10]
for p in personnel_list:
    print(f'ID={p.id}, code={p.personnel_code}, name={p.name}')

print('\n=== ProjectDetail Table (sample with personnel) ===')
projects = ProjectDetail.objects.exclude(
    project_director=''
).exclude(
    project_manager=''
)[:15]
for proj in projects:
    print(f'ID={proj.id}, project_code={proj.project_code}, director={proj.project_director}, manager={proj.project_manager}')

print('\n=== Summary ===')
total_personnel = Personnel.objects.count()
total_projects_with_director = ProjectDetail.objects.exclude(project_director='').count()
total_projects_with_manager = ProjectDetail.objects.exclude(project_manager='').count()

print(f'Total active personnel: {total_personnel}')
print(f'Projects with director: {total_projects_with_director}')
print(f'Projects with manager: {total_projects_with_manager}')
