from django.urls import path
from core import views


urlpatterns = [
    path('user/', views.UserAccountDetailsView.as_view(), name='user-account-details'),
    path('files', views.FilesView.as_view(), name='files')
]
