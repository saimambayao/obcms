# OBC Management System Documentation

## Overview

The Other Bangsamoro Communities (OBC) Management System is a comprehensive web-based platform designed to support the Office for Other Bangsamoro Communities (OOBC) in managing and coordinating services for Bangsamoro communities outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM).

### AI-Enhanced Platform
**OBCMS is the first AI-enhanced government platform** in the Philippines specifically designed to serve Bangsamoro communities with cultural intelligence, evidence-based insights, and intelligent automation.

**Key AI Capabilities:**
- AI-powered needs classification and prediction across all modules
- Cross-module semantic search and evidence synthesis
- Automated report generation with cultural sensitivity
- Intelligent stakeholder matching and partnership prediction
- Real-time anomaly detection and performance forecasting
- Natural language conversational interface for data queries

---

## Documentation Index

> 📌 **Documentation Recently Reorganized!** (October 2025)
>
> **163 markdown files** have been moved from the project root into organized `docs/` subdirectories. See [Documentation Reorganization Summary](DOCUMENTATION_REORGANIZATION_SUMMARY.md) for:
> - Complete list of moved files by category
> - New directory structure
> - File location mappings
>
> **Only 4 files remain in root:** README.md, CLAUDE.md, AGENTS.md, GEMINI.md (AI configuration)

### 📋 Administrator Operations
- [Installation Guide](admin-guide/installation.md)

### 🚀 Deployment & Infrastructure

**⚠️ BEFORE DEPLOYING: Read [CLAUDE.md](../CLAUDE.md) Lines 362-683 - Complete Deployment Checklist**

- **Production Deployment:**
  - [Deployment Readiness Verification](deployment/DEPLOYMENT_READINESS_VERIFICATION.md) ⭐ **FINAL VERIFICATION - 100% Ready**
  - [Production Deployment Issues & Resolution](deployment/production-deployment-issues-resolution.md) ⭐ **Primary Reference**
  - [Production Deployment Troubleshooting](deployment/PRODUCTION_DEPLOYMENT_TROUBLESHOOTING.md) 🆕 **Critical Fixes - CSRF, CSS, Cache**
  - [Deployment Implementation Status](deployment/DEPLOYMENT_IMPLEMENTATION_STATUS.md)
  - [Critical Blockers Fixed](deployment/CRITICAL_BLOCKERS_FIXED.md) ✅
  - [Pre-Deployment Implementation Summary](deployment/pre-deployment-implementation-summary.md)
  - [Pre-Staging Complete](deployment/PRE_STAGING_COMPLETE.md) ✅ **NEW - Ready for Staging**

- **Platform-Specific Guides:**
  - [Coolify Deployment Plan](deployment/coolify-deployment-plan.md)
  - [Coolify Deployment Checklist](deployment/deployment-coolify.md)
  - [Docker Guide](deployment/docker-guide.md)

- **Django 5.2 LTS Upgrade:**

  **⚠️ NEW: Django 5.2 LTS Migration Ready**

  **Quick Start:**
  - [Django 5.2 Quick Start Guide](deployment/DJANGO_5_2_QUICK_START.md) ⭐ **START HERE - Ready to Migrate**
  - [Django 5.2 Migration Analysis](deployment/DJANGO_5_2_MIGRATION_ANALYSIS.md) ✅ **Complete Impact Assessment**

  **Key Highlights:**
  - ✅ **All Dependencies Compatible** - DRF 3.16, django-debug-toolbar 6.0, etc.
  - ✅ **Audit Passed** - 0 critical issues, 3 minor deprecation warnings
  - ✅ **Python 3.12 Fully Supported** - No upgrade needed
  - ✅ **Extended Support** - Until April 2028 (+15 months vs Django 4.2)
  - ✅ **Low Risk** - Minimal breaking changes, mostly configuration

  **Migration Steps:**
  ```bash
  # 1. Run audit
  ./scripts/audit_django_5_compatibility.sh

  # 2. Update Django
  # Edit requirements/base.txt: Django>=5.2.0,<5.3.0
  pip install -r requirements/development.txt

  # 3. Migrate
  cd src && python manage.py migrate

  # 4. Test
  pytest -v
  ```

