import re

from helpers.Helper import Helper

text = """
using Nancy;

public class MyModule : NancyModule
{
    public MyModule()
    {
        Get("/tag/{pathParameter1}", args => Test1((string)args.pathParameter1, null));
        Get("/tag/{pathParameter1}/page-{pathParameter2}", args => Test1((string)args.pathParameter1, args.pathParameter2));
        Post("/tag/{pathParameter1}/page-{pathParameter2}/xyz", args => Test1((string)args.pathParameter1, args.pathParameter2));

        Get("/tag", args => Test2());
    }

    private dynamic Test1(string pathParameter1, int? pathParameter2)
    {
        var queryParameter1 = Request.Query.queryParameter1;
        var queryParameter2 = Request.Query.queryParameter2;
        var headerParameter1 = Request.Headers.HeaderParameter1;
        var headerParameter2 = Request.Headers.HeaderParameter2;
        var bodyParameters = this.Bind<YourRequestBodyClass>();

        var contentType = Request.Headers.ContentType;

        if (contentType == "application/xml")
        {
            return Negotiate.WithContentType("application/xml")
                            .WithModel("<response><message>XML format</message></response>")
                            .WithStatusCode(HttpStatusCode.UnsupportedMediaType);
        }
        else
        {
            return Negotiate.WithModel(new { incomes = incomes }) // Replace `incomes` with your data
                            .WithStatusCode(HttpStatusCode.OK);
        }
    }

    private dynamic Test2()
    {
        return HttpStatusCode.OK;
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
