from django.urls import path

from statuses import views

urlpatterns = [
    path('', views.StatusesIndexView.as_view(), name='statuses_index'),
    path('create/', views.StatusCreateView.as_view(), name='status_create'),
    path(
        '<int:pk>/update/',
        views.StatusUpdateView.as_view(),
        name='status_update'
    ),
    path(
        '<int:pk>/delete/',
        views.StatusDeleteView.as_view(),
        name='status_delete'
    ),
]