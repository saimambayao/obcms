"""Shared constants for the common app."""

STAFF_USER_TYPES = ("oobc_staff", "admin")

# Suggested competency groupings surfaced by OOBC HR leads.
STAFF_COMPETENCY_CATEGORIES = {
    "core": [
        "Critical, Creative, and Strategic Thinking",
        "Effective Communication",
        "Synergistic Collaboration",
        "Complete Staff Work (CSW)",
        "Public Service and Cultural Competence",
    ],
    "leadership": [
        "Planning for Organizational and Systems Change",
        "Building High-Trust Organizational Culture",
        "Supervising Disciplined Execution and Managing for Results",
        "Developing High-Performance Teams",
        "Leading and Influencing Change",
    ],
    "functional": [
        "PAO · Stakeholder Engagement, Community Organizing, and Constituency Building",
        "PAO · Representation Skills",
        "PAO · Social Marketing, Advocacy, and Lobbying",
        "PAO · Project, Program, and Events Management",
        "PAO · Monitoring, Reporting, and Evaluation",
        "LSO · Investigation and Research Skills",
        "LSO · Policy Making, Analysis, and Evaluation",
        "LSO · Legal and Legislative Competence",
        "LSO · Attention to Details and Quality",
        "LSO · Oversight Skills",
        "PIMAO · Strategic Communications",
        "PIMAO · Documentation and Editing Skills",
        "PIMAO · Social Media Skills",
        "PIMAO · Print and Digital Media Skills",
        "PIMAO · Media Handling Skills",
    ],
}

STAFF_COMPETENCY_PROFICIENCY_LEVELS = (
    "Needs Improvement",
    "Developing",
    "Proficient",
    "Exemplary",
)

CALENDAR_MODULE_ORDER = [
    "coordination",
    "mana",
    "planning",
    "policy",
    "staff",
]

CALENDAR_MODULE_LABELS = {
    "coordination": "Coordination",
    "mana": "MANA Field Operations",
    "planning": "Planning & Budgeting",
    "policy": "Policy Tracking",
    "staff": "Staff Operations",
}

CALENDAR_MODULE_DESCRIPTIONS = {
    "coordination": "Events, stakeholder engagements, and inter-agency meetings.",
    "mana": "MANA baseline data collection activities and field deployments.",
    "planning": "Planning milestones, budget workflow stages, and community requests.",
    "policy": "Policy recommendation reviews, implementation starts, and deadlines.",
    "staff": "Team tasks, development actions, and scheduled trainings.",
}

CALENDAR_MODULE_COLORS = {
    "coordination": "bg-blue-500",
    "mana": "bg-amber-500",
    "planning": "bg-teal-500",
    "policy": "bg-pink-500",
    "staff": "bg-teal-600",
}

STAFF_TEAM_DEFINITIONS = [
    {
        "name": "MANA Team",
        "description": (
            "Mapping and Needs Assessment (MANA) team overseeing geospatial and "
            "socio-economic profiling."
        ),
        "mission": (
            "Deliver updated community baselines and data layers to guide OOBC "
            "interventions."
        ),
        "focus": [
            "Community mapping refresh cycles",
            "Needs assessment data quality",
            "Field team readiness and logistics",
        ],
    },
    {
        "name": "M&E Unit",
        "description": (
            "Monitoring and Evaluation unit tracking programme outcomes and "
            "implementation fidelity."
        ),
        "mission": (
            "Transform field reports into actionable insights for adaptive management "
            "and leadership decisions."
        ),
        "focus": [
            "Indicator performance tracking",
            "Data validation and synthesis",
            "Reporting for management and partners",
        ],
    },
    {
        "name": "Planning and Budgeting Unit",
        "description": (
            "Unit aligning programme priorities with financial planning and resource "
            "mobilisation."
        ),
        "mission": (
            "Translate community priorities into resourced plans and monitor execution "
            "timelines."
        ),
        "focus": [
            "Quarterly budgeting cycles",
            "Resource alignment with MANA outputs",
            "Portfolio risk mitigation",
        ],
    },
    {
        "name": "Coordination Unit",
        "description": (
            "Unit orchestrating cross-agency touchpoints and commitments for OOBC "
            "communities."
        ),
        "mission": (
            "Synchronise engagements with BARMM ministries, LGUs, and partners for "
            "cohesive delivery."
        ),
        "focus": [
            "Inter-agency briefings",
            "Stakeholder alignment",
            "Calendar and follow-up management",
        ],
    },
    {
        "name": "Community Development Unit",
        "description": (
            "Unit crafting development packages and support services for OOBC "
            "communities."
        ),
        "mission": (
            "Co-design livelihood, protection, and social support interventions with "
            "communities."
        ),
        "focus": [
            "Livelihood programming",
            "Community consultations",
            "Capability building initiatives",
        ],
    },
    {
        "name": "Research Unit",
        "description": (
            "Research hub documenting emerging issues, indigenous knowledge, and "
            "policy evidence."
        ),
        "mission": (
            "Convert field intelligence into briefs that feed policy and programme "
            "design."
        ),
        "focus": [
            "Qualitative and quantitative studies",
            "Knowledge management",
            "Evidence synthesis",
        ],
    },
]


RECOMMENDATIONS_AREAS = {
    "economic-development": {
        "name": "Economic Development",
        "categories": ["economic_development"],
        "icon": "fas fa-chart-line",
        "color": "green",
    },
    "social-development": {
        "name": "Social Development",
        "categories": ["social_development"],
        "icon": "fas fa-users",
        "color": "purple",
    },
    "cultural-development": {
        "name": "Cultural Development",
        "categories": ["cultural_development"],
        "icon": "fas fa-mosque",
        "color": "orange",
    },
    "promotion-of-welfare": {
        "name": "Promotion of Welfare",
        "categories": ["promotion_of_welfare"],
        "icon": "fas fa-hands-helping",
        "color": "teal",
    },
    "rehabilitation-development": {
        "name": "Rehabilitation & Development",
        "categories": ["infrastructure", "environment"],
        "icon": "fas fa-hammer",
        "color": "blue",
    },
    "protection-rights": {
        "name": "Protection of Rights",
        "categories": ["human_rights"],
        "icon": "fas fa-balance-scale",
        "color": "red",
    },
}
