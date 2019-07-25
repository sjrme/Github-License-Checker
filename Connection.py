import requests
import json
import base64
import Strings
#GET Authorization for account //What to do when auth dies?
#


class Connection:

    auth_header = {}

    HTTP_OKAY = 200
    HTTP_CREATED = 201
    def __init__(self, username, password):
        pre_encoding = username + ':' + password
        base64encoding = base64.b64encode(pre_encoding.encode("utf-8"))  # String to byte
        base64encoding = str(base64encoding, "utf-8")  # Byte to string
        self.auth_header = {"Authorization": "Basic %s" % base64encoding}

    def get_repos(self, organization):

        response = requests.get(url="https://api.github.com/orgs/" + organization + "/repos", headers=self.auth_header)
        print(response.status_code)

        if response.status_code == self.HTTP_OKAY:
            string_response = str(response.content, 'utf-8')  #response.content, which is in bytes, to str
            payload = json.loads(string_response)

            repo_licenses = {}
            for repo in payload:
                if repo["license"] is not None:
                    repo_licenses[repo["name"]] = repo["license"]["name"]
                else:
                    repo_licenses[repo["name"]] = "No License"

        else:
            return None
        return repo_licenses

    def get_license(self, organization, repo_name):
        if self.make_new_branch(organization, repo_name) == self.HTTP_CREATED:
            if self.add_license(organization, repo_name) == self.HTTP_CREATED:
                if self.make_pull_request(organization, repo_name) == self.HTTP_CREATED:
                    return True
        return False

    def make_new_branch(self, organization, repo_name):
        sha_request_url = "https://api.github.com/repos/" + organization + '/' + repo_name + "/git/refs/heads/master"
        sha_http_response = requests.get(url=sha_request_url, headers=self.auth_header)
        sha_string_response = str(sha_http_response.content, "utf-8")
        sha_json_response = json.loads(sha_string_response)
        sha = sha_json_response["object"]["sha"]
        url = "https://api.github.com/repos/" + organization + "/" + repo_name + "/git/refs"
        data = '{"ref": "refs/heads/LicenseBranch", "sha": "' + sha + '"}'

        status_code = requests.post(url=url, headers=self.auth_header, data=data).status_code
        print(status_code)
        return status_code

    def add_license(self, organization, repo_name):
        url = "https://api.github.com/repos/" + organization + "/" + repo_name + "/contents/LICENSE"
        mit_license = Strings.mit1 + organization + Strings.mit2 + Strings.mit3 + Strings.mit4
        base64encoding = base64.b64encode(mit_license.encode("utf-8"))
        base64encoding = str(base64encoding, "utf-8")
        data = '{"message":"Adding MIT License", "content": "' + base64encoding + '", "branch":"LicenseBranch"}'

        status_code = requests.put(url=url, headers=self.auth_header, data=data).status_code
        print(status_code)
        return status_code

    def make_pull_request(self, organization, repo_name):
        url = "https://api.github.com/repos/" + organization + "/" + repo_name + "/pulls"
        data = '{"title":"Request to add License", "head":"LicenseBranch", "base":"master"}'
        status_code = requests.post(url=url, headers=self.auth_header, data=data).status_code

        print(status_code)
        return status_code
