"""Tests for OBCCommunityHistory model and constraint handling."""
import pytest

pytest.skip(
    "Municipal history tests require legacy OBCCommunity lifecycle not available post-refactor.",
    allow_module_level=True,
)
from django.db import connection

from common.models import Barangay, Municipality, Province, Region
from communities.models import OBCCommunity
from municipal_profiles.models import OBCCommunityHistory


def _build_location_hierarchy():
    """Create test location hierarchy."""
    region = Region.objects.create(code="TST-R", name="Test Region")
    province = Province.objects.create(
        region=region,
        code="TST-P",
        name="Test Province",
    )
    municipality = Municipality.objects.create(
        province=province,
        code="TST-M",
        name="Test Municipality",
    )
    barangay = Barangay.objects.create(
        municipality=municipality,
        code="TST-B1",
        name="Test Barangay 1",
    )
    return barangay


@pytest.mark.django_db(transaction=True)
def test_obccommunity_deletion_preserves_history():
    """Test that OBCCommunity can be deleted while preserving history entries."""
    # Debug: Check if migration was applied
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(municipal_profiles_obccommunityhistory);")
        columns = cursor.fetchall()
        community_id_col = [col for col in columns if col[1] == 'community_id'][0]
        print(f"DEBUG: community_id nullable={community_id_col[3] == 0}")

        cursor.execute("PRAGMA foreign_key_list(municipal_profiles_obccommunityhistory);")
        fks = cursor.fetchall()
        community_fk = [fk for fk in fks if fk[3] == 'community_id'][0]
        print(f"DEBUG: community FK on_delete={community_fk[5]}")

    # Arrange: Create location hierarchy and OBC community
    barangay = _build_location_hierarchy()
    community = OBCCommunity.objects.create(
        barangay=barangay,
        estimated_obc_population=100,
        households=25,
        families=20,
    )

    # Create history entries
    history1 = OBCCommunityHistory.objects.create(
        community=community,
        snapshot={"population": 100, "households": 25},
        source=OBCCommunityHistory.SOURCE_MANUAL,
        note="Initial data entry",
    )
    history2 = OBCCommunityHistory.objects.create(
        community=community,
        snapshot={"population": 110, "households": 27},
        source=OBCCommunityHistory.SOURCE_MANUAL,
        note="Updated population",
    )

    community_id = community.id
    history1_id = history1.id
    history2_id = history2.id

    # Act: Delete the OBCCommunity
    community.delete()

    # Assert: History entries are preserved with community=None
    history1_after = OBCCommunityHistory.objects.get(id=history1_id)
    history2_after = OBCCommunityHistory.objects.get(id=history2_id)

    assert history1_after.community is None, "History should have community=None after deletion"
    assert history2_after.community is None, "History should have community=None after deletion"
    assert history1_after.snapshot == {"population": 100, "households": 25}
    assert history2_after.snapshot == {"population": 110, "households": 27}
    assert history1_after.note == "Initial data entry"
    assert history2_after.note == "Updated population"

    # Verify OBCCommunity is actually deleted
    assert not OBCCommunity.objects.filter(id=community_id).exists()


@pytest.mark.django_db(transaction=True)
def test_obccommunityhistory_str_with_deleted_community():
    """Test that __str__ method handles deleted communities gracefully."""
    # Arrange: Create location hierarchy and OBC community
    barangay = _build_location_hierarchy()
    community = OBCCommunity.objects.create(
        barangay=barangay,
        estimated_obc_population=100,
        households=25,
        families=20,
    )

    # Create history entry
    history = OBCCommunityHistory.objects.create(
        community=community,
        snapshot={"population": 100},
        source=OBCCommunityHistory.SOURCE_MANUAL,
    )

    # Check __str__ before deletion
    str_before = str(history)
    assert barangay.name in str_before or "OBC Community" in str_before

    # Delete the community
    community.delete()

    # Refresh history from DB
    history.refresh_from_db()

    # Check __str__ after deletion
    str_after = str(history)
    assert "[Deleted Community]" in str_after, "__str__ should show '[Deleted Community]' when community is None"
    assert "snapshot" in str_after, "__str__ should still show timestamp"


@pytest.mark.django_db(transaction=True)
def test_multiple_communities_with_history_deletion():
    """Test deleting multiple communities with history entries."""
    # Arrange: Create location hierarchy with multiple barangays
    region = Region.objects.create(code="TST2-R", name="Test Region 2")
    province = Province.objects.create(
        region=region,
        code="TST2-P",
        name="Test Province 2",
    )
    municipality = Municipality.objects.create(
        province=province,
        code="TST2-M",
        name="Test Municipality 2",
    )

    # Create multiple communities with history (one per barangay due to unique constraint)
    communities = []
    for i in range(3):
        barangay = Barangay.objects.create(
            municipality=municipality,
            code=f"TST2-B{i+1}",
            name=f"Test Barangay {i+1}",
        )
        community = OBCCommunity.objects.create(
            barangay=barangay,
            estimated_obc_population=100 + i * 10,
            households=25 + i,
            families=20 + i,
        )
        # Add 2 history entries per community
        OBCCommunityHistory.objects.create(
            community=community,
            snapshot={"population": 100 + i * 10},
            source=OBCCommunityHistory.SOURCE_IMPORT,
        )
        OBCCommunityHistory.objects.create(
            community=community,
            snapshot={"population": 100 + i * 10 + 5},
            source=OBCCommunityHistory.SOURCE_MANUAL,
        )
        communities.append(community)

    initial_history_count = OBCCommunityHistory.objects.count()
    assert initial_history_count == 6, "Should have 6 history entries (3 communities × 2 entries)"

    # Act: Delete all communities
    for community in communities:
        community.delete()

    # Assert: All history entries preserved with community=None
    assert OBCCommunityHistory.objects.count() == 6, "All history entries should be preserved"
    assert OBCCommunityHistory.objects.filter(community__isnull=True).count() == 6, "All history entries should have community=None"
    assert OBCCommunity.objects.count() == 0, "All communities should be deleted"
