from django.db import migrations


REGION_XII_DATA = {
    "code": "XII",
    "name": "SOCCSKSARGEN",
    "description": (
        "Region XII covers South Cotabato, Cotabato, Sultan Kudarat, Sarangani, "
        "and the highly urbanized city of General Santos. This seed dataset "
        "provides geographic centroids so integration tests can validate "
        "location services without depending on external imports."
    ),
    "center_coordinates": [124.85, 6.35],
    "bounding_box": [123.70, 5.40, 125.65, 7.60],
    "provinces": [
        {
            "code": "XII-COTABATO",
            "name": "Cotabato",
            "capital": "Kidapawan City",
            "center_coordinates": [124.903, 7.104],
            "bounding_box": [124.10, 6.80, 125.30, 7.60],
            "municipalities": [
                {
                    "code": "XII-COTABATO-KIDAPAWAN",
                    "name": "Kidapawan City",
                    "municipality_type": "component_city",
                    "center_coordinates": [125.089, 7.008],
                    "bounding_box": [125.00, 6.95, 125.16, 7.06],
                    "barangays": [
                        {
                            "code": "XII-COTABATO-KIDAPAWAN-POBLACION",
                            "name": "Poblacion",
                            "is_urban": True,
                            "center_coordinates": [125.089, 7.008],
                            "bounding_box": [125.075, 6.998, 125.103, 7.018],
                        },
                        {
                            "code": "XII-COTABATO-KIDAPAWAN-LAMANNA",
                            "name": "Barangay Lamanan",
                            "is_urban": False,
                            "center_coordinates": [125.045, 7.042],
                            "bounding_box": [125.028, 7.028, 125.062, 7.056],
                        },
                    ],
                },
                {
                    "code": "XII-COTABATO-MLANG",
                    "name": "M'lang",
                    "municipality_type": "municipality",
                    "center_coordinates": [124.888, 6.935],
                    "bounding_box": [124.80, 6.86, 124.97, 7.00],
                    "barangays": [
                        {
                            "code": "XII-COTABATO-MLANG-KATIPUNAN",
                            "name": "Katipunan",
                            "is_urban": False,
                            "center_coordinates": [124.9211486, 7.0150888],
                            "bounding_box": [124.9011486, 6.9950888, 124.9411486, 7.0350888],
                        },
                        {
                            "code": "XII-COTABATO-MLANG-BAGONTAPANG",
                            "name": "Bagontapang",
                            "is_urban": False,
                            "center_coordinates": [124.870, 6.920],
                            "bounding_box": [124.850, 6.900, 124.890, 6.940],
                        },
                    ],
                },
                {
                    "code": "XII-COTABATO-ARAKAN",
                    "name": "Arakan",
                    "municipality_type": "municipality",
                    "center_coordinates": [125.096, 7.389],
                    "bounding_box": [124.98, 7.30, 125.18, 7.46],
                    "barangays": [
                        {
                            "code": "XII-COTABATO-ARAKAN-KATIPUNAN",
                            "name": "Katipunan (Arakan)",
                            "is_urban": False,
                            "center_coordinates": [125.2351242, 7.4223653],
                            "bounding_box": [125.2151242, 7.4023653, 125.2551242, 7.4423653],
                        }
                    ],
                },
                {
                    "code": "XII-COTABATO-MATALAM",
                    "name": "Matalam",
                    "municipality_type": "municipality",
                    "center_coordinates": [124.914, 7.085],
                    "bounding_box": [124.82, 7.01, 125.00, 7.17],
                    "barangays": [
                        {
                            "code": "XII-COTABATO-MATALAM-SANTA-MARIA",
                            "name": "Santa Maria",
                            "is_urban": False,
                            "center_coordinates": [124.9892127, 7.2210551],
                            "bounding_box": [124.9692127, 7.2010551, 125.0092127, 7.2410551],
                        }
                    ],
                },
            ],
        },
        {
            "code": "XII-SULTAN-KUDARAT",
            "name": "Sultan Kudarat",
            "capital": "Isulan",
            "center_coordinates": [124.561, 6.506],
            "bounding_box": [123.88, 5.98, 125.08, 6.89],
            "municipalities": [
                {
                    "code": "XII-SULTAN-KUDARAT-ISULAN",
                    "name": "Isulan",
                    "municipality_type": "municipality",
                    "center_coordinates": [124.605, 6.632],
                    "bounding_box": [124.56, 6.58, 124.65, 6.68],
                    "barangays": [
                        {
                            "code": "XII-SULTAN-KUDARAT-ISULAN-POBLACION",
                            "name": "Poblacion",
                            "is_urban": True,
                            "center_coordinates": [124.605, 6.632],
                            "bounding_box": [124.593, 6.622, 124.617, 6.642],
                        }
                    ],
                },
                {
                    "code": "XII-SULTAN-KUDARAT-TACURONG",
                    "name": "Tacurong City",
                    "municipality_type": "component_city",
                    "center_coordinates": [124.676, 6.692],
                    "bounding_box": [124.63, 6.65, 124.72, 6.74],
                    "barangays": [
                        {
                            "code": "XII-SULTAN-KUDARAT-TACURONG-NEW-LAGAO",
                            "name": "New Lagao",
                            "is_urban": False,
                            "center_coordinates": [124.700, 6.705],
                            "bounding_box": [124.680, 6.690, 124.720, 6.720],
                        }
                    ],
                },
            ],
        },
        {
            "code": "XII-SOUTH-COTABATO",
            "name": "South Cotabato",
            "capital": "Koronadal City",
            "center_coordinates": [124.999, 6.252],
            "bounding_box": [124.60, 5.80, 125.30, 6.63],
            "municipalities": [
                {
                    "code": "XII-SOUTH-COTABATO-KORONADAL",
                    "name": "Koronadal City",
                    "municipality_type": "component_city",
                    "center_coordinates": [124.854, 6.503],
                    "bounding_box": [124.80, 6.46, 124.90, 6.54],
                    "barangays": [
                        {
                            "code": "XII-SOUTH-COTABATO-KORONADAL-SAN-ISIDRO",
                            "name": "San Isidro",
                            "is_urban": True,
                            "center_coordinates": [124.866, 6.520],
                            "bounding_box": [124.852, 6.510, 124.880, 6.530],
                        }
                    ],
                },
                {
                    "code": "XII-SOUTH-COTABATO-TUPI",
                    "name": "Tupi",
                    "municipality_type": "municipality",
                    "center_coordinates": [124.954, 6.333],
                    "bounding_box": [124.90, 6.29, 125.01, 6.38],
                    "barangays": [
                        {
                            "code": "XII-SOUTH-COTABATO-TUPI-POBLACION",
                            "name": "Poblacion",
                            "is_urban": False,
                            "center_coordinates": [124.956, 6.333],
                            "bounding_box": [124.940, 6.320, 124.972, 6.346],
                        }
                    ],
                },
            ],
        },
        {
            "code": "XII-SARANGANI",
            "name": "Sarangani",
            "capital": "Alabel",
            "center_coordinates": [125.397, 5.958],
            "bounding_box": [124.85, 5.30, 125.50, 6.40],
            "municipalities": [
                {
                    "code": "XII-SARANGANI-ALABEL",
                    "name": "Alabel",
                    "municipality_type": "municipality",
                    "center_coordinates": [125.295, 6.106],
                    "bounding_box": [125.24, 6.05, 125.35, 6.16],
                    "barangays": [
                        {
                            "code": "XII-SARANGANI-ALABEL-POBLACION",
                            "name": "Poblacion",
                            "is_urban": False,
                            "center_coordinates": [125.300, 6.108],
                            "bounding_box": [125.285, 6.095, 125.315, 6.121],
                        }
                    ],
                },
                {
                    "code": "XII-SARANGANI-GLAN",
                    "name": "Glan",
                    "municipality_type": "municipality",
                    "center_coordinates": [125.208, 5.824],
                    "bounding_box": [125.15, 5.76, 125.27, 5.88],
                    "barangays": [
                        {
                            "code": "XII-SARANGANI-GLAN-GUMASA",
                            "name": "Gumasa",
                            "is_urban": False,
                            "center_coordinates": [125.213, 5.819],
                            "bounding_box": [125.198, 5.804, 125.228, 5.834],
                        }
                    ],
                },
                {
                    "code": "XII-SARANGANI-GENSAN",
                    "name": "General Santos City",
                    "municipality_type": "independent_city",
                    "center_coordinates": [125.171, 6.116],
                    "bounding_box": [125.11, 6.07, 125.23, 6.16],
                    "barangays": [
                        {
                            "code": "XII-SARANGANI-GENSAN-LABANGAL",
                            "name": "Labangal",
                            "is_urban": True,
                            "center_coordinates": [125.163, 6.126],
                            "bounding_box": [125.148, 6.113, 125.178, 6.139],
                        },
                        {
                            "code": "XII-SARANGANI-GENSAN-TAMBLER",
                            "name": "Tambler",
                            "is_urban": False,
                            "center_coordinates": [125.146, 6.070],
                            "bounding_box": [125.126, 6.050, 125.166, 6.090],
                        },
                    ],
                },
            ],
        },
    ],
}


