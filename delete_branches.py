from subprocess import check_output, call
from re import split

out = check_output(["git", "branch", "--merged"])
print(out)
out = split('\n\s*', out.decode('UTF-8'))
out = map(lambda s: s.strip(), out)
out = filter(lambda s: '*' not in s and 'master' not in s and '' != s, out)
for branch in out:
    call(["git", "branch", "-D", branch])
