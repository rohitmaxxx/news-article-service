from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required


from .views import (
    newsArticleView, newsArticleDetailsView,
    historyRenderView, articlesRenderView, profileRenderView,
    adminRenderView, userView, userLogin, homepageRenderView,
    userTrendingKeywordsView, userTrendingKeyRenderView
    )

from .utils import superuser_required


urlpatterns = [
    path('', login_required(homepageRenderView.as_view())),
    path('profile/', login_required(profileRenderView.as_view()), name="profile"),
    path('admin/', superuser_required(adminRenderView.as_view()), name="admin"),
    path('admin/keywords/', superuser_required(userTrendingKeyRenderView.as_view()), name="keywords"),
    path('admin/trend_keys/', superuser_required(userTrendingKeywordsView.as_view()), name="trend_keys"),
    path('admin/user/', superuser_required(userView.as_view()), name="user"),
    path('news/', login_required(newsArticleView.as_view()), name="news"),
    path('history/articles', login_required(articlesRenderView.as_view()), name="history_articles"),
    path('history/', login_required(historyRenderView.as_view()), name="history"),
    path('news/<int:id>/', login_required(newsArticleDetailsView.as_view()), name="news_details"),
    path('login/', userLogin.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]