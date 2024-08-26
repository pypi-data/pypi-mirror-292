import re

from helpers.Helper import Helper

text = """
use Dancer2;

get '/tag/:pathParameter1' => sub {
    # Just comment
};

get '/tag/:pathParameter1/page-:pathParameter2' => sub {
    # Query parameters
    my $queryParameter1 = param('queryParameter1');
    my $queryParameter2 = param('queryParameter2');
    
    # Header parameters
    my $headerParameter1 = request->headers->get('headerParameter1');
    my $headerParameter2 = request->headers->get('headerParameter2');
    
    # Body parameters
    my $bodyParameters = request->body_parameters->all;
    my $bodyParameter1 = $bodyParameters->{'bodyParameter1'};
    my $bodyParameter2 = $bodyParameters->{'bodyParameter2'};
    
    # Content types and response codes
    my $content_type = request->headers->get('Content-Type');
    if ($content_type eq 'application/xml') {
        return [415, ['Content-Type' => 'application/xml'], "<response><message>XML format</message></response>"];
    } else {
        return [200, ['Content-Type' => 'application/json'], encode_json({incomes => 'data'})];
    }
};

post '/tag/:pathParameter1/page-:pathParameter2/xyz' => sub {
    # Same as above
};

get '/tag' => sub {
    return [200, [], ''];
};

start;

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