- **Database Migration to PostgreSQL:**

  **⚠️ CRITICAL: Before Migration, Review ALL Documents Below**

  **Quick Start Guide:**
  ```bash
  # 1. Create PostgreSQL database (NO PostGIS extension needed!)
  CREATE DATABASE obcms_prod ENCODING 'UTF8';
  CREATE USER obcms_user WITH PASSWORD 'secure-password';
  GRANT ALL PRIVILEGES ON DATABASE obcms_prod TO obcms_user;

  # 2. Update .env
  DATABASE_URL=postgres://obcms_user:password@localhost:5432/obcms_prod

  # 3. Run migrations (all 118 migrations are PostgreSQL-compatible)
  cd src
  python manage.py migrate
  # Expected: All migrations complete in 2-5 minutes
  ```

  **Critical Decisions Made:**
  - ✅ **Geographic Data: Use JSONField (NO PostGIS!)** - Production-ready, works with PostgreSQL native `jsonb`
  - ✅ **Text Queries: 100% Compatible** - All queries already use case-insensitive lookups
  - ✅ **No Code Changes Required** - System is fully PostgreSQL-compatible

  **Essential Reading:**
  - [PostgreSQL Migration Summary](deployment/POSTGRESQL_MIGRATION_SUMMARY.md) ⭐ **START HERE - Complete Overview**
  - [PostgreSQL Migration Review](deployment/POSTGRESQL_MIGRATION_REVIEW.md) ✅ **Technical Analysis**
  - [Case-Sensitive Query Audit](deployment/CASE_SENSITIVE_QUERY_AUDIT.md) ✅ **100% Compatible**

  **Geographic Data (Critical):**
  - [Geographic Data Implementation](improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md) ✅ **NO PostGIS Needed**
  - [PostGIS Migration Guide](improvements/geography/POSTGIS_MIGRATION_GUIDE.md) 📋 **Reference Only (NOT Recommended)**

  **Other Guides:**
  - [PostgreSQL Migration Next Steps](deployment/POSTGRESQL_MIGRATION_NEXT_STEPS.md) 🆕 **When Ready to Migrate**
  - [PostgreSQL Migration Guide](deployment/postgres-migration-guide.md)
  - [Regional MANA Deployment Checklist](deployment/regional_mana_deployment_checklist.md)

### 🌍 Environment Configuration
- [Development Environment](env/development.md)
- [Staging Environment - Complete Guide](env/staging-complete.md) ⭐ **NEW - 12-Step Deployment**
- [Staging Environment](env/staging.md)
- [Production Environment](env/production.md)
- [Testing Environment](env/testing.md)

### 🧪 Testing & Verification
- **Core Documentation:**
  - [Testing Strategy](testing/TESTING_STRATEGY.md) ⭐ **NEW - Comprehensive Testing Guide**
    - Complete test taxonomy (unit, integration, E2E, security, performance)
    - Implementation guides with code examples
    - CI/CD pipeline integration
    - Tools and frameworks reference
  - [Staging Rehearsal Checklist](testing/staging_rehearsal_checklist.md) ⭐ **NEW - Pre-release Dry Run Guide**
  - [Calendar Performance Test Plan](testing/calendar_performance_plan.md) ⭐ **NEW - Scope & Metrics**
- **Test Reports:**
  - [Full Suite Test Report](testing/FULL_SUITE_TEST_REPORT.md) - Comprehensive system test results
  - [Performance Test Results](testing/PERFORMANCE_TEST_RESULTS.md) ⭐ **NEW - 83% Passing**
  - [MANA Test Verification](testing/MANA_TEST_VERIFICATION.md)
  - [Production Test Results](testing/PRODUCTION_TEST_RESULTS.md)
- **Test Environments:**
  - [Region X Demo Setup](testing/REGION_X_DEMO.md)
  - [Test Credentials](testing/TEST_CREDENTIALS.md)

### 💻 Development Guidelines
- **AI Agent Configuration** (in project root):
  - [AI Agents Overview](../AGENTS.md)
  - [Claude Configuration](../CLAUDE.md) ⚙️
  - [Gemini Configuration](../GEMINI.md)
  - [Constitutional Workflow Agent Integration](ai/agents/CONSTITUTIONAL_WORKFLOW_AGENT.md)
- [Development README](development/README.md) - Setup guide
- [Task Template Automation Service Guide](development/task_template_automation.md) ⭐ **NEW - Automation Contract & Examples**

### 📚 Program Guidelines
- [Assistance Program Guidelines](guidelines/OBC_guidelines_assistance.md)
- [MANA Implementation Guidelines](guidelines/OBC_guidelines_mana.md)
- [Policy Coordination Guidelines](guidelines/OBC_guidelines_policy.md)
- [Facilitator Training Guide](guidelines/facilitator_training_guide.md)
- [Participant User Guide](guidelines/participant_user_guide.md)
- [Event vs WorkItem Activity Decision Guide](guidelines/EVENT_VS_WORKITEM_ACTIVITY.md) ⭐ **NEW - Choose the Right Tool**

### 🗺️ Reference Documentation
- [Coordinate System Guide](reference/COORDINATE_SYSTEM.md)
- [Region IX Coordinate Guide](reference/REGION_IX_COORDINATE_GUIDE.md)

