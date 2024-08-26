import re

from helpers.Helper import Helper

text = """
import Kitura
import KituraNet
import SwiftyJSON

let router = Router()

router.get("/tag/:pathParameter1") { request, response, next in
    // Just comment
}

router.get("/tag/:pathParameter1/page-:pathParameter2") { request, response, next in
    // Query parameters
    let queryParameter1 = request.queryParameters["queryParameter1"]
    let queryParameter2 = request.queryParameters["queryParameter2"]
    
    // Header parameters
    let headerParameter1 = request.headers["headerParameter1"]
    let headerParameter2 = request.headers["headerParameter2"]
    
    // Body parameters
    let bodyParameter1 = try? request.read(as: JSON.self)["bodyParameter1"].string
    let bodyParameter2 = try? request.read(as: JSON.self)["bodyParameter2"].string
    
    // Content types and response codes
    if request.headers["Content-Type"] == "application/xml" {
        response.status(.unsupportedMediaType).send("<response><message>XML format</message></response>").end()
    } else {
        let incomes = ["incomes": "data"] // Replace with actual data
        response.status(.ok).send(json: incomes).end()
    }
}

router.post("/tag/:pathParameter1/page-:pathParameter2/xyz") { request, response, next in
    // Same as above
}

router.get("/tag") { request, response, next in
    response.status(.ok).end()
}

Kitura.addHTTPServer(onPort: 8080, with: router)
Kitura.run()

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
