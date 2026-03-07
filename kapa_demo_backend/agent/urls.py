from django.urls import path
from . import views

app_name = "agent"

urlpatterns = [
    path(
        "coverage-gaps/<uuid:id>/act",
        views.CoverageGapActAPIView.as_view(),
        name="coverage-gap-act",
    ),
    path("issues", views.IssueListAPIView.as_view(), name="issue-list"),
    path("issues/<uuid:id>", views.IssueDetailAPIView.as_view(), name="issue-detail"),
    path("research", views.ResearchListAPIView.as_view(), name="research-list"),
    path(
        "research/<uuid:issue_id>",
        views.ResearchByIssueAPIView.as_view(),
        name="research-by-issue",
    ),
    path(
        "questions/<uuid:research_id>",
        views.QuestionsByResearchAPIView.as_view(),
        name="questions-by-research",
    ),
    path(
        "questions/submit",
        views.QuestionsSubmitAPIView.as_view(),
        name="questions-submit",
    ),
    path("fixes", views.FixListAPIView.as_view(), name="fix-list"),
    path(
        "fixes/<uuid:id>/approve",
        views.FixApproveAPIView.as_view(),
        name="fix-approve",
    ),
    path(
        "fixes/<uuid:id>/chat",
        views.FixChatAPIView.as_view(),
        name="fix-chat",
    ),
    path(
        "fixes/<uuid:id>",
        views.FixDetailAPIView.as_view(),
        name="fix-detail",
    ),
    path(
        "fixes/by-issue/<uuid:issue_id>",
        views.FixesByIssueAPIView.as_view(),
        name="fixes-by-issue",
    ),
]
