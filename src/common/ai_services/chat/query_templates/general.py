"""
General System & Help Query Templates for OBCMS Chat System

15+ template variations for system queries, help, navigation, and metadata:
- Help & documentation queries (how to, guides, tutorials)
- System queries (status, updates, announcements)
- Navigation queries (go to, open module, find page)
- Metadata queries (created by, modified date, audit trail)
"""

from typing import Any, Dict
from common.ai_services.chat.query_templates.base import QueryTemplate


# =============================================================================
# HELP & DOCUMENTATION TEMPLATES (5 templates)
# =============================================================================

HELP_DOCUMENTATION_TEMPLATES = [
    QueryTemplate(
        id='help_general',
        category='general',
        pattern=r'\b(help|assist|guide|how do i)\b',
        query_template='help_content',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Help',
            'I need help',
            'Assist me',
            'How do I use this?',
            'User guide'
        ],
        priority=8,
        description='General help request',
        tags=['help', 'documentation']
    ),
    QueryTemplate(
        id='help_how_to_create',
        category='general',
        pattern=r'\b(how to|how do i|help me)\s+(create|add|make|new)\s+(?P<entity>[\w\s]+)\b',
        query_template='help_create_{entity}',
        required_entities=['entity'],
        optional_entities=[],
        examples=[
            'How to create assessment',
            'How do I add community',
            'Help me create project',
            'How to add new task',
            'How do I make a report?'
        ],
        priority=9,
        description='Help with creating entities',
        tags=['help', 'create', 'tutorial']
    ),
    QueryTemplate(
        id='help_how_to_edit',
        category='general',
        pattern=r'\b(how to|how do i|help me)\s+(edit|update|modify|change)\s+(?P<entity>[\w\s]+)\b',
        query_template='help_edit_{entity}',
        required_entities=['entity'],
        optional_entities=[],
        examples=[
            'How to edit assessment',
            'How do I update community',
            'Help me modify project',
            'How to change task status',
            'How do I update profile?'
        ],
        priority=9,
        description='Help with editing entities',
        tags=['help', 'edit', 'tutorial']
    ),
    QueryTemplate(
        id='help_documentation_link',
        category='general',
        pattern=r'\b(documentation|docs|manual|user\s+manual|guide|tutorial|show\s+docs)\b',
        query_template='get_documentation({module})',
        required_entities=[],
        optional_entities=['module'],
        examples=[
            'Documentation',
            'User manual',
            'Guide for communities',
            'Tutorial for MANA',
            'Show docs'
        ],
        priority=7,
        description='Access documentation',
        tags=['help', 'documentation', 'link']
    ),
    QueryTemplate(
        id='help_faq',
        category='general',
        pattern=r'\b(faq|frequently asked|common questions)\b',
        query_template='get_faq_list()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'FAQ',
            'Frequently asked questions',
            'Common questions',
            'Show FAQ',
            'Help FAQ'
        ],
        priority=7,
        description='Show FAQ list',
        tags=['help', 'faq', 'documentation']
    ),
]


# =============================================================================
# SYSTEM STATUS TEMPLATES (4 templates)
# =============================================================================

SYSTEM_STATUS_TEMPLATES = [
    QueryTemplate(
        id='system_status',
        category='general',
        pattern=r'\b(system|server|application)\s+(status|health|state)\b|\bis\s+system\s+running\b',
        query_template='get_system_status()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'System status',
            'Server status',
            'Application health',
            'Is system running?',
            'Check system state'
        ],
        priority=8,
        description='Check system status',
        tags=['system', 'status', 'health']
    ),
    QueryTemplate(
        id='system_updates',
        category='general',
        pattern=r'\b(recent|latest|new)\s+(updates|changes|features|releases)\b|\bwhat\s+changed\s+recently\b',
        query_template='SystemUpdate.objects.filter(published=True).order_by("-created_at")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Recent updates',
            'Latest changes',
            'New features',
            'Latest releases',
            'What changed recently?'
        ],
        priority=7,
        description='Show recent system updates',
        tags=['system', 'updates', 'changelog']
    ),
    QueryTemplate(
        id='system_announcements',
        category='general',
        pattern=r'\b(announcements|news|notices)\b',
        query_template='Announcement.objects.filter(published=True, expiry_date__gte=timezone.now()).order_by("-priority", "-created_at")[:10]',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Announcements',
            'System news',
            'Notices',
            'Show announcements',
            'Recent notices'
        ],
        priority=7,
        description='Show active announcements',
        tags=['system', 'announcements', 'news']
    ),
    QueryTemplate(
        id='system_version',
        category='general',
        pattern=r'\b(version|build\s+number|release\s+info|what\s+version|system\s+version)\b',
        query_template='get_system_version()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Version',
            'Build number',
            'Release info',
            'What version?',
            'System version'
        ],
        priority=6,
        description='Show system version',
        tags=['system', 'version', 'info']
    ),
]


