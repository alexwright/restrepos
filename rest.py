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

def obj_to_json(repo, obj):
    types = { 1: "commit", 2: "tree", 3: "blob" }
    if type(obj) == pygit2.TreeEntry:
        #return obj_to_json(repo, repo[obj.oid])
        return {
            "name": obj.name,
            "type": types[repo[obj.oid].type],
        }
    if obj.type == pygit2.GIT_OBJ_TREE:
        return {
            "type": "tree",
            "entries": map(lambda te: obj_to_json(repo, te), obj),
        }
    if obj.type == pygit2.GIT_OBJ_BLOB:
        return {
            "type": "blob",
            "data": obj.data,
        }

class RepoDetail(restful.Resource):
    def get(self, repo_id):
        repo = get_repo(repo_id)
        return {
            "branches": repo.listall_branches(),
        }

class RepoList(restful.Resource):
    def get(self):
        return repos.keys()

class Tree(restful.Resource):
    def get(self, repo_id, ref, path=None):
        repo = get_repo(repo_id)
        branch = repo.lookup_branch(ref)
        commit = branch.get_object()
        tree = commit.tree

        path_parts = [] if path is None else path.split("/")
        print "Parts: " + str(path_parts)
        obj = traverse(repo, tree, path_parts)

        return obj_to_json(repo, obj)

api.add_resource(RepoList, "/repos")
api.add_resource(RepoDetail, "/repos/<string:repo_id>")
api.add_resource(Tree, "/tree/<string:repo_id>/<string:ref>",
                       "/tree/<string:repo_id>/<string:ref>/<path:path>")

if __name__ == '__main__':
    app.run(debug=True)
