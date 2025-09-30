"""Tests for the OOBC staff management dashboard."""

import json
from datetime import date, timedelta

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from common.constants import STAFF_TEAM_DEFINITIONS
from common.models import (
    PerformanceTarget,
    StaffDevelopmentPlan,
    StaffProfile,
    StaffTask,
    StaffTeam,
    StaffTeamMembership,
    TrainingEnrollment,
    TrainingProgram,
    User,
)


class StaffManagementViewTests(TestCase):
    """Validate staff management flows for profiles, tasks, and teams."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="pass1234",
            user_type="admin",
            is_staff=True,
            is_superuser=True,
            is_approved=True,
        )
        self.staff_member = User.objects.create_user(
            username="staff",
            password="pass1234",
            user_type="oobc_staff",
            is_approved=True,
        )
        self.staff_member.first_name = "Active"
        self.staff_member.last_name = "Member"
        self.staff_member.position = "Policy Officer"
        self.staff_member.save(update_fields=["first_name", "last_name", "position"])
        self.url = reverse("common:staff_management")
        self.task_create_url = reverse("common:staff_task_create")
        self.task_board_url = reverse("common:staff_task_board")
        self.team_assign_url = reverse("common:staff_team_assign")
        self.team_manage_url = reverse("common:staff_team_manage")
        self.profile_list_url = reverse("common:staff_profiles_list")
        self.profile_create_url = reverse("common:staff_profile_create")
        self.client.force_login(self.admin)

    def test_default_teams_are_seeded(self):
        """The dashboard seeds the configured default teams when missing."""

        StaffTeam.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(
            StaffTeam.objects.count(), len(STAFF_TEAM_DEFINITIONS)
        )

    def test_create_task_and_auto_membership(self):
        """Submitting the task form creates a task and links assignee to the team."""

        self.client.get(self.task_create_url)  # ensure default teams exist
        team = StaffTeam.objects.first()
        post_data = {
            "title": "Draft provincial coordination brief",
            "teams": [str(team.id)],
            "assignees": [str(self.staff_member.id)],
            "priority": "high",
            "status": "in_progress",
            "impact": "Aligns inter-agency inputs ahead of the coordination call.",
            "description": "Collect partner notes and draft talking points.",
            "start_date": timezone.now().date().isoformat(),
            "due_date": (timezone.now().date() + timedelta(days=3)).isoformat(),
            "progress": "40",
        }

        response = self.client.post(self.task_create_url, post_data)

        if response.status_code == 200:
            form_errors = response.context["form"].errors.as_json()
            self.fail(f"Task form validation errors: {form_errors}")
        self.assertEqual(response.status_code, 302)
        task = StaffTask.objects.get(title="Draft provincial coordination brief")
        self.assertIn(team, task.teams.all())
        self.assertIn(self.staff_member, task.assignees.all())
        self.assertEqual(task.created_by, self.admin)
        self.assertEqual(task.status, StaffTask.STATUS_IN_PROGRESS)
        self.assertTrue(
            StaffTeamMembership.objects.filter(
                team=team, user=self.staff_member, is_active=True
            ).exists()
        )

    def test_staff_management_points_to_task_board(self):
        """The staff hub links to the dedicated task board instead of embedding it."""

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task_board_url)
        self.assertNotContains(response, "Task management & calendar")

    def test_assign_staff_to_team_view(self):
        """Submission on the team assignment page activates membership."""

        self.client.get(self.team_assign_url)
        team = StaffTeam.objects.first()
        post_data = {
            "team": str(team.id),
            "user": str(self.staff_member.id),
            "role": StaffTeamMembership.ROLE_COORDINATOR,
            "is_active": "on",
            "notes": "Oversees inter-agency updates.",
        }

        response = self.client.post(self.team_assign_url, post_data)

        if response.status_code == 200:
            errors = response.context["form"].errors.as_json()
            self.fail(f"Assignment form errors: {errors}")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            StaffTeamMembership.objects.filter(
                team=team, user=self.staff_member, role=StaffTeamMembership.ROLE_COORDINATOR
            ).exists()
        )

    def test_manage_team_create_view(self):
        """Team management page persists new teams."""

        response = self.client.post(
            self.team_manage_url,
            {
                "form_name": "team",
                "name": "Innovation Unit",
                "description": "Drives experimentation across programmes.",
                "mission": "Surface prototypes into scalable interventions.",
                "focus_areas": "Pilot design\nKnowledge exchange",
                "is_active": "on",
            },
        )

        if response.status_code == 200:
            errors = response.context["form"].errors.as_json()
            self.fail(f"Team form errors: {errors}")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(StaffTeam.objects.filter(name="Innovation Unit").exists())

    def test_seed_staff_workflows_command(self):
        """Management command seeds demo tasks and memberships."""

        StaffTeam.objects.all().delete()
        StaffTask.objects.all().delete()

        call_command("seed_staff_workflows")

        self.assertGreater(StaffTeam.objects.count(), 0)
        self.assertGreater(StaffTask.objects.count(), 0)

    def test_staff_task_board_view(self):
        """Task board renders grouped tasks and accepts status updates."""

        team = StaffTeam.objects.create(name="Coordination Unit")
        task = StaffTask.objects.create(
            title="Prepare coordination brief",
            created_by=self.admin,
        )
        task.teams.add(team)
        task.assignees.set([self.staff_member])

        board_url = reverse("common:staff_task_board")
        response = self.client.get(board_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Staff Task Board")
        self.assertContains(response, task.title)

        response = self.client.post(
            board_url,
            {
                "form_name": "update_task",
                "task_id": task.id,
                "status": StaffTask.STATUS_COMPLETED,
                "progress": 100,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, StaffTask.STATUS_COMPLETED)

    def test_staff_task_board_table_view(self):
        """Table view renders column headers and rows for tasks."""

        team = StaffTeam.objects.create(name="Operations")
        task = StaffTask.objects.create(
            title="Publish weekly bulletin",
            created_by=self.admin,
            due_date=date.today(),
        )
        task.teams.add(team)
        task.assignees.set([self.staff_member])

        response = self.client.get(self.task_board_url, {"view": "table"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["view_mode"], "table")
        self.assertContains(response, "Actions")
        self.assertContains(response, "Publish weekly bulletin")

    def test_staff_task_board_partial_switches_to_board_mode(self):
        """HTMX board partial requests should always return board data."""

        team = StaffTeam.objects.create(name="Innovation")
        task = StaffTask.objects.create(
            title="Prototype new workflow",
            created_by=self.admin,
        )
        task.teams.add(team)

        response = self.client.get(
            self.task_board_url,
            {"view": "table", "partial": "board"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("board_refresh_url", response.context)
        self.assertEqual(response.context["view_mode"], "board")
        self.assertContains(response, "Prototype new workflow")

    def test_staff_task_board_group_by_team(self):
        """Board grouping by team shows the team column helper text."""

        team = StaffTeam.objects.create(name="Rapid Response")
        task = StaffTask.objects.create(
            title="Coordinate field deployment",
            created_by=self.admin,
        )
        task.teams.add(team)

        response = self.client.get(self.task_board_url, {"group": "team"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["group_by"], "team")
        self.assertContains(response, "Rapid Response")
        self.assertContains(response, "Tasks without team ownership")

    def test_staff_task_board_sort_order(self):
        """Table sort direction updates the ordered context list."""

        team = StaffTeam.objects.create(name="Metrics")
        older = StaffTask.objects.create(
            title="Compile quarterly report",
            created_by=self.admin,
            due_date=date(2024, 1, 15),
        )
        older.teams.add(team)
        newer = StaffTask.objects.create(
            title="Publish monthly digest",
            created_by=self.admin,
            due_date=date(2024, 3, 10),
        )
        newer.teams.add(team)

        response = self.client.get(
            self.task_board_url,
            {"view": "table", "sort": "due_date", "order": "desc"},
        )

        self.assertEqual(response.status_code, 200)
        tasks = list(response.context["tasks"])
        self.assertTrue(tasks)
        self.assertEqual(tasks[0], newer)
        self.assertEqual(tasks[-1], older)

    def test_staff_task_board_update_preserves_view(self):
        """Posting an update with a next parameter redirects back to the same view."""

        team = StaffTeam.objects.create(name="Comms")
        task = StaffTask.objects.create(
            title="Refresh talking points",
            created_by=self.admin,
        )
        task.teams.add(team)

        next_url = f"{self.task_board_url}?view=table&sort=due_date"
        response = self.client.post(
            self.task_board_url,
            {
                "form_name": "update_task",
                "task_id": task.id,
                "status": StaffTask.STATUS_IN_PROGRESS,
                "progress": 25,
                "next": next_url,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], next_url)

    def test_staff_task_update_status_endpoint(self):
        """Drag API updates status and progress for completed tasks."""

        team = StaffTeam.objects.create(name="Planning")
        task = StaffTask.objects.create(
            title="Roll up provincial inputs",
            created_by=self.admin,
            status=StaffTask.STATUS_IN_PROGRESS,
            progress=40,
        )
        task.teams.add(team)

        update_url = reverse("common:staff_task_update")
        response = self.client.post(
            update_url,
            data=json.dumps(
                {
                    "task_id": task.id,
                    "group": "status",
                    "value": StaffTask.STATUS_COMPLETED,
                    "order": [task.id],
                }
            ),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        task.refresh_from_db()
        self.assertEqual(task.status, StaffTask.STATUS_COMPLETED)
        self.assertEqual(task.progress, 100)
        self.assertIsNotNone(task.completed_at)

    def test_staff_task_update_team_reassignment(self):
        """Switching columns grouped by team reassigns the task."""

        source = StaffTeam.objects.create(name="Ops")
        target = StaffTeam.objects.create(name="Comms")
        task = StaffTask.objects.create(
            title="Coordinate provincial rollout",
            created_by=self.admin,
        )
        task.teams.add(source)
        task.assignees.set([self.staff_member])

        update_url = reverse("common:staff_task_update")
        response = self.client.post(
            update_url,
            data=json.dumps(
                {
                    "task_id": task.id,
                    "group": "team",
                    "value": target.slug,
                    "order": [task.id],
                }
            ),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["task"]["team"], target.name)
        task.refresh_from_db()
        self.assertIn(target, task.teams.all())
        self.assertTrue(
            StaffTeamMembership.objects.filter(team=target, user=self.staff_member).exists()
        )

    def test_staff_task_update_rejects_unknown_group(self):
        """Unknown group values are rejected with a 400 response."""

        team = StaffTeam.objects.create(name="Logistics")
        task = StaffTask.objects.create(
            title="Draft logistics plan",
            created_by=self.admin,
        )
        task.teams.add(team)

        update_url = reverse("common:staff_task_update")
        response = self.client.post(
            update_url,
            {
                "task_id": task.id,
                "group": "unknown",
                "value": "noop",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_staff_task_modal_get(self):
        """Modal endpoint renders the task form for editing."""

        team = StaffTeam.objects.create(name="Strategy")
        task = StaffTask.objects.create(
            title="Coordinate outreach",
            created_by=self.admin,
        )
        task.teams.add(team)

        modal_url = reverse("common:staff_task_modal", args=[task.id])
        response = self.client.get(modal_url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Save changes")
        self.assertContains(response, task.title)

    def test_staff_task_modal_create_prefills_selected_team(self):
        """Creating a task via HX request preloads the selected team."""

        team = StaffTeam.objects.create(name="Rapid Response")

        modal_url = reverse("common:staff_task_modal_create")
        response = self.client.get(
            modal_url,
            {"team": team.slug},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        selected_teams = form["teams"].value()
        if isinstance(selected_teams, str):
            selected_teams = [selected_teams]
        selected_team_ids = {str(value) for value in selected_teams or []}
        self.assertIn(str(team.pk), selected_team_ids)
        self.assertContains(response, team.name)
        self.assertContains(response, "Save task")

    def test_staff_task_modal_update(self):
        """Posting to the modal saves updates and triggers refresh events."""

        team = StaffTeam.objects.create(name="Field Ops")
        new_team = StaffTeam.objects.create(name="Planning")
        task = StaffTask.objects.create(
            title="Conduct field visit",
            created_by=self.admin,
            status=StaffTask.STATUS_IN_PROGRESS,
            progress=40,
        )
        task.teams.add(team)
        task.assignees.set([self.staff_member])

        modal_url = reverse("common:staff_task_modal", args=[task.id])
        response = self.client.post(
            modal_url,
            {
                "title": "Conduct field visit - Updated",
                "teams": [str(new_team.id)],
                "assignees": [str(self.staff_member.id)],
                "priority": StaffTask.PRIORITY_HIGH,
                "status": StaffTask.STATUS_COMPLETED,
                "impact": "Ensure partner alignment.",
                "description": "Coordinate with local stakeholders.",
                "start_date": timezone.now().date().isoformat(),
                "due_date": (timezone.now().date() + timedelta(days=2)).isoformat(),
                "progress": "100",
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 204)
        trigger = response.headers.get("HX-Trigger")
        self.assertIsNotNone(trigger)
        self.assertIn("task-board-refresh", trigger)
        task.refresh_from_db()
        self.assertEqual(task.title, "Conduct field visit - Updated")
        self.assertIn(new_team, task.teams.all())
        self.assertEqual(task.progress, 100)
        self.assertIn(self.staff_member, task.assignees.all())
        self.assertEqual(task.status, StaffTask.STATUS_COMPLETED)

    def test_staff_task_delete_requires_confirm(self):
        """Deleting without explicit confirmation returns an error."""

        team = StaffTeam.objects.create(name="Ops Center")
        task = StaffTask.objects.create(
            title="Prepare daily brief",
            created_by=self.admin,
        )
        task.teams.add(team)

        delete_url = reverse("common:staff_task_delete", args=[task.id])
        response = self.client.post(delete_url, {}, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertTrue(StaffTask.objects.filter(pk=task.id).exists())

    def test_staff_task_delete_success(self):
        """Confirmed deletion removes the task and signals a refresh."""

        team = StaffTeam.objects.create(name="Design")
        task = StaffTask.objects.create(
            title="Update briefing deck",
            created_by=self.admin,
        )
        task.teams.add(team)

        delete_url = reverse("common:staff_task_delete", args=[task.id])
        response = self.client.post(
            delete_url,
            {"confirm": "yes"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 204)
        trigger = response.headers.get("HX-Trigger")
        self.assertIsNotNone(trigger)
        self.assertIn("task-board-refresh", trigger)
        self.assertFalse(StaffTask.objects.filter(pk=task.id).exists())

    def test_staff_task_inline_update_changes_title(self):
        """Inline table editing updates key fields and redirects back."""

        team = StaffTeam.objects.create(name="Original")
        new_team = StaffTeam.objects.create(name="Updated Team")
        task = StaffTask.objects.create(
            title="Initial title",
            created_by=self.admin,
            status=StaffTask.STATUS_NOT_STARTED,
            progress=10,
        )
        task.teams.add(team)
        task.assignees.set([self.staff_member])

        inline_url = reverse("common:staff_task_inline_update", args=[task.id])
        next_url = f"{self.task_board_url}?view=table"
        response = self.client.post(
            inline_url,
            {
                "title": "Revised title",
                "teams": [str(new_team.id)],
                "assignees": [str(self.staff_member.id)],
                "priority": StaffTask.PRIORITY_HIGH,
                "status": StaffTask.STATUS_IN_PROGRESS,
                "impact": task.impact,
                "description": task.description,
                "start_date": timezone.now().date().isoformat(),
                "due_date": (timezone.now().date() + timedelta(days=3)).isoformat(),
                "progress": "55",
                "linked_event": "",
                "next": next_url,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], next_url)
        task.refresh_from_db()
        self.assertEqual(task.title, "Revised title")
        self.assertIn(new_team, task.teams.all())
        self.assertEqual(task.status, StaffTask.STATUS_IN_PROGRESS)
        self.assertEqual(task.progress, 55)

    def test_staff_task_reorder_within_column(self):
        """Reordering tasks updates board positions sequentially."""

        team = StaffTeam.objects.create(name="Strategy")
        task_a = StaffTask.objects.create(
            title="Draft roadmap",
            created_by=self.admin,
            status=StaffTask.STATUS_IN_PROGRESS,
        )
        task_a.teams.add(team)
        task_b = StaffTask.objects.create(
            title="Collect inputs",
            created_by=self.admin,
            status=StaffTask.STATUS_IN_PROGRESS,
        )
        task_b.teams.add(team)
        task_c = StaffTask.objects.create(
            title="Prepare digest",
            created_by=self.admin,
            status=StaffTask.STATUS_IN_PROGRESS,
        )
        task_c.teams.add(team)

        update_url = reverse("common:staff_task_update")
        response = self.client.post(
            update_url,
            data=json.dumps(
                {
                    "task_id": task_c.id,
                    "group": "status",
                    "value": StaffTask.STATUS_IN_PROGRESS,
                    "order": [task_c.id, task_b.id, task_a.id],
                }
            ),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        task_a.refresh_from_db()
        task_b.refresh_from_db()
        task_c.refresh_from_db()
        self.assertEqual(task_c.board_position, 1)
        self.assertEqual(task_b.board_position, 2)
        self.assertEqual(task_a.board_position, 3)

    def test_staff_task_move_resequences_source_column(self):
        """Moving between columns resequences both target and source."""

        team = StaffTeam.objects.create(name="Insights")
        first = StaffTask.objects.create(
            title="Assemble report",
            created_by=self.admin,
            status=StaffTask.STATUS_NOT_STARTED,
        )
        first.teams.add(team)
        second = StaffTask.objects.create(
            title="Review data",
            created_by=self.admin,
            status=StaffTask.STATUS_NOT_STARTED,
        )
        second.teams.add(team)
        third = StaffTask.objects.create(
            title="Brief leadership",
            created_by=self.admin,
            status=StaffTask.STATUS_IN_PROGRESS,
        )
        third.teams.add(team)
        fourth = StaffTask.objects.create(
            title="Vet talking points",
            created_by=self.admin,
            status=StaffTask.STATUS_IN_PROGRESS,
        )
        fourth.teams.add(team)

        update_url = reverse("common:staff_task_update")
        response = self.client.post(
            update_url,
            data=json.dumps(
                {
                    "task_id": third.id,
                    "group": "status",
                    "value": StaffTask.STATUS_NOT_STARTED,
                    "order": [third.id, first.id, second.id],
                    "source_value": StaffTask.STATUS_IN_PROGRESS,
                    "source_order": [fourth.id],
                }
            ),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        first.refresh_from_db()
        second.refresh_from_db()
        third.refresh_from_db()
        fourth.refresh_from_db()
        self.assertEqual([third.board_position, first.board_position, second.board_position], [1, 2, 3])
        self.assertEqual(third.status, StaffTask.STATUS_NOT_STARTED)
        self.assertEqual(fourth.board_position, 1)

    def test_staff_profile_create_view(self):
        """Creating a staff profile stores competencies and metadata."""

        post_data = {
            "user": str(self.staff_member.id),
            "employment_status": "active",
            "employment_type": "regular",
            "position_classification": "Supervisory",
            "plantilla_item_number": "OSEC-BTA-PAO6-123",
            "salary_grade": "SG 24",
            "salary_step": "2",
            "reports_to": "PAO VI",
            "primary_location": "Cotabato City",
            "job_purpose": "Provide strategic legislative support to MP Uy-Oyod.",
            "key_result_areas": "Legislative research\nCalendar management",
            "major_functions": "Draft bills\nMentor legislative staff",
            "deliverables": "Briefers every session\nLegislative calendars",
            "supervision_lines": "Reports to COS/PAO VI\nConducts weekly team huddle",
            "cross_functional_partners": "Public information team\nPolitical affairs officers",
            "core_competencies": "Critical, Creative, and Strategic Thinking\nEffective Communication",
            "leadership_competencies": "Planning for Organizational and Systems Change",
            "functional_competencies": "PAO · Stakeholder Engagement, Community Organizing, and Constituency Building",
            "qualification_education": "Bachelor's degree relevant to the job",
            "qualification_training": "8 hours of relevant training",
            "qualification_experience": "2 years in legislative work",
            "qualification_eligibility": "Career Service Professional / BARMM Eligibility",
            "qualification_competency": "Critical Thinking – Proficient\nEffective Communication – Exemplary",
            "job_documents_url": "https://example.com/job-design",
            "notes": "Field coordinator for Western Mindanao",
        }

        response = self.client.post(self.profile_create_url, post_data)

        if response.status_code == 200:
            errors = response.context["form"].errors.as_json()
            self.fail(f"Profile form validation errors: {errors}")

        self.assertEqual(response.status_code, 302)
        profile = StaffProfile.objects.get(user=self.staff_member)
        self.assertEqual(profile.primary_location, "Cotabato City")
        self.assertIn("Critical, Creative, and Strategic Thinking", profile.core_competencies)
        self.assertEqual(profile.position_classification, "Supervisory")
        self.assertEqual(profile.salary_grade, "SG 24")
        self.assertIn("Legislative research", profile.key_result_areas)
        self.assertEqual(profile.qualification_training, "8 hours of relevant training")

    def test_staff_profile_update_view(self):
        """Updating a staff profile persists changes to JSON fields."""

        profile = StaffProfile.objects.create(
            user=self.staff_member,
            primary_location="Cotabato",
            core_competencies=["Effective Communication"],
            position_classification="Support",
            key_result_areas=["Research"],
        )
        update_url = reverse("common:staff_profile_update", args=[profile.pk])

        response = self.client.post(
            update_url,
            {
                "user": str(self.staff_member.id),
                "staff_member_name": self.staff_member.get_full_name(),
                "staff_member_username": self.staff_member.username,
                "staff_member_position": self.staff_member.position,
                "employment_status": "on_leave",
                "employment_type": "consultant",
                "position_classification": "Supervisory",
                "plantilla_item_number": "OSEC-BTA-PAO6-321",
                "salary_grade": "SG 25",
                "salary_step": "1",
                "reports_to": "MP Uy-Oyod",
                "primary_location": "General Santos",
                "job_purpose": "Leads legislative affairs portfolio.",
                "key_result_areas": "Research\nStakeholder coordination",
                "major_functions": "Draft plenary speeches\nSupervise staff",
                "deliverables": "Weekly progress reports",
                "supervision_lines": "Coordinates with COS\nHosts daily stand-up",
                "cross_functional_partners": "Media team",
                "core_competencies": "Effective Communication\nSynergistic Collaboration",
                "leadership_competencies": "Leading and Influencing Change",
                "functional_competencies": "LSO · Policy Making, Analysis, and Evaluation",
                "qualification_education": "Bachelor's degree",
                "qualification_training": "16 hours training",
                "qualification_experience": "3 years relevant experience",
                "qualification_eligibility": "Professional Eligibility",
                "qualification_competency": "Critical Thinking – Exemplary",
                "job_documents_url": "https://example.org/updated-jd",
                "notes": "Temporarily supporting policy drafting.",
            },
        )

        if response.status_code == 200:
            errors = response.context["form"].errors.as_json()
            self.fail(f"Profile update errors: {errors}")

        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertEqual(profile.employment_status, StaffProfile.STATUS_ON_LEAVE)
        self.assertIn("Synergistic Collaboration", profile.core_competencies)
        self.assertEqual(profile.position_classification, "Supervisory")
        self.assertEqual(profile.job_purpose, "Leads legislative affairs portfolio.")
        self.assertIn("Research", profile.key_result_areas)
        self.assertEqual(profile.qualification_experience, "3 years relevant experience")

    def test_staff_profile_delete_flow(self):
        """Deleting a profile removes the record."""

        profile = StaffProfile.objects.create(user=self.staff_member)
        delete_url = reverse("common:staff_profile_delete", args=[profile.pk])

        response = self.client.post(delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(StaffProfile.objects.filter(pk=profile.pk).exists())

    def test_staff_profile_list_filters(self):
        """List view supports status and team filtering."""

        profile_active = StaffProfile.objects.create(user=self.staff_member)
        inactive_user = User.objects.create_user(
            username="inactive.staff",
            password="pass1234",
            user_type="oobc_staff",
            is_approved=True,
        )
        inactive_user.first_name = "Inactive"
        inactive_user.last_name = "Member"
        inactive_user.save(update_fields=["first_name", "last_name"])
        profile_inactive = StaffProfile.objects.create(
            user=inactive_user,
            employment_status=StaffProfile.STATUS_INACTIVE,
        )
        team = StaffTeam.objects.create(name="Planning and Budgeting Team")
        StaffTeamMembership.objects.create(team=team, user=profile_active.user)

        response = self.client.get(self.profile_list_url, {"status": "inactive"})
        self.assertContains(response, profile_inactive.user.get_full_name())
        self.assertNotContains(response, profile_active.user.get_full_name())

        response = self.client.get(self.profile_list_url, {"team": team.slug})
        self.assertContains(response, profile_active.user.get_full_name())

    def test_staff_profiles_autocreation_from_directory(self):
        """Visiting the profiles list back-fills missing StaffProfile records."""

        StaffProfile.objects.all().delete()

        response = self.client.get(self.profile_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            StaffProfile.objects.filter(user=self.staff_member).exists()
        )
        self.assertContains(response, self.staff_member.get_full_name())

    def test_staff_performance_dashboard_target_creation(self):
        """Creating a performance target via dashboard persists record."""

        profile = StaffProfile.objects.create(user=self.staff_member)
        url = reverse("common:staff_performance_dashboard")

        response = self.client.post(
            url,
            {
                "form_name": "performance_target",
                "scope": PerformanceTarget.SCOPE_STAFF,
                "staff_profile": profile.id,
                "metric_name": "Policy briefs completed",
                "performance_standard": "Deliver briefs with 95% quality score",
                "target_value": "5",
                "actual_value": "2",
                "unit": "briefs",
                "status": PerformanceTarget.STATUS_AT_RISK,
                "period_start": timezone.now().date().isoformat(),
                "period_end": (timezone.now().date() + timedelta(days=90)).isoformat(),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            PerformanceTarget.objects.filter(
                staff_profile=profile, metric_name="Policy briefs completed"
            ).exists()
        )

    def test_staff_training_development_forms(self):
        """Training dashboard accepts programme, enrollment, and plan submissions."""

        profile = StaffProfile.objects.create(user=self.staff_member)
        url = reverse("common:staff_training_development")

        # Create programme
        response = self.client.post(
            url,
            {
                "form_name": "program",
                "program-title": "Data Storytelling",
                "program-category": "Monitoring",
                "program-description": "Transform monitoring results into narratives.",
                "program-delivery_mode": "hybrid",
                "program-competency_focus": "Monitoring, Reporting, & Evaluation",
                "program-duration_days": 3,
                "program-is_active": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        program = TrainingProgram.objects.get(title="Data Storytelling")

        # Create enrollment
        response = self.client.post(
            url,
            {
                "form_name": "enrollment",
                "enroll-staff_profile": profile.id,
                "enroll-program": program.id,
                "enroll-status": TrainingEnrollment.STATUS_PLANNED,
                "enroll-scheduled_date": timezone.now().date().isoformat(),
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            TrainingEnrollment.objects.filter(
                staff_profile=profile, program=program
            ).exists()
        )

        # Create development plan
        response = self.client.post(
            url,
            {
                "form_name": "plan",
                "plan-staff_profile": profile.id,
                "plan-title": "Strengthen community engagement skills",
                "plan-competency_focus": "PAO · Stakeholder Engagement, Community Organizing, and Constituency Building",
                "plan-status": StaffDevelopmentPlan.STATUS_IN_PROGRESS,
                "plan-target_date": (timezone.now().date() + timedelta(days=60)).isoformat(),
                "plan-support_needed": "Shadow experienced PAOs",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            StaffDevelopmentPlan.objects.filter(
                staff_profile=profile, title="Strengthen community engagement skills"
            ).exists()
        )
