import re

from helpers.Helper import Helper

text = """

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_http_methods(["GET"])
@require_http_methods(["POST"])
@require_http_methods(["GET", "POST"])
def test1(request, pathParameter1, pathParameter2=None):
    # Query parameters
    queryParameter1 = request.GET.get('queryParameter1')
    queryParameter2 = request.GET.get('queryParameter2')

    # Header parameters
    headerParameter1 = request.headers.get('headerParameter1')
    headerParameter2 = request.headers.get('headerParameter2')

    # Body parameters
    if request.body:
        body = json.loads(request.body)
        bodyParameter1 = body.get('bodyParameter1')
        bodyParameter2 = body.get('bodyParameter2')

    # Content types and response codes
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/xml':
        return HttpResponse("<response><message>XML format</message></response>", content_type='application/xml', status=415)
    else:
        return JsonResponse({'incomes': 'data'})  # Replace with actual data

@require_http_methods(["GET"])
def test2(request):
    return HttpResponse('', status=200)

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
