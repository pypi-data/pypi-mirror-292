import re

from helpers.Helper import Helper

text = """
import Vapor

func routes(_ app: Application) throws {
    
    app.get("tag", ":pathParameter1") { req -> HTTPStatus in
        // Just comment
        return .ok
    }

    app.get("tag", ":pathParameter1", "page-:pathParameter2") { req -> HTTPStatus in
        let pathParameter1 = req.parameters.get("pathParameter1") ?? ""
        let pathParameter2 = req.parameters.get("pathParameter2") ?? ""
        
        // Query parameters
        let queryParameter1 = req.query[String.self, at: "queryParameter1"]
        let queryParameter2 = req.query[String.self, at: "queryParameter2"]
        
        // Header parameters
        let headerParameter1 = req.headers["headerParameter1"]
        let headerParameter2 = req.headers["headerParameter2"]
        
        // Body parameters
        let body = try req.content.decode(YourRequestBodyClass.self)
        let bodyParameter1 = body.bodyParameter1
        let bodyParameter2 = body.bodyParameter2
        
        // Content types and response codes
        if req.headers.contentType == .xml {
            return req.response("XML format", as: .xml).status(.unsupportedMediaType)
        } else {
            let incomes = ["incomes": "data"] // Replace with actual data
            return req.response(incomes, as: .json).status(.ok)
        }
    }

    app.post("tag", ":pathParameter1", "page-:pathParameter2", "xyz") { req -> HTTPStatus in
        // Same as above
        return .ok
    }

    app.get("tag") { req -> HTTPStatus in
        return .ok
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
