# BMMS Migration Checklist

**Pre-Flight Checklist for Safe BMMS Migration**
**Date:** October 14, 2025

---

## ✅ Phase 0: Foundation (PRE-PILOT)

**Goal:** Fix critical FK issues without breaking OBCMS
**Timeline:** 1-2 weeks
**Status:** ⏸️ NOT STARTED

### Database Preparation

- [ ] **Create OOBC Organization Record**
  ```sql
  INSERT INTO organizations_organization (id, code, name, org_type, is_active)
  VALUES (gen_random_uuid(), 'OOBC', 'Office for Other Bangsamoro Communities', 'office', true);
  ```
  - [ ] Verify record created successfully
  - [ ] Note organization ID for migration scripts

- [ ] **Backup Production Database**
  - [ ] Full database dump
  - [ ] Verify backup integrity
  - [ ] Test restore procedure
  - [ ] Store backup securely (S3/cloud storage)

- [ ] **Test Database in Staging Environment**
  - [ ] Restore production backup to staging
  - [ ] Apply migration scripts to staging
  - [ ] Verify data integrity in staging
  - [ ] Performance test in staging

---

### User Model Updates

- [ ] **Add OrganizationMembership Support**
  ```python
  # No changes to User model needed - OrganizationMembership already exists
  # Just verify User model has reverse relation:
  # user.organization_memberships.all()
  ```
  - [ ] Verify OrganizationMembership model exists
  - [ ] Test user.organization_memberships query
  - [ ] Test is_primary designation

- [ ] **Create Migration for Existing Users**
  ```python
  # Migration: Link existing OOBC users to OOBC organization
  def migrate_existing_users(apps, schema_editor):
      User = apps.get_model('common', 'User')
      Organization = apps.get_model('organizations', 'Organization')
      OrganizationMembership = apps.get_model('organizations', 'OrganizationMembership')

      oobc_org = Organization.objects.get(code='OOBC')

      # Migrate all OOBC users
      oobc_users = User.objects.filter(user_type__in=['oobc_executive', 'oobc_staff'])
      for user in oobc_users:
          OrganizationMembership.objects.get_or_create(
              user=user,
              organization=oobc_org,
              defaults={'role': 'staff', 'is_primary': True}
          )
  ```
  - [ ] Create migration file
  - [ ] Test migration in development
  - [ ] Test migration in staging
  - [ ] Verify all OOBC users have OrganizationMembership

- [ ] **Add Deprecation Warning to moa_organization Field**
  ```python
  # Add to User model:
  moa_organization = models.ForeignKey(
      'coordination.Organization',
      null=True,
      blank=True,
      on_delete=models.SET_NULL,
      related_name='moa_staff_users_legacy',
      help_text='DEPRECATED: Use organization_memberships instead. Will be removed in BMMS 2.0'
  )
  ```
  - [ ] Update help_text with deprecation notice
  - [ ] Update related_name to avoid conflicts
  - [ ] Document migration path for developers

---

### RBAC System Updates

- [ ] **Update Role Model Organization FK**
  ```python
  # File: src/common/rbac_models.py
  # Change:
  organization = models.ForeignKey(
      'coordination.Organization',  # ❌ OLD
      ...
  )
  # To:
  organization = models.ForeignKey(
      'organizations.Organization',  # ✅ NEW
      ...
  )
  ```
  - [ ] Update Role model
  - [ ] Update UserRole model
  - [ ] Update UserPermission model
  - [ ] Create database migration
  - [ ] Test in development
  - [ ] Test in staging

- [ ] **Update Feature Model Organization FK**
  ```python
  # File: src/common/rbac_models.py
  # Update Feature.organization FK to organizations.Organization
  ```
  - [ ] Update Feature model
  - [ ] Create database migration
  - [ ] Test in development
  - [ ] Test in staging

