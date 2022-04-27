from django.urls import path

from WakeApp.core.views import DashboardView, CreateEventView, EventDetailsView, like_event, MyEvents

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('event/add/', CreateEventView.as_view(), name='create event'),
    path('event/details/<int:pk>', EventDetailsView.as_view(), name='event details'),
    path('event/like/<int:pk>', like_event, name='like event'),
    path('event/my_events/', MyEvents.as_view(), name='my events'),
]