### 📦 Product Roadmap & Strategy
- [OBCMS MVP Scope](product/obcMS-MVP.md)
- [OBCMS Summary](product/obcMS-summary.md)
- [MANA Two Systems Architecture](product/mana_two_systems_architecture.md)

### 🔧 Improvements & Implementation
- **System-Wide:**
  - [Directory Structure Reorganization - COMPLETE](improvements/DIRECTORY_REORGANIZATION_COMPLETE.md) 🆕 **Oct 2025 - Django Best Practices**
  - [Directory Reorganization Plan](improvements/DIRECTORY_STRUCTURE_REORGANIZATION_PLAN.md) 🆕 **Planning Document**
  - [Corrections Applied](improvements/CORRECTIONS_APPLIED.md)
  - [Implementation Complete](improvements/IMPLEMENTATION_COMPLETE.md)
  - [System Isolation Complete](improvements/SYSTEM_ISOLATION_COMPLETE.md)
  - [OBC System Requirements Gap Plan](improvements/obc_system_requirements_gap_plan.md)
  - [Improvement Plan Template](improvements/improvement_plan_template.md)

- **BARMM Integration:**
  - [BARMM Acronyms Implementation](improvements/BARMM_ACRONYMS_IMPLEMENTATION.md)
  - [BARMM MOA Implementation Complete](improvements/BARMM_MOA_IMPLEMENTATION_COMPLETE.md)
  - [BARMM MOA Mandates Implementation](improvements/BARMM_MOA_MANDATES_IMPLEMENTATION.md)

- **Geographic Data:**
  - [Geographic Data Implementation Guide](improvements/geography/GEOGRAPHIC_DATA_IMPLEMENTATION.md) ⭐ **NEW - JSONField vs PostGIS**
  - [PostGIS Migration Guide](improvements/geography/POSTGIS_MIGRATION_GUIDE.md) 📋 **Reference Only (Future)**

- **Module-Specific:**
  - [Planning & Budgeting Implementation Evaluation](improvements/planning_budgeting_implementation_evaluation.md) ⭐ **NEW - Codebase Analysis**
  - [Planning & Budgeting Comprehensive Plan](improvements/planning_budgeting_comprehensive_plan.md) ⭐ **NEW - Research-based**
  - [Planning & Budgeting Module Improvements](improvements/planning_budgeting_module_improvements.md)
  - [3-Tier Navigation Integration Complete](improvements/3_tier_navigation_integration_complete.md) ⭐ **NEW - P&B Navigation** ✅
  - [Navigation Architecture Diagram](improvements/navigation_architecture_diagram.md) ⭐ **NEW - Visual Guide**
  - [Staff Management Module Improvements](improvements/staff_management_module_improvements.md)
  - [Staff Profile Tabs Plan](improvements/staff_profile_tabs_plan.md)
  - [Coordination Calendar Improvement Plan](improvements/coordination-calendar-improvement-plan.md)
  - [Instant UI Improvements Plan](improvements/instant_ui_improvements_plan.md)

- **Work Items Tree Navigation:** ✅ **NEW - Refactored & Production-Ready**
  - [Work Items Tree Refactoring](improvements/WORK_ITEMS_TREE_REFACTORING.md) ⭐ **Complete Refactoring Documentation**
  - [Work Items Tree Quick Reference](development/WORK_ITEMS_TREE_QUICK_REFERENCE.md) 🚀 **Developer Quick Start**
  - [Subtask Nesting Implementation](improvements/SUBTASK_NESTING_IMPLEMENTATION.md) ✅ **NEW - Subtasks Can Have Children (Up to Level 5 = 3 Nested Levels)**

- **Calendar System:**
  - [Advanced Calendar Architecture](improvements/CALENDAR_ADVANCED_ARCHITECTURE.md) ⭐ **NEW - Google Calendar-Inspired UI Design**

- **MOA RBAC System:** 🔐 **NEW - Role-Based Access Control for MOA Users**
  - [MOA RBAC Quick Reference](improvements/MOA_RBAC_QUICK_REFERENCE.md) 🚀 **START HERE - Developer Quick Reference**
    - Quick access decision matrix (can MOA user do X?)
    - Code snippets cheat sheet (10 common patterns)
    - Template tags reference with examples
    - Common pitfalls and solutions
    - Performance tips and troubleshooting
  - [MOA RBAC Design](improvements/MOA_RBAC_DESIGN.md) ⭐ **Complete Architecture & Implementation Guide**
    - Comprehensive RBAC design for Ministry/Agency/Office focal users
    - Three-tier access model: View-Only, Edit-Own, No-Access
    - Database schema changes (moa_organization FK)
    - Permission decorators, mixins, and template tags
    - Defense-in-depth security (view/model/template layers)
    - 7-phase implementation plan with testing strategy
  - [MOA RBAC Implementation Status](improvements/MOA_RBAC_IMPLEMENTATION_STATUS.md) 📊 **Track Implementation Progress**
    - Phase-by-phase task tracking
    - Deployment checklist and validation steps
    - Known issues and risk mitigation
  - [MOA/OOBC Separation Analysis](improvements/MOA_OOBC_SEPARATION_ANALYSIS.md) 📋 **Requirements & Access Control Matrix**

