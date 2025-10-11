"""Comprehensive tests for AI workshop synthesis."""

from datetime import date, time

import pytest

try:
    from django.contrib.auth import get_user_model
    from django.utils import timezone
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for MANA workshop synthesis tests",
        allow_module_level=True,
    )

from common.models import Province, Region
from mana.models import (
    Assessment,
    AssessmentCategory,
    WorkshopActivity,
    WorkshopParticipantAccount,
    WorkshopResponse,
    WorkshopSynthesis,
)
from mana.services.workshop_synthesis import AIWorkshopSynthesizer

User = get_user_model()


@pytest.fixture
def synthesis_setup(db):
    """Create environment for synthesis testing."""
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
    province1 = Province.objects.create(
        code="ZAM",
        name="Zamboanga del Sur",
        region=region,
        is_active=True,
    )
    province2 = Province.objects.create(
        code="ZAN",
        name="Zamboanga del Norte",
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
        province=province1,
    )

    workshop = WorkshopActivity.objects.create(
        assessment=assessment,
        workshop_type="workshop_1",
        title="Workshop 1: Context Understanding",
        description="Understanding community context",
        workshop_day="day_1",
        scheduled_date=date(2025, 1, 1),
        start_time=time(9, 0),
        end_time=time(13, 0),
        duration_hours=4.0,
        target_participants=30,
        methodology="FGD",
        expected_outputs="Context insights",
        created_by=facilitator,
    )

    # Create participants from different provinces and stakeholder types
    participants = []
    for i, (prov, stakeholder) in enumerate(
        [
            (province1, "elder"),
            (province1, "women_leader"),
            (province2, "youth_leader"),
            (province2, "farmer"),
        ]
    ):
        user = User.objects.create_user(
            username=f"participant{i}@test.com",
            email=f"participant{i}@test.com",
            password="testpass",
        )
        participant = WorkshopParticipantAccount.objects.create(
            user=user,
            assessment=assessment,
            stakeholder_type=stakeholder,
            region=prov.region,
            office_business_name=f"Organization {i}",
            province=prov,
            created_by=facilitator,
            current_workshop="workshop_1",
            completed_workshops=[],
            consent_given=True,
            profile_completed=True,
        )
        participants.append(participant)

    # Create responses
    responses = []
    for i, participant in enumerate(participants):
        response = WorkshopResponse.objects.create(
            participant=participant,
            workshop=workshop,
            question_id="q1_context",
            response_data=f"Response from {participant.stakeholder_type} in {participant.province.name}: Important insight {i}.",
            status="submitted",
            submitted_at=timezone.now(),
        )
        responses.append(response)

    return {
        "assessment": assessment,
        "workshop": workshop,
        "facilitator": facilitator,
        "participants": participants,
        "responses": responses,
        "province1": province1,
        "province2": province2,
    }


