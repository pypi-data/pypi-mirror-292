import re

from helpers.Helper import Helper

text = """
<?php

use Laminas\Mvc\Controller\AbstractActionController;
use Laminas\View\Model\JsonModel;
use Laminas\Http\Header\ContentType;

class MyController extends AbstractActionController
{
    public function test1Action()
    {
        $request = $this->getRequest();
        $pathParameter1 = $this->params()->fromRoute('pathParameter1');
        $pathParameter2 = $this->params()->fromRoute('pathParameter2');
        $queryParameter1 = $request->getQuery('queryParameter1');
        $queryParameter2 = $request->getQuery('queryParameter2');
        $headerParameter1 = $request->getHeader('headerParameter1');
        $headerParameter2 = $request->getHeader('headerParameter2');
        $bodyParameters = json_decode($request->getContent(), true);

        $contentType = $request->getHeader('Content-Type')->getFieldValue();
        if ($contentType === 'application/xml') {
            $response = $this->getResponse();
            $response->setHeader('Content-Type', 'application/xml')
                     ->setStatusCode(415)
                     ->setContent("<response><message>XML format</message></response>");
            return $response;
        } else {
            return new JsonModel(['incomes' => $incomes]); // Replace `incomes` with your data
        }
    }

    public function test2Action()
    {
        return $this->getResponse()->setStatusCode(200);
    }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
