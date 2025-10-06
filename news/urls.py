from django.urls import path
from . import views

urlpatterns = [
    path('', views.top, name='top'),  # トップページ
    path('login/', views.user_login, name='login'),  # ログイン
    path('ajax_user_login/', views.ajax_user_login, name='ajax_user_login'),
    path('mypage/', views.mypage, name='mypage'),  # マイページ
    path('articles/', views.article_search, name='article_search'),  # 記事検索
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('view/', views.view_article, name='view_article'),
    path('track_article/', views.track_article, name='track_article'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path("toggle-favorite/", views.toggle_favorite, name="toggle_favorite"), 
]