@pytest.mark.django_db
class TestAIWorkshopSynthesizer:
    """Test AI synthesis functionality."""

    def test_get_responses_no_filter(self, synthesis_setup):
        """Should retrieve all submitted responses without filter."""
        env = synthesis_setup
        workshop = env["workshop"]

        synthesizer = AIWorkshopSynthesizer(workshop)
        responses = synthesizer._get_responses()

        assert len(responses) == 4  # All 4 participants

    def test_get_responses_province_filter(self, synthesis_setup):
        """Should filter responses by province."""
        env = synthesis_setup
        workshop = env["workshop"]
        province1 = env["province1"]

        synthesizer = AIWorkshopSynthesizer(
            workshop, filters={"province_id": province1.id}
        )
        responses = synthesizer._get_responses()

        assert len(responses) == 2  # Only 2 from province1
        for response in responses:
            assert response.participant.province == province1

    def test_get_responses_stakeholder_filter(self, synthesis_setup):
        """Should filter responses by stakeholder type."""
        env = synthesis_setup
        workshop = env["workshop"]

        synthesizer = AIWorkshopSynthesizer(
            workshop, filters={"stakeholder_type": "elder"}
        )
        responses = synthesizer._get_responses()

        assert len(responses) == 1
        assert responses[0].participant.stakeholder_type == "elder"

    def test_get_responses_combined_filters(self, synthesis_setup):
        """Should apply multiple filters."""
        env = synthesis_setup
        workshop = env["workshop"]
        province2 = env["province2"]

        synthesizer = AIWorkshopSynthesizer(
            workshop,
            filters={"province_id": province2.id, "stakeholder_type": "farmer"},
        )
        responses = synthesizer._get_responses()

        assert len(responses) == 1
        assert responses[0].participant.stakeholder_type == "farmer"
        assert responses[0].participant.province == province2

    def test_format_responses(self, synthesis_setup):
        """Should format responses for AI prompt."""
        env = synthesis_setup
        workshop = env["workshop"]

        synthesizer = AIWorkshopSynthesizer(workshop)
        responses = synthesizer._get_responses()
        formatted = synthesizer._format_responses(responses)

        assert "Response 1" in formatted
        assert "Zamboanga del Sur" in formatted
        assert "elder" in formatted or "Elder" in formatted

    def test_get_metadata(self, synthesis_setup):
        """Should extract correct metadata."""
        env = synthesis_setup
        workshop = env["workshop"]

        synthesizer = AIWorkshopSynthesizer(workshop)
        responses = synthesizer._get_responses()
        metadata = synthesizer._get_metadata(responses)

        assert metadata["response_count"] == 4
        assert "Zamboanga del Sur" in metadata["provinces"]
        assert "Zamboanga del Norte" in metadata["provinces"]

    def test_build_prompt(self, synthesis_setup):
        """Should build complete AI prompt."""
        env = synthesis_setup
        workshop = env["workshop"]

        synthesizer = AIWorkshopSynthesizer(workshop)
        responses = synthesizer._get_responses()
        prompt = synthesizer._build_prompt(responses)

        assert workshop.title in prompt
        assert "Total Responses: 4" in prompt
        assert "Key Themes" in prompt
        assert "Recommendations" in prompt

    def test_synthesize_no_responses(self, synthesis_setup):
        """Should handle no responses gracefully."""
        env = synthesis_setup
        workshop = env["workshop"]
        facilitator = env["facilitator"]

        # Delete all responses
        WorkshopResponse.objects.filter(workshop=workshop).delete()

        synthesizer = AIWorkshopSynthesizer(workshop)
        synthesis = synthesizer.synthesize(created_by=facilitator, provider="anthropic")

        assert synthesis.status == "failed"
        assert "No submitted responses" in synthesis.error_message

    def test_synthesize_creates_record(self, synthesis_setup):
        """Should create synthesis record."""
        env = synthesis_setup
        workshop = env["workshop"]
        facilitator = env["facilitator"]

        synthesizer = AIWorkshopSynthesizer(workshop)
        synthesis = synthesizer.synthesize(created_by=facilitator, provider="anthropic")

        assert synthesis.id is not None
        assert synthesis.workshop == workshop
        assert synthesis.assessment == workshop.assessment
        assert synthesis.created_by == facilitator

    def test_synthesize_with_filters(self, synthesis_setup):
        """Should record filters in synthesis."""
        env = synthesis_setup
        workshop = env["workshop"]
        facilitator = env["facilitator"]
        province1 = env["province1"]

        filters = {"province_id": province1.id, "stakeholder_type": "elder"}
        synthesizer = AIWorkshopSynthesizer(workshop, filters)
        synthesis = synthesizer.synthesize(created_by=facilitator)

        assert synthesis.filters == filters

    def test_parse_model_response_json(self, synthesis_setup):
        """Should parse JSON responses from AI."""
        env = synthesis_setup
        workshop = env["workshop"]

        synthesizer = AIWorkshopSynthesizer(workshop)

        json_response = (
            '{"summary": "Test summary", "key_themes": ["theme1", "theme2"]}'
        )
        result = synthesizer._parse_model_response(
            json_response, "Test Provider", "test-model", 150, 2.5
        )

        assert result["synthesis_text"] == "Test summary"
        assert result["key_themes"] == ["theme1", "theme2"]
        assert result["provider"] == "Test Provider"
        assert result["tokens_used"] == 150

    def test_parse_model_response_plain_text(self, synthesis_setup):
        """Should handle plain text responses."""
        env = synthesis_setup
        workshop = env["workshop"]

        synthesizer = AIWorkshopSynthesizer(workshop)

        text_response = "This is a plain text synthesis without JSON structure."
        result = synthesizer._parse_model_response(
            text_response, "Test Provider", "test-model", None, 1.2
        )

        assert result["synthesis_text"] == text_response
        assert result["key_themes"] == []

    def test_approve_synthesis(self, synthesis_setup):
        """Should approve completed synthesis."""
        env = synthesis_setup
        workshop = env["workshop"]
        facilitator = env["facilitator"]

        synthesis = WorkshopSynthesis.objects.create(
            assessment=workshop.assessment,
            workshop=workshop,
            prompt_template="Test prompt",
            status="completed",
            synthesis_text="Test synthesis",
            created_by=facilitator,
        )

        synthesizer = AIWorkshopSynthesizer(workshop)
        approved = synthesizer.approve_synthesis(
            synthesis, reviewed_by=facilitator, review_notes="Looks good"
        )

        assert approved.status == "approved"
        assert approved.reviewed_by == facilitator
        assert approved.review_notes == "Looks good"
        assert approved.approved_at is not None

    def test_cannot_approve_non_completed(self, synthesis_setup):
        """Cannot approve synthesis that's not completed."""
        env = synthesis_setup
        workshop = env["workshop"]
        facilitator = env["facilitator"]

        synthesis = WorkshopSynthesis.objects.create(
            assessment=workshop.assessment,
            workshop=workshop,
            prompt_template="Test prompt",
            status="processing",
            created_by=facilitator,
        )

        synthesizer = AIWorkshopSynthesizer(workshop)

        with pytest.raises(ValueError, match="Can only approve completed"):
            synthesizer.approve_synthesis(synthesis, reviewed_by=facilitator)