- **Task Management System:** ⭐ **NEW - 100% COMPLETE** ✅
  - [Integrated Task Management Evaluation Plan](improvements/integrated_staff_task_management_evaluation_plan.md) - Original plan
  - [Implementation Status](improvements/TASK_MANAGEMENT_IMPLEMENTATION_STATUS.md) - Initial progress
  - [Final Status (85%)](improvements/TASK_MANAGEMENT_FINAL_STATUS.md) - Backend complete
  - [Frontend Completion](improvements/TASK_MANAGEMENT_FRONTEND_COMPLETION.md) - UI implementation
  - [Complete Summary](improvements/TASK_MANAGEMENT_COMPLETE_SUMMARY.md) - Full documentation
  - [Final Verification](improvements/FINAL_VERIFICATION_REPORT.md) - ✅ **100% Verified**

- **MANA Program:**
  - [MANA Improvements Overview](improvements/mana/README.md)
  - [Regional MANA Implementation Status](improvements/regional_mana_implementation_status.md)
  - [Regional MANA Workshop Implementation Summary](improvements/regional_mana_workshop_implementation_summary.md)
  - [Regional MANA Workshop Redesign Plan](improvements/regional_mana_workshop_redesign_plan.md)
  - [Facilitator Controlled Advancement](improvements/mana/facilitator_controlled_advancement.md)
  - [Facilitator User Guide](improvements/mana/facilitator_user_guide.md)
  - [Form Design Standards](improvements/mana/form_design_standards.md)
  - [Implementation Progress](improvements/mana/implementation_progress.md)
  - [Integrated Workflow Plan](improvements/mana/integrated_workflow_plan.md)
  - [Integration Test Scenarios](improvements/mana/integration_test_scenarios.md)

### 📊 Reports & Research
- [OBC Upgrade Proposal](reports/OBC-upgrade.md)
- [OBC Briefing Deck](reports/OBC_briefer.md)
- [OBC Data Overview](reports/OBCdata.md)
- [OOBC Integrative Report](reports/OOBC_integrative_report.md)
- [System Requirements](reports/obc-system-requirements.md)
- [Staff Task Board Research](reports/staff_task_board_research.md)
- [Fast Tree UI Patterns](research/FAST_TREE_UI_PATTERNS.md) ⭐ **NEW - Performance Best Practices**
- [Tree DOM Ordering Best Practices](research/TREE_DOM_ORDERING.md) ⭐ **NEW - Hierarchical Tree Implementation**
- [Tree DOM Ordering Visual Guide](research/TREE_DOM_ORDERING_VISUAL.md) 🎨 **Visual Reference for Tree Tables**
- [Tree Table Bug Fix Guide](research/TREE_BUG_FIX_GUIDE.md) 🔧 **Quick Fix for DOM Ordering Issues**

### 🤖 AI Strategy & Integration ⭐ **PRODUCTION READY - Complete AI Ecosystem**

**STATUS: ✅ ALL PHASES COMPLETE** - 119 files, 59,367 lines of production code, 197 comprehensive tests

- **Quick Start Guides:**
  - [AI User Guide](USER_GUIDE_AI_FEATURES.md) 🎯 **START HERE - User-Focused AI Feature Guide**
    - Overview of all AI capabilities by module
    - How to access AI features in the UI
    - Best practices and usage examples
    - Troubleshooting and FAQ
  - [AI Quick Start (Developer)](ai/AI_QUICK_START.md) ⚡ **Get Started in 30 Minutes**
    - 5-minute AI integration tutorial
    - Common AI tasks with code examples
    - Cultural context integration
    - Cost optimization and caching

- **Strategic Documentation:**
  - [AI Strategy Comprehensive](ai/AI_STRATEGY_COMPREHENSIVE.md) ⭐ **Complete AI Integration Strategy** (135+ pages)
    - **Executive Summary**: Vision for AI-enhanced OBCMS (first AI government platform for Bangsamoro)
    - **Module-Specific Plans**: AI implementation for all 8 modules (Communities, MANA, Coordination, Policy, M&E, etc.)
    - **Cross-Module Features**: Semantic search, intelligent insights, conversational AI, automated evidence synthesis
    - **Technical Architecture**: Google Gemini 2.5 Flash, Vector DB (FAISS), ML pipelines, Redis caching
    - **Implementation Roadmap**: 4-phase plan (Foundation → Intelligence → Analytics → Conversational AI)
    - **Use Cases**: 5 detailed before/after scenarios with time savings
    - **Responsible AI**: Cultural sensitivity framework, bias mitigation, privacy safeguards
    - **ROI Analysis**: 2,857% return, $5.4M annual value, 12-day payback period

