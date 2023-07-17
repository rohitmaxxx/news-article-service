from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.db.models import Count


import json
import logging
from decouple import config

from .models import newsArticle, searchHistory, newsUser
from .utils import apiResponse, prepareFilter, fetchNewsByAPI

DEBUG = config('DEBUG', default=False, cast=bool)
logger = logging.getLogger(__name__)


# Create your views here.


def getNewsData(q, user_id, filters, search_id=None, old_news=None, params_str=""):
    news_data = fetchNewsByAPI(q, filters, params_str, config)
    if (news_data.status_code != 200):
        return None

    news_data = news_data.json()
    if not search_id:
        result_search_history = searchHistory.objects.create(user_id=user_id, search_str=q, total_results=news_data['totalResults'])
        search_id = result_search_history.id
    bulk_data = []
    if old_news:
        print("Latest new fetch count before: ", len(news_data['articles']))
        news_data['articles'] = [_ for _ in news_data['articles'] if _['url'] not in old_news]
        print("Latest new fetch count before: ", len(news_data['articles']))

    print("Article from API: ", len(news_data))

    if 'publishedAt__date' in filters:
        filters.pop('publishedAt__date')
    for data in news_data['articles']:
        if 'source' not in filters:
            filters['source'] = data['source']['name']
        data.pop('source')
        bulk_data.append(newsArticle(search_id=search_id, **data, **filters))

    newsArticle.objects.bulk_create(bulk_data)

    return news_data


class homepageRenderView(View):
    def get(self, request):
        """
        Handle GET requests render page.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - Render homepage page
        """
        return render(request, 'index.html')


class userTrendingKeyRenderView(View):
    def get(self, request):
        """
        Handle GET requests render page.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - Render trending page
        """
        return render(request, 'trending_keys.html')


class profileRenderView(View):
    def get(self, request):
        """
        Handle GET requests render page.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - Render profile page
        """
        return render(request, 'profile.html', {'user': request.user})
    

class adminRenderView(View):
    def get(self, request):
        """
        Handle GET requests render page.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - Render admin page
        """
        return render(request, 'admin.html')


class historyRenderView(View):
    def get(self, request):
        """
        Handle GET requests render page.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - Render keyword searched history page
        """
        return render(request, 'history.html')


class articlesRenderView(View):
    def get(self, request):
        """
        Handle GET requests render page.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - Render article page
        """
        return render(request, 'articles.html')


class userLogin(View):
    def get(self, request):
        """
        Handle GET requests render page.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - Render login page
        """
        return render(request, 'login.html')

    def post(self, request):
        """
        Handle POST requests to login user.

        Args:
        - request: The HTTP request object.
        - username
        - password
        Returns:
        - Redirect to admin user dashboard if user is admin otherwise article page
        """
        body = json.loads(request.body)
        username = body.get('username')
        password = body.get('password')
        next_page = request.GET.get('next')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            redirect_url = '/news_article/'
            if user.is_superuser:
                redirect_url = '/news_article/admin/'
            else:
                if next_page:
                    redirect_url = next_page

            return apiResponse({'redirect_url': redirect_url})
        else:
            return apiResponse({'message': 'Invalid username or password'}, status=False)


