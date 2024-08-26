import re

from helpers.Helper import Helper

text = """
import { NextResponse } from 'next/server';

export async function GET(request, { params }) {
  const { pathParameter1, pathParameter2 } = params;

  // Just comment
  return NextResponse.json({});
}

export async function POST(request) {
  const { pathParameter1, pathParameter2 } = request.nextUrl.query;

  const queryParameter1 = request.nextUrl.searchParams.get('queryParameter1');
  const queryParameter2 = request.nextUrl.searchParams.get('queryParameter2');

  const headerParameter1 = request.headers.get('headerParameter1');
  const headerParameter2 = request.headers.get('headerParameter2');

  const body = await request.json();
  const bodyParameter1 = body.bodyParameter1;
  const bodyParameter2 = body.bodyParameter2;

  if (request.headers.get('Content-Type') === 'application/xml') {
    return new NextResponse("<response><message>XML format</message></response>", {
      status: 415,
      headers: {
        'Content-Type': 'application/xml'
      }
    });
  } else {
    return NextResponse.json({ incomes: 'data' }); // Replace with actual data
  }
}

export async function DELETE() {
  return NextResponse.json({});
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
