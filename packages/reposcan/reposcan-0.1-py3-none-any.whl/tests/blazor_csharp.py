import re

from helpers.Helper import Helper

text = """
@page "/tag/{pathParameter1}/{pathParameter2?}"
@inject HttpClient Http

<h3>Test1</h3>

@functions {
    [Parameter] public string PathParameter1 { get; set; }
    [Parameter] public int? PathParameter2 { get; set; }
    public string QueryParameter1 { get; set; }
    public string QueryParameter2 { get; set; }
    public string HeaderParameter1 { get; set; }
    public string HeaderParameter2 { get; set; }
    public YourRequestBodyClass BodyParameters { get; set; }

    protected override async Task OnInitializedAsync()
    {
        var request = new HttpRequestMessage(HttpMethod.Get, $"/tag/{PathParameter1}/page-{PathParameter2}/xyz");
        request.Headers.Add("queryParameter1", QueryParameter1);
        request.Headers.Add("queryParameter2", QueryParameter2);
        request.Headers.Add("headerParameter1", HeaderParameter1);
        request.Headers.Add("headerParameter2", HeaderParameter2);

        var response = await Http.SendAsync(request);
        var contentType = response.Content.Headers.ContentType.MediaType;
        
        if (contentType == "application/xml")
        {
            // Handle XML response
        }
        else
        {
            var responseBody = await response.Content.ReadAsStringAsync();
            // Handle JSON response
        }
    }
}


"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
