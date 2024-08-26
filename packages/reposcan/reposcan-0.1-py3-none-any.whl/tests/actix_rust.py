import re

from helpers.Helper import Helper

text = """
use actix_web::{web, HttpResponse, HttpRequest, Responder};

#[get("/tag/{path_parameter1}")]
#[get("/tag/{path_parameter1}/page-{path_parameter2}")]
#[post("/tag/{path_parameter1}/page-{path_parameter2}/xyz")]
async fn test1(
    path_parameter1: web::Path<String>,
    path_parameter2: Option<web::Path<u32>>,
    query_parameter1: Option<web::Query<String>>,
    query_parameter2: Option<web::Query<String>>,
    header_parameter1: Option<web::Header<String>>,
    header_parameter2: Option<web::Header<String>>,
    request_body: Option<web::Json<YourRequestBodyClass>>,
    req: HttpRequest
) -> impl Responder {
    let content_type = req.headers().get("Content-Type").unwrap_or(&"application/json".into()).to_str().unwrap_or("application/json");

    let response_body = match content_type {
        "application/xml" => "<response><message>XML format</message></response>".to_string(),
        _ => serde_json::to_string(&incomes).unwrap(),
    };

    if content_type == "application/xml" {
        HttpResponse::UnsupportedMediaType().body(response_body)
    } else {
        HttpResponse::Ok().content_type(content_type).body(response_body)
    }
}

#[get("/tag")]
async fn test2() -> impl Responder {
    HttpResponse::Ok().finish()
}

"""

# Loop all api matches
apiPattern = r'''((?:\#\[(?P<httpMethods>\w+)(?P<paths>.*)\n)|(?:async fn (?P<functionName>\w+).*\n)|(?:(?P<pathParameters>\S+):.*Path.*\n)|(?:(?P<queryParameters>\S+):.*Query.*\n)|(?:(?P<headerParameters>\S+):.*Header.*\n)|(?:(?P<bodyParameters>\S+):.*Body.*\n)|(?:content_type == (?P<contentTypes>\".*\").*\n)|(?:HttpResponse::(?P<responseCodes>\w+).*\n)|.*?\n)*?.*?(?=\n\n\#\[|\Z)'''

# Loop all api matches
apiMatches = re.finditer(apiPattern, text)
apiMatches = [apiMatch for apiMatch in apiMatches if apiMatch.group(0).strip() != ""]
linePatterns = Helper.getLinePatterns(apiPattern)
secondSeparatorParts= [""]
for apiMatch in apiMatches:
    apiMatchResult = Helper.getAPIMatchResult(apiMatch, linePatterns, secondSeparatorParts)
    if apiMatchResult and ("paths" in apiMatchResult or "httpMethods" in apiMatchResult):
        print(apiMatchResult)
