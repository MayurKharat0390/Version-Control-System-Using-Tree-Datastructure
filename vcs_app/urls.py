from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('commit', views.create_commit),
    path('branch', views.create_branch),
    path('checkout', views.checkout),
    path('log', views.get_log),
    path('tree-data', views.get_tree_data),
]
