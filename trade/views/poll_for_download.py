import json

from django.http import HttpResponse, HttpResponseForbidden

from celery.result import AsyncResult

from trade.utils import is_ajax


def poll_for_download(request):
    task_id = request.GET.get("task_id")
    filename = request.GET.get("filename")

    if is_ajax(request):
        result = AsyncResult(task_id)
        if result.ready():
            return HttpResponse(json.dumps({"filename": result.get()}))
        return HttpResponse(json.dumps({"filename": None}))

    try:
        with open(filename, "rb") as excel:
            data = excel.read()
    except :
        return HttpResponseForbidden()
    else:
        response = HttpResponse(data, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
