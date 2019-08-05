import requests
import json
import base64
import Strings


class Connection:
    """
    Makes all connections to Github and returns necessary information from connections to match
    repos to license, and to add licenses to repos that do not have one. 
    
    Attributes
    ----------
        auth_header : dictionary
            Contains information necessary for "Authorization" http header
        HTTP_OKAY : int
            HTTP status code for succesful get request
        HTTP_CREATED : int
            HTTP status code for succesful post or put request
            
    Methods
    ---------
    get_repos(organization)
         Gets names of all repositories in an organization, and maps each to the license the repo owns.
    get_license(organization, repo_name)
        Adds MIT license to repository in a new branch, and makes pull request on the new branch.       
    """
    
    auth_header = {}
    HTTP_OKAY = 200
    HTTP_CREATED = 201
    
    def __init__(self, username, password):
        """
        Parameters
        -----------
        username : str
            Username of owner of Github organization
        password : str
            Password associated with the account owned by username
        """
        
        pre_encoding = username + ':' + password
        base64encoding = base64.b64encode(pre_encoding.encode("utf-8")) #Must change "pre_encoding" to bytes for base64 package.
        base64encoding = str(base64encoding, "utf-8")  #Change base64encoding back to a string, for request package.
        self.auth_header = {"Authorization": "Basic %s" % base64encoding}

    def get_repos(self, organization):
        """Gets names of all repositories in an organization, and maps each to the license the repo owns.
        Parameters
        -----------
        organization: str
            The name of the organization for which all repos will be pulled
        Returns
        -----------
        dictionary
            Maps repo name to the name of the license associated with the repo. If the repo does not have a
            license, it will be mapped to the string "No License
        """
        
        response = requests.get(url="https://api.github.com/orgs/" + organization + "/repos", headers=self.auth_header)
        print(response.status_code)

        if response.status_code == self.HTTP_OKAY:
            string_response = str(response.content, 'utf-8')  
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
        """Adds MIT license to repository in a new branch, and makes pull request on the new branch.
        Parameters
        -----------
        organization: str
            The name of the organization to which the repo belongs
        repo_name: str
            The name of the repo that the method will add the license to
        Returns
        ----------
            True: If license is added
            False: If license failed to add."""
        
        if self.make_new_branch(organization, repo_name) == self.HTTP_CREATED:
            if self.add_license(organization, repo_name) == self.HTTP_CREATED:
                if self.make_pull_request(organization, repo_name) == self.HTTP_CREATED:
                    return True
        return False

    def make_new_branch(self, organization, repo_name):
        """Makes a new branch called "LicenseBranch"
        Parameters
        -----------
        organization: str
            The name of the organization to which the repo belongs
        repo_name: str
            The name of the repo that the method will add a branch to
        Returns
        -----------
        Int
            Status code of the connection made with Github
        """
        
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
        """Add MIT license to LicenseBranch"
        Parameters
        -----------
        organization: str
            The name of the organization to which the repo belongs
        repo_name: str
            The name of the repo that the method will add a license to
        Returns
        -----------
        Int
            Status code of the connection made with Github
        """
        
        url = "https://api.github.com/repos/" + organization + "/" + repo_name + "/contents/LICENSE"
        mit_license = Strings.mit1 + organization + Strings.mit2 + Strings.mit3 + Strings.mit4
        base64encoding = base64.b64encode(mit_license.encode("utf-8"))
        base64encoding = str(base64encoding, "utf-8")
        data = '{"message":"Adding MIT License", "content": "' + base64encoding + '", "branch":"LicenseBranch"}'

        status_code = requests.put(url=url, headers=self.auth_header, data=data).status_code
        print(status_code)
        return status_code

    def make_pull_request(self, organization, repo_name):
        """Makes pull request to merge LicenseBranch to master"
        Parameters
        -----------
        organization: str
            The name of the organization to which the repo belongs
        repo_name: str
            The name of the repo that the method will add a license to
        Returns
        -----------
        Int
            Status code of the connection made with Github
        """
            
        url = "https://api.github.com/repos/" + organization + "/" + repo_name + "/pulls"
        data = '{"title":"Request to add License", "head":"LicenseBranch", "base":"master"}'
        status_code = requests.post(url=url, headers=self.auth_header, data=data).status_code

        print(status_code)
        return status_code
