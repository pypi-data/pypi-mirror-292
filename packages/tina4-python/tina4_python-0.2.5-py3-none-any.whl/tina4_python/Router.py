#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
# flake8: noqa: E501
import mimetypes
import re
import os
import tina4_python
from tina4_python import Constant
from tina4_python.Debug import Debug
from tina4_python import Request
from tina4_python.Response import Response
from tina4_python.Template import Template


class Router:
    variables = None

    @staticmethod
    def get_variables(url, route_path):
        variables = {}
        url_segments = url.strip('/').split('/')
        route_segments = route_path.strip('/').split('/')
        for i, segment in enumerate(route_segments):
            if '{' in segment:  # parameter part
                param_name = re.search(r'{(.*?)}', segment).group(1)
                variables[param_name] = url_segments[i]
        return variables

    # Matches the URL to the route and extracts the parameters
    @staticmethod
    def match(url, route_path):
        matching = False
        variables = {}

        # splitting URL and route and putting them into lists to compare
        url_segments = url.strip('/').split('/')
        route_segments = route_path.strip('/').split('/')

        if len(url_segments) == len(route_segments):
            matching = True
            for i, segment in enumerate(route_segments):
                if '{' in segment:  # parameter part
                    param_name = re.search(r'{(.*?)}', segment).group(1)
                    variables[param_name] = url_segments[i]
                elif segment != url_segments[i]:  # non-parameter part
                    matching = False
                    break

        Router.variables = variables

        return matching

    # Renders the URL and returns the content
    @staticmethod
    async def get_result(url, method, request, headers, session):
        Debug("Root Path " + tina4_python.root_path + " " + url, method, Constant.TINA4_LOG_DEBUG)
        tina4_python.tina4_current_request["url"] = url
        tina4_python.tina4_current_request["headers"] = headers

        # we can add other methods later but right now we validate posts
        if method in [Constant.TINA4_GET, Constant.TINA4_POST, Constant.TINA4_PUT, Constant.TINA4_PATCH, Constant.TINA4_DELETE]:
            content_type = "text/html"
            if "Content-Type" in headers:
                content_type = headers["Content-Type"]
            if "Content-type" in headers:
                content_type = headers["Content-type"]
            if "content-type" in headers:
                content_type = headers["content-type"]

            if content_type == "application/json":
                content = {"error": "403 - Forbidden", "data": {"server": {"url": url}}};
            else:
                content = Template.render_twig_template(
                    "errors/403.twig", {"server": {"url": url}})

            validated = False
            # check to see if we have an auth ability
            if "Authorization" in headers:
                token = headers["Authorization"].replace("Bearer", "").strip()
                if tina4_python.tina4_auth.valid(token):
                    validated = True

            if request["params"] is not None and "formToken" in request["params"]:
                token = request["params"]["formToken"]
                if tina4_python.tina4_auth.valid(token):
                    validated = True

            if request["body"] is not None and "formToken" in request["body"]:
                token = request["body"]["formToken"]
                if tina4_python.tina4_auth.valid(token):
                    validated = True

            if not validated and method != Constant.TINA4_GET:
                return Response(content, Constant.HTTP_FORBIDDEN, Constant.TEXT_HTML)
            else:
                if request["body"] is not None and "formToken" in request["body"]:
                    del request["body"]["formToken"]

        # default response
        result = Response("", Constant.HTTP_NOT_FOUND, Constant.TEXT_HTML)

        # split URL and extract query string
        url_parts = url.split('?')
        url = url_parts[0]

        # Serve statics
        static_file = tina4_python.root_path + os.sep + "src" + os.sep + "public" + url.replace("/", os.sep)
        Debug("Attempting to serve static file: " + static_file, Constant.TINA4_LOG_DEBUG)
        if os.path.isfile(static_file):
            mime_type = mimetypes.guess_type(url)[0]
            with open(static_file, 'rb') as file:
                return Response(file.read(), Constant.HTTP_OK, mime_type)

        for route in tina4_python.tina4_routes.values():
            if route["method"] != method:
                continue
            Debug("Matching route " + route['route'] + " to " + url, Constant.TINA4_LOG_DEBUG)
            if Router.match(url, route['route']):
                if  "swagger" in route and route["swagger"] is not None and "secure" in route["swagger"]:
                    if route["swagger"]["secure"] and not validated:
                        return Response(content, Constant.HTTP_FORBIDDEN, Constant.TEXT_HTML)

                router_response = route["callback"]

                # Add the inline variables  & construct a Request variable
                request["params"].update(Router.variables)

                Request.request = request  # Add the request object
                Request.headers = headers  # Add the headers
                Request.params = request["params"]
                Request.body = request["body"] if "body" in request else None
                Request.session = session

                tina4_python.tina4_current_request = Request

                result = await router_response(request=Request, response=Response)
                break

        # If no route is matched, serve 404
        if result.http_code == Constant.HTTP_NOT_FOUND:
            # Serve twigs if the files exist
            if url == "/":
                twig_file = "index.twig"
            else:
                twig_file = url + ".twig"

            # see if we can find the twig file
            if os.path.isfile(tina4_python.root_path + os.sep + "src" + os.sep + "templates" + os.sep + twig_file):
                Debug("Looking for twig file",
                      tina4_python.root_path + os.sep + "src" + os.sep + "templates" + os.sep + twig_file,
                      Constant.TINA4_LOG_DEBUG)
                content = Template.render_twig_template(twig_file, {"request": tina4_python.tina4_current_request})
                if content != "":
                    return Response(content, Constant.HTTP_OK, Constant.TEXT_HTML)

        if result.http_code == Constant.HTTP_NOT_FOUND:
            content = Template.render_twig_template(
                "errors/404.twig", {"server": {"url": url}})
            return Response(content, Constant.HTTP_NOT_FOUND, Constant.TEXT_HTML)

        return result

    @staticmethod
    async def resolve(method, url, request, headers, session):
        url = Router.clean_url(url)
        Debug(method, "Resolving URL: " + url, Constant.TINA4_LOG_DEBUG)
        return await Router.get_result(url, method, request, headers, session)

    # cleans the url of double slashes
    @staticmethod
    def clean_url(url):
        return url.replace('//', '/')

    # adds a route to the router
    @staticmethod
    def add(method, route, callback):
        Debug("Adding a route: " + route, Constant.TINA4_LOG_DEBUG)
        if not callback in tina4_python.tina4_routes:
            tina4_python.tina4_routes[callback] = {"route": route, "callback": callback, "method": method, "swagger": None}
        else:
            tina4_python.tina4_routes[callback]["route"] = route
            tina4_python.tina4_routes[callback]["callback"] = callback
            tina4_python.tina4_routes[callback]["method"] = method

        if '{' in route:  # store the parameters if needed
            route_variables = re.findall(r'{(.*?)}', route)
            tina4_python.tina4_routes[callback]["params"] = route_variables



