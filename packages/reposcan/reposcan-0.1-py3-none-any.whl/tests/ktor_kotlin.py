import re

from helpers.Helper import Helper

text = """
import io.ktor.application.*
import io.ktor.features.ContentNegotiation
import io.ktor.features.StatusPages
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.jackson.jackson
import io.ktor.request.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.request.receive
import io.ktor.server.request.receiveParameters

data class YourRequestBodyClass(val bodyParameter1: String?, val bodyParameter2: String?)

fun Application.module() {
    install(ContentNegotiation) {
        jackson { }
    }

    install(StatusPages) {
        exception<Throwable> { cause ->
            call.respond(HttpStatusCode.InternalServerError, cause.localizedMessage)
        }
    }

    routing {
        get("/tag/{pathParameter1}") {
            call.respond(HttpStatusCode.OK)
        }

        route("/tag/{pathParameter1}/page-{pathParameter2}") {
            get {
                val queryParameter1 = call.request.queryParameters["queryParameter1"]
                val queryParameter2 = call.request.queryParameters["queryParameter2"]

                val headerParameter1 = call.request.headers["headerParameter1"]
                val headerParameter2 = call.request.headers["headerParameter2"]

                val bodyParameters = call.receive<YourRequestBodyClass>()
                val bodyParameter1 = bodyParameters.bodyParameter1
                val bodyParameter2 = bodyParameters.bodyParameter2

                val contentType = call.request.contentType()
                when (contentType) {
                    ContentType.Application.Xml -> {
                        call.respondText("<response><message>XML format</message></response>", ContentType.Application.Xml, HttpStatusCode.UnsupportedMediaType)
                    }
                    ContentType.Application.Json -> {
                        call.respond(mapOf("incomes" to "data")) // Replace with actual data
                    }
                    else -> {
                        call.respond(mapOf("incomes" to "data")) // Replace with actual data
                    }
                }
            }
        }

        post("/tag/{pathParameter1}/page-{pathParameter2}/xyz") {
            // Same as above
        }

        get("/tag") {
            call.respond(HttpStatusCode.OK)
        }
    }
}

fun main() {
    embeddedServer(Netty, port = 8080, module = Application::module).start(wait = true)
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