- **Module-Specific AI Documentation:**
  - [Communities AI Implementation Complete](improvements/COMMUNITIES_AI_IMPLEMENTATION_COMPLETE.md) ✅ **AI Data Validation, Needs Classifier, Community Matching**
  - [MANA AI Intelligence Implementation](improvements/MANA_AI_INTELLIGENCE_IMPLEMENTATION.md) ✅ **Response Analysis, Theme Extraction, Report Generation**
  - [MANA AI Quick Reference](improvements/MANA_AI_QUICK_REFERENCE.md) 🚀 **Fast Reference for MANA AI**
  - [Coordination AI Implementation](improvements/COORDINATION_AI_IMPLEMENTATION.md) ✅ **Stakeholder Matching, Partnership Prediction, Meeting Intelligence**
  - [Policy AI Enhancement](improvements/POLICY_AI_ENHANCEMENT.md) ✅ **Evidence Gathering, Policy Generation, Impact Simulation**
  - [Policy AI Quick Reference](improvements/POLICY_AI_QUICK_REFERENCE.md) 🚀 **Fast Reference for Policy AI**
  - [M&E AI Implementation](improvements/ME_AI_IMPLEMENTATION.md) ✅ **Anomaly Detection, Performance Forecasting, Risk Analysis**
  - [Unified Search Implementation](improvements/UNIFIED_SEARCH_IMPLEMENTATION.md) ✅ **Semantic Search Across All Modules**
  - [Conversational AI Implementation](improvements/CONVERSATIONAL_AI_IMPLEMENTATION.md) ✅ **Natural Language Chat Interface**

- **Implementation Tracking:**
  - [AI Implementation Complete Summary](../AI_IMPLEMENTATION_COMPLETE_SUMMARY.md) 📊 **Production Status & Metrics**
    - 119 total files created (59 Phase 1 + 60 Phases 2-4)
    - 59,367 lines of production code
    - 197 comprehensive tests (79 Phase 1 + 106 Phases 2-4)
    - 31,140+ lines of documentation
    - Cost analysis: $80-180/month, 2,857% ROI
  - [AI Implementation Checklist](ai/AI_IMPLEMENTATION_CHECKLIST.md) 📋 **Track Your Progress**
    - Phase-by-phase task checklist (Foundation, Intelligence, Analytics, Conversational AI)
    - Infrastructure setup tasks (API config, vector DB, monitoring)
    - Module-specific implementation tasks
    - Cultural sensitivity and ethics checklist
    - Security and privacy requirements
    - Success metrics dashboard

- **Deployment & Operations:**
  - [AI Deployment Guide](deployment/AI_DEPLOYMENT_GUIDE.md) 🚀 **Production Deployment Steps**
  - [Communities AI Setup Guide](improvements/COMMUNITIES_AI_SETUP_GUIDE.md) ⚙️ **Communities Module Setup**
  - **Chat System Troubleshooting:** 🔧 **NEW - Complete Operational Guide**
    - [Chat System Status](ai/chat/STATUS.md) ⭐ **CHECK HERE FIRST** (✅ UI Working, ✅ CSRF Fixed, ⚠️ API Quota)
    - [Troubleshooting Guide](ai/chat/TROUBLESHOOTING_GUIDE.md) 📖 **Detailed Solutions & Implementation**
    - [Chat Documentation](ai/chat/README.md) 📚 **Quick Reference & Testing**

### 🎨 UI & Experience

- **AI Chat Widget Debugging:** 🐛 **NEW - Complete Debug Suite**
  - [AI Chat Debug Summary](ui/AI_CHAT_DEBUG_SUMMARY.md) ⭐ **START HERE - Complete Overview**
  - [AI Chat Positioning Debug Guide](ui/AI_CHAT_POSITIONING_DEBUG_GUIDE.md) 📖 **Comprehensive Troubleshooting**
  - [AI Chat Quick Fix Reference](ui/AI_CHAT_QUICK_FIX_REFERENCE.md) 🔧 **Copy-Paste Solutions**
  - [AI Chat Positioning Diagrams](ui/AI_CHAT_POSITIONING_DIAGRAMS.md) 📐 **Visual Architecture**
  - **Debug Scripts:**
    - [Console Debugger](testing/ai_chat_console_debugger.js) - Full diagnostic tool
    - [Visual Debugger](testing/ai_chat_visual_debugger.js) - Visual overlay tool

