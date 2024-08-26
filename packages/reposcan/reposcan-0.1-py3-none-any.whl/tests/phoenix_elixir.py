import re

from helpers.Helper import Helper

text = '''
defmodule MyAppWeb.MyController do
  use MyAppWeb, :controller

  action_fallback MyAppWeb.FallbackController

  @doc """
  Route: GET /tag/:pathParameter1
  Route: GET/POST /tag/:pathParameter1/page-:pathParameter2
  Route: GET /tag/:pathParameter1/page-:pathParameter2/xyz
  """
  def test1(conn, %{"pathParameter1" => pathParameter1, "pathParameter2" => pathParameter2}) do
    queryParameter1 = get_req_header(conn, "queryParameter1") |> List.first()
    queryParameter2 = get_req_header(conn, "queryParameter2") |> List.first()
    headerParameter1 = get_req_header(conn, "headerParameter1") |> List.first()
    headerParameter2 = get_req_header(conn, "headerParameter2") |> List.first()
    bodyParameters = conn.body_params

    content_type = get_req_header(conn, "content-type") |> List.first()
    
    response_body = case content_type do
      "application/xml" ->
        "<response><message>XML format</message></response>"

      "application/json" ->
        # Replace `incomes` with your data
        Poison.encode!(%{incomes: incomes})

      _ ->
        # Replace `incomes` with your data
        Poison.encode!(%{incomes: incomes})
    end

    conn
    |> put_resp_content_type(content_type)
    |> send_resp(
      case content_type do
        "application/xml" -> 415
        _ -> 200
      end,
      response_body
    )
  end

  def test2(conn, _params) do
    conn
    |> send_resp(200, "")
  end
end

'''
# Loop all api matches
apiPattern = r'''((?:.*@require_http_methods\((?P<httpMethods>\[.*\])?.*\)\n)|(?:def (?P<functionName>\w+) (?P<pathParameters>\(.*\)):\n)|(?:.*request.GET.get(?P<queryParameters>.*)\n)|(?:.*request.headers.get(?P<headerParameters>.*)\n)|(?:.*json.loads\(request.body\).get(?P<bodyParameters>.*)\n)|(?:.*request.content_type == (?P<contentTypes>.*)\n)|(?:.*return .* status=(?P<responseCodes>\d+).*\n)|.*?\n)*?.*?(?=\n\n@require_http_methods|\Z)'''
