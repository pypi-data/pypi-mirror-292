import re

from helpers.Helper import Helper

text = """
const Hapi = require('@hapi/hapi');

const init = async () => {
    const server = Hapi.server({
        port: 3000,
        host: 'localhost'
    });

    server.route({
        method: 'GET',
        path: '/tag/{pathParameter1}',
        handler: (request, h) => {
            // Just comment
            return h.response().code(200);
        }
    });

    server.route({
        method: ['GET', 'POST'],
        path: '/tag/{pathParameter1}/page-{pathParameter2}',
        handler: (request, h) => {
            // Query parameters
            const queryParameter1 = request.query.queryParameter1;
            const queryParameter2 = request.query.queryParameter2;

            // Header parameters
            const headerParameter1 = request.headers.headerparameter1;
            const headerParameter2 = request.headers.headerparameter2;

            // Body parameters
            const bodyParameter1 = request.payload.bodyParameter1;
            const bodyParameter2 = request.payload.bodyParameter2;

            // Content types and response codes
            if (request.headers['content-type'] === 'application/xml') {
                return h.response("<response><message>XML format</message></response>").type('application/xml').code(415);
            } else {
                return h.response({ incomes: 'data' }).code(200); // Replace with actual data
            }
        }
    });

    server.route({
        method: 'GET',
        path: '/tag',
        handler: (request, h) => {
            return h.response().code(200);
        }
    });

    await server.start();
    console.log('Server running on %s', server.info.uri);
};

process.on('unhandledRejection', (err) => {
    console.log(err);
    process.exit(1);
});

init();


"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
