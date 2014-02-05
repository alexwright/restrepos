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

class TreeTraversalError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def traverse(repo, tree, path):
    if len(path) == 0:
        return tree

    name = path.pop(0)
    if name not in tree:
        raise TreeTraversalError("path not found")

    obj = repo[tree[name].oid]
    if len(path) == 0:
        return obj

    if obj.type == pygit2.GIT_OBJ_TREE:
        return traverse(repo, obj, path)
    raise TreeTraversalError("tried to traverse a non-tree")

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