def _ensure_region_xii(apps, schema_editor):
    Region = apps.get_model("common", "Region")
    Province = apps.get_model("common", "Province")
    Municipality = apps.get_model("common", "Municipality")
    Barangay = apps.get_model("common", "Barangay")

    region_defaults = {
        "name": REGION_XII_DATA["name"],
        "description": REGION_XII_DATA["description"],
        "is_active": True,
        "center_coordinates": REGION_XII_DATA["center_coordinates"],
        "bounding_box": REGION_XII_DATA["bounding_box"],
    }
    region, created = Region.objects.get_or_create(
        code=REGION_XII_DATA["code"], defaults=region_defaults
    )
    if not created:
        for field, value in region_defaults.items():
            setattr(region, field, value)
        region.save(update_fields=list(region_defaults.keys()) + ["updated_at"])

    for province_payload in REGION_XII_DATA["provinces"]:
        province_defaults = {
            "name": province_payload["name"],
            "capital": province_payload["capital"],
            "is_active": True,
            "center_coordinates": province_payload["center_coordinates"],
            "bounding_box": province_payload["bounding_box"],
        }
        province, created = Province.objects.get_or_create(
            code=province_payload["code"],
            defaults={**province_defaults, "region": region},
        )
        if not created:
            for field, value in province_defaults.items():
                setattr(province, field, value)
            if province.region_id != region.id:
                province.region = region
            province.save(
                update_fields=list(province_defaults.keys()) + ["region", "updated_at"]
            )

        for municipality_payload in province_payload["municipalities"]:
            municipality_defaults = {
                "name": municipality_payload["name"],
                "municipality_type": municipality_payload["municipality_type"],
                "is_active": True,
                "center_coordinates": municipality_payload["center_coordinates"],
                "bounding_box": municipality_payload["bounding_box"],
            }
            municipality, created = Municipality.objects.get_or_create(
                code=municipality_payload["code"],
                defaults={**municipality_defaults, "province": province},
            )
            if not created:
                for field, value in municipality_defaults.items():
                    setattr(municipality, field, value)
                if municipality.province_id != province.id:
                    municipality.province = province
                municipality.save(
                    update_fields=list(municipality_defaults.keys())
                    + ["province", "updated_at"]
                )

            for barangay_payload in municipality_payload["barangays"]:
                barangay_defaults = {
                    "name": barangay_payload["name"],
                    "is_urban": barangay_payload["is_urban"],
                    "is_active": True,
                    "center_coordinates": barangay_payload["center_coordinates"],
                    "bounding_box": barangay_payload["bounding_box"],
                }
                barangay, created = Barangay.objects.get_or_create(
                    code=barangay_payload["code"],
                    defaults={**barangay_defaults, "municipality": municipality},
                )
                if not created:
                    for field, value in barangay_defaults.items():
                        setattr(barangay, field, value)
                    if barangay.municipality_id != municipality.id:
                        barangay.municipality = municipality
                    barangay.save(
                        update_fields=list(barangay_defaults.keys())
                        + ["municipality", "updated_at"]
                    )


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0036_workitem_activity_category_and_more"),
    ]

    operations = [
        migrations.RunPython(_ensure_region_xii, reverse_code=migrations.RunPython.noop),
    ]
