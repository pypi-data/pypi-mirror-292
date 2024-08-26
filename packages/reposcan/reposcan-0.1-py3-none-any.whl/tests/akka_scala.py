import re

from helpers.Helper import Helper

text = """
import akka.http.scaladsl.model._
import akka.http.scaladsl.server.Directives._
import akka.http.scaladsl.server.Route
import spray.json._

object MyRoutes {

  def routes: Route =
    path("tag" / Segment) { pathParameter1 =>
      get {
        complete(StatusCodes.OK)
      }
    } ~
    path("tag" / Segment / "page-" / IntNumber) { (pathParameter1, pathParameter2) =>
      (get & parameters('queryParameter1.?, 'queryParameter2.?) & headers) { (queryParameter1, queryParameter2, headers) =>
        entity(as[JsValue]) { body =>
          val headerParameter1 = headers.find(_.name == "headerParameter1").map(_.value)
          val headerParameter2 = headers.find(_.name == "headerParameter2").map(_.value)
          val bodyParameter1 = (body \ "bodyParameter1").asOpt[String]
          val bodyParameter2 = (body \ "bodyParameter2").asOpt[String]

          // Content types and response codes
          if (headers.find(_.name == "Content-Type").exists(_.value == "application/xml")) {
            complete(HttpEntity(ContentTypes.`application/xml(UTF-8)`, "<response><message>XML format</message></response>"))
          } else {
            complete(StatusCodes.OK, JsObject("incomes" -> JsString("data"))) // Replace with actual data
          }
        }
      }
    } ~
    path("tag" / Segment / "page-" / IntNumber / "xyz") { (pathParameter1, pathParameter2) =>
      get {
        complete(StatusCodes.OK)
      }
    } ~
    path("tag") {
      get {
        complete(StatusCodes.OK)
      }
    }
}

"""

# Loop all api matches
# No solution yet
apiPattern = r'''((?:\#\[(?P<httpMethods>\w+)(?P<paths>.*)\n)|(?:async fn (?P<functionName>\w+).*\n)|(?:(?P<pathParameters>\S+):.*Path.*\n)|(?:(?P<queryParameters>\S+):.*Query.*\n)|(?:(?P<headerParameters>\S+):.*Header.*\n)|(?:(?P<bodyParameters>\S+):.*Body.*\n)|(?:content_type == (?P<contentTypes>\".*\").*\n)|(?:HttpResponse::(?P<responseCodes>\w+).*\n)|.*?\n)*?.*?(?=\n\n\#\[|\Z)'''