- **Dashboard Consistency:** ⭐ **NEW - Standardization Initiative**
  - [Consistent Dashboard Implementation Plan](improvements/UI/CONSISTENT_DASHBOARD_IMPLEMENTATION_PLAN.md) - 7-module standardization
  - [Hero Section Specifications](improvements/UI/HERO_SECTION_SPECIFICATIONS.md) - Module-specific designs
  - [Color Scheme Implementation Plan](improvements/UI/COLOR_SCHEME_IMPLEMENTATION_PLAN.md) ⭐ **NEW - Primary & Module Colors**
  - [Dashboard Hero Implementation Summary](improvements/UI/DASHBOARD_HERO_IMPLEMENTATION_SUMMARY.md) - Phase 1 complete
  - [UI Refinements Complete](improvements/UI/UI_REFINEMENTS_COMPLETE.md) ✅ **NEW - Production Ready**
  - [OBCMS UI Structure Analysis](improvements/UI/OBCMS_UI_STRUCTURE_ANALYSIS.md) - Audit results
  - [Quick Actions Template](improvements/ui/QUICK_ACTIONS_TEMPLATE.md) ⭐ **NEW - Flex-based Bottom Alignment**

- **Stat Card Design System:** ⭐ **NEW - Official Standard**
  - [Stat Card Template](improvements/ui/STATCARD_TEMPLATE.md) ⭐ **NEW - 3D Milk White Design (Official)**
  - [Stat Card Auto-Refresh Guide](improvements/ui/STATCARD_AUTO_REFRESH_GUIDE.md) ⚡ **NEW - Live Updates with HTMX**
  - [Stat Card Implementation Tracker](improvements/ui/STATCARD_IMPLEMENTATION_TRACKER.md) 🚧 **In Progress (3/15 Complete)**
  - [Stat Card Implementation Progress](improvements/ui/STATCARD_IMPLEMENTATION_PROGRESS.md) 📊 **20% Complete**

- **Calendar Architecture & Fixes:** 🆕 **NEW - Clean Architecture for FullCalendar v6**
  - [Calendar Architecture Clean](improvements/UI/CALENDAR_ARCHITECTURE_CLEAN.md) ⭐ **START HERE - Complete Architecture Guide**
  - [Calendar Architecture Diagrams](improvements/UI/CALENDAR_ARCHITECTURE_DIAGRAMS.md) 📊 **Visual Layout Diagrams**
  - [Calendar Fix Implementation Steps](improvements/UI/CALENDAR_FIX_IMPLEMENTATION_STEPS.md) 🚀 **Step-by-Step Implementation**
  - [Calendar Event Filtering and Icons Fix](improvements/UI/CALENDAR_EVENT_FILTERING_AND_ICONS_FIX.md) ✅ **NEW - Event Filtering & Icons Working**
  - [Calendar Overflow Strategy](improvements/UI/CALENDAR_EVENT_OVERFLOW_STRATEGY.md) ⭐ **Google Calendar Pattern**
  - [Implementation Code](improvements/UI/CALENDAR_OVERFLOW_IMPLEMENTATION_CODE.md) ✅ **Ready-to-Use Code Snippets**
  - [UX Flow Diagram](improvements/UI/CALENDAR_OVERFLOW_UX_FLOW.md) 📊 **Visual UX Guide**
  - [Visual Comparison](improvements/UI/CALENDAR_OVERFLOW_VISUAL_COMPARISON.md) 📸 **Before/After Analysis**
  - [Quick Reference](improvements/UI/CALENDAR_OVERFLOW_QUICK_REFERENCE.md) 🚀 **One-Page Setup Guide**
  - [Advanced Modern Calendar Fix](improvements/UI/CALENDAR_ADVANCED_MODERN_FIX.md) ✅ **NEW - Full-Height Layout Fix**
  - [Advanced Calendar Before/After](improvements/UI/CALENDAR_ADVANCED_BEFORE_AFTER.md) 📸 **NEW - Visual Comparison**
  - [Full-Screen Calendar Pattern](ui/FULL_SCREEN_CALENDAR_PATTERN.md) 📋 **NEW - Reusable Pattern Guide**

- **Calendar Sidebar & Inline Editing:** ✅ **Production Ready**
  - [Work Item Sidebar Implementation Complete](improvements/UI/WORK_ITEM_SIDEBAR_IMPLEMENTATION_COMPLETE.md) ✅ **NEW - Detail View in Sidebar**

