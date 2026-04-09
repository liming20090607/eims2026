from eims_app.models.model_tenant import Tenant

count = Tenant.objects.count()
print(f"Tenant count: {count}")
for t in Tenant.objects.all():
    print(f" - {t.name} (active: {t.is_active})")
