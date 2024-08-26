import re

from helpers.Helper import Helper

text = """
import ratpack.groovy.template.GroovyTemplateModule
import ratpack.server.RatpackServer
import ratpack.handling.Context
import ratpack.handling.Handler

class MyHandler implements Handler {

    @Override
    void handle(Context ctx) throws Exception {
        def pathParameter1 = ctx.getPathTokens().pathParameter1
        def pathParameter2 = ctx.getPathTokens().pathParameter2

        // Query parameters
        def queryParameter1 = ctx.request.queryParams.queryParameter1
        def queryParameter2 = ctx.request.queryParams.queryParameter2

        // Header parameters
        def headerParameter1 = ctx.request.headers.get('headerParameter1')
        def headerParameter2 = ctx.request.headers.get('headerParameter2')

        // Body parameters
        def bodyParams = ctx.parse(BodyParser.JSON).blockingGet()
        def bodyParameter1 = bodyParams.bodyParameter1
        def bodyParameter2 = bodyParams.bodyParameter2

        // Content types and response codes
        def contentType = ctx.request.headers.get('Content-Type')
        if (contentType == 'application/xml') {
            ctx.response.headers.set('Content-Type', 'application/xml')
            ctx.response.status(415).send('<response><message>XML format</message></response>')
        } else {
            def incomes = [incomes: 'data'] // Replace with actual data
            ctx.response.headers.set('Content-Type', 'application/json')
            ctx.response.status(200).send(groovy.json.JsonOutput.toJson(incomes))
        }
    }
}

RatpackServer.start {
    it.registryOf {
        it.add(GroovyTemplateModule)
    }
    it.handlers {
        get('tag/:pathParameter1', new MyHandler())
        get('tag/:pathParameter1/page-:pathParameter2', new MyHandler())
        post('tag/:pathParameter1/page-:pathParameter2/xyz', new MyHandler())
        get('tag') { ctx -> ctx.render('') }
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
