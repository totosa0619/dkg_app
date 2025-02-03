from django.urls import path
from diagrams import views

urlpatterns = [
    # Custom diagrams
    path('diagrams-all', views.diagrams_all, name='diagrams-all-list'),
    path('diagrams', views.DiagramsListAPIView.as_view(), name='custom-diagram-api-list'),
    path('diagrams/<str:slug>', views.DiagramView.as_view(), name='custom-diagram-api-rud'),
    path("diagrams/verify-passkey/<str:slug>", views.VerifyDiagramPasskey.as_view(), name="diagram-passkey-verify"),
    path('diagrams-file/', views.custom_diagram_api_file, name='custom-diagram-api-file'),
    path('diagrams-file/<str:diagram_slug>', views.custom_diagram_api_file, name='custom-diagram-api-file-folder'),
    path('stock-history/<str:ticker>', views.raw_stock_history_data, name='custom-diagram-api-stock-history'),
    
    # Platform access
    path('platform-access/', views.RequestPlatformAccess.as_view(), name='platform-access-request'),

     # Category Endpoints
    path('categories/', views.CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail'),

    # IT Tool Product Endpoints
    path('it-tools/', views.ITToolProductListCreateAPIView.as_view(), name='it-tool-list-create'),
    path('it-tools/<int:pk>/', views.ITToolProductRetrieveUpdateDestroyAPIView.as_view(), name='it-tool-detail'),
]
