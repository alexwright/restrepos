from flask import Flask
from flask.ext import restful
import pygit2

app = Flask(__name__)
api = restful.Api(app)

repos = {
    "gitolite-admin": {
        "name": "The Gitolite admin repo",
        "path": "/home/alex/gitolite-admin",
    },
}

def get_repo(repo_id):
    if repo_id not in repos:
        raise "unknown repo"

    info = repos[repo_id]
    return pygit2.Repository(info["path"])

class RepoDetail(restful.Resource):
    def get(self, repo_id):
        repo = get_repo(repo_id)
        return {
            "branches": repo.listall_branches(),
        }

class RepoList(restful.Resource):
    def get(self):
        return repos.keys()

api.add_resource(RepoList, "/repos")
api.add_resource(RepoDetail, "/repos/<string:repo_id>")

if __name__ == '__main__':
    app.run(debug=True)