- [ ] **Migrate Existing RBAC Data**
  ```python
  # Migration: Link existing roles to OOBC organization
  def migrate_rbac_data(apps, schema_editor):
      Role = apps.get_model('common', 'Role')
      Organization = apps.get_model('organizations', 'Organization')

      oobc_org = Organization.objects.get(code='OOBC')

      # Update all organization-scoped roles
      Role.objects.filter(scope='organization', organization__isnull=True).update(
          organization=oobc_org
      )
  ```
  - [ ] Create migration file
  - [ ] Test migration in development
  - [ ] Test migration in staging
  - [ ] Verify all roles have correct organization

---

### WorkItem Model Updates

- [ ] **Update WorkItem Organization FK**
  ```python
  # File: src/common/work_item_model.py
  # Change:
  organization = models.ForeignKey(
      'coordination.Organization',  # ❌ OLD
      ...
  )
  # To:
  organization = models.ForeignKey(
      'organizations.Organization',  # ✅ NEW
      ...
  )
  ```
  - [ ] Update WorkItem model
  - [ ] Create database migration
  - [ ] Test in development
  - [ ] Test in staging

- [ ] **Migrate Existing WorkItems**
  ```python
  # Migration: Link existing work items to OOBC organization
  def migrate_workitems(apps, schema_editor):
      WorkItem = apps.get_model('common', 'WorkItem')
      Organization = apps.get_model('organizations', 'Organization')

      oobc_org = Organization.objects.get(code='OOBC')

      # Update all work items without organization
      WorkItem.objects.filter(organization__isnull=True).update(
          organization=oobc_org
      )
  ```
  - [ ] Create migration file
  - [ ] Test migration in development
  - [ ] Test migration in staging
  - [ ] Verify all work items have organization

---

### Testing & Validation

- [ ] **Unit Tests**
  - [ ] Test OrganizationMembership CRUD
  - [ ] Test user.organization_memberships.all()
  - [ ] Test is_primary organization
  - [ ] Test Role model with organizations.Organization
  - [ ] Test WorkItem model with organizations.Organization

- [ ] **Integration Tests**
  - [ ] Test user login with OrganizationMembership
  - [ ] Test permission checks with new RBAC FKs
  - [ ] Test dashboard with organization context
  - [ ] Test API endpoints with organization filtering

- [ ] **Backward Compatibility Tests**
  - [ ] ✅ OOBC users can log in
  - [ ] ✅ OOBC data is accessible
  - [ ] ✅ OOBC dashboards show correct data
  - [ ] ✅ OOBC reports generate successfully
  - [ ] ✅ No permission errors for OOBC users
  - [ ] ✅ All existing features work as before

- [ ] **Performance Tests**
  - [ ] Query time <300ms for single-org queries
  - [ ] Dashboard load time <1s
  - [ ] API response time <200ms
  - [ ] Memory usage <2GB
  - [ ] Database connections <50

---

### Deployment

- [ ] **Staging Deployment**
  - [ ] Deploy to staging environment
  - [ ] Run migrations on staging database
  - [ ] Test all critical flows
  - [ ] Performance testing
  - [ ] Security testing

- [ ] **Production Deployment Plan**
  - [ ] Schedule maintenance window
  - [ ] Notify users of downtime
  - [ ] Prepare rollback plan
  - [ ] Backup production database
  - [ ] Deploy to production
  - [ ] Run migrations
  - [ ] Verify functionality
  - [ ] Monitor for 24 hours

---

## ✅ Phase 1: Pilot Launch

**Goal:** Enable 3 pilot MOAs (MOH, MOLE, MAFAR)
**Timeline:** 2-4 weeks after Phase 0
**Status:** ⏸️ AWAITING PHASE 0

### Organization Setup

