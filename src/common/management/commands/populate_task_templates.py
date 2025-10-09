"""Management command to populate task templates for all domains."""

from django.core.management.base import BaseCommand
from django.db import transaction
from common.models import TaskTemplate, TaskTemplateItem, StaffTask


class Command(BaseCommand):
    help = "Populate task templates for MANA, Coordination, Policy, Services, and Monitoring domains"

    def handle(self, *args, **options):
        self.stdout.write("Creating task templates...")

        with transaction.atomic():
            # Clear existing templates if recreating
            if options.get("clear"):
                TaskTemplate.objects.all().delete()
                self.stdout.write(self.style.WARNING("Cleared existing templates"))

            # MANA Templates
            self.create_mana_templates()

            # Coordination Templates
            self.create_coordination_templates()

            # Policy Templates
            self.create_policy_templates()

            # Services Templates
            self.create_services_templates()

            # Monitoring Templates
            self.create_monitoring_templates()

        self.stdout.write(self.style.SUCCESS("Successfully created all task templates"))

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing templates before creating new ones",
        )

    def create_mana_templates(self):
        """Create MANA assessment task templates."""
        self.stdout.write("Creating MANA templates...")

        # 1. MANA Assessment Full Cycle (25+ tasks)
        template = TaskTemplate.objects.create(
            name="mana_assessment_full_cycle",
            domain=StaffTask.DOMAIN_MANA,
            description="Complete MANA assessment cycle with all phases",
        )

        tasks = [
            # Planning Phase
            (
                1,
                "Assemble assessment team for {assessment_name}",
                "Identify and recruit team members with relevant expertise",
                "high",
                8,
                0,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                2,
                "Develop assessment methodology",
                "Design data collection approach and tools",
                "high",
                16,
                3,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                3,
                "Prepare data collection tools",
                "Develop surveys, interview guides, FGD protocols",
                "high",
                12,
                5,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                4,
                "Schedule field visits",
                "Coordinate with LGUs and communities for site visits",
                "medium",
                6,
                7,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                5,
                "Conduct team orientation",
                "Brief team on methodology, ethics, and protocols",
                "high",
                4,
                10,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            # Data Collection Phase
            (
                6,
                "Conduct surveys in target areas",
                "Administer structured surveys to respondents",
                "high",
                40,
                14,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                7,
                "Perform key informant interviews",
                "Interview stakeholders and community leaders",
                "high",
                24,
                14,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                8,
                "Facilitate focus group discussions",
                "Conduct FGDs with community members",
                "high",
                16,
                17,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                9,
                "Complete mapping activities",
                "Map community infrastructure and resources",
                "medium",
                16,
                20,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                10,
                "Collect baseline data",
                "Gather demographic and socioeconomic data",
                "high",
                20,
                21,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                11,
                "Document field observations",
                "Record qualitative observations and insights",
                "medium",
                12,
                24,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            # Analysis Phase
            (
                12,
                "Clean and validate survey data",
                "Check data quality and resolve inconsistencies",
                "high",
                16,
                28,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                13,
                "Analyze quantitative data",
                "Perform statistical analysis of survey results",
                "high",
                24,
                30,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                14,
                "Analyze qualitative data",
                "Code and analyze interview and FGD transcripts",
                "high",
                20,
                32,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                15,
                "Identify community needs",
                "Synthesize findings to identify priority needs",
                "critical",
                16,
                35,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                16,
                "Prioritize identified needs",
                "Score and rank needs based on criteria",
                "high",
                12,
                37,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                17,
                "Validate findings with stakeholders",
                "Present preliminary findings for feedback",
                "high",
                8,
                40,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            # Report Writing Phase
            (
                18,
                "Draft executive summary",
                "Write concise summary of key findings",
                "high",
                8,
                42,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                19,
                "Write methodology section",
                "Document assessment approach and methods",
                "medium",
                8,
                43,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                20,
                "Compile findings and analysis",
                "Write detailed findings by theme/area",
                "high",
                24,
                44,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                21,
                "Create visualizations and maps",
                "Develop charts, graphs, and maps for report",
                "medium",
                12,
                47,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                22,
                "Develop recommendations",
                "Draft actionable recommendations based on findings",
                "critical",
                16,
                49,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                23,
                "Format and compile draft report",
                "Assemble all sections into coherent document",
                "medium",
                8,
                52,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            # Review Phase
            (
                24,
                "Internal review of draft report",
                "Team review for quality and completeness",
                "high",
                12,
                54,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
            (
                25,
                "Incorporate stakeholder feedback",
                "Revise report based on comments",
                "high",
                16,
                56,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
            (
                26,
                "Final approval by assessment lead",
                "Final review and sign-off",
                "critical",
                4,
                60,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                assessment_phase=phase,
            )

        # 2. MANA Assessment Desk Review (10 tasks)
        template = TaskTemplate.objects.create(
            name="mana_assessment_desk_review",
            domain=StaffTask.DOMAIN_MANA,
            description="Desk review assessment methodology",
        )

        tasks = [
            (
                1,
                "Define desk review scope",
                "Identify documents and data sources to review",
                "high",
                4,
                0,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                2,
                "Collect secondary data sources",
                "Gather reports, studies, administrative data",
                "high",
                12,
                2,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                3,
                "Review government reports",
                "Analyze LGU and national government documents",
                "medium",
                16,
                5,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                4,
                "Review academic literature",
                "Examine relevant research and studies",
                "medium",
                16,
                5,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                5,
                "Extract key data points",
                "Compile statistics and indicators from sources",
                "high",
                12,
                8,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                6,
                "Analyze document findings",
                "Synthesize information from all sources",
                "high",
                20,
                10,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                7,
                "Identify data gaps",
                "Note missing information and limitations",
                "medium",
                8,
                13,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                8,
                "Draft desk review report",
                "Write comprehensive desk review document",
                "high",
                16,
                15,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                9,
                "Peer review of report",
                "Internal quality check",
                "medium",
                8,
                18,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
            (
                10,
                "Finalize desk review",
                "Incorporate feedback and finalize",
                "high",
                4,
                20,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                assessment_phase=phase,
            )

        # 3. MANA Assessment Survey (15 tasks)
        template = TaskTemplate.objects.create(
            name="mana_assessment_survey",
            domain=StaffTask.DOMAIN_MANA,
            description="Survey-based assessment methodology",
        )

        tasks = [
            (
                1,
                "Design survey questionnaire",
                "Develop survey questions aligned with objectives",
                "high",
                12,
                0,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                2,
                "Determine sampling strategy",
                "Define sample size and selection method",
                "high",
                8,
                2,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                3,
                "Pilot test survey instrument",
                "Test survey with small sample",
                "medium",
                8,
                5,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                4,
                "Revise survey based on pilot",
                "Refine questions and format",
                "medium",
                6,
                7,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                5,
                "Train survey enumerators",
                "Conduct training on survey administration",
                "high",
                8,
                9,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                6,
                "Coordinate with communities",
                "Arrange survey schedule with LGUs",
                "medium",
                6,
                10,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                7,
                "Administer surveys",
                "Conduct surveys with target respondents",
                "high",
                40,
                12,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                8,
                "Monitor data collection quality",
                "Spot-check surveys for completeness",
                "medium",
                8,
                14,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                9,
                "Enter survey data",
                "Input responses into database",
                "high",
                20,
                20,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                10,
                "Clean survey dataset",
                "Check for errors and outliers",
                "high",
                12,
                23,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                11,
                "Perform statistical analysis",
                "Analyze survey data with statistical tools",
                "high",
                24,
                25,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                12,
                "Generate survey tables and charts",
                "Create visual summaries of results",
                "medium",
                12,
                28,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                13,
                "Write survey findings report",
                "Document survey results and insights",
                "high",
                16,
                30,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                14,
                "Review survey report",
                "Internal quality review",
                "medium",
                8,
                33,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
            (
                15,
                "Finalize survey report",
                "Final revisions and approval",
                "high",
                6,
                35,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                assessment_phase=phase,
            )

        # 4. MANA Assessment Participatory (20 tasks)
        template = TaskTemplate.objects.create(
            name="mana_assessment_participatory",
            domain=StaffTask.DOMAIN_MANA,
            description="Participatory assessment with community engagement",
        )

        tasks = [
            (
                1,
                "Plan participatory approach",
                "Design community engagement strategy",
                "high",
                8,
                0,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                2,
                "Identify community facilitators",
                "Recruit local facilitators",
                "high",
                6,
                2,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                3,
                "Prepare participatory tools",
                "Develop tools for community mapping, ranking, etc.",
                "high",
                12,
                4,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                4,
                "Train facilitators",
                "Conduct participatory methods training",
                "high",
                8,
                7,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                5,
                "Mobilize community participants",
                "Invite and confirm community members",
                "medium",
                8,
                9,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                6,
                "Conduct community mapping exercise",
                "Facilitate participatory mapping session",
                "high",
                12,
                12,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                7,
                "Facilitate needs ranking activity",
                "Guide community in prioritizing needs",
                "high",
                8,
                14,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                8,
                "Hold problem tree analysis session",
                "Analyze root causes with community",
                "medium",
                8,
                16,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                9,
                "Conduct seasonal calendar activity",
                "Map community activities across seasons",
                "medium",
                6,
                18,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                10,
                "Facilitate visioning exercise",
                "Community develops vision for future",
                "medium",
                8,
                20,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                11,
                "Document participatory outputs",
                "Compile and photograph all outputs",
                "high",
                12,
                22,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                12,
                "Conduct validation workshop",
                "Present findings to community for feedback",
                "high",
                8,
                25,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                13,
                "Analyze participatory data",
                "Synthesize community-generated information",
                "high",
                20,
                27,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                14,
                "Triangulate with other data",
                "Compare with surveys and secondary data",
                "high",
                12,
                30,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                15,
                "Develop community action plan",
                "Co-create plan with community",
                "high",
                16,
                32,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                16,
                "Draft participatory assessment report",
                "Write comprehensive report",
                "high",
                24,
                35,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                17,
                "Create photo documentation",
                "Compile photos and visual materials",
                "medium",
                8,
                38,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                18,
                "Share draft with community",
                "Present draft report to participants",
                "high",
                6,
                40,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
            (
                19,
                "Incorporate community feedback",
                "Revise based on community input",
                "high",
                12,
                42,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
            (
                20,
                "Finalize participatory report",
                "Complete final version",
                "high",
                8,
                45,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                assessment_phase=phase,
            )

        # 5. MANA Baseline Study (12 tasks)
        template = TaskTemplate.objects.create(
            name="mana_baseline_study",
            domain=StaffTask.DOMAIN_MANA,
            description="Baseline study for program monitoring",
        )

        tasks = [
            (
                1,
                "Define baseline indicators",
                "Identify key indicators to measure",
                "high",
                8,
                0,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                2,
                "Review existing baseline data",
                "Assess available secondary data",
                "medium",
                8,
                2,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                3,
                "Design data collection plan",
                "Plan primary data collection approach",
                "high",
                12,
                5,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                4,
                "Develop data collection tools",
                "Create forms and instruments",
                "high",
                12,
                7,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                5,
                "Collect baseline data",
                "Gather data on all indicators",
                "high",
                32,
                10,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                6,
                "Verify data accuracy",
                "Cross-check data for reliability",
                "medium",
                8,
                17,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                7,
                "Analyze baseline data",
                "Calculate baseline values for indicators",
                "high",
                16,
                20,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                8,
                "Establish baseline benchmarks",
                "Set targets based on baseline values",
                "high",
                8,
                23,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                9,
                "Write baseline study report",
                "Document baseline findings",
                "high",
                16,
                25,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                10,
                "Create baseline database",
                "Set up database for monitoring",
                "medium",
                12,
                28,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
            (
                11,
                "Review baseline report",
                "Internal quality review",
                "medium",
                6,
                30,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
            (
                12,
                "Finalize baseline study",
                "Complete and approve report",
                "high",
                4,
                32,
                StaffTask.ASSESSMENT_PHASE_REVIEW,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                assessment_phase=phase,
            )

        # 6. MANA Workshop Facilitation (6 tasks)
        template = TaskTemplate.objects.create(
            name="mana_workshop_facilitation",
            domain=StaffTask.DOMAIN_MANA,
            description="Workshop planning and facilitation",
        )

        tasks = [
            (
                1,
                "Develop workshop agenda",
                "Plan session flow and activities",
                "high",
                6,
                0,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                2,
                "Prepare workshop materials",
                "Create handouts, presentations, exercises",
                "high",
                12,
                3,
                StaffTask.ASSESSMENT_PHASE_PLANNING,
            ),
            (
                3,
                "Coordinate workshop logistics",
                "Arrange venue, equipment, catering",
                "medium",
                8,
                5,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                4,
                "Facilitate workshop sessions",
                "Lead workshop activities",
                "high",
                16,
                7,
                StaffTask.ASSESSMENT_PHASE_DATA_COLLECTION,
            ),
            (
                5,
                "Document workshop outputs",
                "Record discussions and decisions",
                "high",
                8,
                8,
                StaffTask.ASSESSMENT_PHASE_ANALYSIS,
            ),
            (
                6,
                "Prepare workshop report",
                "Write summary of outcomes and next steps",
                "medium",
                8,
                10,
                StaffTask.ASSESSMENT_PHASE_REPORT_WRITING,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                assessment_phase=phase,
            )

        self.stdout.write(self.style.SUCCESS("✓ Created 6 MANA templates"))

    def create_coordination_templates(self):
        """Create coordination and partnership task templates."""
        self.stdout.write("Creating Coordination templates...")

        # 1. Event Meeting Standard (8 tasks)
        template = TaskTemplate.objects.create(
            name="event_meeting_standard",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Standard meeting planning and execution",
        )

        tasks = [
            (
                1,
                "Identify meeting objectives",
                "Define purpose and expected outcomes",
                "high",
                2,
                0,
            ),
            (
                2,
                "Prepare meeting agenda",
                "Develop detailed agenda with time allocation",
                "high",
                3,
                1,
            ),
            (
                3,
                "Invite participants",
                "Send invitations and confirm attendance",
                "medium",
                4,
                2,
            ),
            (
                4,
                "Prepare meeting materials",
                "Assemble documents, presentations, handouts",
                "medium",
                6,
                4,
            ),
            (
                5,
                "Arrange meeting logistics",
                "Book venue, set up equipment",
                "medium",
                3,
                6,
            ),
            (
                6,
                "Facilitate meeting",
                "Lead meeting and manage discussions",
                "high",
                4,
                7,
            ),
            (
                7,
                "Prepare meeting minutes",
                "Document decisions and action items",
                "high",
                4,
                8,
            ),
            (
                8,
                "Follow up on action items",
                "Track progress on commitments",
                "medium",
                6,
                14,
            ),
        ]

        for seq, title, desc, priority, hours, days in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
            )

        # 2. Event Workshop Full (12 tasks)
        template = TaskTemplate.objects.create(
            name="event_workshop_full",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Comprehensive workshop planning",
        )

        tasks = [
            (
                1,
                "Define workshop objectives",
                "Clarify learning goals and outputs",
                "high",
                4,
                0,
            ),
            (
                2,
                "Design workshop curriculum",
                "Develop session plan and modules",
                "high",
                12,
                2,
            ),
            (
                3,
                "Identify resource persons",
                "Recruit facilitators and speakers",
                "high",
                6,
                5,
            ),
            (
                4,
                "Prepare workshop materials",
                "Create presentations, exercises, handouts",
                "high",
                16,
                7,
            ),
            (
                5,
                "Arrange workshop venue",
                "Book venue and accommodation",
                "medium",
                6,
                10,
            ),
            (
                6,
                "Send workshop invitations",
                "Invite participants and manage registration",
                "medium",
                8,
                12,
            ),
            (
                7,
                "Finalize workshop logistics",
                "Confirm catering, equipment, transportation",
                "high",
                8,
                18,
            ),
            (
                8,
                "Conduct pre-workshop orientation",
                "Brief facilitators and participants",
                "medium",
                4,
                19,
            ),
            (
                9,
                "Facilitate workshop",
                "Lead multi-day workshop sessions",
                "critical",
                24,
                20,
            ),
            (
                10,
                "Collect participant feedback",
                "Administer evaluation forms",
                "medium",
                4,
                22,
            ),
            (
                11,
                "Prepare workshop report",
                "Document proceedings and outputs",
                "high",
                12,
                23,
            ),
            (
                12,
                "Follow up with participants",
                "Share materials and next steps",
                "medium",
                6,
                28,
            ),
        ]

        for seq, title, desc, priority, hours, days in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
            )

        # 3. Event Conference Full (15 tasks)
        template = TaskTemplate.objects.create(
            name="event_conference_full",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Large-scale conference planning",
        )

        tasks = [
            (
                1,
                "Establish conference committee",
                "Form organizing team with roles",
                "high",
                4,
                0,
            ),
            (
                2,
                "Define conference theme and objectives",
                "Set conference direction",
                "high",
                8,
                2,
            ),
            (
                3,
                "Develop conference program",
                "Plan sessions, panels, presentations",
                "high",
                20,
                5,
            ),
            (
                4,
                "Identify and invite keynote speakers",
                "Secure high-profile speakers",
                "critical",
                12,
                10,
            ),
            (
                5,
                "Call for conference papers",
                "Issue call and manage submissions",
                "high",
                8,
                15,
            ),
            (
                6,
                "Select and notify presenters",
                "Review submissions and invite presenters",
                "high",
                16,
                30,
            ),
            (
                7,
                "Secure conference venue",
                "Book venue with adequate capacity",
                "critical",
                8,
                20,
            ),
            (
                8,
                "Arrange conference logistics",
                "Coordinate accommodation, catering, AV",
                "high",
                24,
                35,
            ),
            (
                9,
                "Promote conference",
                "Marketing and participant recruitment",
                "high",
                20,
                25,
            ),
            (
                10,
                "Manage conference registration",
                "Set up system and track registrants",
                "high",
                16,
                30,
            ),
            (
                11,
                "Prepare conference materials",
                "Print programs, badges, materials",
                "medium",
                20,
                50,
            ),
            (
                12,
                "Conduct pre-conference logistics check",
                "Final walkthrough and preparations",
                "critical",
                12,
                58,
            ),
            (
                13,
                "Implement conference",
                "Execute multi-day conference",
                "critical",
                48,
                60,
            ),
            (
                14,
                "Collect participant evaluations",
                "Gather feedback on sessions",
                "medium",
                8,
                62,
            ),
            (
                15,
                "Prepare conference proceedings",
                "Compile papers and final report",
                "high",
                40,
                65,
            ),
        ]

        for seq, title, desc, priority, hours, days in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
            )

        # 4. Partnership Negotiation (6 tasks)
        template = TaskTemplate.objects.create(
            name="partnership_negotiation",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Partnership development and MOA negotiation",
        )

        tasks = [
            (
                1,
                "Identify partnership opportunities",
                "Research potential partner organizations",
                "high",
                8,
                0,
            ),
            (
                2,
                "Initial partnership meeting",
                "Discuss mutual interests and goals",
                "high",
                4,
                7,
            ),
            (
                3,
                "Draft partnership proposal",
                "Outline partnership scope and activities",
                "high",
                12,
                10,
            ),
            (
                4,
                "Negotiate partnership terms",
                "Discuss roles, resources, commitments",
                "critical",
                16,
                14,
            ),
            (5, "Draft MOA/MOU", "Prepare formal agreement document", "high", 12, 21),
            (
                6,
                "Finalize and sign partnership agreement",
                "Legal review and signing ceremony",
                "critical",
                8,
                28,
            ),
        ]

        for seq, title, desc, priority, hours, days in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
            )

        # 5. Quarterly Coordination Meeting (10 tasks)
        template = TaskTemplate.objects.create(
            name="quarterly_coordination_meeting",
            domain=StaffTask.DOMAIN_COORDINATION,
            description="Quarterly stakeholder coordination meeting",
        )

        tasks = [
            (
                1,
                "Review previous quarter activities",
                "Compile accomplishments and challenges",
                "high",
                8,
                0,
            ),
            (
                2,
                "Prepare quarterly reports",
                "Create reports for stakeholders",
                "high",
                16,
                3,
            ),
            (
                3,
                "Develop meeting agenda",
                "Plan discussion topics and presentations",
                "high",
                6,
                6,
            ),
            (
                4,
                "Invite MAO focal persons",
                "Send invitations to all partners",
                "medium",
                4,
                8,
            ),
            (
                5,
                "Prepare presentation materials",
                "Create slides and handouts",
                "high",
                12,
                10,
            ),
            (
                6,
                "Arrange meeting logistics",
                "Book venue, catering, accommodation",
                "medium",
                8,
                12,
            ),
            (
                7,
                "Conduct pre-meeting orientation",
                "Brief presenters on format",
                "medium",
                3,
                13,
            ),
            (
                8,
                "Facilitate coordination meeting",
                "Lead quarterly meeting",
                "high",
                8,
                14,
            ),
            (
                9,
                "Document meeting outcomes",
                "Prepare minutes and action plan",
                "high",
                8,
                15,
            ),
            (
                10,
                "Follow up on coordination commitments",
                "Track partner action items",
                "medium",
                12,
                21,
            ),
        ]

        for seq, title, desc, priority, hours, days in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
            )

        self.stdout.write(self.style.SUCCESS("✓ Created 5 Coordination templates"))

    def create_policy_templates(self):
        """Create policy development task templates."""
        self.stdout.write("Creating Policy templates...")

        # 1. Policy Development Full Cycle (15 tasks)
        template = TaskTemplate.objects.create(
            name="policy_development_full_cycle",
            domain=StaffTask.DOMAIN_POLICY,
            description="Complete policy development lifecycle",
        )

        tasks = [
            (
                1,
                "Identify policy issue",
                "Define problem requiring policy response",
                "high",
                8,
                0,
                StaffTask.POLICY_PHASE_DRAFTING,
            ),
            (
                2,
                "Research policy options",
                "Review best practices and precedents",
                "high",
                16,
                3,
                StaffTask.POLICY_PHASE_EVIDENCE,
            ),
            (
                3,
                "Collect evidence for policy",
                "Gather data supporting policy need",
                "high",
                24,
                7,
                StaffTask.POLICY_PHASE_EVIDENCE,
            ),
            (
                4,
                "Analyze stakeholder positions",
                "Map stakeholder interests",
                "high",
                12,
                12,
                StaffTask.POLICY_PHASE_DRAFTING,
            ),
            (
                5,
                "Draft initial policy recommendation",
                "Write first draft of policy",
                "high",
                20,
                15,
                StaffTask.POLICY_PHASE_DRAFTING,
            ),
            (
                6,
                "Internal review of draft",
                "Team review of policy draft",
                "high",
                8,
                20,
                StaffTask.POLICY_PHASE_REVIEW,
            ),
            (
                7,
                "Revise policy based on feedback",
                "Incorporate internal comments",
                "medium",
                12,
                22,
                StaffTask.POLICY_PHASE_REVIEW,
            ),
            (
                8,
                "Prepare policy brief",
                "Create executive summary document",
                "high",
                8,
                25,
                StaffTask.POLICY_PHASE_DRAFTING,
            ),
            (
                9,
                "Conduct stakeholder consultation",
                "Present policy to stakeholders",
                "critical",
                16,
                28,
                StaffTask.POLICY_PHASE_CONSULTATION,
            ),
            (
                10,
                "Analyze consultation feedback",
                "Review stakeholder input",
                "high",
                12,
                32,
                StaffTask.POLICY_PHASE_CONSULTATION,
            ),
            (
                11,
                "Finalize policy recommendation",
                "Incorporate consultation feedback",
                "high",
                16,
                35,
                StaffTask.POLICY_PHASE_DRAFTING,
            ),
            (
                12,
                "Prepare submission package",
                "Assemble all supporting documents",
                "high",
                8,
                40,
                StaffTask.POLICY_PHASE_SUBMISSION,
            ),
            (
                13,
                "Submit policy to CM Office",
                "Formal submission with cover letter",
                "critical",
                4,
                42,
                StaffTask.POLICY_PHASE_SUBMISSION,
            ),
            (
                14,
                "Respond to policy questions",
                "Address queries from reviewers",
                "high",
                12,
                50,
                StaffTask.POLICY_PHASE_SUBMISSION,
            ),
            (
                15,
                "Track policy approval status",
                "Monitor progress through approval process",
                "medium",
                8,
                55,
                StaffTask.POLICY_PHASE_MONITORING,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                policy_phase=phase,
            )

        # 2. Policy Review Cycle (5 tasks)
        template = TaskTemplate.objects.create(
            name="policy_review_cycle",
            domain=StaffTask.DOMAIN_POLICY,
            description="Policy review and revision process",
        )

        tasks = [
            (
                1,
                "Review policy draft",
                "Comprehensive review for quality",
                "high",
                8,
                0,
                StaffTask.POLICY_PHASE_REVIEW,
            ),
            (
                2,
                "Check evidence sources",
                "Verify citations and data",
                "medium",
                6,
                2,
                StaffTask.POLICY_PHASE_REVIEW,
            ),
            (
                3,
                "Provide feedback to author",
                "Write detailed review comments",
                "high",
                4,
                4,
                StaffTask.POLICY_PHASE_REVIEW,
            ),
            (
                4,
                "Review revised policy",
                "Check incorporation of feedback",
                "medium",
                4,
                7,
                StaffTask.POLICY_PHASE_REVIEW,
            ),
            (
                5,
                "Approve policy for submission",
                "Final sign-off",
                "critical",
                2,
                9,
                StaffTask.POLICY_PHASE_REVIEW,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                policy_phase=phase,
            )

        # 3. Policy Implementation (8 tasks)
        template = TaskTemplate.objects.create(
            name="policy_implementation",
            domain=StaffTask.DOMAIN_POLICY,
            description="Policy implementation and monitoring",
        )

        tasks = [
            (
                1,
                "Develop implementation plan",
                "Plan policy rollout activities",
                "high",
                16,
                0,
                StaffTask.POLICY_PHASE_IMPLEMENTATION,
            ),
            (
                2,
                "Identify implementation partners",
                "Engage stakeholders for implementation",
                "high",
                8,
                5,
                StaffTask.POLICY_PHASE_IMPLEMENTATION,
            ),
            (
                3,
                "Conduct policy orientation",
                "Brief implementers on policy",
                "high",
                8,
                10,
                StaffTask.POLICY_PHASE_IMPLEMENTATION,
            ),
            (
                4,
                "Implement policy activities",
                "Execute implementation plan",
                "critical",
                40,
                14,
                StaffTask.POLICY_PHASE_IMPLEMENTATION,
            ),
            (
                5,
                "Monitor policy implementation",
                "Track implementation progress",
                "high",
                20,
                30,
                StaffTask.POLICY_PHASE_MONITORING,
            ),
            (
                6,
                "Assess policy impact",
                "Evaluate policy outcomes",
                "high",
                24,
                60,
                StaffTask.POLICY_PHASE_MONITORING,
            ),
            (
                7,
                "Prepare implementation report",
                "Document implementation and impact",
                "high",
                16,
                90,
                StaffTask.POLICY_PHASE_MONITORING,
            ),
            (
                8,
                "Recommend policy adjustments",
                "Identify improvements based on monitoring",
                "medium",
                12,
                100,
                StaffTask.POLICY_PHASE_MONITORING,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                policy_phase=phase,
            )

        self.stdout.write(self.style.SUCCESS("✓ Created 3 Policy templates"))

    def create_services_templates(self):
        """Create service delivery task templates."""
        self.stdout.write("Creating Services templates...")

        # 1. Service Offering Setup (6 tasks)
        template = TaskTemplate.objects.create(
            name="service_offering_setup",
            domain=StaffTask.DOMAIN_SERVICES,
            description="Set up new service offering",
        )

        tasks = [
            (
                1,
                "Define service parameters",
                "Specify eligibility, benefits, process",
                "high",
                8,
                0,
                StaffTask.SERVICE_PHASE_SETUP,
            ),
            (
                2,
                "Develop application forms",
                "Create application templates",
                "high",
                8,
                3,
                StaffTask.SERVICE_PHASE_SETUP,
            ),
            (
                3,
                "Establish review criteria",
                "Define evaluation standards",
                "high",
                6,
                5,
                StaffTask.SERVICE_PHASE_SETUP,
            ),
            (
                4,
                "Set budget allocation",
                "Determine service budget",
                "critical",
                4,
                7,
                StaffTask.SERVICE_PHASE_SETUP,
            ),
            (
                5,
                "Prepare service guidelines",
                "Write operational guidelines",
                "high",
                12,
                9,
                StaffTask.SERVICE_PHASE_SETUP,
            ),
            (
                6,
                "Launch service offering",
                "Announce and open applications",
                "high",
                6,
                14,
                StaffTask.SERVICE_PHASE_SETUP,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                service_phase=phase,
            )

        # 2. Application Review Process (4 tasks)
        template = TaskTemplate.objects.create(
            name="application_review_process",
            domain=StaffTask.DOMAIN_SERVICES,
            description="Review service application",
        )

        tasks = [
            (
                1,
                "Check application completeness",
                "Verify all required documents submitted",
                "high",
                2,
                0,
                StaffTask.SERVICE_PHASE_REVIEW,
            ),
            (
                2,
                "Verify eligibility",
                "Confirm applicant meets criteria",
                "high",
                3,
                1,
                StaffTask.SERVICE_PHASE_REVIEW,
            ),
            (
                3,
                "Evaluate application",
                "Score against review criteria",
                "high",
                4,
                3,
                StaffTask.SERVICE_PHASE_REVIEW,
            ),
            (
                4,
                "Notify applicant of decision",
                "Send approval or rejection letter",
                "high",
                2,
                7,
                StaffTask.SERVICE_PHASE_REVIEW,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                service_phase=phase,
            )

        # 3. Service Delivery (5 tasks)
        template = TaskTemplate.objects.create(
            name="service_delivery",
            domain=StaffTask.DOMAIN_SERVICES,
            description="Deliver service to approved beneficiary",
        )

        tasks = [
            (
                1,
                "Prepare service delivery",
                "Arrange logistics for service provision",
                "high",
                6,
                0,
                StaffTask.SERVICE_PHASE_DELIVERY,
            ),
            (
                2,
                "Deliver service",
                "Provide service to beneficiary",
                "critical",
                8,
                3,
                StaffTask.SERVICE_PHASE_DELIVERY,
            ),
            (
                3,
                "Document service delivery",
                "Complete delivery records",
                "high",
                3,
                4,
                StaffTask.SERVICE_PHASE_DELIVERY,
            ),
            (
                4,
                "Follow up with beneficiary",
                "Check satisfaction and impact",
                "medium",
                4,
                14,
                StaffTask.SERVICE_PHASE_FOLLOWUP,
            ),
            (
                5,
                "Report on service outcomes",
                "Document results for monitoring",
                "medium",
                6,
                30,
                StaffTask.SERVICE_PHASE_REPORTING,
            ),
        ]

        for seq, title, desc, priority, hours, days, phase in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                service_phase=phase,
            )

        self.stdout.write(self.style.SUCCESS("✓ Created 3 Services templates"))

    def create_monitoring_templates(self):
        """Create monitoring and evaluation task templates."""
        self.stdout.write("Creating Monitoring templates...")

        # 1. PPA Budget Cycle (10 tasks)
        template = TaskTemplate.objects.create(
            name="ppa_budget_cycle",
            domain=StaffTask.DOMAIN_MONITORING,
            description="PPA budget formulation and monitoring",
        )

        tasks = [
            (
                1,
                "Formulate PPA budget proposal",
                "Prepare detailed budget for PPA",
                "high",
                16,
                0,
                "lead",
            ),
            (
                2,
                "Prepare budget justification",
                "Write rationale for budget request",
                "high",
                12,
                5,
                "lead",
            ),
            (
                3,
                "Review budget alignment",
                "Check alignment with policies and priorities",
                "medium",
                8,
                8,
                "reviewer",
            ),
            (
                4,
                "Submit budget proposal",
                "Submit to DBM through CM Office",
                "critical",
                4,
                12,
                "lead",
            ),
            (
                5,
                "Prepare technical hearing materials",
                "Create presentation and backup documents",
                "high",
                16,
                30,
                "contributor",
            ),
            (
                6,
                "Attend technical hearing",
                "Present and defend budget proposal",
                "critical",
                8,
                45,
                "lead",
            ),
            (
                7,
                "Revise budget based on feedback",
                "Adjust proposal per DBM comments",
                "high",
                12,
                48,
                "lead",
            ),
            (
                8,
                "Track budget allocation",
                "Monitor approval and release",
                "medium",
                8,
                90,
                "monitor",
            ),
            (
                9,
                "Monitor budget utilization",
                "Track obligations and disbursements",
                "high",
                12,
                120,
                "monitor",
            ),
            (
                10,
                "Prepare budget accountability report",
                "Report on budget performance",
                "high",
                16,
                350,
                "lead",
            ),
        ]

        for seq, title, desc, priority, hours, days, role in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                task_role=role,
            )

        # 2. PPA Technical Hearing (5 tasks)
        template = TaskTemplate.objects.create(
            name="ppa_technical_hearing",
            domain=StaffTask.DOMAIN_MONITORING,
            description="Prepare for budget technical hearing",
        )

        tasks = [
            (
                1,
                "Compile PPA performance data",
                "Gather data on past performance",
                "high",
                12,
                0,
                "contributor",
            ),
            (
                2,
                "Prepare presentation slides",
                "Create technical hearing presentation",
                "high",
                16,
                3,
                "lead",
            ),
            (
                3,
                "Develop Q&A responses",
                "Anticipate questions and prepare answers",
                "high",
                12,
                5,
                "contributor",
            ),
            (
                4,
                "Conduct mock presentation",
                "Practice presentation with team",
                "medium",
                4,
                7,
                "lead",
            ),
            (
                5,
                "Finalize hearing materials",
                "Print and organize all documents",
                "medium",
                4,
                8,
                "contributor",
            ),
        ]

        for seq, title, desc, priority, hours, days, role in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                task_role=role,
            )

        # 3. PPA Outcome Monitoring (7 tasks)
        template = TaskTemplate.objects.create(
            name="ppa_outcome_monitoring",
            domain=StaffTask.DOMAIN_MONITORING,
            description="Monitor PPA outcomes and impact",
        )

        tasks = [
            (
                1,
                "Define outcome indicators",
                "Identify indicators to track",
                "high",
                8,
                0,
                "lead",
            ),
            (
                2,
                "Establish data collection system",
                "Set up monitoring tools",
                "high",
                12,
                5,
                "contributor",
            ),
            (
                3,
                "Collect quarterly outcome data",
                "Gather data from field",
                "high",
                16,
                30,
                "monitor",
            ),
            (
                4,
                "Analyze outcome achievement",
                "Compare actual vs target outcomes",
                "high",
                12,
                95,
                "lead",
            ),
            (
                5,
                "Prepare outcome monitoring report",
                "Document findings and trends",
                "high",
                16,
                100,
                "lead",
            ),
            (
                6,
                "Conduct outcome validation",
                "Verify data accuracy with stakeholders",
                "medium",
                8,
                105,
                "reviewer",
            ),
            (
                7,
                "Recommend PPA adjustments",
                "Propose improvements based on monitoring",
                "high",
                12,
                110,
                "lead",
            ),
        ]

        for seq, title, desc, priority, hours, days, role in tasks:
            TaskTemplateItem.objects.create(
                template=template,
                title=title,
                description=desc,
                priority=priority,
                estimated_hours=hours,
                sequence=seq,
                days_from_start=days,
                task_role=role,
            )

        self.stdout.write(self.style.SUCCESS("✓ Created 3 Monitoring templates"))
