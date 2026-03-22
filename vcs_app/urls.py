from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('commit', views.create_commit),
    path('branch', views.create_branch),
    path('checkout', views.checkout),
    path('log', views.get_log),
    path('full-history', views.get_full_history),
    path('levels', views.get_bfs_levels),
    path('search', views.search_commit),
    path('lca', views.get_lca),
    path('node-analytics/<str:commit_id>', views.get_node_analytics),
    path('tree-data', views.get_tree_data),
    path('reset', views.reset_repo),
]