class userView(View):
    def get(self, request):
        """
        Handle GET requests to retrieve all created users except admin.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - API response with serialized user data with following dictionary keys:
            - user_id
            - quota
            - username
            - email
            - is_active
            - created_at
        """
        user_data = newsUser.objects.filter(is_superuser=False)
        serialized_data = []
        for data in user_data:
            data_dict = {
                "user_id": data.id,
                "quota": data.quota,
                "username": data.username,
                "email": data.email,
                "is_active": data.is_active,
                "created_at": data.date_joined,
            }
            serialized_data.append(data_dict)

        return apiResponse(serialized_data)
    
    def post(self, request):
        """
        Handle POST requests to add new user.

        Args:
        - request: The HTTP request object.
        - username
        - quota
        - email
        - password
        Returns:
        - Redirect to admin user dashboard
        """
        body = request.POST
        username = body['username'].strip()
        quota = body['quota'].strip()
        email = body['email'].strip()
        password = body['password'].strip()

        if not quota:
            quota = 0

        user = newsUser.objects.create_user(username, email, password, quota=int(quota))

        email_temp = f'''
                Dear { username },

                Your password is: { password }

                Please keep this information secure and do not share it with anyone.

                Thank you.
                ''',
        
        print("Send password")
        try:
            send_mail(
                "Your Password",
                f"Your news article username: {username} and password is: { password }",
                config('EMAIL_HOST_USER'),
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("Password email failed: ", e)

        return redirect('/news_article/admin/')
        
    def patch(self, request):
        body = json.loads(request.body)
        user_data = get_object_or_404(newsUser, id=body['user_id'])
        user_data.is_active = body['is_active']
        user_data.save()

        return apiResponse(None)


class newsArticleView(View):
    """
    View class for handling news article requests.

    Methods:
    - get: Retrieve news articles searched keywords by user id.
    - post: Create or retrieve news articles based on the user's query.
    """

    def get(self, request):
        """
        Handle GET requests to retrieve news articles searched keywords by user id.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - API response with serialized news article searched keywords with following dictionary keys:
            - id
            - search_str
            - total_results
            - count
            - created_at
        """
        try:
            news_data = searchHistory.objects.filter(user_id=request.user.id).order_by('-created_at')
            serialized_data = []
            for data in news_data:
                data_dict = {
                    'id': data.id,
                    'search_str': data.search_str,
                    'total_results': data.total_results if data.total_results else 0,
                    'count': data.count,
                    'created_at': data.created_at
                }
                serialized_data.append(data_dict)

            return apiResponse(serialized_data)
        except newsArticle.DoesNotExist:
            return apiResponse({'Error': "News not found"}, status=False)


    def post(self, request):
        """
        Handle POST requests to create or retrieve news articles based on the user's query.

        Args:
        - request: The HTTP request object.
        - query: Query string to search news.
        - fetch_latest: Boolean value to detect it latest news needs to be searched.
        - filters: Filters retrieve news accordingly. Following filters includes
            - source
            - category
            - language
            - publishedAt

        Returns:
        - API response with news article data. With following dictionary keys:
            - title
            - author
            - description
            - url
            - publishedAt
        """
        try:
            body = json.loads(request.body)
            q = body.get('query', '').strip()
            search_id = body.get('search_id', '').strip()
            fetch_latest = body.get('fetch_latest', False)
            filters = prepareFilter(body.get('filters'))
            user_id = request.user.id
            first_time_load = False
            article_data = []

            if not request.user.quota > 0 and q:
                return apiResponse(None, msg=f"Your keyword quota is zero. Contact admin to increase")
            if q:
                result_search_history = searchHistory.objects.filter(user_id=user_id, search_str=q).first()
            else:
                if search_id:
                    result_search_history = searchHistory.objects.filter(user_id=user_id, id=search_id).order_by('-updated_at').first()
                else:
                    result_search_history = searchHistory.objects.filter(user_id=user_id).order_by('-updated_at').first()
                if not result_search_history:
                    return apiResponse(None, msg="Please enter a valid search input")
                first_time_load = True

            if result_search_history:
                if q:
                    result_search_history.count += 1
                q = result_search_history.search_str
                current_time = timezone.localtime(timezone.now())
                time_difference = (current_time - result_search_history.updated_at).total_seconds()
                keyword_threshold = int(config('KEYWORD_THRESHOLD'))
                if time_difference < keyword_threshold and not (first_time_load or fetch_latest):  # 900 seconds = 15 minutes
                    return apiResponse(None, msg=f"Try this keyword after {round((keyword_threshold - time_difference)/60, 2)} min", status=True)
                # Update Updated datetime for asked keyword
                result_articles = newsArticle.objects.filter(search_id=result_search_history.id, **filters).order_by('-publishedAt')
                old_news = [_.url for _ in result_articles]
                print("Existing local article: ", len(result_articles))
                if fetch_latest or (not old_news):
                    from_date_q = ''
                    if old_news:
                        print("Data not exist on local", filters)
                        latest_date = result_articles[0].publishedAt
                        from_date_q = f'&from={latest_date.year}-{latest_date.month}-{latest_date.day}'
                    news_data = getNewsData(q, user_id, filters, search_id=result_search_history.id, old_news=old_news, params_str=from_date_q)
                    print("Check filters", filters)
                    if news_data:
                        article_data.extend(news_data['articles'])
                        result_search_history.total_results += len(news_data['articles'])
                for d in result_articles:
                    data_dict = {
                        "title": d.title,
                        "author": d.author,
                        "description": d.description,
                        "url": d.url,
                        "publishedAt": d.publishedAt,
                    }
                    article_data.append(data_dict)
                
                result_search_history.save()
                print("Keyword already exist: ", q)
            else:
                result_search_history = searchHistory.objects.create(user_id=user_id, search_str=q, total_results=0)
                search_id = result_search_history.id
                news_data = getNewsData(q, user_id, filters, search_id=search_id)
                if news_data:
                    article_data = news_data['articles']
                    result_search_history.total_results = len(news_data['articles'])
                    result_search_history.save()

                # Decrease quata when new keyword searched by user
                request.user.quota -= 1
                request.user.save()

            respose_data = {
                'search_id': result_search_history.id,
                'query': result_search_history.search_str,
                'totalResults': result_search_history.total_results,
                'articles': article_data,
            }

            return apiResponse(respose_data)
        except Exception as e:
            print(e)
            return apiResponse({"Error": "Error in creating news"}, status=False)


class newsArticleDetailsView(View):
    def get(self, request, id):
        """
        Handle GET requests to retrieve news article by search keyword.

        Args:
        - request: The logged in user HTTP request object and search id

        Returns:
        - API response with serialized news article with following dictionary keys:
            - id
            - author
            - title
            - description
            - url
            - publishedAt
        """
        try:
            news_data = newsArticle.objects.filter(search_id=id).order_by('-publishedAt')
            serialized_data = []
            for data in news_data:
                data_dict = {
                    'id': data.id,
                    'author': data.author,
                    'title': data.title,
                    'description': data.description,
                    'url': data.url,
                    'publishedAt': data.publishedAt,
                }
                serialized_data.append(data_dict)

            return apiResponse(serialized_data)
        except newsArticle.DoesNotExist:
            return apiResponse({'Error': "News not found"}, status=False)


class userTrendingKeywordsView(View):
    def get(self, request):
        """
        Handle GET requests to retrieve trending searched keywords by user.

        Args:
        - request: The logged in user HTTP request object.

        Returns:
        - API response with serialized news article searched keywords with following dictionary keys:
            - keyword
            - count
        """
        trending_searches = searchHistory.objects.values('search_str', 'count').order_by('-count')

        data_dict = {}
        for trend in trending_searches:
            search_str = trend['search_str']
            if search_str not in data_dict:
                data_dict[search_str] = trend['count']
            else:
                data_dict[search_str] += trend['count']
        sorted_data = sorted(data_dict.items(), key=lambda item: item[1], reverse=True)
        result = [{'keyword': search_str, 'count': count} for search_str, count in sorted_data]

        print(f"Search string:", result)
        return apiResponse(result)