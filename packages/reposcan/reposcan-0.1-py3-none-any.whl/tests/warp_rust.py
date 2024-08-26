import re

from helpers.Helper import Helper

text = """
use warp::{Filter, http::Response, Rejection, Reply};

async fn test1(
    path_parameter1: String,
    path_parameter2: Option<u32>,
    query_parameter1: Option<String>,
    query_parameter2: Option<String>,
    header_parameter1: Option<String>,
    header_parameter2: Option<String>,
    request_body: Option<YourRequestBodyClass>,
    content_type: String
) -> Result<impl Reply, Rejection> {
    let response_body = match content_type.as_str() {
        "application/xml" => "<response><message>XML format</message></response>".to_string(),
        _ => serde_json::to_string(&incomes).unwrap(),
    };

    let status_code = if content_type == "application/xml" { 415 } else { 200 };

    Ok(Response::builder()
        .status(status_code)
        .header("Content-Type", content_type)
        .body(response_body)
        .unwrap())
}

async fn test2() -> Result<impl Reply, Rejection> {
    Ok(warp::reply::with_status("", warp::http::StatusCode::OK))
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
