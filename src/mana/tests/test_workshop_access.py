"""Comprehensive tests for workshop access control and sequential progression."""

from datetime import date, time

import pytest

try:
    from django.contrib.auth import get_user_model
    from django.utils import timezone
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for MANA workshop access tests",
        allow_module_level=True,
    )

from common.models import Province, Region
from mana.models import (
    Assessment,
    AssessmentCategory,
    WorkshopAccessLog,
    WorkshopActivity,
    WorkshopParticipantAccount,
)
from mana.services.workshop_access import WorkshopAccessManager

User = get_user_model()


@pytest.fixture
def setup_workshop_environment(db):
    """Create complete workshop environment for testing."""
    facilitator = User.objects.create_user(
        username="facilitator@test.com",
        email="facilitator@test.com",
        password="testpass",
        is_staff=True,
    )

    category = AssessmentCategory.objects.create(
        name="Regional MANA",
        category_type="needs_assessment",
    )

    region = Region.objects.create(
        code="IX", name="Zamboanga Peninsula", is_active=True
    )
    province = Province.objects.create(
        code="ZAM",
        name="Zamboanga del Sur",
        region=region,
        is_active=True,
    )

    assessment = Assessment.objects.create(
        title="Regional Assessment 2025",
        category=category,
        description="Test assessment",
        objectives="Test objectives",
        assessment_level="regional",
        primary_methodology="workshop",
        status="data_collection",
        priority="high",
        planned_start_date=date(2025, 1, 1),
        planned_end_date=date(2025, 1, 10),
        created_by=facilitator,
        lead_assessor=facilitator,
        province=province,
    )

    # Create all 5 workshops
    workshops = []
    for i in range(1, 6):
        workshop = WorkshopActivity.objects.create(
            assessment=assessment,
            workshop_type=f"workshop_{i}",
            title=f"Workshop {i}",
            description=f"Workshop {i} description",
            workshop_day=f"day_{i}",
            scheduled_date=date(2025, 1, i),
            start_time=time(9, 0),
            end_time=time(13, 0),
            duration_hours=4.0,
            target_participants=30,
            methodology="FGD",
            expected_outputs="Insights",
            created_by=facilitator,
        )
        workshops.append(workshop)

    # Create participant
    participant_user = User.objects.create_user(
        username="participant@test.com",
        email="participant@test.com",
        password="testpass",
    )

    participant = WorkshopParticipantAccount.objects.create(
        user=participant_user,
        assessment=assessment,
        stakeholder_type="elder",
        region=province.region,
        office_business_name="Community Council",
        province=province,
        created_by=facilitator,
        current_workshop="workshop_1",
        completed_workshops=[],
        consent_given=True,
        consent_date=timezone.now(),
        profile_completed=True,
    )

    return {
        "assessment": assessment,
        "workshops": workshops,
        "facilitator": facilitator,
        "participant": participant,
        "participant_user": participant_user,
        "province": province,
    }


