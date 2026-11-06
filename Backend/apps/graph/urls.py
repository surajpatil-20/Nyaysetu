from django.urls import path
from .views import CaseGraphView, GraphStatusView, GraphSyncView

urlpatterns = [
    path('cases/<int:case_id>/', CaseGraphView.as_view(), name='case-graph'),
    path('status/', GraphStatusView.as_view(), name='graph-status'),
    path('sync/', GraphSyncView.as_view(), name='graph-sync'),
]

