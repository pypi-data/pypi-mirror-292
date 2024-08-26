import re

from helpers.Helper import Helper

text = """
use Mojolicious::Lite;

get '/tag/:pathParameter1' => sub {
    my $c = shift;
    # Just comment
};

get '/tag/:pathParameter1/page-:pathParameter2' => sub {
    my $c = shift;
    
    # Query parameters
    my $queryParameter1 = $c->param('queryParameter1');
    my $queryParameter2 = $c->param('queryParameter2');
    
    # Header parameters
    my $headerParameter1 = $c->req->headers->header('headerParameter1');
    my $headerParameter2 = $c->req->headers->header('headerParameter2');
    
    # Body parameters
    my $body_params = $c->req->json;
    my $bodyParameter1 = $body_params->{'bodyParameter1'};
    my $bodyParameter2 = $body_params->{'bodyParameter2'};
    
    # Content types and response codes
    if ($c->req->headers->content_type eq 'application/xml') {
        $c->render(
            text => "<response><message>XML format</message></response>",
            format => 'xml',
            status => 415
        );
    } else {
        $c->render(
            json => { incomes => 'data' }, # Replace with actual data
            status => 200
        );
    }
};

post '/tag/:pathParameter1/page-:pathParameter2/xyz' => sub {
    my $c = shift;
    # Same as above
};

get '/tag' => sub {
    my $c = shift;
    $c->render(text => '');
};

app->start;

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