- [ ] **Create Pilot MOA Organizations**
  ```sql
  INSERT INTO organizations_organization (id, code, name, org_type, is_active, is_pilot)
  VALUES
      (gen_random_uuid(), 'MOH', 'Ministry of Health', 'ministry', true, true),
      (gen_random_uuid(), 'MOLE', 'Ministry of Labor and Employment', 'ministry', true, true),
      (gen_random_uuid(), 'MAFAR', 'Ministry of Agriculture, Fisheries and Agrarian Reform', 'ministry', true, true);
  ```
  - [ ] Create MOH organization
  - [ ] Create MOLE organization
  - [ ] Create MAFAR organization
  - [ ] Verify all 3 organizations created
  - [ ] Set is_pilot=true for pilot MOAs

- [ ] **Create Pilot MOA Administrator Accounts**
  - [ ] Create MOH admin user
  - [ ] Create MOLE admin user
  - [ ] Create MAFAR admin user
  - [ ] Assign OrganizationMembership (role='admin', is_primary=true)
  - [ ] Test login for each pilot admin

- [ ] **Configure Pilot MOA Settings**
  - [ ] Enable all modules for pilot MOAs
    - [ ] enable_mana = True
    - [ ] enable_planning = True
    - [ ] enable_budgeting = True
    - [ ] enable_me = True
    - [ ] enable_coordination = True
    - [ ] enable_policies = True
  - [ ] Set primary_region for each MOA
  - [ ] Configure contact information

---

### Model Organization Scoping

- [ ] **OBCCommunity Model**
  ```python
  # Add organization FK (nullable initially)
  organization = models.ForeignKey(
      'organizations.Organization',
      null=True,  # Nullable during migration
      blank=True,
      on_delete=models.PROTECT,
      related_name='communities',
  )
  ```
  - [ ] Add organization FK field
  - [ ] Create database migration
  - [ ] Migrate OOBC communities (assign to OOBC org)
  - [ ] Make organization FK required (NOT NULL)
  - [ ] Add index on organization_id
  - [ ] Update queries to filter by organization

- [ ] **Assessment Model**
  ```python
  # Add organization FK
  organization = models.ForeignKey(
      'organizations.Organization',
      null=True,
      blank=True,
      on_delete=models.PROTECT,
      related_name='assessments',
  )
  ```
  - [ ] Add organization FK field
  - [ ] Create database migration
  - [ ] Migrate OOBC assessments
  - [ ] Make organization FK required
  - [ ] Add index on organization_id
  - [ ] Update MANA module queries

- [ ] **PPA Model**
  ```python
  # Add implementing_moa FK
  implementing_moa = models.ForeignKey(
      'organizations.Organization',
      null=True,
      blank=True,
      on_delete=models.PROTECT,
      related_name='ppas',
  )
  ```
  - [ ] Add implementing_moa FK field
  - [ ] Create database migration
  - [ ] Migrate OOBC PPAs
  - [ ] Make FK required
  - [ ] Add index
  - [ ] Update M&E module queries

---

### View Updates

- [ ] **Communities Views**
  - [ ] Update community_list view with organization filtering
  - [ ] Update community_detail view with organization check
  - [ ] Update community_create view to set organization
  - [ ] Update community_edit view with organization validation
  - [ ] Update provincial_view with organization scoping
  - [ ] Update municipal_view with organization scoping

- [ ] **MANA Views**
  - [ ] Update assessment_list view with organization filtering
  - [ ] Update assessment_detail view with organization check
  - [ ] Update assessment_create view to set organization
  - [ ] Update regional_overview with organization scoping

- [ ] **M&E Views**
  - [ ] Update ppa_list view with organization filtering
  - [ ] Update ppa_detail view with organization check
  - [ ] Update ppa_create view to set organization
  - [ ] Update indicator_tracking with organization scoping

---

### API Updates

- [ ] **Communities API**
  - [ ] Add organization filtering to OBCCommunityViewSet
  - [ ] Update create endpoint to set organization
  - [ ] Add organization field to serializers
  - [ ] Update API documentation

- [ ] **MANA API**
  - [ ] Add organization filtering to AssessmentViewSet
  - [ ] Update create endpoint to set organization
  - [ ] Update API documentation

