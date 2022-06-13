import json

from django.http import HttpResponse, JsonResponse

from trade.utils import is_ajax
from user.models import User


def get_usernames(request):
    if is_ajax(request):
        term = request.GET.get('term')
        users = User.objects.filter(username__icontains=term)[:10]
        usernames = list(users.values_list('username', flat=True))
    else:
        usernames = 'fail'
    return JsonResponse(usernames, safe=False)


def get_emails(request):
    if is_ajax(request):
        term = request.GET.get('term', '')
        users = User.objects.filter(email__icontains=term)
        emails = list(users.values_list('email', flat=True))
        json_data = json.dumps(emails)
    else:
        json_data = 'fail'
    mimetype = "application/json"
    return HttpResponse(json_data, mimetype)
