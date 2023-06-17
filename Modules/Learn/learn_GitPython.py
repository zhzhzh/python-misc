from git import RemoteProgress
from git.repo import Repo

# https://gitpython.readthedocs.io/en/stable/intro.html


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE") # type: ignore
        # end

repo_dir = '/Users/jzhang14/GitHub/pluto-ruleapps'
repo = Repo(repo_dir)

assert not repo.bare
print(f'repo.bare: {repo.bare}')
print(f'repo.untracked_files: {repo.untracked_files}')
print(f'dirty: {repo.is_dirty()}')


print(f'repo.head: {repo.head}, {repo.head.ref}')
print(f'repo.head.master: {repo.heads.master}')

print(f'repo.remote: {repo.remote}')
origin = repo.remote()
print(f'origin.exists: {origin.exists()}')
if origin.exists():
    origin.pull(progress=MyProgressPrinter())
