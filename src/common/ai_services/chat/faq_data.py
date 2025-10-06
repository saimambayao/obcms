"""
Enhanced FAQ Data Structure for OBCMS Chat System

This module provides the enhanced FAQ database with full metadata support:
- ID, category, priority
- Primary question + variants
- Response + response_type
- Source verification
- Usage analytics
- Maintenance tracking

Version: 2.0
Date: January 7, 2025
Status: Active
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.utils import timezone

# FAQ Categories with Priority Ranges
CATEGORY_PRIORITY_RANGES = {
    'system_identity': (18, 20),  # CRITICAL - New user's first questions
    'access_help': (15, 17),      # CRITICAL - Getting started, permissions
    'geography': (12, 14),        # HIGH - Location queries
    'modules': (10, 12),          # HIGH - Understanding capabilities
    'support': (8, 10),           # MEDIUM - User assistance
    'statistics': (5, 8),         # LOW - Data queries
}


class EnhancedFAQ:
    """Enhanced FAQ entry with full metadata."""

    def __init__(
        self,
        faq_id: str,
        category: str,
        priority: int,
        primary_question: str,
        variants: List[str],
        response: str,
        response_type: str = 'instant',
        source: str = None,
        source_url: str = None,
        related_queries: List[str] = None,
        examples: List[str] = None,
    ):
        self.id = faq_id
        self.category = category
        self.priority = priority
        self.primary_question = primary_question
        self.variants = variants or []
        self.response = response
        self.response_type = response_type
        self.source = source
        self.source_url = source_url
        self.related_queries = related_queries or []
        self.examples = examples or []

        # Analytics (will be populated from cache/database)
        self.usage_count = 0
        self.helpful_votes = 0
        self.unhelpful_votes = 0

        # Maintenance (lazy-loaded)
        self.status = 'active'
        self._last_verified = None  # Will be calculated on first access
        self._next_review_date = None  # Will be calculated on first access

    @property
    def last_verified(self):
        """Get last verified date (lazy-loaded)."""
        if self._last_verified is None:
            from django.utils import timezone
            self._last_verified = timezone.now().date()
        return self._last_verified

    @property
    def next_review_date(self):
        """Get next review date (lazy-loaded)."""
        if self._next_review_date is None:
            self._next_review_date = self._calculate_next_review()
        return self._next_review_date

    def _calculate_next_review(self):
        """Calculate next review date based on priority."""
        if self.priority >= 15:  # High priority
            return self.last_verified + timedelta(days=30)
        elif self.priority >= 10:  # Medium priority
            return self.last_verified + timedelta(days=90)
        else:  # Low priority
            return self.last_verified + timedelta(days=180)

    def to_dict(self):
        """Convert to dictionary format."""
        return {
            'id': self.id,
            'category': self.category,
            'priority': self.priority,
            'primary_question': self.primary_question,
            'variants': self.variants,
            'response': self.response,
            'response_type': self.response_type,
            'source': self.source,
            'source_url': self.source_url,
            'related_queries': self.related_queries,
            'examples': self.examples,
            'usage_count': self.usage_count,
            'helpful_votes': self.helpful_votes,
            'unhelpful_votes': self.unhelpful_votes,
            'status': self.status,
            'last_verified': str(self.last_verified),
            'next_review_date': str(self.next_review_date),
        }

    def get_all_patterns(self):
        """Get all matching patterns (primary + variants)."""
        return [self.primary_question.lower()] + [v.lower() for v in self.variants]


# ============================================================================
# PHASE 1: SYSTEM IDENTITY FAQs (20 FAQs, Priority 18-20)
# ============================================================================

PHASE_1_SYSTEM_IDENTITY = [
    # ========== Core Identity (Priority 20) ==========
    EnhancedFAQ(
        faq_id='faq_001_obcms_definition',
        category='system_identity',
        priority=20,
        primary_question='What is OBCMS?',
        variants=[
            "what's obcms",
            "obcms meaning",
            "define obcms",
            "obcms definition",
            "tell me about obcms",
            "explain obcms",
            "obcms",
        ],
        response=(
            "OBCMS (Office for Other Bangsamoro Communities Management System) is a "
            "comprehensive platform for managing programs, services, and data for "
            "Bangsamoro communities outside BARMM.\n\n"
            "**Key Features:**\n"
            "• Communities - OBC profiles and demographics\n"
            "• MANA - Mapping and Needs Assessment\n"
            "• Coordination - Partnerships and stakeholders\n"
            "• Policies - Policy recommendations\n"
            "• M&E - Projects, Programs, and Activities\n"
            "• Staff - Task management and calendar"
        ),
        response_type='instant',
        source='CLAUDE.md - Architecture Overview',
        source_url='CLAUDE.md#architecture-overview',
        related_queries=[
            'What is OOBC?',
            'What modules are available?',
            'How do I get started?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_002_oobc_definition',
        category='system_identity',
        priority=20,
        primary_question='What is OOBC?',
        variants=[
            "what's oobc",
            "oobc meaning",
            "oobc full form",
            "office for other bangsamoro communities",
            "oobc definition",
            "oobc",
        ],
        response=(
            "OOBC (Office for Other Bangsamoro Communities) is the government office "
            "serving Bangsamoro communities in Regions IX, X, XI, and XII outside the "
            "Bangsamoro Autonomous Region (BARMM).\n\n"
            "**Coverage Areas:**\n"
            "• Region IX - Zamboanga Peninsula\n"
            "• Region X - Northern Mindanao\n"
            "• Region XI - Davao Region\n"
            "• Region XII - SOCCSKSARGEN"
        ),
        response_type='instant',
        source='CLAUDE.md - Domain Context',
        source_url='CLAUDE.md#domain-specific-context',
        related_queries=[
            'What is OBC?',
            'What regions does OOBC serve?',
            'What is BARMM?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_003_obc_definition',
        category='system_identity',
        priority=20,
        primary_question='What is OBC?',
        variants=[
            "obc meaning",
            "obc definition",
            "other bangsamoro communities",
            "what are obcs",
            "obc",
        ],
        response=(
            "OBC (Other Bangsamoro Communities) refers to Bangsamoro communities "
            "living outside the Bangsamoro Autonomous Region in Muslim Mindanao (BARMM), "
            "primarily in Regions IX, X, XI, and XII.\n\n"
            "These communities maintain their Bangsamoro identity while residing in "
            "areas not included in the BARMM autonomous region. OOBC provides services "
            "and support to these communities."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
        related_queries=[
            'What is OOBC?',
            'What is BARMM?',
            'How many OBC communities are there?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_004_barmm_definition',
        category='system_identity',
        priority=20,
        primary_question='What is BARMM?',
        variants=[
            "barmm meaning",
            "what's barmm",
            "bangsamoro autonomous region",
            "barmm definition",
            "barmm full form",
            "barmm",
        ],
        response=(
            "BARMM (Bangsamoro Autonomous Region in Muslim Mindanao) is the autonomous "
            "region in the southern Philippines, created in 2019 to provide self-governance "
            "to Bangsamoro people.\n\n"
            "**Important:** OOBC serves Bangsamoro communities OUTSIDE BARMM in Regions IX, X, XI, and XII."
        ),
        response_type='instant',
        source='CLAUDE.md - Domain Context',
        source_url='CLAUDE.md#domain-specific-context',
        related_queries=[
            'What is OOBC?',
            'What regions does OOBC serve?',
            'Why are there OBC communities outside BARMM?',
        ],
    ),

    # ========== Module Abbreviations (Priority 19) ==========
    EnhancedFAQ(
        faq_id='faq_005_mana_definition',
        category='system_identity',
        priority=19,
        primary_question='What is MANA?',
        variants=[
            "mana meaning",
            "what's mana",
            "mana module",
            "mana definition",
            "mapping and needs assessment",
            "mana",
        ],
        response=(
            "MANA stands for Mapping and Needs Assessment.\n\n"
            "It's the OBCMS module for conducting and managing community assessments:\n"
            "• Workshop planning and scheduling\n"
            "• Community needs identification\n"
            "• Assessment data collection\n"
            "• Priority needs analysis\n"
            "• Evidence-based planning"
        ),
        response_type='instant',
        source='CLAUDE.md - Core Applications',
        source_url='CLAUDE.md#core-applications',
        related_queries=[
            'How do I create an assessment?',
            'List recent workshops',
            'What modules are available?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_006_me_definition',
        category='system_identity',
        priority=19,
        primary_question='What is M&E?',
        variants=[
            "m&e meaning",
            "me module",
            "monitoring and evaluation",
            "what is m and e",
            "m&e",
        ],
        response=(
            "M&E stands for Monitoring and Evaluation.\n\n"
            "It's the OBCMS module for tracking projects, programs, and activities (PPAs):\n"
            "• Project planning and management\n"
            "• Program implementation tracking\n"
            "• Activity monitoring\n"
            "• Performance measurement\n"
            "• Impact evaluation"
        ),
        response_type='instant',
        source='CLAUDE.md - Core Applications',
        source_url='CLAUDE.md#core-applications',
        related_queries=[
            'What are PPAs?',
            'List active projects',
            'What modules are available?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_007_ppa_definition',
        category='system_identity',
        priority=19,
        primary_question='What are PPAs?',
        variants=[
            "ppa meaning",
            "ppas",
            "projects programs activities",
            "what is ppa",
            "ppa definition",
        ],
        response=(
            "PPAs stand for Projects, Programs, and Activities.\n\n"
            "These are the initiatives managed in the M&E module:\n"
            "• **Projects** - Time-bound initiatives with specific objectives\n"
            "• **Programs** - Ongoing collections of related projects\n"
            "• **Activities** - Specific actions within projects/programs\n\n"
            "PPAs are tracked by Ministries, Offices, and Agencies (MOAs)."
        ),
        response_type='instant',
        source='CLAUDE.md - Core Applications',
        source_url='CLAUDE.md#core-applications',
        related_queries=[
            'What is M&E?',
            'List active programs',
            'What are MOAs?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_008_moa_definition',
        category='system_identity',
        priority=19,
        primary_question='What are MOAs?',
        variants=[
            "moa meaning",
            "moas",
            "ministries offices agencies",
            "what is moa",
            "moa definition",
        ],
        response=(
            "MOAs stand for Ministries, Offices, and Agencies.\n\n"
            "These are the government entities that implement programs and services:\n"
            "• **Ministries** - Government departments with specific mandates\n"
            "• **Offices** - Government units (like OOBC)\n"
            "• **Agencies** - Specialized government organizations\n\n"
            "MOAs implement PPAs (Projects, Programs, and Activities) for OBC communities."
        ),
        response_type='instant',
        source='CLAUDE.md - Domain Context',
        source_url='CLAUDE.md#domain-specific-context',
        related_queries=[
            'What are PPAs?',
            'List all ministries',
            'What is M&E?',
        ],
    ),

    # ========== Purpose & Getting Started (Priority 18) ==========
    EnhancedFAQ(
        faq_id='faq_009_system_purpose',
        category='system_identity',
        priority=18,
        primary_question='What can I do with OBCMS?',
        variants=[
            "what can obcms do",
            "obcms features",
            "obcms capabilities",
            "what is this for",
            "what does obcms do",
            "system features",
        ],
        response=(
            "OBCMS helps you manage all aspects of OBC community services:\n\n"
            "**Communities Module:**\n"
            "• Register and profile OBC communities\n"
            "• Track demographics and needs\n"
            "• Map geographic locations\n\n"
            "**MANA Module:**\n"
            "• Conduct needs assessments\n"
            "• Schedule workshops\n"
            "• Analyze community priorities\n\n"
            "**Coordination Module:**\n"
            "• Manage partnerships\n"
            "• Track stakeholder engagement\n"
            "• Coordinate multi-agency initiatives\n\n"
            "**Policies Module:**\n"
            "• Draft policy recommendations\n"
            "• Track implementation\n"
            "• Evidence-based proposals\n\n"
            "**M&E Module:**\n"
            "• Monitor projects and programs\n"
            "• Evaluate impact\n"
            "• Track MOA activities\n\n"
            "**Staff Module:**\n"
            "• Manage tasks and calendar\n"
            "• Team coordination\n"
            "• Schedule meetings"
        ),
        response_type='instant',
        source='CLAUDE.md - Architecture Overview',
        source_url='CLAUDE.md#core-applications',
        related_queries=[
            'How do I get started?',
            'Can I use this?',
            'What is MANA?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_010_getting_started',
        category='system_identity',
        priority=18,
        primary_question='How do I get started with OBCMS?',
        variants=[
            "getting started",
            "how to start",
            "how do i begin",
            "first steps",
            "quick start",
            "start using obcms",
        ],
        response=(
            "**Getting Started with OBCMS:**\n\n"
            "1. **Log In** - Use your OOBC staff credentials at the login page\n"
            "2. **Explore Dashboard** - See overview of communities, programs, and activities\n"
            "3. **Choose a Module:**\n"
            "   • Communities - View OBC profiles\n"
            "   • MANA - Conduct assessments\n"
            "   • Coordination - Manage partnerships\n"
            "   • Policies - Draft recommendations\n"
            "   • M&E - Track projects\n"
            "   • Staff - Manage tasks\n\n"
            "4. **Ask Questions** - Use this AI assistant for help anytime\n\n"
            "**Need Help?** Try asking:\n"
            "• 'Show all communities'\n"
            "• 'List recent workshops'\n"
            "• 'How many active partnerships?'"
        ),
        response_type='instant',
        source='CLAUDE.md - Development Guidelines',
        source_url='CLAUDE.md#development-guidelines',
        related_queries=[
            'How do I log in?',
            'Can I use this?',
            'What can I do with OBCMS?',
        ],
    ),

    # ========== Regional Context (Priority 18) ==========
    EnhancedFAQ(
        faq_id='faq_011_coverage_regions',
        category='system_identity',
        priority=18,
        primary_question='What regions does OOBC serve?',
        variants=[
            "which regions",
            "coverage areas",
            "oobc regions",
            "service areas",
            "geographic coverage",
            "regions covered",
        ],
        response=(
            "OOBC serves Bangsamoro communities in 4 regions:\n\n"
            "**Region IX - Zamboanga Peninsula**\n"
            "• Zamboanga del Norte\n"
            "• Zamboanga del Sur\n"
            "• Zamboanga Sibugay\n\n"
            "**Region X - Northern Mindanao**\n"
            "• Bukidnon\n"
            "• Misamis Oriental\n"
            "• Misamis Occidental\n"
            "• Camiguin\n"
            "• Lanao del Norte\n\n"
            "**Region XI - Davao Region**\n"
            "• Davao del Norte\n"
            "• Davao del Sur\n"
            "• Davao Oriental\n"
            "• Davao de Oro\n"
            "• Davao Occidental\n\n"
            "**Region XII - SOCCSKSARGEN**\n"
            "• South Cotabato\n"
            "• Cotabato (North Cotabato)\n"
            "• Sultan Kudarat\n"
            "• Sarangani\n"
            "• General Santos City"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
        related_queries=[
            'Where is Cotabato?',
            'What is SOCCSKSARGEN?',
            'How many provinces?',
        ],
    ),

    # ========== Ultra-Simple Question Handling (Priority 18) ==========
    EnhancedFAQ(
        faq_id='faq_012_help_simple',
        category='system_identity',
        priority=18,
        primary_question='Help',
        variants=[
            "help me",
            "i need help",
            "assist",
            "assistance",
            "support",
        ],
        response=(
            "**How can I help you?**\n\n"
            "Try asking:\n"
            "• **About the system:** 'What is OBCMS?', 'What modules are available?'\n"
            "• **Locations:** 'Where is Cotabato?', 'What regions are covered?'\n"
            "• **Getting started:** 'How do I log in?', 'How do I get started?'\n"
            "• **Data queries:** 'How many communities?', 'List recent workshops'\n"
            "• **Modules:** 'What is MANA?', 'Show all partnerships'\n\n"
            "You can ask questions in natural language, and I'll do my best to help!"
        ),
        response_type='instant',
        source='FAQ Expansion Plan - Simple Questions',
        source_url='docs/ai/faqs/FAQ_EXPANSION_PLAN.md#simple-questions-focus',
    ),

    EnhancedFAQ(
        faq_id='faq_013_where_simple',
        category='system_identity',
        priority=18,
        primary_question='Where?',
        variants=[
            "where",
            "location",
            "place",
        ],
        response=(
            "**Where would you like information about?**\n\n"
            "Try asking:\n"
            "• **Provinces:** 'Where is Cotabato?', 'Where is Zamboanga?'\n"
            "• **Regions:** 'What regions does OOBC serve?'\n"
            "• **Cities:** 'Where is Davao?', 'Where is General Santos?'\n"
            "• **Coverage:** 'What is SOCCSKSARGEN?', 'What is Region IX?'\n\n"
            "I can provide location information for all areas covered by OOBC!"
        ),
        response_type='instant',
        source='FAQ Expansion Plan - Simple Questions',
        source_url='docs/ai/faqs/FAQ_EXPANSION_PLAN.md#ultra-simple-question-handling',
    ),

    EnhancedFAQ(
        faq_id='faq_014_what_simple',
        category='system_identity',
        priority=18,
        primary_question='What?',
        variants=[
            "what",
            "huh",
        ],
        response=(
            "**What would you like to know?**\n\n"
            "Try asking:\n"
            "• **About the system:** 'What is OBCMS?', 'What is OOBC?'\n"
            "• **Modules:** 'What is MANA?', 'What are PPAs?'\n"
            "• **Capabilities:** 'What can I do?', 'What modules are available?'\n"
            "• **Statistics:** 'How many communities?', 'How many workshops?'\n\n"
            "I'm here to answer your questions about OBCMS!"
        ),
        response_type='instant',
        source='FAQ Expansion Plan - Simple Questions',
        source_url='docs/ai/faqs/FAQ_EXPANSION_PLAN.md#single-word--two-word-queries',
    ),

    # ========== Regional Definitions (Priority 18) ==========
    EnhancedFAQ(
        faq_id='faq_015_region_ix',
        category='system_identity',
        priority=18,
        primary_question='What is Region IX?',
        variants=[
            "region 9",
            "region ix",
            "zamboanga peninsula",
            "region nine",
        ],
        response=(
            "**Region IX - Zamboanga Peninsula**\n\n"
            "A region in the southwestern Philippines consisting of:\n"
            "• **Zamboanga del Norte**\n"
            "• **Zamboanga del Sur**\n"
            "• **Zamboanga Sibugay**\n"
            "• **Zamboanga City** (highly urbanized)\n\n"
            "OOBC serves Bangsamoro communities in this region outside BARMM."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
        related_queries=[
            'Where is Zamboanga?',
            'What regions does OOBC serve?',
            'How many provinces in Region IX?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_016_region_x',
        category='system_identity',
        priority=18,
        primary_question='What is Region X?',
        variants=[
            "region 10",
            "region x",
            "northern mindanao",
            "region ten",
        ],
        response=(
            "**Region X - Northern Mindanao**\n\n"
            "A region in northern Mindanao consisting of:\n"
            "• **Bukidnon**\n"
            "• **Lanao del Norte**\n"
            "• **Misamis Occidental**\n"
            "• **Misamis Oriental**\n"
            "• **Camiguin**\n"
            "• **Cagayan de Oro City** (highly urbanized)\n"
            "• **Iligan City** (highly urbanized)\n\n"
            "OOBC serves Bangsamoro communities in this region outside BARMM."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
        related_queries=[
            'Where is Bukidnon?',
            'What regions does OOBC serve?',
            'How many provinces in Region X?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_017_region_xi',
        category='system_identity',
        priority=18,
        primary_question='What is Region XI?',
        variants=[
            "region 11",
            "region xi",
            "davao region",
            "region eleven",
        ],
        response=(
            "**Region XI - Davao Region**\n\n"
            "A region in southeastern Mindanao consisting of:\n"
            "• **Davao del Norte**\n"
            "• **Davao del Sur**\n"
            "• **Davao Oriental**\n"
            "• **Davao de Oro** (formerly Compostela Valley)\n"
            "• **Davao Occidental**\n"
            "• **Davao City** (highly urbanized)\n\n"
            "OOBC serves Bangsamoro communities in this region outside BARMM."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
        related_queries=[
            'Where is Davao?',
            'What regions does OOBC serve?',
            'How many provinces in Region XI?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_018_region_xii',
        category='system_identity',
        priority=18,
        primary_question='What is Region XII?',
        variants=[
            "region 12",
            "region xii",
            "soccsksargen",
            "region twelve",
            "what is soccsksargen",
        ],
        response=(
            "**Region XII - SOCCSKSARGEN**\n\n"
            "SOCCSKSARGEN is an acronym that stands for:\n"
            "• **SO**uth **C**otabato\n"
            "• **C**otabato (North Cotabato)\n"
            "• **S**ultan **K**udarat\n"
            "• **SAR**angani\n"
            "• **GEN**eral Santos City\n\n"
            "This region is in south-central Mindanao. OOBC serves Bangsamoro "
            "communities in this region outside BARMM."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
        related_queries=[
            'Where is Cotabato?',
            'What regions does OOBC serve?',
            'How many provinces in Region XII?',
        ],
    ),

    # ========== Additional Core Questions (Priority 18) ==========
    EnhancedFAQ(
        faq_id='faq_019_who_uses_obcms',
        category='system_identity',
        priority=18,
        primary_question='Who uses OBCMS?',
        variants=[
            "who can use this",
            "who is this for",
            "target users",
            "intended users",
            "users of obcms",
        ],
        response=(
            "**OBCMS is used by:**\n\n"
            "**OOBC Staff:**\n"
            "• Community development officers\n"
            "• Program coordinators\n"
            "• Policy analysts\n"
            "• M&E specialists\n"
            "• Regional coordinators\n\n"
            "**Partner Organizations:**\n"
            "• MOAs (Ministries, Offices, Agencies)\n"
            "• NGOs and civil society partners\n"
            "• Local government units\n"
            "• Community organizations\n\n"
            "**Management:**\n"
            "• OOBC leadership\n"
            "• Program directors\n"
            "• Strategic planning team"
        ),
        response_type='instant',
        source='CLAUDE.md - Domain Context',
        source_url='CLAUDE.md#domain-specific-context',
        related_queries=[
            'Can I use this?',
            'How do I get access?',
            'What can I do with OBCMS?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_020_why_obcms',
        category='system_identity',
        priority=18,
        primary_question='Why was OBCMS created?',
        variants=[
            "purpose of obcms",
            "why obcms",
            "reason for obcms",
            "obcms purpose",
            "why do we need obcms",
        ],
        response=(
            "**OBCMS was created to:**\n\n"
            "**1. Centralize Data Management**\n"
            "• Unified database of OBC communities\n"
            "• Eliminate data silos and duplication\n"
            "• Evidence-based decision making\n\n"
            "**2. Improve Service Delivery**\n"
            "• Better coordination between MOAs\n"
            "• Targeted program implementation\n"
            "• Efficient resource allocation\n\n"
            "**3. Track Impact**\n"
            "• Monitor program effectiveness\n"
            "• Evaluate community development\n"
            "• Measure outcomes and impact\n\n"
            "**4. Support Strategic Planning**\n"
            "• Needs-based programming\n"
            "• Policy recommendations\n"
            "• Long-term development planning\n\n"
            "**Result:** Better services for Bangsamoro communities outside BARMM."
        ),
        response_type='instant',
        source='CLAUDE.md - OOBC Mission',
        source_url='CLAUDE.md#domain-specific-context',
        related_queries=[
            'What is OOBC?',
            'What can I do with OBCMS?',
            'Who uses OBCMS?',
        ],
    ),
]


# ============================================================================
# PHASE 2: ACCESS & HELP FAQs (15 FAQs, Priority 15-17)
# ============================================================================

PHASE_2_ACCESS_HELP = [
    # ========== Authentication & Access (Priority 17) ==========
    EnhancedFAQ(
        faq_id='faq_021_how_to_login',
        category='access_help',
        priority=17,
        primary_question='How do I log in?',
        variants=[
            "login",
            "log in",
            "sign in",
            "how to login",
            "how do i sign in",
            "logging in",
        ],
        response=(
            "**To log in to OBCMS:**\n\n"
            "1. Go to the OBCMS login page at your organization's URL\n"
            "2. Enter your **OOBC staff credentials**:\n"
            "   • Username or email address\n"
            "   • Password\n"
            "3. Click **'Log In'**\n\n"
            "**First Time Login:**\n"
            "• Use the temporary password provided by your administrator\n"
            "• You'll be prompted to change your password\n\n"
            "**Trouble logging in?** Try: 'I can't log in' or 'Forgot password'"
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
        related_queries=[
            'I can\'t log in',
            'Forgot password',
            'How do I get access?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_022_who_can_access',
        category='access_help',
        priority=17,
        primary_question='Can I use this?',
        variants=[
            "who can access",
            "can i access",
            "who can use obcms",
            "am i allowed",
            "do i have access",
            "eligibility",
        ],
        response=(
            "**OBCMS is available to:**\n\n"
            "**OOBC Staff Members:**\n"
            "• Community development officers\n"
            "• Program coordinators\n"
            "• Policy analysts\n"
            "• M&E specialists\n"
            "• Regional coordinators\n"
            "• Administrative staff\n\n"
            "**Partner Organizations (with approval):**\n"
            "• MOA representatives\n"
            "• NGO partners\n"
            "• LGU coordinators\n\n"
            "**To request access:** Contact your supervisor or IT administrator.\n\n"
            "Try: 'How do I get access?'"
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
        related_queries=[
            'How do I get access?',
            'Who uses OBCMS?',
            'How do I log in?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_023_forgot_password',
        category='access_help',
        priority=17,
        primary_question='Forgot password',
        variants=[
            "forgot password",
            "reset password",
            "password recovery",
            "can't remember password",
            "lost password",
            "recover password",
        ],
        response=(
            "**To reset your password:**\n\n"
            "1. Go to the OBCMS login page\n"
            "2. Click **'Forgot Password?'** link\n"
            "3. Enter your email address\n"
            "4. Check your email for reset instructions\n"
            "5. Click the reset link (valid for 24 hours)\n"
            "6. Create a new secure password\n\n"
            "**Didn't receive the email?**\n"
            "• Check spam/junk folder\n"
            "• Verify you used your registered email\n"
            "• Contact IT support if no email arrives\n\n"
            "**Need immediate help?** Contact your IT administrator."
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
        related_queries=[
            'How do I change my password?',
            'I can\'t log in',
            'Who do I contact for help?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_024_cant_login',
        category='access_help',
        priority=17,
        primary_question='I can\'t log in',
        variants=[
            "can't login",
            "cannot login",
            "login not working",
            "login failed",
            "login error",
            "unable to login",
        ],
        response=(
            "**Login Troubleshooting:**\n\n"
            "**1. Check Your Credentials**\n"
            "• Verify username/email is correct\n"
            "• Check if Caps Lock is on\n"
            "• Ensure no extra spaces\n\n"
            "**2. Reset Your Password**\n"
            "• Click 'Forgot Password?' on login page\n"
            "• Follow email instructions\n\n"
            "**3. Clear Browser Cache**\n"
            "• Try a different browser\n"
            "• Clear cookies and cache\n"
            "• Use incognito/private mode\n\n"
            "**4. Check Account Status**\n"
            "• Account may be inactive\n"
            "• Contact your administrator\n\n"
            "**Still having issues?** Contact IT support with:\n"
            "• Your username/email\n"
            "• Error message (if any)\n"
            "• Browser and device info"
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
        related_queries=[
            'Forgot password',
            'Who do I contact for help?',
            'How do I log in?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_025_request_access',
        category='access_help',
        priority=17,
        primary_question='How do I get access?',
        variants=[
            "request access",
            "get access",
            "need access",
            "how to get account",
            "create account",
            "sign up",
        ],
        response=(
            "**To request OBCMS access:**\n\n"
            "**For OOBC Staff:**\n"
            "1. Contact your department supervisor\n"
            "2. Fill out the access request form\n"
            "3. Specify required modules and permissions\n"
            "4. Wait for approval (usually 1-3 business days)\n"
            "5. Receive login credentials via email\n\n"
            "**For Partner Organizations:**\n"
            "1. Have your organization head send formal request to OOBC\n"
            "2. Include: Purpose, required access level, user details\n"
            "3. Complete data sharing agreement (if required)\n"
            "4. Await approval from OOBC management\n\n"
            "**Contact:** IT Administrator or your OOBC coordinator"
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
        related_queries=[
            'Can I use this?',
            'Who do I contact for help?',
            'How do I log in?',
        ],
    ),

    # ========== Help & Support (Priority 16) ==========
    EnhancedFAQ(
        faq_id='faq_026_contact_support',
        category='access_help',
        priority=16,
        primary_question='Who do I contact for help?',
        variants=[
            "contact support",
            "help desk",
            "support contact",
            "who helps",
            "technical support",
            "get help",
        ],
        response=(
            "**OBCMS Support Contacts:**\n\n"
            "**IT Support (Technical Issues):**\n"
            "• Email: [IT support email]\n"
            "• Response time: 24-48 hours\n"
            "• For: Login issues, bugs, technical errors\n\n"
            "**Module Support (How-to Questions):**\n"
            "• Email: [Module support email]\n"
            "• Response time: 1-2 business days\n"
            "• For: Module usage, data entry, workflows\n\n"
            "**System Administrator:**\n"
            "• For: Access requests, permissions, account management\n\n"
            "**Emergency Contact:**\n"
            "• Phone: [Emergency support number]\n"
            "• For: Critical system outages only\n\n"
            "**In your message, include:**\n"
            "• Your name and role\n"
            "• Detailed description of issue\n"
            "• Screenshots (if applicable)\n"
            "• Steps to reproduce problem"
        ),
        response_type='instant',
        source='CLAUDE.md - Support',
        source_url='CLAUDE.md#support',
        related_queries=[
            'How do I report a bug?',
            'How do I request a feature?',
            'Is there a user guide?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_027_report_bug',
        category='access_help',
        priority=16,
        primary_question='How do I report a bug?',
        variants=[
            "report bug",
            "bug report",
            "found a bug",
            "something is broken",
            "error report",
            "issue report",
        ],
        response=(
            "**To report a bug in OBCMS:**\n\n"
            "**1. Document the Issue**\n"
            "• What were you trying to do?\n"
            "• What happened instead?\n"
            "• When did it occur?\n\n"
            "**2. Gather Information**\n"
            "• Take screenshots showing the error\n"
            "• Note the URL where error occurred\n"
            "• Copy any error messages\n"
            "• Note your browser and version\n\n"
            "**3. Submit Report**\n"
            "• Email IT support: [IT support email]\n"
            "• Subject: 'Bug Report: [Brief description]'\n"
            "• Include all documentation from steps 1-2\n\n"
            "**4. Track Your Report**\n"
            "• You'll receive a ticket number\n"
            "• Expect response within 24-48 hours\n"
            "• Critical bugs addressed immediately\n\n"
            "**Priority Levels:**\n"
            "• **Critical** - System down, data loss\n"
            "• **High** - Feature not working, blocking work\n"
            "• **Medium** - Issue with workaround\n"
            "• **Low** - Minor inconvenience"
        ),
        response_type='instant',
        source='CLAUDE.md - Development Guidelines',
        source_url='CLAUDE.md#development-guidelines',
        related_queries=[
            'Who do I contact for help?',
            'How do I request a feature?',
            'I can\'t log in',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_028_request_feature',
        category='access_help',
        priority=16,
        primary_question='How do I request a feature?',
        variants=[
            "request feature",
            "feature request",
            "suggest feature",
            "new feature",
            "enhancement request",
            "improvement suggestion",
        ],
        response=(
            "**To request a new feature:**\n\n"
            "**1. Check if Feature Exists**\n"
            "• Review user guide\n"
            "• Ask this AI assistant\n"
            "• Check with colleagues\n\n"
            "**2. Prepare Your Request**\n"
            "• **What:** Describe the feature clearly\n"
            "• **Why:** Explain the business need\n"
            "• **Who:** Who would benefit?\n"
            "• **How:** Describe desired functionality\n\n"
            "**3. Submit Request**\n"
            "• Email: [Feature request email]\n"
            "• Subject: 'Feature Request: [Feature name]'\n"
            "• Include all details from step 2\n\n"
            "**4. Review Process**\n"
            "• Acknowledgment within 5 business days\n"
            "• Evaluation by development team\n"
            "• Priority assessment\n"
            "• Implementation timeline (if approved)\n\n"
            "**Note:** Features are prioritized based on:\n"
            "• Number of users impacted\n"
            "• Alignment with OOBC mission\n"
            "• Technical feasibility\n"
            "• Resource availability"
        ),
        response_type='instant',
        source='CLAUDE.md - Development Guidelines',
        source_url='CLAUDE.md#development-guidelines',
        related_queries=[
            'How do I report a bug?',
            'Who do I contact for help?',
            'What can I do with OBCMS?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_029_user_guide',
        category='access_help',
        priority=16,
        primary_question='Is there a user guide?',
        variants=[
            "user guide",
            "manual",
            "documentation",
            "where is the manual",
            "user manual",
            "help documentation",
        ],
        response=(
            "**OBCMS Documentation Resources:**\n\n"
            "**User Guides (by module):**\n"
            "• Communities Module Guide\n"
            "• MANA Assessment Guide\n"
            "• Coordination Module Guide\n"
            "• Policies Module Guide\n"
            "• M&E Module Guide\n"
            "• Staff Module Guide\n\n"
            "**Quick Start Guides:**\n"
            "• Getting Started with OBCMS\n"
            "• Basic Navigation\n"
            "• Common Tasks\n\n"
            "**Access Documentation:**\n"
            "1. Click **'Help'** icon in top navigation\n"
            "2. Select your module from dropdown\n"
            "3. Browse or search documentation\n\n"
            "**Need specific help?** Ask this AI assistant:\n"
            "• 'How do I create a community profile?'\n"
            "• 'How do I conduct an assessment?'\n"
            "• 'How do I add a partnership?'"
        ),
        response_type='instant',
        source='CLAUDE.md - Documentation',
        source_url='CLAUDE.md#documentation-guidelines',
        related_queries=[
            'How do I get started?',
            'Where can I find tutorials?',
            'How do I get training?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_030_get_training',
        category='access_help',
        priority=16,
        primary_question='How do I get training?',
        variants=[
            "training",
            "get training",
            "learn obcms",
            "training sessions",
            "workshops",
            "tutorials",
        ],
        response=(
            "**OBCMS Training Options:**\n\n"
            "**New User Orientation:**\n"
            "• Scheduled monthly\n"
            "• 2-hour session covering basics\n"
            "• Required for new staff\n"
            "• Contact HR to register\n\n"
            "**Module-Specific Training:**\n"
            "• Communities Module - 2 hours\n"
            "• MANA Module - 4 hours\n"
            "• Coordination Module - 2 hours\n"
            "• M&E Module - 3 hours\n"
            "• Policies Module - 2 hours\n\n"
            "**On-Demand Resources:**\n"
            "• Video tutorials (Help menu)\n"
            "• Interactive demos\n"
            "• User guide PDFs\n"
            "• This AI assistant (ask anytime!)\n\n"
            "**Request Custom Training:**\n"
            "• For teams/departments\n"
            "• Email: [Training coordinator email]\n"
            "• Include: Number of participants, preferred modules, dates\n\n"
            "**Refresher Training:**\n"
            "• Available upon request\n"
            "• Recommended quarterly"
        ),
        response_type='instant',
        source='CLAUDE.md - Training',
        source_url='CLAUDE.md#training',
        related_queries=[
            'Is there a user guide?',
            'How do I get started?',
            'Where can I find tutorials?',
        ],
    ),

    # ========== Documentation & Getting Started (Priority 15) ==========
    EnhancedFAQ(
        faq_id='faq_031_browser_support',
        category='access_help',
        priority=15,
        primary_question='What browsers are supported?',
        variants=[
            "supported browsers",
            "browser compatibility",
            "which browser",
            "best browser",
            "browser requirements",
        ],
        response=(
            "**Supported Browsers:**\n\n"
            "**Fully Supported (Recommended):**\n"
            "• **Google Chrome** - Latest version\n"
            "• **Mozilla Firefox** - Latest version\n"
            "• **Microsoft Edge** - Latest version\n"
            "• **Safari** - Version 14+ (macOS/iOS)\n\n"
            "**Minimum Requirements:**\n"
            "• Chrome 90+\n"
            "• Firefox 88+\n"
            "• Edge 90+\n"
            "• Safari 14+\n\n"
            "**Not Supported:**\n"
            "• Internet Explorer (all versions)\n"
            "• Outdated browser versions\n\n"
            "**For Best Performance:**\n"
            "• Keep browser updated\n"
            "• Enable JavaScript\n"
            "• Allow cookies\n"
            "• Minimum screen resolution: 1024x768\n\n"
            "**Mobile Browsers:**\n"
            "• Chrome (Android)\n"
            "• Safari (iOS)\n"
            "• Limited functionality on small screens"
        ),
        response_type='instant',
        source='CLAUDE.md - Technical Requirements',
        source_url='CLAUDE.md#environment-configuration',
        related_queries=[
            'Is there a mobile app?',
            'System requirements',
            'I can\'t log in',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_032_mobile_app',
        category='access_help',
        priority=15,
        primary_question='Is there a mobile app?',
        variants=[
            "mobile app",
            "mobile version",
            "phone app",
            "android app",
            "ios app",
            "app download",
        ],
        response=(
            "**OBCMS Mobile Access:**\n\n"
            "**Currently:**\n"
            "• No dedicated mobile app\n"
            "• Mobile-responsive web interface available\n"
            "• Access via mobile browser (Chrome/Safari)\n\n"
            "**Mobile Web Features:**\n"
            "• View community profiles\n"
            "• Access dashboards\n"
            "• View reports\n"
            "• Update tasks\n"
            "• Limited data entry\n\n"
            "**Best Practices for Mobile:**\n"
            "• Use landscape mode for better view\n"
            "• Stable internet connection required\n"
            "• Some features work better on desktop\n\n"
            "**Recommended for Mobile:**\n"
            "• Quick lookups\n"
            "• Status checks\n"
            "• Task updates\n"
            "• Report viewing\n\n"
            "**Not Recommended for Mobile:**\n"
            "• Complex data entry\n"
            "• Report generation\n"
            "• Bulk operations\n"
            "• Document uploads\n\n"
            "**Future Plans:**\n"
            "• Native mobile app under consideration\n"
            "• Contact management for feature requests"
        ),
        response_type='instant',
        source='CLAUDE.md - Frontend Integration',
        source_url='CLAUDE.md#frontend-integration',
        related_queries=[
            'What browsers are supported?',
            'How do I request a feature?',
            'What can I do with OBCMS?',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_033_change_password',
        category='access_help',
        priority=15,
        primary_question='How do I change my password?',
        variants=[
            "change password",
            "update password",
            "new password",
            "modify password",
            "password change",
        ],
        response=(
            "**To change your password:**\n\n"
            "**1. Access Account Settings**\n"
            "• Click your profile icon (top right)\n"
            "• Select **'Account Settings'**\n"
            "• Click **'Security'** tab\n\n"
            "**2. Change Password**\n"
            "• Click **'Change Password'**\n"
            "• Enter current password\n"
            "• Enter new password\n"
            "• Confirm new password\n"
            "• Click **'Save Changes'**\n\n"
            "**Password Requirements:**\n"
            "• Minimum 8 characters\n"
            "• At least one uppercase letter\n"
            "• At least one lowercase letter\n"
            "• At least one number\n"
            "• At least one special character (!@#$%^&*)\n\n"
            "**Password Best Practices:**\n"
            "• Don't reuse old passwords\n"
            "• Don't share your password\n"
            "• Change password every 90 days\n"
            "• Use unique password for OBCMS\n\n"
            "**Forgot current password?** Try: 'Forgot password'"
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
        related_queries=[
            'Forgot password',
            'How do I update my profile?',
            'Security settings',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_034_update_profile',
        category='access_help',
        priority=15,
        primary_question='How do I update my profile?',
        variants=[
            "update profile",
            "edit profile",
            "change profile",
            "profile settings",
            "my profile",
            "account settings",
        ],
        response=(
            "**To update your profile:**\n\n"
            "**1. Access Profile Settings**\n"
            "• Click your profile icon (top right)\n"
            "• Select **'Account Settings'** or **'My Profile'**\n\n"
            "**2. Edit Information**\n"
            "• **Basic Info:** Name, email, phone\n"
            "• **Position:** Job title, department\n"
            "• **Photo:** Upload profile picture\n"
            "• **Preferences:** Language, timezone, notifications\n\n"
            "**3. Save Changes**\n"
            "• Click **'Save'** or **'Update Profile'**\n"
            "• Confirm changes if prompted\n\n"
            "**Editable Fields:**\n"
            "✅ Display name\n"
            "✅ Contact information\n"
            "✅ Profile photo\n"
            "✅ Notification preferences\n"
            "✅ Dashboard layout\n\n"
            "**Cannot Edit (Contact Admin):**\n"
            "❌ Username\n"
            "❌ Email (primary)\n"
            "❌ User role/permissions\n"
            "❌ Department assignment"
        ),
        response_type='instant',
        source='CLAUDE.md - User Management',
        source_url='CLAUDE.md#authentication',
        related_queries=[
            'How do I change my password?',
            'Who do I contact for help?',
            'Account settings',
        ],
    ),

    EnhancedFAQ(
        faq_id='faq_035_find_tutorials',
        category='access_help',
        priority=15,
        primary_question='Where can I find tutorials?',
        variants=[
            "tutorials",
            "video tutorials",
            "how-to guides",
            "learning resources",
            "training videos",
            "walkthrough",
        ],
        response=(
            "**OBCMS Tutorial Resources:**\n\n"
            "**In-App Tutorials:**\n"
            "1. Click **'Help'** icon (top navigation)\n"
            "2. Select **'Tutorials'** tab\n"
            "3. Choose your topic:\n"
            "   • Getting Started (10 min)\n"
            "   • Module Tutorials (15-30 min each)\n"
            "   • Advanced Features (varies)\n\n"
            "**Video Library:**\n"
            "• Dashboard overview\n"
            "• Creating community profiles\n"
            "• Conducting MANA assessments\n"
            "• Managing partnerships\n"
            "• Tracking projects\n"
            "• Generating reports\n\n"
            "**Interactive Demos:**\n"
            "• Step-by-step walkthroughs\n"
            "• Practice in demo environment\n"
            "• No risk of affecting real data\n\n"
            "**Quick Tips:**\n"
            "• Hover over any icon for tooltip\n"
            "• Click '?' icon for context help\n"
            "• Check 'What's New' for feature updates\n\n"
            "**Live Training:**\n"
            "• Monthly new user sessions\n"
            "• Module-specific workshops\n"
            "Try: 'How do I get training?'"
        ),
        response_type='instant',
        source='CLAUDE.md - Documentation',
        source_url='CLAUDE.md#documentation-guidelines',
        related_queries=[
            'How do I get training?',
            'Is there a user guide?',
            'How do I get started?',
        ],
    ),
]


# ============================================================================
# PHASE 3: GEOGRAPHIC ESSENTIALS FAQs (20 FAQs, Priority 12-14)
# ============================================================================

PHASE_3_GEOGRAPHY = [
    # Note: Some provinces already have legacy FAQs, these enhance them
    # Priority 14: Major Provinces
    EnhancedFAQ(
        faq_id='faq_036_where_south_cotabato',
        category='geography',
        priority=14,
        primary_question='Where is South Cotabato?',
        variants=[
            "south cotabato location",
            "south cotabato province",
            "where is south cotabato province",
        ],
        response=(
            "**South Cotabato** is a province in **Region XII (SOCCSKSARGEN)** in south-central Mindanao.\n\n"
            "**Capital:** Koronadal City\n"
            "**Major Cities/Municipalities:** General Santos City, Polomolok, Tupi, T'boli\n"
            "**Known for:** Agriculture (pineapple, coconut), T'boli culture, Lake Sebu\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_037_where_sultan_kudarat',
        category='geography',
        priority=14,
        primary_question='Where is Sultan Kudarat?',
        variants=[
            "sultan kudarat location",
            "sultan kudarat province",
        ],
        response=(
            "**Sultan Kudarat** is a province in **Region XII (SOCCSKSARGEN)** in south-central Mindanao.\n\n"
            "**Capital:** Isulan\n"
            "**Major Municipalities:** Tacurong City, Esperanza, Lambayong\n"
            "**Named after:** Sultan Muhammad Dipatuan Kudarat\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_038_where_lanao_del_norte',
        category='geography',
        priority=14,
        primary_question='Where is Lanao del Norte?',
        variants=[
            "lanao del norte location",
            "lanao del norte province",
        ],
        response=(
            "**Lanao del Norte** is a province in **Region X (Northern Mindanao)**.\n\n"
            "**Capital:** Tubod\n"
            "**Major Cities:** Iligan City (highly urbanized)\n"
            "**Known for:** Maria Cristina Falls, industrial area\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    # Priority 13: Cities & Additional Provinces
    EnhancedFAQ(
        faq_id='faq_039_where_general_santos',
        category='geography',
        priority=13,
        primary_question='Where is General Santos?',
        variants=[
            "general santos location",
            "general santos city",
            "gensan",
        ],
        response=(
            "**General Santos City** (GenSan) is a highly urbanized city in **Region XII (SOCCSKSARGEN)**.\n\n"
            "**Region:** SOCCSKSARGEN (Region XII)\n"
            "**Known for:** Tuna capital of the Philippines, seaport\n"
            "**Economy:** Fishing industry, agriculture, commerce\n\n"
            "**OOBC Coverage:** Bangsamoro communities in the city"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_040_where_cagayan_de_oro',
        category='geography',
        priority=13,
        primary_question='Where is Cagayan de Oro?',
        variants=[
            "cagayan de oro location",
            "cagayan de oro city",
            "cdo",
        ],
        response=(
            "**Cagayan de Oro City** (CDO) is a highly urbanized city in **Region X (Northern Mindanao)**.\n\n"
            "**Region:** Northern Mindanao (Region X)\n"
            "**Capital of:** Misamis Oriental (provincial capital)\n"
            "**Known for:** White-water rafting, commerce, education hub\n\n"
            "**OOBC Coverage:** Bangsamoro communities in the city"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_041_where_iligan',
        category='geography',
        priority=13,
        primary_question='Where is Iligan?',
        variants=[
            "iligan location",
            "iligan city",
        ],
        response=(
            "**Iligan City** is a highly urbanized city in **Region X (Northern Mindanao)**.\n\n"
            "**Region:** Northern Mindanao (Region X)\n"
            "**Known for:** City of Majestic Waterfalls, industrial center\n"
            "**Economy:** Steel industry, manufacturing, power generation\n\n"
            "**OOBC Coverage:** Bangsamoro communities in the city"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_042_where_zamboanga_city',
        category='geography',
        priority=13,
        primary_question='Where is Zamboanga City?',
        variants=[
            "zamboanga city location",
            "zamboanga city",
        ],
        response=(
            "**Zamboanga City** is a highly urbanized city in **Region IX (Zamboanga Peninsula)**.\n\n"
            "**Region:** Zamboanga Peninsula (Region IX)\n"
            "**Known for:** City of Flowers, Chavacano language, Fort Pilar\n"
            "**Economy:** Fishing, trade, tourism\n\n"
            "**OOBC Coverage:** Bangsamoro communities in the city"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_043_where_sarangani',
        category='geography',
        priority=13,
        primary_question='Where is Sarangani?',
        variants=[
            "sarangani location",
            "sarangani province",
        ],
        response=(
            "**Sarangani** is a province in **Region XII (SOCCSKSARGEN)** in southern Mindanao.\n\n"
            "**Capital:** Alabel\n"
            "**Known for:** Beaches, tuna industry, marine resources\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_044_where_misamis_oriental',
        category='geography',
        priority=13,
        primary_question='Where is Misamis Oriental?',
        variants=[
            "misamis oriental location",
            "misamis oriental province",
        ],
        response=(
            "**Misamis Oriental** is a province in **Region X (Northern Mindanao)**.\n\n"
            "**Capital:** Cagayan de Oro City\n"
            "**Known for:** Commerce, agriculture\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_045_where_davao_del_sur',
        category='geography',
        priority=13,
        primary_question='Where is Davao del Sur?',
        variants=[
            "davao del sur location",
            "davao del sur province",
        ],
        response=(
            "**Davao del Sur** is a province in **Region XI (Davao Region)**.\n\n"
            "**Capital:** Digos City\n"
            "**Known for:** Agriculture, Mount Apo (highest peak in Philippines)\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    # Priority 12: Regional Statistics
    EnhancedFAQ(
        faq_id='faq_046_provinces_region_ix',
        category='geography',
        priority=12,
        primary_question='How many provinces are in Region IX?',
        variants=[
            "region 9 provinces",
            "region ix province count",
            "zamboanga peninsula provinces",
        ],
        response=(
            "**Region IX (Zamboanga Peninsula)** has **3 provinces**:\n\n"
            "1. Zamboanga del Norte\n"
            "2. Zamboanga del Sur\n"
            "3. Zamboanga Sibugay\n\n"
            "Plus **1 highly urbanized city:** Zamboanga City\n\n"
            "All are covered by OOBC for Bangsamoro community services."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_047_provinces_region_x',
        category='geography',
        priority=12,
        primary_question='How many provinces are in Region X?',
        variants=[
            "region 10 provinces",
            "region x province count",
            "northern mindanao provinces",
        ],
        response=(
            "**Region X (Northern Mindanao)** has **5 provinces**:\n\n"
            "1. Bukidnon\n"
            "2. Camiguin\n"
            "3. Lanao del Norte\n"
            "4. Misamis Occidental\n"
            "5. Misamis Oriental\n\n"
            "Plus **2 highly urbanized cities:** Cagayan de Oro and Iligan\n\n"
            "All are covered by OOBC for Bangsamoro community services."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_048_provinces_region_xi',
        category='geography',
        priority=12,
        primary_question='How many provinces are in Region XI?',
        variants=[
            "region 11 provinces",
            "region xi province count",
            "davao region provinces",
        ],
        response=(
            "**Region XI (Davao Region)** has **5 provinces**:\n\n"
            "1. Davao de Oro (formerly Compostela Valley)\n"
            "2. Davao del Norte\n"
            "3. Davao del Sur\n"
            "4. Davao Occidental\n"
            "5. Davao Oriental\n\n"
            "Plus **1 highly urbanized city:** Davao City\n\n"
            "All are covered by OOBC for Bangsamoro community services."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_049_provinces_region_xii',
        category='geography',
        priority=12,
        primary_question='How many provinces are in Region XII?',
        variants=[
            "region 12 provinces",
            "region xii province count",
            "soccsksargen provinces",
        ],
        response=(
            "**Region XII (SOCCSKSARGEN)** has **4 provinces**:\n\n"
            "1. Cotabato (North Cotabato)\n"
            "2. Sarangani\n"
            "3. South Cotabato\n"
            "4. Sultan Kudarat\n\n"
            "Plus **1 highly urbanized city:** General Santos City\n\n"
            "All are covered by OOBC for Bangsamoro community services."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_050_how_many_regions',
        category='geography',
        priority=12,
        primary_question='How many regions does OOBC cover?',
        variants=[
            "oobc regions",
            "number of regions",
            "total regions",
        ],
        response=(
            "**OOBC covers 4 regions** in Mindanao:\n\n"
            "1. **Region IX** - Zamboanga Peninsula (3 provinces)\n"
            "2. **Region X** - Northern Mindanao (5 provinces)\n"
            "3. **Region XI** - Davao Region (5 provinces)\n"
            "4. **Region XII** - SOCCSKSARGEN (4 provinces)\n\n"
            "**Total:** 4 regions, 17 provinces, multiple highly urbanized cities\n\n"
            "These regions contain Bangsamoro communities outside BARMM."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_051_largest_province',
        category='geography',
        priority=12,
        primary_question='What is the largest province in OOBC coverage?',
        variants=[
            "biggest province",
            "largest province obcms",
        ],
        response=(
            "**Bukidnon** is the largest province in OOBC coverage by land area.\n\n"
            "**Region:** X (Northern Mindanao)\n"
            "**Area:** Approximately 8,293.9 km²\n"
            "**Capital:** Malaybalay City\n"
            "**Known for:** Pineapple plantations, Del Monte, cool climate\n\n"
            "Bukidnon has significant Bangsamoro communities served by OOBC."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    # Additional geographic FAQs to reach 20 total
    EnhancedFAQ(
        faq_id='faq_052_where_misamis_occidental',
        category='geography',
        priority=13,
        primary_question='Where is Misamis Occidental?',
        variants=[
            "misamis occidental location",
            "misamis occidental province",
        ],
        response=(
            "**Misamis Occidental** is a province in **Region X (Northern Mindanao)**.\n\n"
            "**Capital:** Oroquieta City\n"
            "**Known for:** Agriculture, fishing\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_053_where_zamboanga_del_norte',
        category='geography',
        priority=13,
        primary_question='Where is Zamboanga del Norte?',
        variants=[
            "zamboanga del norte location",
            "zamboanga del norte province",
        ],
        response=(
            "**Zamboanga del Norte** is a province in **Region IX (Zamboanga Peninsula)**.\n\n"
            "**Capital:** Dipolog City\n"
            "**Known for:** Orchids, Dapitan (Rizal's exile site)\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_054_where_zamboanga_del_sur',
        category='geography',
        priority=13,
        primary_question='Where is Zamboanga del Sur?',
        variants=[
            "zamboanga del sur location",
            "zamboanga del sur province",
        ],
        response=(
            "**Zamboanga del Sur** is a province in **Region IX (Zamboanga Peninsula)**.\n\n"
            "**Capital:** Pagadian City\n"
            "**Known for:** Agriculture, mining\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_055_where_zamboanga_sibugay',
        category='geography',
        priority=13,
        primary_question='Where is Zamboanga Sibugay?',
        variants=[
            "zamboanga sibugay location",
            "zamboanga sibugay province",
        ],
        response=(
            "**Zamboanga Sibugay** is a province in **Region IX (Zamboanga Peninsula)**.\n\n"
            "**Capital:** Ipil\n"
            "**Known for:** Pearl farming, fishing\n\n"
            "**OOBC Coverage:** Bangsamoro communities in this province"
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),
]


# ============================================================================
# PHASE 4: MODULES & FEATURES FAQs (25 FAQs, Priority 10-12)
# ============================================================================

PHASE_4_MODULES = [
    # Priority 12: Core Module Operations
    EnhancedFAQ(
        faq_id='faq_056_create_community_profile',
        category='modules',
        priority=12,
        primary_question='How do I create a community profile?',
        variants=[
            "add community",
            "new community profile",
            "register community",
        ],
        response=(
            "**To create a community profile:**\n\n"
            "1. Navigate to **Communities** module\n"
            "2. Click **'Add New Community'** button\n"
            "3. Fill in required fields:\n"
            "   • Community name\n"
            "   • Region, Province, Municipality, Barangay\n"
            "   • Population data\n"
            "   • Contact information\n"
            "4. Add optional details:\n"
            "   • Demographics\n"
            "   • Needs assessment data\n"
            "   • Geographic coordinates\n"
            "5. Click **'Save'** to create profile\n\n"
            "**Required permissions:** Communities module access"
        ),
        response_type='instant',
        source='CLAUDE.md - Communities Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_057_conduct_mana_assessment',
        category='modules',
        priority=12,
        primary_question='How do I conduct a MANA assessment?',
        variants=[
            "create assessment",
            "mana workshop",
            "needs assessment",
        ],
        response=(
            "**To conduct a MANA assessment:**\n\n"
            "1. Navigate to **MANA** module\n"
            "2. Click **'New Assessment'**\n"
            "3. Select community\n"
            "4. Schedule workshop:\n"
            "   • Date and time\n"
            "   • Venue\n"
            "   • Participants\n"
            "5. During workshop:\n"
            "   • Document community needs\n"
            "   • Prioritize needs\n"
            "   • Record data\n"
            "6. Submit assessment for review\n\n"
            "**See also:** User Guide > MANA Module"
        ),
        response_type='instant',
        source='CLAUDE.md - MANA Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_058_add_partnership',
        category='modules',
        priority=12,
        primary_question='How do I add a partnership?',
        variants=[
            "create partnership",
            "new coordination",
            "add stakeholder partnership",
        ],
        response=(
            "**To add a partnership:**\n\n"
            "1. Navigate to **Coordination** module\n"
            "2. Click **'Add Partnership'**\n"
            "3. Enter partnership details:\n"
            "   • Partner organization\n"
            "   • Partnership type\n"
            "   • Start date\n"
            "   • Purpose/objectives\n"
            "4. Add stakeholders\n"
            "5. Define roles and responsibilities\n"
            "6. Click **'Save'**\n\n"
            "**Track:** Activities, meetings, outcomes"
        ),
        response_type='instant',
        source='CLAUDE.md - Coordination Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_059_create_policy_recommendation',
        category='modules',
        priority=12,
        primary_question='How do I create a policy recommendation?',
        variants=[
            "add policy",
            "draft recommendation",
            "new policy proposal",
        ],
        response=(
            "**To create a policy recommendation:**\n\n"
            "1. Navigate to **Policies** module\n"
            "2. Click **'New Recommendation'**\n"
            "3. Fill in details:\n"
            "   • Title\n"
            "   • Problem statement\n"
            "   • Proposed solution\n"
            "   • Evidence/data support\n"
            "   • Target communities\n"
            "4. Attach supporting documents\n"
            "5. Submit for review\n\n"
            "**Track:** Review status, implementation"
        ),
        response_type='instant',
        source='CLAUDE.md - Policies Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_060_add_project',
        category='modules',
        priority=12,
        primary_question='How do I add a project?',
        variants=[
            "create project",
            "new ppa",
            "add program",
        ],
        response=(
            "**To add a project:**\n\n"
            "1. Navigate to **M&E** module\n"
            "2. Click **'Add Project'**\n"
            "3. Enter project details:\n"
            "   • Project name\n"
            "   • MOA responsible\n"
            "   • Start/end dates\n"
            "   • Budget\n"
            "   • Target communities\n"
            "4. Define activities\n"
            "5. Set monitoring indicators\n"
            "6. Click **'Save'**\n\n"
            "**Track:** Progress, budget, impact"
        ),
        response_type='instant',
        source='CLAUDE.md - M&E Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_061_create_task',
        category='modules',
        priority=12,
        primary_question='How do I create a task?',
        variants=[
            "add task",
            "new task",
            "task management",
        ],
        response=(
            "**To create a task:**\n\n"
            "1. Navigate to **Staff** module\n"
            "2. Click **'New Task'**\n"
            "3. Fill in task details:\n"
            "   • Title\n"
            "   • Description\n"
            "   • Priority (Low/Medium/High)\n"
            "   • Due date\n"
            "   • Assigned to\n"
            "4. Add tags/labels\n"
            "5. Click **'Create Task'**\n\n"
            "**View:** Kanban board, List view, Calendar"
        ),
        response_type='instant',
        source='CLAUDE.md - Staff Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_062_schedule_workshop',
        category='modules',
        priority=12,
        primary_question='How do I schedule a workshop?',
        variants=[
            "create workshop",
            "mana workshop schedule",
            "plan assessment workshop",
        ],
        response=(
            "**To schedule a workshop:**\n\n"
            "1. Navigate to **MANA** > **Workshops**\n"
            "2. Click **'Schedule Workshop'**\n"
            "3. Enter details:\n"
            "   • Workshop title\n"
            "   • Community/location\n"
            "   • Date and time\n"
            "   • Venue\n"
            "   • Expected participants\n"
            "4. Add facilitators\n"
            "5. Send invitations\n"
            "6. Click **'Save'**\n\n"
            "**See:** Calendar view for all workshops"
        ),
        response_type='instant',
        source='CLAUDE.md - MANA Module',
        source_url='CLAUDE.md#core-applications',
    ),

    # Priority 11: Module Features
    EnhancedFAQ(
        faq_id='faq_063_communities_module_overview',
        category='modules',
        priority=11,
        primary_question='What is the Communities module?',
        variants=[
            "communities module features",
            "about communities module",
        ],
        response=(
            "**Communities Module** manages OBC community profiles and data.\n\n"
            "**Features:**\n"
            "• Community registration and profiling\n"
            "• Demographic data tracking\n"
            "• Geographic mapping\n"
            "• Needs assessment integration\n"
            "• Contact management\n"
            "• Document storage\n\n"
            "**Use for:** Maintaining comprehensive community database"
        ),
        response_type='instant',
        source='CLAUDE.md - Communities Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_064_coordination_module_overview',
        category='modules',
        priority=11,
        primary_question='What is the Coordination module?',
        variants=[
            "coordination module features",
            "about coordination module",
        ],
        response=(
            "**Coordination Module** manages partnerships and stakeholder engagement.\n\n"
            "**Features:**\n"
            "• Partnership tracking\n"
            "• Stakeholder database\n"
            "• Multi-agency collaboration\n"
            "• Meeting management\n"
            "• Resource booking\n"
            "• Communication logs\n\n"
            "**Use for:** Coordinating with MOAs, NGOs, LGUs"
        ),
        response_type='instant',
        source='CLAUDE.md - Coordination Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_065_policies_module_overview',
        category='modules',
        priority=11,
        primary_question='What is the Policies module?',
        variants=[
            "policies module features",
            "about policies module",
        ],
        response=(
            "**Policies Module** manages policy recommendations and advocacy.\n\n"
            "**Features:**\n"
            "• Policy recommendation drafting\n"
            "• Evidence-based proposals\n"
            "• Review and approval workflow\n"
            "• Implementation tracking\n"
            "• Impact assessment\n"
            "• Document management\n\n"
            "**Use for:** Evidence-based policy advocacy"
        ),
        response_type='instant',
        source='CLAUDE.md - Policies Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_066_export_data',
        category='modules',
        priority=11,
        primary_question='How do I export data?',
        variants=[
            "download data",
            "export to excel",
            "export csv",
        ],
        response=(
            "**To export data:**\n\n"
            "1. Navigate to desired module\n"
            "2. Apply any filters\n"
            "3. Click **'Export'** button\n"
            "4. Choose format:\n"
            "   • Excel (.xlsx)\n"
            "   • CSV (.csv)\n"
            "   • PDF (reports)\n"
            "5. Select fields to include\n"
            "6. Click **'Download'**\n\n"
            "**Available in:** All major modules"
        ),
        response_type='instant',
        source='CLAUDE.md - Data Management',
        source_url='CLAUDE.md#development-guidelines',
    ),

    EnhancedFAQ(
        faq_id='faq_067_search_communities',
        category='modules',
        priority=11,
        primary_question='How do I search for communities?',
        variants=[
            "find community",
            "community search",
            "lookup community",
        ],
        response=(
            "**To search for communities:**\n\n"
            "1. Navigate to **Communities** module\n"
            "2. Use search bar at top\n"
            "3. Search by:\n"
            "   • Community name\n"
            "   • Location (region/province/municipality)\n"
            "   • Barangay\n"
            "4. Apply filters:\n"
            "   • Region\n"
            "   • Population size\n"
            "   • Assessment status\n"
            "5. View results\n\n"
            "**Tip:** Use advanced filters for precise results"
        ),
        response_type='instant',
        source='CLAUDE.md - Communities Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_068_filter_results',
        category='modules',
        priority=11,
        primary_question='How do I filter results?',
        variants=[
            "apply filters",
            "narrow down results",
            "filter data",
        ],
        response=(
            "**To filter results:**\n\n"
            "1. Look for **'Filters'** button/panel\n"
            "2. Select filter criteria:\n"
            "   • Date range\n"
            "   • Status\n"
            "   • Location\n"
            "   • Type/category\n"
            "3. Apply filters\n"
            "4. View filtered results\n"
            "5. Clear filters to reset\n\n"
            "**Available in:** All list views"
        ),
        response_type='instant',
        source='CLAUDE.md - User Interface',
        source_url='CLAUDE.md#development-guidelines',
    ),

    EnhancedFAQ(
        faq_id='faq_069_view_reports',
        category='modules',
        priority=11,
        primary_question='How do I view reports?',
        variants=[
            "access reports",
            "generate report",
            "report viewing",
        ],
        response=(
            "**To view reports:**\n\n"
            "1. Navigate to **Reports** section\n"
            "2. Select report type:\n"
            "   • Community summaries\n"
            "   • Assessment reports\n"
            "   • Partnership reports\n"
            "   • Project status reports\n"
            "3. Set parameters:\n"
            "   • Date range\n"
            "   • Regions/communities\n"
            "4. Click **'Generate Report'**\n"
            "5. View/download/print\n\n"
            "**Formats:** PDF, Excel, on-screen view"
        ),
        response_type='instant',
        source='CLAUDE.md - Reporting',
        source_url='CLAUDE.md#development-guidelines',
    ),

    EnhancedFAQ(
        faq_id='faq_070_track_tasks',
        category='modules',
        priority=11,
        primary_question='How do I track my tasks?',
        variants=[
            "view my tasks",
            "task list",
            "my assignments",
        ],
        response=(
            "**To track your tasks:**\n\n"
            "1. Navigate to **Staff** > **My Tasks**\n"
            "2. View options:\n"
            "   • **Kanban Board** - Drag and drop\n"
            "   • **List View** - Sortable list\n"
            "   • **Calendar** - Timeline view\n"
            "3. Filter by:\n"
            "   • Status (To Do/In Progress/Done)\n"
            "   • Priority\n"
            "   • Due date\n"
            "4. Update task status\n"
            "5. Add comments/notes\n\n"
            "**Dashboard widget:** See tasks overview"
        ),
        response_type='instant',
        source='CLAUDE.md - Staff Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_071_use_calendar',
        category='modules',
        priority=11,
        primary_question='How do I use the calendar?',
        variants=[
            "calendar features",
            "schedule events",
            "view calendar",
        ],
        response=(
            "**To use the calendar:**\n\n"
            "1. Navigate to **Staff** > **Calendar**\n"
            "2. View modes:\n"
            "   • Month view\n"
            "   • Week view\n"
            "   • Day view\n"
            "3. Create event: Click on date/time\n"
            "4. Event types:\n"
            "   • Meetings\n"
            "   • Workshops\n"
            "   • Tasks (deadlines)\n"
            "   • Personal events\n"
            "5. Color-coded by type\n\n"
            "**Sync:** Export to Google Calendar/Outlook"
        ),
        response_type='instant',
        source='CLAUDE.md - Staff Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_072_add_stakeholders',
        category='modules',
        priority=11,
        primary_question='How do I add stakeholders?',
        variants=[
            "create stakeholder",
            "register stakeholder",
            "new stakeholder",
        ],
        response=(
            "**To add stakeholders:**\n\n"
            "1. Navigate to **Coordination** > **Stakeholders**\n"
            "2. Click **'Add Stakeholder'**\n"
            "3. Enter information:\n"
            "   • Name/Organization\n"
            "   • Type (MOA/NGO/LGU/Private)\n"
            "   • Contact details\n"
            "   • Areas of focus\n"
            "4. Link to partnerships\n"
            "5. Click **'Save'**\n\n"
            "**Use for:** Managing partner database"
        ),
        response_type='instant',
        source='CLAUDE.md - Coordination Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_073_upload_documents',
        category='modules',
        priority=11,
        primary_question='How do I upload documents?',
        variants=[
            "attach files",
            "upload files",
            "document upload",
        ],
        response=(
            "**To upload documents:**\n\n"
            "1. Navigate to relevant record (community/project/partnership)\n"
            "2. Find **'Documents'** section\n"
            "3. Click **'Upload'** or drag-and-drop\n"
            "4. Select files from computer\n"
            "5. Add metadata:\n"
            "   • Document type\n"
            "   • Description\n"
            "   • Tags\n"
            "6. Click **'Upload'**\n\n"
            "**Supported:** PDF, Word, Excel, Images (max 10MB per file)"
        ),
        response_type='instant',
        source='CLAUDE.md - Document Management',
        source_url='CLAUDE.md#development-guidelines',
    ),

    # Priority 10: Advanced Features
    EnhancedFAQ(
        faq_id='faq_074_customize_dashboard',
        category='modules',
        priority=10,
        primary_question='Can I customize my dashboard?',
        variants=[
            "dashboard customization",
            "personalize dashboard",
            "dashboard widgets",
        ],
        response=(
            "**Yes! Dashboard customization options:**\n\n"
            "1. Click **settings icon** on dashboard\n"
            "2. Add/remove widgets:\n"
            "   • Recent activities\n"
            "   • Task summary\n"
            "   • Calendar events\n"
            "   • Quick stats\n"
            "3. Arrange widgets (drag and drop)\n"
            "4. Set default module view\n"
            "5. Save layout\n\n"
            "**Personalize:** Choose what you see first"
        ),
        response_type='instant',
        source='CLAUDE.md - User Interface',
        source_url='CLAUDE.md#frontend-integration',
    ),

    EnhancedFAQ(
        faq_id='faq_075_set_notifications',
        category='modules',
        priority=10,
        primary_question='How do I set notifications?',
        variants=[
            "notification settings",
            "email alerts",
            "notification preferences",
        ],
        response=(
            "**To set notifications:**\n\n"
            "1. Go to **Account Settings** > **Notifications**\n"
            "2. Choose notification types:\n"
            "   • Task assignments\n"
            "   • Upcoming deadlines\n"
            "   • Comments/mentions\n"
            "   • System updates\n"
            "3. Select delivery method:\n"
            "   • Email\n"
            "   • In-app notifications\n"
            "   • Both\n"
            "4. Set frequency (immediate/daily digest)\n"
            "5. Save preferences"
        ),
        response_type='instant',
        source='CLAUDE.md - User Management',
        source_url='CLAUDE.md#authentication',
    ),

    EnhancedFAQ(
        faq_id='faq_076_share_reports',
        category='modules',
        priority=10,
        primary_question='How do I share reports?',
        variants=[
            "send report",
            "report sharing",
            "distribute reports",
        ],
        response=(
            "**To share reports:**\n\n"
            "1. Generate report\n"
            "2. Click **'Share'** button\n"
            "3. Options:\n"
            "   • **Email** - Send to recipients\n"
            "   • **Link** - Generate shareable link\n"
            "   • **Download** - Share file manually\n"
            "4. Set permissions (view only/edit)\n"
            "5. Add message (optional)\n"
            "6. Send\n\n"
            "**Tip:** Links expire after 30 days"
        ),
        response_type='instant',
        source='CLAUDE.md - Reporting',
        source_url='CLAUDE.md#development-guidelines',
    ),

    EnhancedFAQ(
        faq_id='faq_077_collaborate_team',
        category='modules',
        priority=10,
        primary_question='How do I collaborate with team members?',
        variants=[
            "team collaboration",
            "work with team",
            "team features",
        ],
        response=(
            "**Collaboration features:**\n\n"
            "**1. Comments**\n"
            "• Add comments to any record\n"
            "• @mention colleagues\n"
            "• Threaded discussions\n\n"
            "**2. Shared Tasks**\n"
            "• Assign tasks to multiple people\n"
            "• Track progress together\n\n"
            "**3. Document Collaboration**\n"
            "• Share documents\n"
            "• Version control\n"
            "• Co-editing (coming soon)\n\n"
            "**4. Activity Feed**\n"
            "• See team updates\n"
            "• Track changes"
        ),
        response_type='instant',
        source='CLAUDE.md - Collaboration',
        source_url='CLAUDE.md#development-guidelines',
    ),

    EnhancedFAQ(
        faq_id='faq_078_track_budgets',
        category='modules',
        priority=10,
        primary_question='How do I track program budgets?',
        variants=[
            "budget tracking",
            "financial monitoring",
            "budget management",
        ],
        response=(
            "**To track budgets:**\n\n"
            "1. Navigate to **M&E** > **Project**\n"
            "2. View **'Budget'** tab\n"
            "3. Track:\n"
            "   • Total allocation\n"
            "   • Funds utilized\n"
            "   • Remaining balance\n"
            "   • Expense categories\n"
            "4. Add expenditures\n"
            "5. Generate financial reports\n\n"
            "**Reports:** Budget vs. actual spending"
        ),
        response_type='instant',
        source='CLAUDE.md - M&E Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_079_measure_impact',
        category='modules',
        priority=10,
        primary_question='How do I measure impact?',
        variants=[
            "impact assessment",
            "impact measurement",
            "evaluate impact",
        ],
        response=(
            "**To measure impact:**\n\n"
            "1. Navigate to **M&E** module\n"
            "2. Set baseline indicators\n"
            "3. Track progress:\n"
            "   • Output indicators\n"
            "   • Outcome indicators\n"
            "   • Impact indicators\n"
            "4. Collect data regularly\n"
            "5. Analyze trends\n"
            "6. Generate impact reports\n\n"
            "**Use:** Evidence for policy recommendations"
        ),
        response_type='instant',
        source='CLAUDE.md - M&E Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_080_generate_custom_reports',
        category='modules',
        priority=10,
        primary_question='How do I generate custom reports?',
        variants=[
            "custom reporting",
            "create custom report",
            "report builder",
        ],
        response=(
            "**To generate custom reports:**\n\n"
            "1. Navigate to **Reports** > **Custom**\n"
            "2. Click **'New Custom Report'**\n"
            "3. Select data source:\n"
            "   • Communities\n"
            "   • Assessments\n"
            "   • Projects\n"
            "   • Partnerships\n"
            "4. Choose fields to include\n"
            "5. Apply filters\n"
            "6. Set grouping/sorting\n"
            "7. Preview and generate\n\n"
            "**Save:** Reuse custom report templates"
        ),
        response_type='instant',
        source='CLAUDE.md - Reporting',
        source_url='CLAUDE.md#development-guidelines',
    ),
]


# ============================================================================
# PHASE 5: STATISTICS & ADVANCED FAQs (20 FAQs, Priority 5-8)
# ============================================================================

PHASE_5_STATISTICS = [
    # Priority 8: System Statistics - Note: These require database queries
    EnhancedFAQ(
        faq_id='faq_081_how_many_communities',
        category='statistics',
        priority=8,
        primary_question='How many communities are in OBCMS?',
        variants=[
            "total communities",
            "community count",
            "number of communities",
        ],
        response=(
            "To get the current community count, I'll need to query the database.\n\n"
            "Try asking: 'List all communities' or 'Show communities by region'"
        ),
        response_type='database_query',
        source='CLAUDE.md - Communities Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_082_how_many_provinces',
        category='statistics',
        priority=8,
        primary_question='How many provinces are covered?',
        variants=[
            "province count",
            "total provinces",
            "number of provinces",
        ],
        response=(
            "**OOBC covers 17 provinces** across 4 regions:\n\n"
            "• **Region IX:** 3 provinces\n"
            "• **Region X:** 5 provinces\n"
            "• **Region XI:** 5 provinces\n"
            "• **Region XII:** 4 provinces\n\n"
            "Plus multiple highly urbanized cities."
        ),
        response_type='instant',
        source='CLAUDE.md - Geographic Scope',
        source_url='CLAUDE.md#geographic-scope',
    ),

    EnhancedFAQ(
        faq_id='faq_083_how_many_barangays',
        category='statistics',
        priority=8,
        primary_question='How many OBC barangays are there?',
        variants=[
            "barangay count",
            "total barangays",
            "number of barangays",
        ],
        response=(
            "To get the current barangay count, I'll need to query the database.\n\n"
            "Try asking: 'List all barangays' or 'Show barangays in [province name]'"
        ),
        response_type='database_query',
        source='CLAUDE.md - Communities Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_084_how_many_partnerships',
        category='statistics',
        priority=8,
        primary_question='How many partnerships are active?',
        variants=[
            "partnership count",
            "active partnerships",
            "number of partnerships",
        ],
        response=(
            "To get the current partnership count, I'll need to query the database.\n\n"
            "Try asking: 'List all partnerships' or 'Show active partnerships'"
        ),
        response_type='database_query',
        source='CLAUDE.md - Coordination Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_085_how_many_projects',
        category='statistics',
        priority=8,
        primary_question='How many projects are ongoing?',
        variants=[
            "project count",
            "active projects",
            "ongoing projects",
        ],
        response=(
            "To get the current project count, I'll need to query the database.\n\n"
            "Try asking: 'List all projects' or 'Show ongoing projects'"
        ),
        response_type='database_query',
        source='CLAUDE.md - M&E Module',
        source_url='CLAUDE.md#core-applications',
    ),

    # Priority 7: Module Statistics
    EnhancedFAQ(
        faq_id='faq_086_how_many_assessments',
        category='statistics',
        priority=7,
        primary_question='How many MANA assessments have been conducted?',
        variants=[
            "assessment count",
            "total assessments",
            "number of assessments",
        ],
        response=(
            "To get the current assessment count, I'll need to query the database.\n\n"
            "Try asking: 'List all assessments' or 'Show recent workshops'"
        ),
        response_type='database_query',
        source='CLAUDE.md - MANA Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_087_workshops_this_year',
        category='statistics',
        priority=7,
        primary_question='How many workshops this year?',
        variants=[
            "workshop count",
            "annual workshops",
            "workshops conducted",
        ],
        response=(
            "To get the current year's workshop count, I'll need to query the database.\n\n"
            "Try asking: 'List workshops this year' or 'Show recent workshops'"
        ),
        response_type='database_query',
        source='CLAUDE.md - MANA Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_088_how_many_policies',
        category='statistics',
        priority=7,
        primary_question='How many policy recommendations?',
        variants=[
            "policy count",
            "total policies",
            "policy recommendations",
        ],
        response=(
            "To get the current policy recommendation count, I'll need to query the database.\n\n"
            "Try asking: 'List all policy recommendations' or 'Show policies by status'"
        ),
        response_type='database_query',
        source='CLAUDE.md - Policies Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_089_how_many_moas',
        category='statistics',
        priority=7,
        primary_question='How many MOAs are in the system?',
        variants=[
            "moa count",
            "total moas",
            "number of moas",
        ],
        response=(
            "To get the current MOA count, I'll need to query the database.\n\n"
            "Try asking: 'List all MOAs' or 'Show MOAs by type'"
        ),
        response_type='database_query',
        source='CLAUDE.md - M&E Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_090_how_many_stakeholders',
        category='statistics',
        priority=7,
        primary_question='How many stakeholders are registered?',
        variants=[
            "stakeholder count",
            "total stakeholders",
            "registered stakeholders",
        ],
        response=(
            "To get the current stakeholder count, I'll need to query the database.\n\n"
            "Try asking: 'List all stakeholders' or 'Show stakeholders by type'"
        ),
        response_type='database_query',
        source='CLAUDE.md - Coordination Module',
        source_url='CLAUDE.md#core-applications',
    ),

    EnhancedFAQ(
        faq_id='faq_091_how_many_users',
        category='statistics',
        priority=7,
        primary_question='How many users are in the system?',
        variants=[
            "user count",
            "total users",
            "staff count",
        ],
        response=(
            "For security reasons, user counts are only available to administrators.\n\n"
            "**Contact:** System administrator for user statistics"
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
    ),

    # Priority 6: Data Quality & Management
    EnhancedFAQ(
        faq_id='faq_092_data_verification',
        category='statistics',
        priority=6,
        primary_question='How is data verified?',
        variants=[
            "data quality",
            "data validation",
            "verify data",
        ],
        response=(
            "**OBCMS Data Verification Process:**\n\n"
            "**1. Entry Validation**\n"
            "• Required field checks\n"
            "• Format validation\n"
            "• Range checks\n\n"
            "**2. Review Workflow**\n"
            "• Data entry by staff\n"
            "• Supervisor review\n"
            "• Approval before publication\n\n"
            "**3. Regular Audits**\n"
            "• Quarterly data quality checks\n"
            "• Discrepancy reports\n"
            "• Corrections and updates\n\n"
            "**4. Source Documentation**\n"
            "• All data linked to source documents\n"
            "• Audit trail maintained"
        ),
        response_type='instant',
        source='CLAUDE.md - Data Management',
        source_url='CLAUDE.md#development-guidelines',
    ),

    EnhancedFAQ(
        faq_id='faq_093_data_update_frequency',
        category='statistics',
        priority=6,
        primary_question='How often is data updated?',
        variants=[
            "data freshness",
            "update schedule",
            "data currency",
        ],
        response=(
            "**Data Update Frequencies:**\n\n"
            "**Real-Time:**\n"
            "• Task updates\n"
            "• Calendar events\n"
            "• Comments and activity feeds\n\n"
            "**Daily:**\n"
            "• Dashboard statistics\n"
            "• Report generation\n\n"
            "**As Needed:**\n"
            "• Community profiles (when changes occur)\n"
            "• Partnerships (when status changes)\n"
            "• Projects (regular monitoring updates)\n\n"
            "**Periodic:**\n"
            "• MANA assessments (annually or bi-annually)\n"
            "• Impact evaluations (project cycles)"
        ),
        response_type='instant',
        source='CLAUDE.md - Data Management',
        source_url='CLAUDE.md#development-guidelines',
    ),

    EnhancedFAQ(
        faq_id='faq_094_who_can_edit_data',
        category='statistics',
        priority=6,
        primary_question='Who can edit community data?',
        variants=[
            "data permissions",
            "edit permissions",
            "data access control",
        ],
        response=(
            "**Data Editing Permissions:**\n\n"
            "**Community Data:**\n"
            "• **Community Officers** - Can edit assigned communities\n"
            "• **Supervisors** - Can edit and approve\n"
            "• **Administrators** - Full access\n\n"
            "**Module-Specific:**\n"
            "• **MANA Coordinators** - Assessment data\n"
            "• **Coordination Staff** - Partnerships\n"
            "• **Policy Analysts** - Policy recommendations\n"
            "• **M&E Officers** - Projects and programs\n\n"
            "**Read-Only:**\n"
            "• Partner organization users\n"
            "• Report viewers\n\n"
            "**Contact:** Administrator for permission changes"
        ),
        response_type='instant',
        source='CLAUDE.md - Authentication',
        source_url='CLAUDE.md#authentication',
    ),

    EnhancedFAQ(
        faq_id='faq_095_privacy_protection',
        category='statistics',
        priority=6,
        primary_question='How is privacy protected?',
        variants=[
            "data privacy",
            "data security",
            "privacy policy",
        ],
        response=(
            "**OBCMS Privacy Protection:**\n\n"
            "**1. Access Control**\n"
            "• Role-based permissions\n"
            "• Secure authentication\n"
            "• Activity logging\n\n"
            "**2. Data Encryption**\n"
            "• HTTPS/SSL for data transmission\n"
            "• Database encryption at rest\n"
            "• Secure backups\n\n"
            "**3. Privacy Compliance**\n"
            "• Data Privacy Act compliance\n"
            "• Minimal data collection\n"
            "• Purpose limitation\n\n"
            "**4. User Rights**\n"
            "• Access your own data\n"
            "• Request corrections\n"
            "• Data portability\n\n"
            "**See:** Privacy Policy documentation"
        ),
        response_type='instant',
        source='CLAUDE.md - Security',
        source_url='CLAUDE.md#security--performance',
    ),

    EnhancedFAQ(
        faq_id='faq_096_can_delete_data',
        category='statistics',
        priority=6,
        primary_question='Can I delete data?',
        variants=[
            "delete records",
            "data deletion",
            "remove data",
        ],
        response=(
            "**Data Deletion Policy:**\n\n"
            "**Can Delete:**\n"
            "• Your own draft records\n"
            "• Personal tasks and notes\n"
            "• Uploaded documents (before approval)\n\n"
            "**Cannot Delete (Archive instead):**\n"
            "• Approved community profiles\n"
            "• Published assessments\n"
            "• Active projects/partnerships\n"
            "• Historical records\n\n"
            "**Requires Administrator:**\n"
            "• Deletion of approved records\n"
            "• Bulk deletions\n"
            "• Permanent data removal\n\n"
            "**Note:** Most data is archived (soft delete) for audit trail\n\n"
            "**Contact:** Administrator for data deletion requests"
        ),
        response_type='instant',
        source='CLAUDE.md - Data Management',
        source_url='CLAUDE.md#development-guidelines',
    ),

    # Priority 5: Advanced Features
    EnhancedFAQ(
        faq_id='faq_097_what_is_api',
        category='statistics',
        priority=5,
        primary_question='What is the API?',
        variants=[
            "api access",
            "api documentation",
            "application programming interface",
        ],
        response=(
            "**OBCMS API (Application Programming Interface)**\n\n"
            "**Purpose:**\n"
            "• Programmatic access to OBCMS data\n"
            "• Integration with external systems\n"
            "• Custom applications and dashboards\n\n"
            "**Features:**\n"
            "• RESTful API design\n"
            "• JWT authentication\n"
            "• JSON data format\n"
            "• Comprehensive endpoints\n\n"
            "**Access:**\n"
            "• Available to approved developers\n"
            "• Requires API key\n"
            "• Documentation at /api/docs/\n\n"
            "**Contact:** IT administrator for API access"
        ),
        response_type='instant',
        source='CLAUDE.md - API Development',
        source_url='CLAUDE.md#api-development',
    ),

    EnhancedFAQ(
        faq_id='faq_098_system_integration',
        category='statistics',
        priority=5,
        primary_question='How do I integrate with other systems?',
        variants=[
            "integration options",
            "connect systems",
            "system interoperability",
        ],
        response=(
            "**System Integration Options:**\n\n"
            "**1. API Integration**\n"
            "• Use OBCMS REST API\n"
            "• Programmatic data exchange\n"
            "• Real-time synchronization\n\n"
            "**2. Data Export/Import**\n"
            "• Excel/CSV exports\n"
            "• Bulk data import tools\n"
            "• Scheduled exports\n\n"
            "**3. Webhooks (Coming Soon)**\n"
            "• Event-driven notifications\n"
            "• Automated triggers\n\n"
            "**4. Database Connection (Advanced)**\n"
            "• Direct database access (read-only)\n"
            "• For business intelligence tools\n"
            "• Requires special approval\n\n"
            "**Contact:** IT team for integration planning"
        ),
        response_type='instant',
        source='CLAUDE.md - API Development',
        source_url='CLAUDE.md#api-development',
    ),

    EnhancedFAQ(
        faq_id='faq_099_automate_tasks',
        category='statistics',
        priority=5,
        primary_question='Can I automate tasks?',
        variants=[
            "task automation",
            "automated workflows",
            "automation features",
        ],
        response=(
            "**Automation Features in OBCMS:**\n\n"
            "**Current Automation:**\n"
            "• **Email Notifications** - Automatic alerts\n"
            "• **Deadline Reminders** - Task due date alerts\n"
            "• **Report Scheduling** - Auto-generated reports\n"
            "• **Status Updates** - Workflow transitions\n\n"
            "**Coming Soon:**\n"
            "• Custom workflow automation\n"
            "• Rule-based triggers\n"
            "• Bulk operations\n"
            "• Integration webhooks\n\n"
            "**Advanced (via API):**\n"
            "• Custom automation scripts\n"
            "• External tool integration\n\n"
            "**Contact:** Feature requests for automation needs"
        ),
        response_type='instant',
        source='CLAUDE.md - Background Tasks',
        source_url='CLAUDE.md#key-technical-components',
    ),

    EnhancedFAQ(
        faq_id='faq_100_bulk_import_data',
        category='statistics',
        priority=5,
        primary_question='How do I bulk import data?',
        variants=[
            "bulk upload",
            "import data",
            "mass data entry",
        ],
        response=(
            "**Bulk Data Import Process:**\n\n"
            "**1. Prepare Data**\n"
            "• Download import template (Excel/CSV)\n"
            "• Fill in data following template format\n"
            "• Validate data completeness\n\n"
            "**2. Import**\n"
            "• Navigate to module\n"
            "• Click **'Import Data'**\n"
            "• Upload your file\n"
            "• Map columns to fields\n\n"
            "**3. Validation**\n"
            "• System validates all entries\n"
            "• Review error report\n"
            "• Fix errors and re-upload\n\n"
            "**4. Confirmation**\n"
            "• Review import summary\n"
            "• Confirm import\n"
            "• Data added to system\n\n"
            "**Supported Modules:**\n"
            "• Communities\n"
            "• Stakeholders\n"
            "• Projects (limited)\n\n"
            "**Contact:** Administrator for large imports (>1000 records)"
        ),
        response_type='instant',
        source='CLAUDE.md - Data Management',
        source_url='CLAUDE.md#development-guidelines',
    ),
]


# ============================================================================
# FAQ Lookup Functions
# ============================================================================

def get_all_faqs() -> List[EnhancedFAQ]:
    """Get all enhanced FAQs from all phases."""
    return (
        PHASE_1_SYSTEM_IDENTITY +
        PHASE_2_ACCESS_HELP +
        PHASE_3_GEOGRAPHY +
        PHASE_4_MODULES +
        PHASE_5_STATISTICS
    )


def get_faqs_by_category(category: str) -> List[EnhancedFAQ]:
    """Get FAQs filtered by category."""
    return [faq for faq in get_all_faqs() if faq.category == category]


def get_faqs_by_priority_range(min_priority: int, max_priority: int) -> List[EnhancedFAQ]:
    """Get FAQs within priority range."""
    return [
        faq for faq in get_all_faqs()
        if min_priority <= faq.priority <= max_priority
    ]


def get_faq_by_id(faq_id: str) -> Optional[EnhancedFAQ]:
    """Get FAQ by ID."""
    for faq in get_all_faqs():
        if faq.id == faq_id:
            return faq
    return None


def build_pattern_to_faq_map() -> Dict[str, EnhancedFAQ]:
    """
    Build a map of all patterns (primary + variants) to FAQ objects.

    Returns:
        Dict mapping lowercase patterns to EnhancedFAQ objects
    """
    pattern_map = {}
    for faq in get_all_faqs():
        for pattern in faq.get_all_patterns():
            pattern_map[pattern] = faq
    return pattern_map


# Build pattern map at module load time
PATTERN_TO_FAQ_MAP = build_pattern_to_faq_map()