@pytest.mark.django_db
class TestSynthesisWorkflow:
    """Test end-to-end synthesis workflows."""

    def test_generate_review_regenerate_approve(self, synthesis_setup):
        """Test complete synthesis workflow."""
        env = synthesis_setup
        workshop = env["workshop"]
        facilitator = env["facilitator"]

        # Generate initial synthesis
        synthesizer = AIWorkshopSynthesizer(workshop)
        synthesis1 = synthesizer.synthesize(created_by=facilitator)

        assert synthesis1.status in ["completed", "processing", "failed"]

        # Simulate completed status for testing
        synthesis1.status = "completed"
        synthesis1.synthesis_text = "Initial synthesis"
        synthesis1.save()

        # Regenerate
        synthesis2 = synthesizer.regenerate_synthesis(synthesis1, facilitator)
        assert synthesis2.id != synthesis1.id  # New record

        # Approve second synthesis
        synthesis2.status = "completed"
        synthesis2.synthesis_text = "Revised synthesis"
        synthesis2.save()

        approved = synthesizer.approve_synthesis(
            synthesis2, facilitator, "Final version"
        )
        assert approved.status == "approved"

    def test_multiple_syntheses_for_workshop(self, synthesis_setup):
        """Should allow multiple syntheses with different filters."""
        env = synthesis_setup
        workshop = env["workshop"]
        facilitator = env["facilitator"]
        province1 = env["province1"]
        province2 = env["province2"]

        # Synthesis for province 1
        synth1 = AIWorkshopSynthesizer(workshop, {"province_id": province1.id})
        synthesis1 = synth1.synthesize(created_by=facilitator)

        # Synthesis for province 2
        synth2 = AIWorkshopSynthesizer(workshop, {"province_id": province2.id})
        synthesis2 = synth2.synthesize(created_by=facilitator)

        all_syntheses = WorkshopSynthesis.objects.filter(workshop=workshop)
        assert all_syntheses.count() >= 2
