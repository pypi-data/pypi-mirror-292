import re

from helpers.Helper import Helper

text = """
import play.api.mvc._
import play.api.libs.json.Json

class MyController @Inject()(cc: ControllerComponents) extends AbstractController(cc) {

  def test1(pathParameter1: String, pathParameter2: Int) = Action { request =>
    // Query parameters
    val queryParameter1 = request.getQueryString("queryParameter1").getOrElse("")
    val queryParameter2 = request.getQueryString("queryParameter2").getOrElse("")

    // Header parameters
    val headerParameter1 = request.headers.get("headerParameter1").getOrElse("")
    val headerParameter2 = request.headers.get("headerParameter2").getOrElse("")

    // Body parameters
    val body = request.body.asJson.getOrElse(Json.obj())
    val bodyParameter1 = (body \ "bodyParameter1").asOpt[String].getOrElse("")
    val bodyParameter2 = (body \ "bodyParameter2").asOpt[String].getOrElse("")

    // Content types and response codes
    request.contentType match {
      case Some("application/xml") =>
        Results.Status(415).contentType("application/xml").send("<response><message>XML format</message></response>")
      case Some("application/json") =>
        Results.Ok(Json.obj("incomes" -> "data")) // Replace with actual data
      case _ =>
        Results.Ok(Json.obj("incomes" -> "data")) // Replace with actual data
    }
  }

  def test2() = Action {
    Results.Ok
  }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