- [ ] **M&E API**
  - [ ] Add organization filtering to PPAViewSet
  - [ ] Update create endpoint to set organization
  - [ ] Update API documentation

---

### Dashboard Updates

- [ ] **Main Dashboard**
  - [ ] Add organization context to dashboard
  - [ ] Update stat cards with organization filtering
  - [ ] Add organization selector (for OOBC/OCM)
  - [ ] Test with different organization contexts

- [ ] **Module Dashboards**
  - [ ] Update Communities dashboard
  - [ ] Update MANA dashboard
  - [ ] Update M&E dashboard
  - [ ] Update Coordination dashboard

---

### Testing & Validation

- [ ] **Data Isolation Tests**
  - [ ] ✅ MOH cannot see MOLE data
  - [ ] ✅ MOLE cannot see MAFAR data
  - [ ] ✅ MAFAR cannot see MOH data
  - [ ] ✅ OOBC data remains isolated
  - [ ] ✅ OCM can view all MOA data (read-only)

- [ ] **CRUD Operation Tests**
  - [ ] MOH can create communities
  - [ ] MOH can create assessments
  - [ ] MOH can create PPAs
  - [ ] MOLE can create communities
  - [ ] MAFAR can create communities
  - [ ] All created data properly scoped

- [ ] **Permission Tests**
  - [ ] MOH admin has full access to MOH data
  - [ ] MOH staff has limited access to MOH data
  - [ ] MOH viewer has read-only access to MOH data
  - [ ] MOH admin cannot access MOLE data

- [ ] **OCM Aggregation Tests**
  - [ ] OCM can view MOH data
  - [ ] OCM can view MOLE data
  - [ ] OCM can view MAFAR data
  - [ ] OCM can view OOBC data
  - [ ] OCM cannot edit any MOA data

- [ ] **Performance Tests**
  - [ ] Query time with 4 organizations <300ms
  - [ ] Dashboard load time <1s
  - [ ] API response time <200ms
  - [ ] Concurrent user testing (50+ users)

---

### User Training

- [ ] **Pilot MOA Training Materials**
  - [ ] Create MOH user manual
  - [ ] Create MOLE user manual
  - [ ] Create MAFAR user manual
  - [ ] Create video tutorials
  - [ ] Create quick reference guides

- [ ] **Training Sessions**
  - [ ] MOH admin training (2 hours)
  - [ ] MOH staff training (2 hours)
  - [ ] MOLE admin training (2 hours)
  - [ ] MOLE staff training (2 hours)
  - [ ] MAFAR admin training (2 hours)
  - [ ] MAFAR staff training (2 hours)

- [ ] **Support Setup**
  - [ ] Create support email (support@bmms.barmm.gov.ph)
  - [ ] Create support ticketing system
  - [ ] Assign support staff
  - [ ] Create FAQ document
  - [ ] Create troubleshooting guide

---

## ✅ Phase 2: Expand Scoping (DURING PILOT)

**Goal:** Add organization scoping to remaining models
**Timeline:** 3-6 months during pilot operation
**Status:** ⏸️ AWAITING PHASE 1

### Priority 2 Models

- [ ] **StakeholderEngagement**
  - [ ] Add organization FK
  - [ ] Migrate existing data
  - [ ] Update coordination views
  - [ ] Test data isolation

- [ ] **Partnership**
  - [ ] Add lead_organization FK
  - [ ] Keep M2M for multi-org partnerships
  - [ ] Update coordination views
  - [ ] Test data isolation

- [ ] **StrategicPlan**
  - [ ] Add organization FK
  - [ ] Migrate existing data
  - [ ] Update planning views
  - [ ] Test data isolation

- [ ] **BudgetProposal**
  - [ ] Add organization FK
  - [ ] Migrate existing data
  - [ ] Update budget_preparation views
  - [ ] Test data isolation

- [ ] **Disbursement**
  - [ ] Add organization FK
  - [ ] Migrate existing data
  - [ ] Update budget_execution views
  - [ ] Test data isolation

