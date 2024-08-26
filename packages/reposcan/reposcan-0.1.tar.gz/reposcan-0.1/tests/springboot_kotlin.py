import re

from helpers.Helper import Helper

text = """
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.web.bind.annotation.*

@SpringBootApplication
class Application

fun main(args: Array<String>) {
    runApplication<Application>(*args)
}

@RestController
@RequestMapping("/tag")
class MyController {

    @GetMapping("/{pathParameter1}")
    fun test1(@PathVariable pathParameter1: String): ResponseEntity<String> {
        // Just comment
        return ResponseEntity.ok().build()
    }

    @RequestMapping("/{pathParameter1}/page-{pathParameter2}", method = [RequestMethod.GET, RequestMethod.POST])
    fun test1(
        @PathVariable pathParameter1: String,
        @PathVariable pathParameter2: Int,
        @RequestParam queryParameter1: String?,
        @RequestParam queryParameter2: String?,
        @RequestHeader headerParameter1: String?,
        @RequestHeader headerParameter2: String?,
        @RequestBody requestBody: YourRequestBodyClass?,
        @RequestHeader("Content-Type") contentType: String
    ): ResponseEntity<Any> {
        return when (contentType) {
            "application/xml" -> ResponseEntity.status(HttpStatus.UNSUPPORTED_MEDIA_TYPE)
                .contentType(MediaType.APPLICATION_XML)
                .body("<response><message>XML format</message></response>")
            else -> ResponseEntity.ok().body(mapOf("incomes" to "data")) // Replace with actual data
        }
    }

    @GetMapping("/tag")
    fun test2(): ResponseEntity<Void> {
        return ResponseEntity.ok().build()
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
