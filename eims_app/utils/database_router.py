class CompanyDatabaseRouter:
    """
    A router to control all database operations for models in the multi-system architecture.
    
    Routes database queries based on the current_system attribute set by PathResolverMiddleware.
    """
    
    def db_for_read(self, model, **hints):
        """Route read operations to the appropriate database."""
        # Django core models always use root_admin database
        if model._meta.app_label in ['auth', 'admin', 'contenttypes', 'sessions']:
            return 'root_admin'
        
        # CRITICAL: ALWAYS route Tenant and its related models to root_admin
        # This is essential because Tenant only exists in root_admin database
        # and is referenced by ForeignKey from many company-isolated models
        if model._meta.app_label == 'eims_app' and model.__name__ in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule', 'TenantModulePermission',
            'CompanyExecutiveRole', 'DepartmentRole', 'ApprovalChain',
            'ContractApproval', 'SealApproval', 'ArchiveApproval'
        ]:
            return 'root_admin'
        
        # CRITICAL: Personnel, Employee, ProjectDetail must ALWAYS route to company databases based on request context
        # They are tenant-isolated models with db_constraint=False
        # Personnel has FK to ProjectDetail - they MUST be in the same database!
        if model._meta.app_label == 'eims_app' and model.__name__ in ['Personnel', 'Employee', 'ProjectDetail',
            'CostProjectInfo', 'CostProjectUnified', 'CostTaskPlan', 'CostTaskImplementation',
            'CostReviewResult', 'CostPaymentStatus', 'CostProjectArchive', 'CostRemunerationDistribution',
            'CostConsultingReminder']:
            request = hints.get('request')
            if request:
                system = getattr(request, 'current_system', None)
                if system in ['dingce', 'shengchang', 'jiachengda']:
                    return system
                elif system == 'root':
                    # For /root/ path, try session tenant first
                    if hasattr(request, 'session') and request.session.get('tenant_id'):
                        try:
                            from eims_app.models import Tenant
                            tenant = Tenant.objects.using('root_admin').get(id=request.session.get('tenant_id'))
                            if tenant.code in ['dingce', 'shengchang', 'jiachengda']:
                                return tenant.code
                        except:
                            pass
                    # No session tenant or error - use dingce database (default MySQL)
                    return 'dingce'
            # No request context - use dingce database (MySQL)
            return 'dingce'
        
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
                # For /root/ access, try to get tenant from session
                if hasattr(request, 'session') and request.session.get('tenant_id'):
                    tenant_id = request.session.get('tenant_id')
                    # Get tenant info to determine which database to use
                    try:
                        from eims_app.models import Tenant
                        tenant = Tenant.objects.using('root_admin').get(id=tenant_id)
                        if tenant.code == 'dingce':
                            return 'dingce'
                        elif tenant.code == 'shengchang':
                            return 'shengchang'
                        elif tenant.code == 'jiachengda':
                            return 'jiachengda'
                        else:
                            return 'root_admin'
                    except:
                        pass
                
                # For tenant-isolated models (Employee, Personnel, ProjectDetail, Department),
                # when no tenant_id in session, use 'dingce' database (MySQL)
                # These models are distributed across company databases
                if model.__name__ in ['Employee', 'Personnel', 'ProjectDetail', 'Department', 'Contract', 'OutputPayment', 'ProjectRole', 'ProjectDynamic', 'ProjectReporter',
                    'CostProjectInfo', 'CostProjectUnified', 'CostTaskPlan', 'CostTaskImplementation',
                    'CostReviewResult', 'CostPaymentStatus', 'CostProjectArchive', 'CostRemunerationDistribution',
                    'CostConsultingReminder']:
                    return 'dingce'
                
                # If no tenant in session and model is not tenant-isolated, use root_admin (super admin context)
                return 'root_admin'
        
        # For tenant-isolated business models without request context,
        # use dingce database (MySQL)
        # Note: CompanyExecutiveRole, DepartmentRole, and ApprovalChain are NOT here - they use root_admin because they reference User/CompanyExecutiveRole
        if model._meta.app_label == 'eims_app' and model.__name__ in [
            'Department', 'Employee', 'Personnel', 'ProjectDetail', 'Contract', 
            'OutputPayment', 'ProjectRole', 'ProjectDynamic', 'ProjectReporter',
            'CostProjectInfo', 'CostProjectUnified', 'CostTaskPlan', 'CostTaskImplementation',
            'CostReviewResult', 'CostPaymentStatus', 'CostProjectArchive', 'CostRemunerationDistribution',
            'CostConsultingReminder'
        ]:
            return 'dingce'
        
        # For business models like Department, etc., 
        # try to get tenant from hints or use dingce database (MySQL)
        return 'dingce'
    
    def db_for_write(self, model, **hints):
        """Route write operations to the appropriate database."""
        # Django core models always use root_admin database
        if model._meta.app_label in ['auth', 'admin', 'contenttypes', 'sessions']:
            return 'root_admin'
        
        # CRITICAL: ALWAYS route Tenant and its related models to root_admin
        # This is essential because Tenant only exists in root_admin database
        # and is referenced by ForeignKey from many company-isolated models
        if model._meta.app_label == 'eims_app' and model.__name__ in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule', 'TenantModulePermission',
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
        
        # For business models like Department, etc., 
        # try to get tenant from hints or use dingce database (MySQL)
        return 'dingce'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations only within the same database.
        Root admin and user models can access all databases.
        """
        # Get model names
        model1_name = obj1.__class__.__name__
        model2_name = obj2.__class__.__name__
        
        # CRITICAL: ALWAYS allow Tenant to have cross-database relations
        # Tenant only exists in root_admin, but is referenced by many company-isolated models
        if obj1._meta.app_label == 'eims_app' and model1_name in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule', 'TenantModulePermission', 
            'DepartmentRole', 'CompanyExecutiveRole', 'ApprovalChain',
            'ContractApproval', 'SealApproval', 'ArchiveApproval',
            'Employee', 'Personnel', 'ProjectDetail', 'Department',  # CRITICAL: Add tenant-isolated models
            'CostProjectInfo', 'CostProjectUnified', 'CostTaskPlan', 'CostTaskImplementation',  # 造价咨询模型
            'CostReviewResult', 'CostPaymentStatus', 'CostProjectArchive', 'CostRemunerationDistribution',  # 造价咨询模型
            'CostConsultingReminder'  # 造价咨询提醒模型
        ]:
            return True
        if obj2._meta.app_label == 'eims_app' and model2_name in [
            'UserProfile', 'UserTenantRelation', 'Tenant', 'TenantModule', 'TenantModulePermission',
            'DepartmentRole', 'CompanyExecutiveRole', 'ApprovalChain',
            'ContractApproval', 'SealApproval', 'ArchiveApproval',
            'Employee', 'Personnel', 'ProjectDetail', 'Department',  # CRITICAL: Add tenant-isolated models
            'CostProjectInfo', 'CostProjectUnified', 'CostTaskPlan', 'CostTaskImplementation',  # 造价咨询模型
            'CostReviewResult', 'CostPaymentStatus', 'CostProjectArchive', 'CostRemunerationDistribution',  # 造价咨询模型
            'CostConsultingReminder'  # 造价咨询提醒模型
        ]:
            return True
        
        # Allow Department to relate with User (for manager field)
        if model1_name == 'Department' or model2_name == 'Department':
            if model1_name == 'User' or model2_name == 'User':
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
        
        # User authentication and tenant models only migrate on root_admin
        # CompanyExecutiveRole, DepartmentRole, ApprovalChain, and Approval models only migrate on root_admin because they reference User/Tenant
        # NOTE: Personnel, Employee, ProjectDetail migrate to all company databases (tenant-isolated with db_constraint=False)
        # Personnel has FK to ProjectDetail, both must be in same company database
        if app_label == 'eims_app' and model_name in [
            'userprofile', 'usertenantrelation', 'tenant', 'tenantmodule', 'tenantmodulepermission',
            'companyexecutiverole', 'departmentrole', 'approvalchain',
            'contractapproval', 'sealapproval', 'archiveapproval'
        ]:
            return db == 'root_admin'
        
        # Other eims_app models migrate on all company databases
        if app_label == 'eims_app':
            if db in ['dingce', 'shengchang', 'jiachengda', 'root_admin', 'default']:
                return True
        
        # For other cases, don't allow migration
        return False