- **Delete Confirmation Best Practices:** 📚 **NEW - Complete Reference Guide**
  - [Delete Confirmation Best Practices](ui/DELETE_CONFIRMATION_BEST_PRACTICES.md) ⭐ **Complete Django + HTMX + Tailwind Guide**
    - Modal UI/UX patterns and design principles
    - HTMX implementation strategies (server-rendered, dialog element, hx-confirm)
    - Delete button anti-patterns and solutions
    - Instant UI updates and optimistic deletion
    - Tree view updates and cascading deletes
    - Complete working examples with code
    - Accessibility considerations (WCAG 2.1 AA)
    - Comprehensive testing checklist
  - [Delete Confirmation Quick Reference](ui/DELETE_CONFIRMATION_QUICK_REFERENCE.md) 🚀 **One-Page Cheat Sheet**
  - [Delete Confirmation Visual Examples](ui/DELETE_CONFIRMATION_VISUAL_EXAMPLES.md) 📸 **Before/After Mockups**
  - [Calendar Sidebar Detail Quick Reference](ui/CALENDAR_SIDEBAR_DETAIL_QUICK_REFERENCE.md) 🚀 **NEW - Developer Guide**
  - [Calendar Inline Editing Implementation](improvements/UI/CALENDAR_INLINE_EDITING_IMPLEMENTATION.md) ✅ **Full Inline Edit Feature**
  - [Calendar Inline Editing Quick Reference](improvements/UI/CALENDAR_INLINE_EDITING_QUICK_REFERENCE.md) 🚀 **Developer Quick Start**
  - [Calendar Inline Editing Summary](improvements/UI/CALENDAR_INLINE_EDITING_SUMMARY.md) 📋 **Feature Overview**

- **Admin Panel:**
  - [Admin Panel UI Evaluation](ui/admin_panel_ui_evaluation.md) ⭐ **NEW - Comprehensive Analysis**
  - [Admin Panel UI Improvement Plan](ui/admin_panel_ui_improvement_plan.md) ⭐ **NEW - Implementation Roadmap**
  - [Admin Interface Guide](ui/admin-interface-guide.md)
  - [Critical UI Fixes Implementation Complete](ui/critical_ui_fixes_implementation_complete.md) ✅ **NEW - Bug Fixes & Accessibility**
  - [Comprehensive UI/UX Evaluation](ui/comprehensive_ui_ux_evaluation.md) ⭐ **NEW - Full System Analysis**

- **Color System & Design:**
  - [OBCMS Color System](ui/obcms_color_system.md) ⭐ **NEW - Official Color Palette** (WCAG AA Compliant)
  - [Color Migration Guide](ui/color_migration_guide.md) ⭐ **NEW - Purple to Ocean/Emerald/Gold**

- **Design Resources:**
  - [Component Library](ui/component-library.md)
  - [UI Design System](ui/ui-design-system.md)
  - [UI Documentation](ui/ui-documentation.md)

---

## System Architecture

The OBC Management System is built using modern web technologies:

- **Backend**: Django 4.2+ (Python web framework)
- **Database**: PostgreSQL (with SQLite for development)
- **Frontend**: HTML5, CSS3, Tailwind CSS, JavaScript with HTMX
- **API**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens) + Django Session Auth
- **Background Tasks**: Celery with Redis
- **Deployment**: Docker, Nginx, Gunicorn
- **Reverse Proxy**: Traefik (Coolify) / Nginx

---

## Core Modules

### 1. Community Management
- OBC community profiles and demographics
- Geographic information and administrative hierarchy
- Community stakeholder management
- Livelihood and infrastructure tracking

**AI Features:**
- AI data validation (population consistency, ethnolinguistic verification)
- Needs classifier (12 categories with confidence scores)
- Community similarity matching for benchmarking
- Predicted needs visualization
- Automated data anomaly detection

### 2. MANA (Mapping and Needs Assessment)
- **Two-System Architecture:**
  - **Regional MANA:** Workshop-based participant assessments
  - **Provincial MANA:** Provincial-level community mapping
- Comprehensive needs assessment tools
- Community mapping and visualization
- Baseline studies and data collection
- Survey management and analysis

**AI Features:**
- Response analysis (theme extraction, sentiment analysis)
- Automated needs extraction (10 categories)
- Auto-report generation (executive summaries, findings)
- Cultural validation (Bangsamoro appropriateness checking)
- Meeting intelligence (summarization, action items)

### 3. Coordination and Collaboration
- Multi-stakeholder engagement tracking
- Meeting and event management
- Partnership and MOA/MOU management
- BARMM Ministries & Agencies coordination
- Communication and coordination tools

**AI Features:**
- Stakeholder matching (multi-criteria similarity)
- Partnership success prediction (ML-based scoring)
- Meeting summarization (key points, action items)
- Auto-task creation from meeting transcripts
- Resource optimization recommendations

