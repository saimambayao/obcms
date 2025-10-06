from django.urls import path

from . import views

app_name = "communities"

urlpatterns = [
    # Geographic Data URLs
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
