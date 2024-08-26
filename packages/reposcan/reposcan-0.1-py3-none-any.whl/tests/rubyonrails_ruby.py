import re

from helpers.Helper import Helper

text = """
class MyController < ApplicationController
  before_action :parse_body_parameters, only: [:test1]

  def test1
    path_parameter1 = params[:pathParameter1]
    path_parameter2 = params[:pathParameter2]

    query_parameter1 = params[:queryParameter1]
    query_parameter2 = params[:queryParameter2]

    header_parameter1 = request.headers['headerParameter1']
    header_parameter2 = request.headers['headerParameter2']

    body_parameter1 = @body_params[:bodyParameter1]
    body_parameter2 = @body_params[:bodyParameter2]

    case request.content_type
    when 'application/xml'
      render xml: "<response><message>XML format</message></response>", status: 415
    else
      render json: { incomes: incomes }, status: 200 # Replace `incomes` with your data
    end
  end

  def test2
    head :ok
  end

  private

  def parse_body_parameters
    @body_params = JSON.parse(request.body.read).symbolize_keys
  rescue JSON::ParserError
    @body_params = {}
  end
end

"""

# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
