import re

from helpers.Helper import Helper

text = """
#[macro_use] extern crate rocket;

use rocket::http::ContentType;
use rocket::response::content;
use rocket::serde::json::Json;
use rocket::Request;
use rocket::data::FromData;

#[get("/tag/<path_parameter1>")]
#[get("/tag/<path_parameter1>/page-<path_parameter2>")]
#[post("/tag/<path_parameter1>/page-<path_parameter2>/xyz")]
fn test1(
    path_parameter1: String,
    path_parameter2: Option<u32>,
    query_parameter1: Option<String>,
    query_parameter2: Option<String>,
    header_parameter1: Option<String>,
    header_parameter2: Option<String>,
    request_body: Option<Json<YourRequestBodyClass>>,
    request: &Request
) -> (ContentType, String) {
    let content_type = request.headers().get_one("Content-Type").unwrap_or("application/json");

    let response_body = match content_type {
        "application/xml" => "<response><message>XML format</message></response>".to_string(),
        "application/json" | _ => serde_json::to_string(&incomes).unwrap(),
    };

    let status_code = if content_type == "application/xml" { 415 } else { 200 };

    (ContentType::new(content_type), response_body)
}

#[get("/tag")]
fn test2() -> &'static str {
    ""
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@ApiResponse\((?:responseCode = )?\"(?P<responseCodes>\d+)\".*\n)|(?:.*@RequestMapping\((?:value = )?\"(?P<paths>(.*?(?P<pathParameters>\{\w+\})?.*?))\".*\n)|(?:.*@RequestMapping.*\(.*method = \{(.*(?P<httpMethods>\.\w+)*?.*)\}.*\n)|(?:.*@RequestMapping.*?\(.*?((?:consumes|produces) = (?P<contentTypes>\{[^}]+\}).*)\n)|(?:.*?(?:public|protected|private) \S+ (?P<functionName>\w+)\(.*\n)|(?:.*@RequestParam\((?:value = )?\"(?P<queryParameters>.*)\".*\n)|(?:.*@RequestHeader\((?:value = )?\"(?P<headerParameters>.*)\".*\n)|(?:.*@RequestBody.*Map<String, Object> (?P<bodyParameters>\w+).*\n)|.*?\n)*?.*\;\n\s*\}'''
