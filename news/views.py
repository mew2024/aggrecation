from django_ratelimit.decorators import ratelimit
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from news.forms import UserLoginForm
from news.models import Article, ViewingHistory, Favorite
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from urllib.parse import quote
import feedparser

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'このユーザー名は既に使われています')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, '登録が完了しました。ログインしてください')
        return redirect('login')

    return render(request, 'register.html')


def ajax_user_login(request):
    """
    非同期ログイン（Ajax用）
    """
    if request.method == 'POST':
        identifier = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # ユーザー取得
        user_obj = None
        try:
            user_obj = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user_obj = User.objects.get(email=identifier)
            except User.DoesNotExist:
                pass

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                next_url = request.POST.get('next', '/mypage/')
                if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    next_url = '/mypage/'
                return JsonResponse({"success": True, "redirect_url": next_url})

        return JsonResponse({"success": False, "message": "ユーザー名、またはパスワードが正しくありません"})

    return JsonResponse({"success": False, "message": "不正なリクエストです"})

    
def user_logout(request):
    logout(request)
    return redirect('top')
    
def top(request):
    query = request.GET.get('q', '')
    if query:
        articles = Article.objects.filter(title__icontains=query)
    else:
        articles = Article.objects.all()
        
    paginator = Paginator(articles, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        'articles': page_obj,
        'query': query,
    }
    return render(request, 'top.html', context)

@login_required
def mypage(request):
    user = request.user
    history_list = user.viewinghistory_set.all().order_by('-viewed_at')
    
    history_paginator = Paginator(history_list, 5)
    history_page_number = request.GET.get('history_page')
    history = history_paginator.get_page(history_page_number)
    
    favorites = Favorite.objects.filter(user=request.user)
    fav_paginator = Paginator(favorites, 5)
    fav_page_number = request.GET.get("fav_page")
    fav_page_obj = fav_paginator.get_page(fav_page_number)
    
    context = {
        'user': user,
        'history': history,
        'favorites': fav_page_obj,
    }
    return render(request, 'mypage.html', context)

def article_search(request):
    query = request.GET.get('q', '').strip()
    encoded_query = quote(query)  # URLエンコード
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"

    feed = feedparser.parse(rss_url)
    articles = []

    for entry in feed.entries:
        # キーワードがタイトルに含まれる場合だけ追加（query が空なら全部）
        if not query or query.lower() in entry.title.lower():
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'published': getattr(entry, 'published', '')
            })
            
    paginator = Paginator(articles, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    

    context = {
        'articles': page_obj,
        'query': query,
    }
    return render(request, 'article_search.html', context)


def view_article(request):
    link = request.GET.get("url")
    title = request.GET.get("title", link)
    
    if not link:
        return redirect("top")
    
    if not url_has_allowed_host_and_scheme(url=link, allowed_hosts=None):
        messages.error(request, "不正なリクエストです")
        return redirect("top")
    
    if request.user.is_authenticated:
        article, created = Article.objects.get_or_create(
            title=title,
            defaults={"article_url": link}
        )
    ViewingHistory.objects.create(
        user=request.user,
        article=article, 
        article_url=link
        )
    
    return redirect(link)

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if request.user.is_authenticated:
        ViewingHistory.objects.create(
            user = request.user,
            article = article,
            article_url = request.build_absolute_uri()
        )
    
    return render(request, 'article_detail.html', {'article':article})  

def toggle_favorite(request):
    if request.method == "POST":
        article_id = request.POST.get("article_id")
        article = get_object_or_404(Article, id=article_id)
        
        fav, created = Favorite.objects.get_or_create(
            user=request.user,
            url=article.article_url,
            defaults={"title": article.title}
            )
        if not created:
            fav.delete()
            return JsonResponse({"status": "removed"})
        return JsonResponse({"status": "added"})
    return JsonResponse({"status": "error"}, status=400)
    
@require_POST
def track_article(request):
    """
    Ajax で記事閲覧履歴を記録する
    """
    
    import json
    data = json.loads(request.body)
    link = data.get('link')
    title = data.get('title')
    if link and title and request.user.is_authenticated:
        article, created = Article.objects.get_or_create(
            title=title,
            defaults={'article_url':link}
        )
        
        ViewingHistory.objects.create(
            user=request.user,
            article=article
            )
        
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def ajax_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=username, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "redirect_url": "/mypage"})
        else:
            return JsonResponse({"success": False, "message": "入力内容が間違っています"})
    return JsonResponse({"success": False, "message": "不正なリクエストです"})

@ratelimit(key='ip', rate='5/m', block=True)
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            # ユーザー取得
            try:
                user_obj = User.objects.get(username=identifier)
            except User.DoesNotExist:
                try:
                    user_obj = User.objects.get(email=identifier)
                except User.DoesNotExist:
                    user_obj = None

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"{user.username}でログインしました")

                    # nextパラメータがあればそこへリダイレクト、なければマイページ
                    next_url = request.GET.get('next', 'mypage')
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        return redirect(next_url)
                    return redirect('mypage')

            messages.error(request, "ユーザー名、またはパスワードが正しくありません")
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})        