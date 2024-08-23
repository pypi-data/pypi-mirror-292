from functools import cache
import json
import os
import time
import typing
from zuu.app.git import git_update_repo
from zuu.core.singleton import SingletonMetaclass
from zuu.stdpkg.json import touch_json
from zuu.struct.simple_io_dict import SimpleIOLooseDict

class GhRepoCache(metaclass=SingletonMetaclass):
    __path : str = os.path.expanduser("~/.zuu/gh_repos")
    __cache_path  : str = os.path.join(__path, "cache")

    def __init__(self):
        self.__non_exist_init()

    def __non_exist_init(self):
        os.makedirs(self.__cache_path, exist_ok=True)
        touch_json(os.path.join(self.__path, "gh_repos.json"), json.dumps({"repos" : []}))
        self.__index = SimpleIOLooseDict(os.path.join(self.__path, "gh_repos.json"))

    @cache
    def __name(self, path : str):
        if path.startswith("https://"):
            path = path[len("https://"):]
        if path.startswith("github.com/"):
            path = path[len("github.com/"):]
        if path.endswith(".git"):
            path = path[:-len(".git")]
        return path
    
    def exists(self, path : str, branch : str = None):
        for repo in self.__index["repos"]:
            if repo["path"] != path:
                continue
                
            if branch != repo.get("branch", None):
                continue

            return True

        return False

    def add(self, path : str, branch : str):
        if self.exists(path, branch):
            return
        
        self.__index["repos"].append({
            "path" : path,
            "branch" : branch,
        })
        os.makedirs(os.path.join(self.__cache_path, str(len(self.__index["repos"]) - 1)), exist_ok=True)
        git_update_repo(os.path.join(self.__cache_path, str(len(self.__index["repos"]) - 1)), path, branch)
        self.__index._save()

    @property
    def last_checked(self):
        return self.__index.get("last_checked", 0)
    
    @property
    def check_interval(self):
        return self.__index.get("check_interval", 24 * 60 * 60)
    
    @property
    def expired(self):
        return self.last_checked + self.check_interval < time.time()

    def remove_by_path(self, path : str, branch : str = None):
        for i, repo in enumerate([*self.__index["repos"]] + [None]):
            if repo is None:
                return 0

            if repo["path"] != path:
                continue

            if branch != repo.get("branch", None):
                continue

            break
        
        
        self.remove_by_id(i)

    def remove_by_id(self, i : int):
        # remove at i and rename i+n to i+n-1
        del self.__index["repos"][i]
        
        # Rename directories
        for j in range(i + 1, len(self.__index["repos"]) + 1):
            old_path = os.path.join(self.__cache_path, str(j))
            new_path = os.path.join(self.__cache_path, str(j - 1))
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
        
        self.__index._save()

    def update(self, force : bool = False):
        if not self.expired and not force:
            return

        for i, _ in enumerate(self.__index["repos"]):
            git_update_repo(os.path.join(self.__cache_path, str(i)))

    def __recurs_check_path(self, token, path):
        tlen = len(token)
        for o in os.listdir(self.__cache_path):
            if os.path.exists(os.path.join(self.__cache_path, o, path[tlen:])):
                return os.path.join(self.__cache_path, o, path[tlen:])

    def resolve_path_asc(self, path : str):
        """
        resolve path in asc order
        """
        if path.startswith("shared"):
            res = self.__recurs_check_path("shared", path)
        
        elif path.startswith("@"):
            res = self.__recurs_check_path("@", path)
        else:
            for i, repo in enumerate(self.__index["repos"]):
                reponame = self.__name(repo["path"])
                if path.startswith(reponame):
                    res = os.path.join(self.__cache_path, str(i), path[len(reponame) + 1:])
                elif path.startswith(str(i)):
                    res = os.path.join(self.__cache_path, str(i), path[len(str(i)) + 1:])
                else:
                    continue
                break

        return os.path.abspath(res) if res else None

    def resolve_path_order(self, path : str, order :typing.List[int] = None):
        if not order:
            order = [*range(len(self.__index["repos"]))]
        
        assert all(-1 < i < len(self.__index["repos"]) for i in order)

        for i in order:
            if os.path.exists(os.path.join(self.__cache_path, str(i), path)):
                res = os.path.join(self.__cache_path, str(i), path)
            elif path.startswith("@") and os.path.exists(os.path.join(self.__cache_path, str(i), path[1:])):
                res = os.path.join(self.__cache_path, str(i), path[1:])
            elif path.startswith("shared") and os.path.exists(os.path.join(self.__cache_path, str(i), path[7:])):
                res = os.path.join(self.__cache_path, str(i), path[7:])
            elif path.startswith((reponame := self.__name(self.__index["repos"][i]["path"]))) and \
                os.path.exists(os.path.join(self.__cache_path, str(i), path[len(reponame) + 1:])):
                res = os.path.join(self.__cache_path, str(i), path[len(reponame) + 1:])
            else:
                continue
            break

        return os.path.abspath(res) if res else None
        

    def info(self):
        val = []
        for i, repo in enumerate(self.__index["repos"]):
            reponame = self.__name(repo["path"])
            val.append(
                {
                    "id" : i,
                    "path" : repo["path"],
                    "branch" : repo["branch"],
                    "name" : reponame,
                }
            )
        return val
    

def click_add_command(obj):
    cls = GhRepoCache
    import click
    assert isinstance(obj, click.Group)
    @click.command("update", help="Update the cache.")
    @click.option("--force", "-f", is_flag=True, default=False, help="Force update")
    def update_command(force):
        """
        Update the cache.
        """
        cls().update(force=force)

    @click.command("add", help="Add a repository to the cache.")
    @click.argument("path")
    @click.argument("branch", default="master", required=False)
    def add_command(path, branch):
        """
        Add a repository to the cache.
        """
        cls().add(path, branch)

    @click.command("remove", help="Remove a repository from the cache.")
    @click.option("--path", "-p", help="The path of the repository to remove.")
    @click.option("--branch", "-b", help="The branch of the repository to remove.")
    @click.option("--id", "-i", type=int, help="The id of the repository to remove.")
    def remove_command(path, branch, id):
        """
        Remove a repository from  the cache.
        """
        if isinstance(id, int) and (path or branch):
            raise click.ClickException("You can't specify both an id and a path.")
        
        if isinstance(id, int):
            try:
                cls().remove_by_id(id)
            except:  #noqa
                raise click.ClickException(f"Repository with id {id} not found.")
            return     

        val = cls().remove_by_path(path, branch)
        if val == 0:
            raise click.ClickException(f"Repository '{path}' not found.")

    @click.command("info", help="Show information about the cache.")
    def info_command():
        """
        Show information about the cache.
        """
        for repo in cls().info():
            line = f"{repo['id']}: {repo['name']}"
            if repo.get("branch", None):
                line += f" ({repo['branch']})"
            print(line)

    obj.add_command(update_command)
    obj.add_command(add_command)
    obj.add_command(remove_command)
    obj.add_command(info_command)
    return obj



            