from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from datetime import datetime
import requests



def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper



def apiResponse(data, status=True, msg='', status_code=None):
    status = True if status == True else False
    if status_code is None:
        status_code = 200 if status else 400
    # print("=============== :req:  ", data)
    resp_data = {
        "status": 'success' if status else 'failed',
        "data": data,
        'message': msg
    }

    return JsonResponse(resp_data, status=status_code, safe=False)


def prepareFilter(filters):
    if not filters:
        return {}
    allowed_filters = ['source', 'category', 'language', 'publishedAt']
    new_filters = {}
    for key in filters:
        if (key in allowed_filters) and filters[key]:
            if key == 'publishedAt':
                date_object = datetime.strptime(filters[key], "%m/%d/%Y")
                new_filters['publishedAt__date'] = date_object.date()
                continue
        new_filters[key] = filters[key]
    return new_filters


def prepareFilterQueryParams(filters):
    if not filters:
        return ''
    filter_q = ''
    for key in filters:
        if key == 'publishedAt__date':
            date = filters[key]
            filter_q += f'&from={date}&to={date}'
            continue
        filter_q += f'&{key}={filters[key]}'

    return filter_q


def fetchNewsByAPI(q, filters, params_str, config):
    url = f"https://newsapi.org/v2/everything?q={q}&sortBy=publishedAt&apiKey={config('NEWS_API_KEY')}{params_str}{prepareFilterQueryParams(filters)}"

    print("Final URL: ", url)
    return requests.get(url)


def fetchNewsHeadlineByAPI(q, filters, params_str, config):
    url = f"https://newsapi.org/v2/top-headlines?q={q}&sortBy=publishedAt&apiKey={config('NEWS_API_KEY')}{params_str}{prepareFilterQueryParams(filters)}"

    print("Final URL: ", url)
    return requests.get(url)