from django.urls import path
from administration.views import EventsView,create_event,get_events,get_event_by_date,update_event, InductionApplicationsView, ViewInductionPostApplications,ViewInductionApplicantView
from administration import views
from .views import (
    NewsLettersView,
    UserActivityView,
    SuccessStoryView,
    EventView,
    DashboardView,
    MagazineListView,
    SuccessStoryCreateView,
    ConsentView,
    CampaignListView,
    


)

urlpatterns = [
     path("newsletters/", NewsLettersView.as_view(), name="newsletters"),
    path("activity/", UserActivityView.as_view(), name="user_activity"),
    path("campaigns/", CampaignListView.as_view(), name="campaigns"),
    path("success-stories/", SuccessStoryView.as_view(), name="success_stories"),
    path("events/", EventView.as_view(), name="events"),
    path("dashboard/", DashboardView.as_view(), name="marketing-dashboard"),
    path("induction", view=InductionApplicationsView.as_view(), name="mar-induction"),
    path("magazines/", MagazineListView.as_view(), name="magazines"),
    path("success-stories/create/", SuccessStoryCreateView.as_view(), name="create_success_story"),
    path(
        "induction/application/<int:id>",
        view=ViewInductionPostApplications.as_view(),
        name="induction-application-posts",
    ),
    path(
        "induction/application/view/<int:id>",
        view=ViewInductionApplicantView.as_view(),
        name="induction-application-view",
    ),
    #  Evenet Management
    path("event-management", EventsView.as_view(), name="marketing-event-management"),
    path('events/', EventsView.as_view(), name='marketing-events'),
    path('events/create/', create_event, name='create-event'),
    path('events/data/', get_events, name='events-data'),
    path('events/create/', create_event, name='create-event'),
    path('events/data/view', get_event_by_date, name='create-event'),
    path('events/<int:event_id>/update/', update_event, name='update-event'),
    path('events-by-date/', views.events_by_date, name='events_by_date'),

    path('induction/cosentform/', ConsentView.as_view(), name='signcosentform'),

    
]