- [ ] **ProgressReport**
  - [ ] Add organization FK (inherits from PPA)
  - [ ] Update M&E views
  - [ ] Test data isolation

- [ ] **Communication**
  - [ ] Add organization FK
  - [ ] Migrate existing data
  - [ ] Update coordination views
  - [ ] Test data isolation

- [ ] **CoordinationNote**
  - [ ] Add organization FK
  - [ ] Migrate existing data
  - [ ] Update coordination views
  - [ ] Test data isolation

- [ ] **ConsultationFeedback**
  - [ ] Add organization FK (inherits from Engagement)
  - [ ] Update coordination views
  - [ ] Test data isolation

---

### Priority 3 Models

- [ ] **OrganizationContact**
  - [ ] Migrate from coordination.Organization to organizations.Organization
  - [ ] Update queries
  - [ ] Test relationships

- [ ] **CommunicationTemplate**
  - [ ] Add organization FK for org-specific templates
  - [ ] Migrate existing templates
  - [ ] Update coordination views

- [ ] **StaffProfile**
  - [ ] Link to OrganizationMembership
  - [ ] Update staff management views
  - [ ] Test staff access

- [ ] **StaffTeam**
  - [ ] Add organization FK
  - [ ] Migrate existing teams
  - [ ] Update staff management views

---

### All Views & APIs

- [ ] **Coordination Module**
  - [ ] Update all views with organization filtering
  - [ ] Update all APIs with organization filtering
  - [ ] Update dashboards
  - [ ] Test data isolation

- [ ] **Planning Module**
  - [ ] Update all views with organization filtering
  - [ ] Update all APIs with organization filtering
  - [ ] Update dashboards
  - [ ] Test data isolation

- [ ] **Budget Preparation Module**
  - [ ] Update all views with organization filtering
  - [ ] Update all APIs with organization filtering
  - [ ] Update dashboards
  - [ ] Test data isolation

- [ ] **Budget Execution Module**
  - [ ] Update all views with organization filtering
  - [ ] Update all APIs with organization filtering
  - [ ] Update dashboards
  - [ ] Test data isolation

- [ ] **Policies Module**
  - [ ] Update all views with organization filtering
  - [ ] Update all APIs with organization filtering
  - [ ] Update dashboards
  - [ ] Test data isolation

- [ ] **Project Central**
  - [ ] Update all views with organization filtering
  - [ ] Update all APIs with organization filtering
  - [ ] Update dashboards
  - [ ] Test data isolation

---

### Performance Optimization

- [ ] **Database Indexes**
  - [ ] Verify indexes on all organization_id fields
  - [ ] Add composite indexes for common queries
  - [ ] Analyze query performance
  - [ ] Optimize slow queries

- [ ] **Caching Strategy**
  - [ ] Implement Redis caching for dashboard stats
  - [ ] Cache permission checks
  - [ ] Cache organization context
  - [ ] Set appropriate TTLs

- [ ] **Query Optimization**
  - [ ] Use select_related for FKs
  - [ ] Use prefetch_related for M2M
  - [ ] Optimize aggregation queries
  - [ ] Eliminate N+1 query problems

---

## ✅ Phase 3: Full Rollout (44 MOAs)

**Goal:** Onboard all 44 BARMM MOAs
**Timeline:** 6-12 months after successful pilot
**Status:** ⏸️ AWAITING PHASE 2

### Organization Creation

- [ ] **Create All 44 MOA Organizations**
  - [ ] Research and document all 44 MOA codes
  - [ ] Create organization records in database
  - [ ] Verify all organizations active
  - [ ] Configure module enablement per MOA

### Batch Onboarding

- [ ] **Wave 1: 8-10 MOAs**
  - [ ] Create MOA organizations
  - [ ] Create admin accounts
  - [ ] Train MOA staff
  - [ ] Monitor for 2 weeks
  - [ ] Validate data isolation

