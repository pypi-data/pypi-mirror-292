import re

from helpers.Helper import Helper

text = """
const Koa = require('koa');
const Router = require('@koa/router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

router.get('/tag/:pathParameter1', ctx => {
    // Just comment
    ctx.status = 200;
});

router.get('/tag/:pathParameter1/page-:pathParameter2', ctx => {
    // Query parameters
    const queryParameter1 = ctx.query.queryParameter1;
    const queryParameter2 = ctx.query.queryParameter2;

    // Header parameters
    const headerParameter1 = ctx.headers['headerparameter1'];
    const headerParameter2 = ctx.headers['headerparameter2'];

    // Body parameters
    const bodyParameter1 = ctx.request.body.bodyParameter1;
    const bodyParameter2 = ctx.request.body.bodyParameter2;

    // Content types and response codes
    if (ctx.headers['content-type'] === 'application/xml') {
        ctx.status = 415;
        ctx.type = 'application/xml';
        ctx.body = "<response><message>XML format</message></response>";
    } else {
        ctx.status = 200;
        ctx.body = { incomes: 'data' }; // Replace with actual data
    }
});

router.post('/tag/:pathParameter1/page-:pathParameter2/xyz', ctx => {
    // Same as above
});

router.get('/tag', ctx => {
    ctx.status = 200;
});

app
    .use(bodyParser())
    .use(router.routes())
    .use(router.allowedMethods());

app.listen(3000, () => {
    console.log('Server running on port 3000');
});

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
