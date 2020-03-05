# gitlab-cli

This is a python script which uses requests and gitlab api to easily perform CRUD operations on gitlab projects.

I use this script to automatically add any folder i create on my machine for automatic versioning.  If i accidentally
delete a file or folder i can restore it from gitlab, if i make a change and what to see how it was before i look at 
gitlab.  

```bash
usage: gitlab-cli [-h] [-u URL] [-t TOKEN] [-v VERSION] [-V] [-m METHOD]
                  [-P PARAMETERS] [-p] [-B BODY] [-H HEADERS]
                  [--create_project name] [--delete_project name]
                  [--execute_request [method path [...]]]
                  [--get_all_projects GET_ALL_PROJECTS]
                  [--get_project_id name] [--rename_project name new_name]
                  [--search [query [...]]]
                  [function_or_path [function_or_path ...]]

gitlab-cli 1.0 - Run gitlab apis on the commandline
Accepts partials for args ie, --c instead of --create_project

positional arguments:
  function_or_path      The function to call or the relative path of api ie
                        projects. Possible functions are: create_project ,
                        delete_project , execute_request , get_all_projects ,
                        get_project_id , rename_project , search

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL of your gitlab instance, default is
                        http://localhost:8929
  -t TOKEN, --token TOKEN
                        User token go here:
                        http://localhost:8929/profile/personal_access_tokens
                        and create a token, default is: F9zyUdjqi9pKo7QswLKu
  -v VERSION, --version VERSION
                        The version of gitlab api to use default: 4
  -V, --program-version
                        show program's version number and exit
  -m METHOD, --method METHOD
                        If using raw request this is the http method to use
                        like get,post,put,delete,ect. Default is GET
  -P PARAMETERS, --parameters PARAMETERS
                        Parameters to pass to request
  -p, --pretty          pretty print json
  -B BODY, --body BODY  Body to pass to request
  -H HEADERS, --headers HEADERS
                        Headers to pass to request
  --create_project name
  --delete_project name
  --execute_request [method path [ ...]]
                        Optional args: [params] [body] [headers]
  --get_all_projects GET_ALL_PROJECTS
  --get_project_id name
  --rename_project name new_name
  --search [query [ ...]]
                        Optional args: [scope=projects]

```