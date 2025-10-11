import json
from pathlib import Path

import pytest

try:
    from django.contrib.auth.models import Group
    from django.core import management
except ImportError:  # pragma: no cover - handled via skip
    pytest.skip(
        "Django is required for MANA management command tests",
        allow_module_level=True,
    )

from mana.models import WorkshopQuestionDefinition
from mana.schema import get_questions_for_workshop


@pytest.mark.django_db
def test_sync_mana_question_schema(tmp_path, settings):
    schema_data = {
        "workshop_1": {
            "questions": [
                {
                    "id": "q1",
                    "text": "Sample",
                    "type": "text",
                }
            ]
        }
    }
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(schema_data), encoding="utf-8")

    settings.MANA_QUESTION_SCHEMA_VERSION = "test"

    management.call_command(
        "sync_mana_question_schema", str(schema_path), schema_version="test"
    )

    assert WorkshopQuestionDefinition.objects.filter(version="test").count() == 1
    questions = get_questions_for_workshop("workshop_1")
    assert questions and questions[0]["id"] == "q1"


@pytest.mark.django_db
def test_ensure_mana_roles_creates_groups():
    management.call_command("ensure_mana_roles")
    assert Group.objects.filter(name="mana_facilitator").exists()
    facilitator_group = Group.objects.get(name="mana_facilitator")
    perms = set(facilitator_group.permissions.values_list("codename", flat=True))
    assert "can_facilitate_workshop" in perms
