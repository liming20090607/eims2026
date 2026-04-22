"""
Database Router for Multi-System Architecture
Automatically routes database operations to the correct company database based on request context.
"""


class CompanyDatabaseRouter:
    """
    A router to control all database operations for models in the multi-system architecture.
    
    Routes database queries based on the current_system attribute set by PathResolverMiddleware.
    """
    
    def db_for_read(self, model, **hints):
        """Route read operations to the appropriate database."""
        # Django core models always use root_admin database (not default)
        if model._meta.app_label in ['auth', 'admin', 'contenttypes', 'sessions']:
            return 'root_admin'
        
        # User authentication models must use root_admin
        # This includes UserProfile, UserTenantRelation, Tenant, etc.
        # CompanyExecutiveRole, DepartmentRole, ApprovalChain, and Approval models MUST use root_admin because they have ForeignKey to User/Tenant/CompanyExecutiveRole
        # NOTE: Personnel, Employee, ProjectDetail are tenant-isolated with db_constraint=False, route to company database based on request context
        # Personnel has FK to ProjectDetail, both must be in same company database
        if model._meta.app_label == 'eims_app' and model.__name__ in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule',
            'CompanyExecutiveRole', 'DepartmentRole', 'ApprovalChain',
            'ContractApproval', 'SealApproval', 'ArchiveApproval'
        ]:
            return 'root_admin'
        
        request = hints.get('request')
        if request:
            system = getattr(request, 'current_system', None)
            if system == 'dingce':
                return 'dingce'
            elif system == 'shengchang':
                return 'shengchang'
            elif system == 'jiachengda':
                return 'jiachengda'
            elif system == 'root':
                return 'root_admin'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Route write operations to the appropriate database."""
        # Django core models always use root_admin database (not default)
        if model._meta.app_label in ['auth', 'admin', 'contenttypes', 'sessions']:
            return 'root_admin'
        
        # User authentication models must use root_admin
        # This includes UserProfile, UserTenantRelation, Tenant, etc.
        # CompanyExecutiveRole, DepartmentRole, ApprovalChain, and Approval models MUST use root_admin because they have ForeignKey to User/Tenant/CompanyExecutiveRole
        # NOTE: Personnel, Employee, ProjectDetail are tenant-isolated with db_constraint=False, route to company database based on request context
        # Personnel has FK to ProjectDetail, both must be in same company database
        if model._meta.app_label == 'eims_app' and model.__name__ in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule',
            'CompanyExecutiveRole', 'DepartmentRole', 'ApprovalChain',
            'ContractApproval', 'SealApproval', 'ArchiveApproval'
        ]:
            return 'root_admin'
        
        request = hints.get('request')
        if request:
            system = getattr(request, 'current_system', None)
            if system == 'dingce':
                return 'dingce'
            elif system == 'shengchang':
                return 'shengchang'
            elif system == 'jiachengda':
                return 'jiachengda'
            elif system == 'root':
                return 'root_admin'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations only within the same database.
        Root admin and user models can access all databases.
        """
        # Allow relations for user authentication models
        # CompanyExecutiveRole, DepartmentRole, and Approval models are included because they reference User/Tenant
        # NOTE: Personnel, Employee, ProjectDetail are tenant-isolated with db_constraint=False, stay in company database
        if obj1._meta.app_label == 'eims_app' and obj1.__class__.__name__ in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule',
            'CompanyExecutiveRole', 'DepartmentRole',
            'ContractApproval', 'SealApproval', 'ArchiveApproval'
        ]:
            return True
        if obj2._meta.app_label == 'eims_app' and obj2.__class__.__name__ in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule',
            'CompanyExecutiveRole', 'DepartmentRole',
            'ContractApproval', 'SealApproval', 'ArchiveApproval'
        ]:
            return True
        
        db_list = ('dingce', 'shengchang', 'jiachengda', 'root_admin')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            # If both are in the same database, allow
            if obj1._state.db == obj2._state.db:
                return True
            # If one is root_admin, allow cross-database relations
            if obj1._state.db == 'root_admin' or obj2._state.db == 'root_admin':
                return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Control which database migrations run on which database.
        Django core apps only migrate on root_admin.
        User authentication models only migrate on root_admin.
        Other eims_app models migrate on all company databases.
        """
        # Django core apps only migrate on root_admin database
        if app_label in ['auth', 'admin', 'contenttypes', 'sessions']:
            return db == 'root_admin'
        
        # User authentication models only migrate on root_admin
        # CompanyExecutiveRole, DepartmentRole, and Approval models only migrate on root_admin because they reference User/Tenant
        # NOTE: Personnel, Employee, ProjectDetail migrate to all company databases (tenant-isolated with db_constraint=False)
        # Personnel has FK to ProjectDetail, both must be in same company database
        if app_label == 'eims_app' and model_name in [
            'userprofile', 'usertenantrelation', 'tenant', 'tenantmodule',
            'companyexecutiverole', 'departmentrole',
            'contractapproval', 'sealapproval', 'archiveapproval'
        ]:
            return db == 'root_admin'
        
        # Other eims_app models migrate on all company databases
        if app_label == 'eims_app':
            if db in ['dingce', 'shengchang', 'jiachengda', 'root_admin', 'default']:
                return True
        
        # For other cases, don't allow migration
        return False
