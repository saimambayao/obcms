"""Management command to reset the OOBC staff directory."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from common.constants import STAFF_USER_TYPES
from common.models import User


STAFF_DIRECTORY_ENTRIES = [
    {
        "name": "Noron S. Andan, MPA, MAEd",
        "credentials": "",
        "position": "Executive Director",
        "user_type": "oobc_executive",
    },
    {
        "name": "Quraish D. Langcap",
        "credentials": "",
        "position": "Deputy Executive Director",
        "user_type": "oobc_executive",
    },
    {
        "name": "Norhan B. Hadji Abdullah",
        "credentials": "",
        "position": "Development Management Officer IV",
    },
    {
        "name": "Rusman B. Musa",
        "credentials": "",
        "position": "Development Management Officer III",
    },
    {
        "name": "Farhanna U. Kabalu",
        "credentials": "",
        "position": "Planning Officer II",
    },
    {
        "name": "Al-Amid P. Gandawali",
        "credentials": "",
        "position": "Information System Analyst II",
    },
    {
        "name": "Michael A. Berwal",
        "credentials": "",
        "position": "Administrative Officer II",
    },
    {
        "name": "Esnain C. Mapait",
        "credentials": "",
        "position": "Community Development Officer I",
    },
    {
        "name": "Mohammad Hamid M. Bato",
        "credentials": "",
        "position": "Planning Officer I",
    },
    {
        "name": "Habiba B. Abunawas",
        "credentials": "",
        "position": "Development Management Officer I",
    },
    {
        "name": "Datu Noah P. Damping",
        "credentials": "",
        "position": "Administrative Assistant V",
    },
    {
        "name": "Ramla L. Manguda",
        "credentials": "",
        "position": "Administrative Assistant I",
    },
    {
        "name": "Nor-hayya A. Donde",
        "credentials": "",
        "position": "Administrative Assistant I",
    },
    {
        "name": "Ummu Calthoom L. Basug",
        "credentials": "",
        "position": "Administrative Assistant I",
    },
    {
        "name": "Mardiya M. Jaukal",
        "credentials": "",
        "position": "Administrative Assistant I",
    },
    {
        "name": "Rayyana G. Pendi",
        "credentials": "",
        "position": "Administrative Assistant I",
    },
    {"name": "Herdan V. Tang", "credentials": "", "position": "Records Officer I"},
    {
        "name": "Datu Abdulbasit T. Esmael",
        "credentials": "",
        "position": "Supply Officer I",
    },
    {
        "name": "Omulheir M. Noddin",
        "credentials": "",
        "position": "Information Officer I",
    },
    {
        "name": "Mohadier S. Gawan",
        "credentials": "",
        "position": "Project Evaluation Officer I",
    },
    {
        "name": "Sittie Fayesha S. Tumog",
        "credentials": "",
        "position": "Information Assistant",
    },
    {"name": "Hamde B. Samana", "credentials": "", "position": "Administrative Aide V"},
    {
        "name": "Mohaimen R. Gumander",
        "credentials": "",
        "position": "Administrative Aide V",
    },
    {
        "name": "Akmad S. Gandawali",
        "credentials": "",
        "position": "Administrative Aide V",
    },
    {
        "name": "Marifel C. Introducion",
        "credentials": "",
        "position": "Administrative Aide V",
    },
]


class Command(BaseCommand):
    """Replace existing staff users with the provided directory entries."""

    help = (
        "Deletes existing staff users (admin and OOBC staff types) and recreates "
        "the directory with the configured entries."
    )

    def handle(self, *args, **options):
        staff_types = set(STAFF_USER_TYPES)
        directory_entries = STAFF_DIRECTORY_ENTRIES

        with transaction.atomic():
            deleted_count, _ = User.objects.filter(user_type__in=staff_types).delete()

            created_users: list[User] = []
            for entry in directory_entries:
                full_name = entry["name"]
                credentials = entry["credentials"]
                position = entry["position"]

                # Extract first and last name
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    first_name = " ".join(name_parts[:-1])
                    last_name = name_parts[-1]
                else:
                    first_name = full_name
                    last_name = ""

                # Create username from full name
                username_base = slugify(full_name.replace(".", "")) or "staff"
                username = username_base
                suffix = 2
                while User.objects.filter(username=username).exists():
                    username = f"{username_base}{suffix}"
                    suffix += 1

                # Create display position with credentials if available
                display_position = position
                if credentials:
                    display_position = f"{position} ({credentials})"

                user = User.objects.create(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=entry.get("user_type", "oobc_staff"),
                    email=f"{username}@oobc.local",
                    position=display_position,
                    organization=(
                        "Office for Other Bangsamoro Communities, Office of the Chief "
                        "Minister (Bangsamoro Autonomous Region in Muslim Mindanao)"
                    ),
                    is_active=True,
                    is_staff=True,
                    is_approved=True,
                )
                user.set_unusable_password()
                user.save(update_fields=["password"])
                created_users.append(user)

        created_list = ", ".join(user.get_full_name() for user in created_users)
        self.stdout.write(
            self.style.SUCCESS(
                "Staff directory reset complete. Deleted "
                f"{deleted_count} staff users and created {len(created_users)} entries:"
            )
        )
        self.stdout.write(created_list)
