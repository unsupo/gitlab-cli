#!/usr/local/bin/python3
# AUTHOR: jarndt

import argparse
import inspect
import json
import re
from pprint import pprint

import requests

VERSION = "1.0"
DESCRIPTION = '''\
Run gitlab apis on the commandline
Accepts partials for args ie, --c instead of --create_project
'''
EXAMPLES = '''\
./gitlab-cli.py --e get projects "{\"search\": {\"name\":\"test\"},\"simple\": \"true\"}" -p
'''


class GitlabCLI:
    token = "F9zyUdjqi9pKo7QswLKu"
    gitlab_url = "http://localhost:8929"
    version = 4
    base_path = "/api/v{version}/"
    pretty = False
    called_function = None

    def __init__(self):
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        functions = []
        builtins = ['__init__', 'get_url', 'command_line']
        for method in methods:
            if method[0] in builtins: continue
            functions.append(method[0])
        self.functions = functions

    def get_url(self):
        return self.gitlab_url + self.base_path.format(version=self.version)

    def command_line(self):
        v = '%(prog)s {version}'.format(version=VERSION)
        my_parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=v + " - " + DESCRIPTION, prog="gitlab-cli"
        )
        my_parser.add_argument("-u", "--url", default=self.gitlab_url,
                               help="URL of your gitlab instance, default is {gitlab_url}"
                               .format(gitlab_url=self.gitlab_url))
        my_parser.add_argument("-t", "--token", default=self.token,
                               help="User token go here: {token_url} and create a token, default is: {token}"
                               .format(token_url="{gitlab_url}/profile/personal_access_tokens"
                                       .format(gitlab_url=self.gitlab_url), token=self.token))
        my_parser.add_argument("-v", "--version", default=self.version, type=int,
                               help="The version of gitlab api to use default: {version}"
                               .format(version=self.version))
        my_parser.add_argument("-V", "--program-version", action='version',
                               version=v)
        my_parser.add_argument("-m", "--method", default="get",
                               help="If using raw request this is the http method to use like get,post,put,delete,"
                                    "ect.  Default is GET")
        my_parser.add_argument("-P", "--parameters",
                               help="Parameters to pass to request")
        my_parser.add_argument("-p", "--pretty", help="pretty print json", action="store_true")
        my_parser.add_argument("-B", "--body",
                               help="Body to pass to request")
        my_parser.add_argument("-H", "--headers",
                               help="Headers to pass to request")
        my_parser.add_argument("function_or_path", nargs="*", default=None,
                               help="The function to call or the relative path of api ie projects. "
                                    "Possible functions are: {functions}".format(functions=' , '.join(self.functions)))
        for function in self.functions:
            # inspect.signature(eval('self.execute_request')).parameters['method'].default == inspect._empty
            params = inspect.signature(eval('self.' + function)).parameters.values()
            param_names = [i.name for i in params if i.default == inspect._empty]
            optionals = [(i.name, i.default) for i in params if i.default != inspect._empty]
            my_parser.add_argument("--" + function,
                                   nargs="*" if optionals else len(param_names) if len(param_names) > 0 else None,
                                   metavar=tuple(param_names) if param_names and not optionals
                                   else (' '.join(param_names), "") if param_names and optionals else None,
                                   help="Optional args: " + " ".join(["[{0}={1}]".format(*p)
                                                                      if p[1] else "[{0}]".format(p[0])
                                                                      for p in optionals])
                                   if len(optionals) > 0 else None)

        args = my_parser.parse_args()
        self.token = args.token
        self.gitlab_url = args.url
        self.version = args.version
        self.pretty = args.pretty

        for arg, value in args.__dict__.items():
            if arg in self.functions and value:
                self.called_function = function
                try:
                    res = eval('self.' + arg)(*value)
                    if self.pretty:
                        pprint(res)
                    else:
                        print(res)
                except Exception as e:
                    print(e)
                exit(0)
        if args.function_or_path and args.function_or_path[0] in self.functions:
            try:
                for function in self.functions:
                    if args.function_or_path[0] == function:
                        self.called_function = function
                        res = eval('self.' + function)(*args.function_or_path[1:])
                        if self.pretty:
                            pprint(res)
                        else:
                            print(res)
            except Exception as e:
                print(e)
        elif len(args.function_or_path) == 0:
            my_parser.print_help()
        else:
            print(self.execute_request(args.method, args.function_or_path, args.parameters, args.body, args.headers))

    @staticmethod
    def parse_str_to_json(value):
        if value and isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as e:
                if re.match("^(\w+=\w+,?)+$", value):
                    d = {}
                    for v in value.split(","):
                        vv = v.split("=")
                        d[vv[0]] = vv[1]
                    return d
                raise Exception("Invalid json for str or string not in format a=b,c=d...: " + value + "\n" + str(e))
        return value

    def execute_request(self, method, path, params=None, body=None, headers=None):

        h = {'PRIVATE-TOKEN': self.token}
        if headers: h.update(headers)
        return requests.request(method, self.get_url() + path,
                                data=body,
                                params=self.parse_str_to_json(params),
                                headers=self.parse_str_to_json(h)).json()

    def get_project_id(self, name):
        if not name: raise Exception("name of new project Required for method " + self.called_function)
        try:
            return [i['id'] for i in self.execute_request("get", "projects") if i['name'] == name][0]
        except IndexError as e:
            raise IndexError("No project with name:\t{0}\nDid you mean:\t\t{1}"
                             .format(name, self.search(name)[0]['name']))

    def get_all_projects(self):
        return [i['name'] for i in self.execute_request('get', 'projects')]

    def create_project(self, name):
        if not name: raise Exception("name of new project Required for method " + self.called_function)
        return self.execute_request("post", "projects", params={'name': name})

    def delete_project(self, name):
        if not name: raise Exception("name of new project Required for method " + self.called_function)
        return self.execute_request('delete', 'projects/' + str(self.get_project_id(name)))

    def rename_project(self, name, new_name):
        if not name: raise Exception("name of new project Required for method " + self.called_function)
        if not name: raise Exception("new_name of new project Required for method " + self.called_function)
        return self.execute_request("put", "projects/" + str(self.get_project_id(name)),
                                    params={'name': new_name, 'path': new_name})

    def search(self, query, scope="projects"):
        return self.execute_request('get', 'search', params={'scope': scope, "search": query})


if __name__ == '__main__':
    GitlabCLI().command_line()