@pytest.mark.django_db
class TestWorkshopAccessManager:
    """Test sequential workshop access management."""

    def test_initial_access_only_workshop_1(self, setup_workshop_environment):
        """New participant should only access workshop 1."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]

        manager = WorkshopAccessManager(assessment)
        allowed = manager.get_allowed_workshops(participant)

        assert allowed == ["workshop_1"]
        assert manager.is_workshop_accessible(participant, "workshop_1")
        assert not manager.is_workshop_accessible(participant, "workshop_2")

    def test_mark_workshop_complete_advances(self, setup_workshop_environment):
        """Completing a workshop records progress without auto-advancing."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]
        facilitator = env["facilitator"]

        manager = WorkshopAccessManager(assessment)
        result = manager.mark_workshop_complete(
            participant, "workshop_1", metadata={"test": True}
        )

        assert result is True
        participant.refresh_from_db()
        assert "workshop_1" in participant.completed_workshops
        assert participant.current_workshop == "workshop_1"
        assert participant.facilitator_advanced_to == "workshop_1"

        allowed = manager.get_allowed_workshops(participant)
        assert allowed == ["workshop_1"]

        # Facilitator advancement unlocks workshop 2
        manager.advance_all_participants("workshop_2", facilitator)
        participant.refresh_from_db()
        allowed_after_advance = manager.get_allowed_workshops(participant)
        assert participant.current_workshop == "workshop_2"
        assert allowed_after_advance[:2] == ["workshop_1", "workshop_2"]

    def test_complete_all_workshops(self, setup_workshop_environment):
        """Complete all 5 workshops sequentially."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]
        facilitator = env["facilitator"]

        manager = WorkshopAccessManager(assessment)

        # Complete all workshops
        for i in range(1, 6):
            workshop_type = f"workshop_{i}"
            result = manager.mark_workshop_complete(participant, workshop_type)
            assert result is True
            if i < 5:
                manager.advance_all_participants(f"workshop_{i + 1}", facilitator)

        participant.refresh_from_db()
        assert len(participant.completed_workshops) == 5
        assert participant.current_workshop == "workshop_5"
        assert participant.facilitator_advanced_to == "workshop_5"

    def test_cannot_complete_already_completed(self, setup_workshop_environment):
        """Cannot mark same workshop complete twice."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]

        manager = WorkshopAccessManager(assessment)
        manager.mark_workshop_complete(participant, "workshop_1")

        # Second attempt should return False
        result = manager.mark_workshop_complete(participant, "workshop_1")
        assert result is False

    def test_access_log_created(self, setup_workshop_environment):
        """Access actions should be logged."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]

        manager = WorkshopAccessManager(assessment)
        manager.mark_workshop_complete(participant, "workshop_1")

        logs = WorkshopAccessLog.objects.filter(
            participant=participant, action_type="complete"
        )
        assert logs.count() == 1

    def test_reset_participant_progress(self, setup_workshop_environment):
        """Facilitator can reset participant progress."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]
        facilitator = env["facilitator"]

        manager = WorkshopAccessManager(assessment)

        # Complete some workshops
        manager.mark_workshop_complete(participant, "workshop_1")
        manager.mark_workshop_complete(participant, "workshop_2")

        # Reset
        result = manager.reset_participant_progress(participant, facilitator)
        assert result is True

        participant.refresh_from_db()
        assert participant.completed_workshops == []
        assert participant.current_workshop == "workshop_1"

    def test_advance_all_participants(self, setup_workshop_environment):
        """Facilitator can advance all participants to specific workshop."""
        env = setup_workshop_environment
        assessment = env["assessment"]
        facilitator = env["facilitator"]

        # Create second participant
        user2 = User.objects.create_user(
            username="participant2@test.com",
            email="participant2@test.com",
            password="testpass",
        )
        participant2 = WorkshopParticipantAccount.objects.create(
            user=user2,
            assessment=assessment,
            stakeholder_type="youth_leader",
            region=env["province"].region,
            office_business_name="Youth Org",
            province=env["province"],
            created_by=facilitator,
            current_workshop="workshop_1",
            completed_workshops=[],
            consent_given=True,
            profile_completed=True,
        )

        manager = WorkshopAccessManager(assessment)
        count = manager.advance_all_participants("workshop_2", facilitator)

        assert count == 2  # Both participants advanced

    def test_progress_summary(self, setup_workshop_environment):
        """Progress summary should calculate correctly."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]
        facilitator = env["facilitator"]

        manager = WorkshopAccessManager(assessment)

        # Complete 2 workshops
        manager.mark_workshop_complete(participant, "workshop_1")
        manager.advance_all_participants("workshop_2", facilitator)
        manager.mark_workshop_complete(participant, "workshop_2")

        participant.refresh_from_db()
        summary = manager.get_progress_summary(participant)

        assert summary["completed_count"] == 2
        assert summary["total_workshops"] == 5
        assert summary["completion_percentage"] == 40.0
        assert summary["current_workshop"] == "workshop_2"
        assert summary["next_workshop"] == "workshop_3"

    def test_assessment_progress_summary(self, setup_workshop_environment):
        """Assessment-level progress tracking works."""
        env = setup_workshop_environment
        assessment = env["assessment"]
        facilitator = env["facilitator"]
        participant1 = env["participant"]

        # Create second participant who completes more
        user2 = User.objects.create_user(
            username="participant2@test.com",
            email="participant2@test.com",
            password="testpass",
        )
        participant2 = WorkshopParticipantAccount.objects.create(
            user=user2,
            assessment=assessment,
            stakeholder_type="farmer",
            region=env["province"].region,
            office_business_name="Farmers Assoc",
            province=env["province"],
            created_by=facilitator,
            current_workshop="workshop_1",
            completed_workshops=[],
            consent_given=True,
            profile_completed=True,
        )

        manager = WorkshopAccessManager(assessment)

        # Participant 1 completes 2 workshops
        manager.mark_workshop_complete(participant1, "workshop_1")
        manager.mark_workshop_complete(participant2, "workshop_1")
        manager.advance_all_participants("workshop_2", facilitator)

        manager.mark_workshop_complete(participant1, "workshop_2")
        manager.mark_workshop_complete(participant2, "workshop_2")
        manager.advance_all_participants("workshop_3", facilitator)

        # Participant 2 completes remaining workshops with facilitator advancement
        manager.mark_workshop_complete(participant2, "workshop_3")
        manager.advance_all_participants("workshop_4", facilitator)
        manager.mark_workshop_complete(participant2, "workshop_4")
        manager.advance_all_participants("workshop_5", facilitator)
        manager.mark_workshop_complete(participant2, "workshop_5")

        summary = manager.get_assessment_progress_summary()

        assert summary["total_participants"] == 2
        assert summary["fully_completed"] == 1
        assert summary["by_workshop"]["workshop_1"]["completed"] == 2
        assert summary["by_workshop"]["workshop_5"]["completed"] == 1


@pytest.mark.django_db
class TestWorkshopAccessControl:
    """Test permission boundaries and access restrictions."""

    def test_participant_cannot_skip_workshops(self, setup_workshop_environment):
        """Participant cannot access future workshops without completing previous."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]

        manager = WorkshopAccessManager(assessment)

        # Should not be able to access workshop 3 without completing 1 and 2
        assert not manager.is_workshop_accessible(participant, "workshop_3")

    def test_completed_workshops_remain_accessible(self, setup_workshop_environment):
        """Completed workshops should remain accessible for review."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]
        facilitator = env["facilitator"]

        manager = WorkshopAccessManager(assessment)
        manager.mark_workshop_complete(participant, "workshop_1")
        manager.advance_all_participants("workshop_2", facilitator)
        manager.mark_workshop_complete(participant, "workshop_2")
        manager.advance_all_participants("workshop_3", facilitator)

        participant.refresh_from_db()
        # Workshop 1 should still be accessible
        assert manager.is_workshop_accessible(participant, "workshop_1")
        assert manager.is_workshop_accessible(participant, "workshop_2")
        # Current workshop (3) should be accessible after facilitator advancement
        assert manager.is_workshop_accessible(participant, "workshop_3")

    def test_manual_unlock_by_facilitator(self, setup_workshop_environment):
        """Facilitator can manually unlock any workshop."""
        env = setup_workshop_environment
        participant = env["participant"]
        assessment = env["assessment"]
        facilitator = env["facilitator"]

        manager = WorkshopAccessManager(assessment)

        # Manually unlock workshop 4 (skipping 2 and 3)
        result = manager.unlock_workshop(participant, "workshop_4", facilitator)
        assert result is True

        participant.refresh_from_db()
        assert participant.current_workshop == "workshop_4"

        # Unlock log should exist
        logs = WorkshopAccessLog.objects.filter(
            participant=participant,
            action_type="unlock",
            workshop__workshop_type="workshop_4",
        )
        assert logs.exists()