def get(path: str):
    """
    Get router
    :param arguments:
    :return:
    """
    def actual_get(callback):
        route_paths = path.split('|')
        for route_path in route_paths:
            Router.add(Constant.TINA4_GET, route_path, callback)
        return callback

    return actual_get


def post(path):
    """
    Post router
    :param path:
    :return:
    """
    def actual_post(callback):
        route_paths = path.split('|')
        for route_path in route_paths:
            Router.add(Constant.TINA4_POST, route_path, callback)
        return callback

    return actual_post


def put(path):
    """
    Put router
    :param path:
    :return:
    """
    def actual_put(callback):
        route_paths = path.split('|')
        for route_path in route_paths:
            Router.add(Constant.TINA4_PUT, route_path, callback)
        return callback

    return actual_put


def patch(path):
    """
    Patch router
    :param path:
    :return:
    """
    def actual_patch(callback):
        route_paths = path.split('|')
        for route_path in route_paths:
            Router.add(Constant.TINA4_PATCH, route_path, callback)
        return callback

    return actual_patch


def delete(path):
    """
    Delete router
    :param path:
    :return:
    """
    def actual_delete(callback):
        route_paths = path.split('|')
        for route_path in route_paths:
            Router.add(Constant.TINA4_DELETE, route_path, callback)
        return callback

    return actual_delete
