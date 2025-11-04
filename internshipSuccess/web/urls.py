from django.urls import path
from .views import (
    HomeView,
    InductionPostsView,
    SuccefullApplicationView,
    InductionApplicationCreateView,
    AboutView,
    ServicesView,
    NewsView,
    ContactView,
    MarketingView,
    TeamView,
    ManagementView,
    PlacementView,
    RecruitmentView,
    RecruitmentInterns,
    InternWorkplace,
    hostSourcing,
    mentorship_and_site,
    CheckApplicationStatus,
    upload_questionnaire_affidavit
    

)
from .views import create_questionnaire, verify_email


urlpatterns = [
    path("", view=HomeView.as_view(), name="home"),
    path("inductions", view=InductionPostsView.as_view(), name="web-induction-posts"),
    path("about", view=AboutView.as_view(), name="about-page"),
    path("services", view=ServicesView.as_view(), name="services-page"),
    path("news", view=NewsView.as_view(), name="news-page"),
    path("contact", view=ContactView.as_view(), name="contact-page"),
    path("marketing", view=MarketingView.as_view(), name="marketing-page"),
    path("team", view=TeamView.as_view(), name="team-page"),
    path("management/", view=ManagementView.as_view(), name="management-page"),
    path("placement/", view=PlacementView.as_view(), name="placement-page"),
    path("recruitment/", view=RecruitmentView.as_view(), name="recruitment-page"),
    path("recruitmentOfIntern/", view=RecruitmentInterns.as_view(), name="InternRecruitment-page"),
    path("InternWockplace/", view=InternWorkplace.as_view(), name="InternWorkplace-page"),
    path("hostSourcing/", view=hostSourcing.as_view(), name="hostSourcing-page"),
    path("mentorship_and_site/", view=hostSourcing.as_view(), name="mentorship_and_site-page"),
    path(
        "inductions/application/<int:id>",
        view=InductionApplicationCreateView.as_view(),
        name="induction-application",
    ),
    path(
        "inductions/application/status",
        view=CheckApplicationStatus.as_view(),
        name="induction-application-status",
    ),
    path(
        "inductions/application/success",
        view=SuccefullApplicationView.as_view(),
        name="induction-application-success",
    ),
    path(
        "questionnaire/create/<int:application_id>/",
        create_questionnaire,
        name="create_questionnaire",
    ),
    path(
        "questionnaire/affidavit/<int:questionnaire_id>/",
        upload_questionnaire_affidavit,
        name="upload_questionnaire_affidavit",
    ),
    path('verify-email/<int:application_id>/', verify_email, name='verify_email'),
]