# =============================================================================
# NAVIGATION TEMPLATES (3 templates)
# =============================================================================

NAVIGATION_TEMPLATES = [
    QueryTemplate(
        id='navigation_go_to_module',
        category='general',
        pattern=r'\b(go to|open|navigate to|take me to)\s+(?P<module>[\w\s]+)\b',
        query_template='get_module_url("{module}")',
        required_entities=['module'],
        optional_entities=[],
        examples=[
            'Go to dashboard',
            'Open communities',
            'Navigate to MANA',
            'Take me to projects',
            'Go to coordination'
        ],
        priority=9,
        description='Navigate to module',
        tags=['navigation', 'module', 'redirect']
    ),
    QueryTemplate(
        id='navigation_dashboard',
        category='general',
        pattern=r'\b(home|dashboard|main page)\b',
        query_template='redirect_to_dashboard()',
        required_entities=[],
        optional_entities=[],
        examples=[
            'Home',
            'Dashboard',
            'Main page',
            'Go home',
            'Take me to dashboard'
        ],
        priority=8,
        description='Go to dashboard',
        tags=['navigation', 'dashboard', 'home']
    ),
    QueryTemplate(
        id='navigation_find_page',
        category='general',
        pattern=r'\b(find|search|where is)\s+(page|section|module)\s+(?P<keyword>[\w\s]+)\b',
        query_template='search_pages("{keyword}")',
        required_entities=['keyword'],
        optional_entities=[],
        examples=[
            'Find page reports',
            'Search section analytics',
            'Where is module settings?',
            'Find reports page',
            'Search for communities section'
        ],
        priority=8,
        description='Search for pages',
        tags=['navigation', 'search', 'pages']
    ),
]


# =============================================================================
# METADATA TEMPLATES (3 templates)
# =============================================================================

METADATA_TEMPLATES = [
    QueryTemplate(
        id='metadata_created_by',
        category='general',
        pattern=r'\bwho created\s+(?P<entity>[\w\s]+)\b',
        query_template='get_creator_info("{entity}")',
        required_entities=['entity'],
        optional_entities=[],
        examples=[
            'Who created this assessment?',
            'Who created community profile?',
            'Who created this project?',
            'Who created this task?'
        ],
        priority=7,
        description='Show entity creator',
        tags=['metadata', 'creator', 'audit']
    ),
    QueryTemplate(
        id='metadata_modified_date',
        category='general',
        pattern=r'\b(when|what time)\s+(was|were)\s+(?P<entity>[\w\s]+)\s+(modified|updated|changed|edited)\b',
        query_template='get_modification_date("{entity}")',
        required_entities=['entity'],
        optional_entities=[],
        examples=[
            'When was this modified?',
            'What time was assessment updated?',
            'When was community changed?',
            'When was project edited?'
        ],
        priority=7,
        description='Show modification date',
        tags=['metadata', 'date', 'audit']
    ),
    QueryTemplate(
        id='metadata_audit_log',
        category='general',
        pattern=r'\b(audit|history|changes|log)\s+(for|of)\s+(?P<entity>[\w\s]+)\b',
        query_template='AuditLog.objects.filter(object_repr__icontains="{entity}").select_related("user", "content_type").order_by("-timestamp")[:30]',
        required_entities=['entity'],
        optional_entities=[],
        examples=[
            'Audit log for assessment',
            'History of community',
            'Changes for project',
            'Log of this task',
            'Show history for report'
        ],
        priority=8,
        description='Show audit trail',
        tags=['metadata', 'audit', 'history']
    ),
]


# =============================================================================
# COMBINE ALL GENERAL TEMPLATES
# =============================================================================

GENERAL_TEMPLATES = (
    HELP_DOCUMENTATION_TEMPLATES +
    SYSTEM_STATUS_TEMPLATES +
    NAVIGATION_TEMPLATES +
    METADATA_TEMPLATES
)

# Total: 5 + 4 + 3 + 3 = 15 general templates with 50+ example query variations