- [ ] **Wave 2: 8-10 MOAs**
  - [ ] Create MOA organizations
  - [ ] Create admin accounts
  - [ ] Train MOA staff
  - [ ] Monitor for 2 weeks
  - [ ] Validate data isolation

- [ ] **Wave 3: 8-10 MOAs**
  - [ ] Create MOA organizations
  - [ ] Create admin accounts
  - [ ] Train MOA staff
  - [ ] Monitor for 2 weeks
  - [ ] Validate data isolation

- [ ] **Wave 4: 8-10 MOAs**
  - [ ] Create MOA organizations
  - [ ] Create admin accounts
  - [ ] Train MOA staff
  - [ ] Monitor for 2 weeks
  - [ ] Validate data isolation

- [ ] **Wave 5: Remaining MOAs**
  - [ ] Create MOA organizations
  - [ ] Create admin accounts
  - [ ] Train MOA staff
  - [ ] Monitor for 2 weeks
  - [ ] Validate data isolation

---

### Scale Testing

- [ ] **Performance Testing with 44 Organizations**
  - [ ] Query time <500ms with full load
  - [ ] Dashboard load time <2s
  - [ ] API response time <500ms
  - [ ] Concurrent user testing (200+ users)
  - [ ] Database connection pooling

- [ ] **Data Integrity Validation**
  ```sql
  -- Verify no orphaned data
  SELECT COUNT(*) FROM communities_obccommunity WHERE organization_id IS NULL;

  -- Verify data distribution across MOAs
  SELECT o.code, COUNT(c.id) AS community_count
  FROM organizations_organization o
  LEFT JOIN communities_obccommunity c ON c.organization_id = o.id
  GROUP BY o.code
  ORDER BY o.code;
  ```
  - [ ] No orphaned data
  - [ ] Data properly distributed
  - [ ] No cross-organization leaks

---

### Monitoring & Support

- [ ] **Production Monitoring**
  - [ ] Set up application monitoring (New Relic, DataDog, etc.)
  - [ ] Monitor query performance
  - [ ] Monitor error rates
  - [ ] Monitor user activity
  - [ ] Set up alerts for issues

- [ ] **User Support**
  - [ ] Expand support team
  - [ ] Create MOA-specific support channels
  - [ ] Weekly check-ins with each MOA
  - [ ] Gather feedback and improvement suggestions
  - [ ] Monthly user satisfaction surveys

---

## Success Metrics

### Technical Metrics

- [ ] ✅ All 44 MOAs can log in and access only their data
- [ ] ✅ 100% data isolation (no cross-organization leaks)
- [ ] ✅ Query performance <500ms for single-org queries
- [ ] ✅ Dashboard load time <2s
- [ ] ✅ API response time <500ms
- [ ] ✅ Zero downtime during migration
- [ ] ✅ Test coverage >95%

### Operational Metrics

- [ ] ✅ OOBC continues to function normally throughout migration
- [ ] ✅ Zero data loss during migration
- [ ] ✅ All pilot MOAs successfully onboarded
- [ ] ✅ All 44 MOAs operational within 12 months
- [ ] ✅ User satisfaction >80%
- [ ] ✅ Support ticket response time <24 hours

---

## Rollback Plan

### Phase 0 Rollback

If Phase 0 fails:
1. Restore database from backup
2. Revert code changes
3. Test OOBC functionality
4. Analyze failure cause
5. Fix issues and retry

### Phase 1 Rollback

If Phase 1 fails:
1. Disable pilot MOA accounts
2. Keep OOBC operational
3. Analyze failure cause
4. Fix issues and retry
5. No data loss - pilot MOAs start fresh

### Phase 2/3 Rollback

If Phase 2/3 fails:
1. Stop new MOA onboarding
2. Keep existing MOAs operational
3. Analyze failure cause
4. Fix issues and resume
5. Incremental rollout reduces risk

---

**Document Status:** ✅ Ready for Use
**Last Updated:** October 14, 2025
**Next Review:** Start of Phase 0 Implementation
