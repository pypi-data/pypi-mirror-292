import re

from helpers.Helper import Helper

text = """
require 'sinatra'
require 'json'

post '/tag/:pathParameter1/page-:pathParameter2/xyz' do
  pathParameter1 = params[:pathParameter1]
  pathParameter2 = params[:pathParameter2].to_i

  queryParameter1 = params[:queryParameter1]
  queryParameter2 = params[:queryParameter2]

  headerParameter1 = request.env['HTTP_HEADERPARAMETER1']
  headerParameter2 = request.env['HTTP_HEADERPARAMETER2']

  body_params = JSON.parse(request.body.read) rescue {}

  content_type = request.content_type

  case content_type
  when 'application/xml'
    content_type 'application/xml'
    status 415
    "<response><message>XML format</message></response>"
  else
    content_type 'application/json'
    status 200
    { incomes: incomes }.to_json # Replace `incomes` with your data
  end
end

get '/tag' do
  status 200
end

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
