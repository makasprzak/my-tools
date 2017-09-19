from subprocess import check_output, call
from re import split

call(["git", "fetch", "-p"])
out = check_output(["git", "branch", "-r", "--merged"])
out = split('\n\s*', out)
out = map(lambda s: s.strip(), out)
out = map(lambda s: s.replace("origin/", ""), out)
out = filter(lambda s: 'master' not in s and '' != s, out)
print "Following branches will be deleted:"
for branch in out:
    print branch
    
for branch in out:
    call(["git", "push", "--delete", "origin", branch])
