import re

from helpers.Helper import Helper

text = """
class MyController {

    def test1(String pathParameter1, Integer pathParameter2) {
        // Query parameters
        def queryParameter1 = params.queryParameter1
        def queryParameter2 = params.queryParameter2

        // Header parameters
        def headerParameter1 = request.getHeader('headerParameter1')
        def headerParameter2 = request.getHeader('headerParameter2')

        // Body parameters
        def bodyParams = request.JSON
        def bodyParameter1 = bodyParams.bodyParameter1
        def bodyParameter2 = bodyParams.bodyParameter2

        // Content types and response codes
        if (request.getContentType() == 'application/xml') {
            render(contentType: 'application/xml', text: '<response><message>XML format</message></response>', status: 415)
        } else {
            def incomes = [incomes: 'data'] // Replace with actual data
            render(contentType: 'application/json', text: grails.converters.JSON.convert(incomes), status: 200)
        }
    }

    def test2() {
        render(status: 200)
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
