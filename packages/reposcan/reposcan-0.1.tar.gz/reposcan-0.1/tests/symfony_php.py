import re

from helpers.Helper import Helper

text = """
<?php

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class MyController
{
    /**
     * @Route("/tag/{pathParameter1}", name="test1", methods={"GET", "POST"})
     * @Route("/tag/{pathParameter1}/page-{pathParameter2}", name="test2", methods={"GET", "POST"})
     * @Route("/tag/{pathParameter1}/page-{pathParameter2}/xyz", name="test3", methods={"GET"})
     */
    public function test1(Request $request, $pathParameter1, $pathParameter2)
    {
        $queryParameter1 = $request->query->get('queryParameter1');
        $queryParameter2 = $request->query->get('queryParameter2');
        $headerParameter1 = $request->headers->get('headerParameter1');
        $headerParameter2 = $request->headers->get('headerParameter2');
        $bodyParameters = json_decode($request->getContent(), true);

        $contentType = $request->headers->get('Content-Type');
        if ($contentType === 'application/xml') {
            return new Response("<response><message>XML format</message></response>", 415, ['Content-Type' => 'application/xml']);
        } else {
            return new JsonResponse(['incomes' => $incomes], 200); // Replace `incomes` with your data
        }
    }

    /**
     * @Route("/tag", name="test2", methods={"GET"})
     */
    public function test2()
    {
        return new Response('', 200);
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
