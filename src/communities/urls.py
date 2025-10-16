from django.urls import path

from . import views, data_utils

app_name = "communities"

urlpatterns = [
    # ============================================================================
    # PHASE 0.4: Communities URLs migrated from common/urls.py
    # ============================================================================
    # Core Communities URLs
    path("", views.communities_home, name="communities_home"),
    path("add/", views.communities_add, name="communities_add"),
    path(
        "add-municipality/",
        communities_views.communities_add_municipality,
        name="communities_add_municipality",
    ),
    path(
        "add-province/",
        communities_views.communities_add_province,
        name="communities_add_province",
    ),
    path(
        "<int:community_id>/",
        communities_views.communities_view,
        name="communities_view",
    ),
    path(
        "<int:community_id>/edit/",
        communities_views.communities_edit,
        name="communities_edit",
    ),
    path(
        "<int:community_id>/delete/",
        communities_views.communities_delete,
        name="communities_delete",
    ),
    path(
        "<int:community_id>/restore/",
        communities_views.communities_restore,
        name="communities_restore",
    ),

    # Management URLs
    path("manage/", views.communities_manage, name="communities_manage"),
    path(
        "managemunicipal/",
        communities_views.communities_manage_municipal,
        name="communities_manage_municipal",
    ),
    path(
        "managebarangayobc/",
        views.communities_manage_barangay_obc,
        name="communities_manage_barangay_obc",
    ),
    path(
        "managemunicipalobc/",
        views.communities_manage_municipal_obc,
        name="communities_manage_municipal_obc",
    ),
    path(
        "manageprovincial/",
        communities_views.communities_manage_provincial,
        name="communities_manage_provincial",
    ),
    path(
        "manageprovincialobc/",
        communities_views.communities_manage_provincial,
        name="communities_manage_provincial_obc",
    ),

    # Municipal Coverage URLs
    path(
        "municipal/<int:coverage_id>/",
        communities_views.communities_view_municipal,
        name="communities_view_municipal",
    ),
    path(
        "municipal/<int:coverage_id>/edit/",
        communities_views.communities_edit_municipal,
        name="communities_edit_municipal",
    ),
    path(
        "municipal/<int:coverage_id>/delete/",
        communities_views.communities_delete_municipal,
        name="communities_delete_municipal",
    ),
    path(
        "municipal/<int:coverage_id>/restore/",
        communities_views.communities_restore_municipal,
        name="communities_restore_municipal",
    ),

    # Provincial Coverage URLs
    path(
        "province/<int:coverage_id>/",
        communities_views.communities_view_provincial,
        name="communities_view_provincial",
    ),
    path(
        "province/<int:coverage_id>/edit/",
        communities_views.communities_edit_provincial,
        name="communities_edit_provincial",
    ),
    path(
        "province/<int:coverage_id>/delete/",
        communities_views.communities_delete_provincial,
        name="communities_delete_provincial",
    ),
    path(
        "province/<int:coverage_id>/submit/",
        communities_views.communities_submit_provincial,
        name="communities_submit_provincial",
    ),
    path(
        "province/<int:coverage_id>/restore/",
        communities_views.communities_restore_provincial,
        name="communities_restore_provincial",
    ),

    # Stakeholders & Location URLs
    path(
        "stakeholders/",
        communities_views.communities_stakeholders,
        name="communities_stakeholders",
    ),
    path("locations/centroid/", communities_views.location_centroid, name="location_centroid"),

    # Data Import/Export/Report URLs
    path(
        "import/",
        data_utils.import_communities_csv,
        name="import_communities",
    ),
    path(
        "export/",
        data_utils.export_communities,
        name="export_communities"
    ),
    path(
        "report/",
        data_utils.generate_obc_report,
        name="generate_obc_report",
    ),
    path("data-guidelines/", data_utils.data_guidelines, name="data_guidelines"),

    # ============================================================================
    # Geographic Data URLs (existing)
    # ============================================================================
    path("geographic-data/", views.geographic_data_list, name="geographic_data_list"),
    path("geographic-data/add-layer/", views.add_data_layer, name="add_data_layer"),
    path(
        "geographic-data/create-visualization/",
        views.create_visualization,
        name="create_visualization",
    ),

    # AI Intelligence Endpoints - TODO: Implement these views
    # path(
    #     'ai/similar/<int:pk>/',
    #     views.ai_similar_communities,
    #     name='ai-similar'
    # ),
    # path(
    #     'ai/classify-needs/<int:pk>/',
    #     views.ai_classify_needs,
    #     name='ai-classify-needs'
    # ),
    # path(
    #     'ai/generate-report/<int:pk>/',
    #     views.ai_generate_report,
    #     name='ai-generate-report'
    # ),
    # path(
    #     'ai/validate-data/<int:pk>/',
    #     views.ai_validate_data,
    #     name='ai-validate-data'
    # ),
]