### 4. Policy Tracking & Recommendations
- Policy recommendation lifecycle management
- Evidence-based policy development
- Impact assessment and monitoring
- Document management and version control

**AI Features:**
- Cross-module evidence gathering (31+ citations)
- AI policy generation (culturally appropriate)
- Impact simulation (4 scenarios: optimistic, realistic, pessimistic, community-led)
- BARMM compliance checking
- Evidence synthesis and summarization

### 5. M&E (Monitoring & Evaluation / Project Management)
- Programs, Projects, and Activities (PPA) management
- Budget planning and approval workflows
- Performance monitoring and reporting
- Alert and notification system

**AI Features:**
- Budget anomaly detection (95%+ accuracy)
- Timeline delay prediction
- Automated M&E reporting
- Performance forecasting (70-75% accuracy)
- Risk analysis and early warning

### 6. Data Management
- Data import and export tools
- Field mapping and validation
- Backup and recovery procedures
- Data quality management

**AI Features:**
- Semantic search across all modules
- Natural language query interface
- AI-powered search summaries
- Intelligent result ranking

### 7. Staff Management
- User account management and approvals
- Role-based access control (RBAC)
- Staff profiles and organizational structure
- Task management and coordination

**AI Features:**
- Conversational AI chat interface
- Natural language data queries
- Multi-turn conversation tracking
- Intent classification and auto-suggestions

---

## Quick Start Guides

### For Developers
1. Read [Development Environment Setup](env/development.md)
2. Configure [Claude AI Integration](development/CLAUDE.md)
3. Review [Improvement Plan Template](improvements/improvement_plan_template.md)

### For Deployment Engineers
1. **Start Here:** [Production Deployment Issues & Resolution](deployment/production-deployment-issues-resolution.md)
2. Review [Critical Blockers Fixed](deployment/CRITICAL_BLOCKERS_FIXED.md)
3. Follow [Deployment Implementation Status](deployment/DEPLOYMENT_IMPLEMENTATION_STATUS.md)
4. Choose platform:
   - Coolify: [Coolify Deployment Checklist](deployment/deployment-coolify.md)
   - Docker: [Docker Guide](deployment/docker-guide.md)

### For MANA Facilitators
1. Read [Facilitator Training Guide](guidelines/facilitator_training_guide.md)
2. Understand [Facilitator User Guide](improvements/mana/facilitator_user_guide.md)
3. Review [Regional MANA Workshop Redesign Plan](improvements/regional_mana_workshop_redesign_plan.md)

### For MANA Participants
1. Read [Participant User Guide](guidelines/participant_user_guide.md)
2. Follow workshop instructions provided by your facilitator

### For System Administrators
1. Review [Installation Guide](admin-guide/installation.md)
2. Configure [Production Environment](env/production.md)
3. Set up [PostgreSQL Migration](deployment/postgres-migration-guide.md)

### For QA Engineers & Testers
1. Read [Testing Strategy](testing/TESTING_STRATEGY.md) - Start here for comprehensive testing guidance
2. Set up test environment: [Testing Environment](env/testing.md)
3. Run tests: See [Testing README](testing/README.md) for quick commands
4. Review test reports: [Full Suite Test Report](testing/FULL_SUITE_TEST_REPORT.md)

---

## Documentation Organization

```
docs/
├── README.md                      # This file
├── admin-guide/                   # Administrator operations
├── ai/                           # AI strategy & implementation (NEW)
├── deployment/                    # Deployment & infrastructure guides
├── development/                   # Development tools & AI configuration
├── env/                          # Environment-specific configuration
├── guidelines/                   # Program implementation guidelines
├── improvements/                 # Implementation & improvement tracking
│   └── mana/                    # MANA-specific improvements
├── product/                      # Product roadmap & strategy
├── reference/                    # Technical reference documentation
├── reports/                      # Research reports & analysis
├── research/                     # Technical research & best practices
├── testing/                      # Testing guides & verification
└── ui/                          # UI/UX design documentation
```

---

## Support

For technical support or questions:

- **Email**: support@oobc.barmm.gov.ph
- **Phone**: +63 (64) 421-1977
- **Address**: OOBC Building, Cotabato City, Maguindanao del Norte

## Version Information

- **Current Version**: 1.0.0
- **Release Date**: 2024-2025
- **License**: Government of the Philippines
- **Maintained by**: Office for Other Bangsamoro Communities (OOBC)

## Quick Links

- [Main README](../README.md) - Project overview
- System Status: https://status.obc.barmm.gov.ph
- API Documentation: https://api.obc.barmm.gov.ph/docs

---

**Last Updated:** October 2025
**Documentation Status:** Complete and organized
