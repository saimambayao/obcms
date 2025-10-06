"""Signal handlers linking barangay communities and municipality coverage."""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import MunicipalityCoverage, OBCCommunity, ProvinceCoverage


@receiver(post_save, sender=OBCCommunity)
def sync_municipality_coverage_on_save(sender, instance, **kwargs):
    """Create or update municipality coverage after a community is saved."""

    municipality = instance.barangay.municipality
    MunicipalityCoverage.sync_for_municipality(municipality)
    if municipality and municipality.province:
        ProvinceCoverage.sync_for_province(municipality.province)


@receiver(post_delete, sender=OBCCommunity)
def sync_municipality_coverage_on_delete(sender, instance, **kwargs):
    """Keep municipality coverage in sync when a community is removed."""

    municipality = instance.barangay.municipality
    MunicipalityCoverage.sync_for_municipality(municipality)
    if municipality and municipality.province:
        ProvinceCoverage.sync_for_province(municipality.province)


@receiver(post_delete, sender=MunicipalityCoverage)
def sync_provincial_coverage_on_municipal_delete(sender, instance, **kwargs):
    """Sync provincial coverage when municipal coverage is hard deleted."""
    if instance.municipality and instance.municipality.province:
        ProvinceCoverage.sync_for_province(instance.municipality.province)
