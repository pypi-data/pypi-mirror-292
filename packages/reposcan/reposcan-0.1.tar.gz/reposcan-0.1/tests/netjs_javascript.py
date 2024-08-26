import re

from helpers.Helper import Helper

text = """
import { Controller, Get, Post, Query, Headers, Body, Param, Req, Res, HttpStatus } from '@nestjs/common';
import { Request, Response } from 'express';

@Controller('tag')
export class MyController {

  @Get('/:pathParameter1')
  test1(@Param('pathParameter1') pathParameter1: string): string {
    // Just comment
    return 'OK';
  }

  @Get('/:pathParameter1/page-:pathParameter2')
  @Post('/:pathParameter1/page-:pathParameter2/xyz')
  test1(
    @Param('pathParameter1') pathParameter1: string,
    @Param('pathParameter2') pathParameter2: number,
    @Query('queryParameter1') queryParameter1: string,
    @Query('queryParameter2') queryParameter2: string,
    @Headers('headerParameter1') headerParameter1: string,
    @Headers('headerParameter2') headerParameter2: string,
    @Body() requestBody: any,
    @Req() request: Request,
    @Res() response: Response
  ) {
    const contentType = request.headers['content-type'];
    if (contentType === 'application/xml') {
      response.status(HttpStatus.UNSUPPORTED_MEDIA_TYPE).type('application/xml').send("<response><message>XML format</message></response>");
    } else {
      response.status(HttpStatus.OK).json({ incomes: 'data' }); // Replace with actual data
    }
  }

  @Get()
  test2(): string {
    return 'OK';
  }
}

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
