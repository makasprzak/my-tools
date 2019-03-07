from subprocess import check_output, Popen
import subprocess
import argparse
import json
import dateutil.parser
from functools import reduce
import collections

parser = argparse.ArgumentParser(description="Your git work history tool")
parser.add_argument("-d", "--directory", required=False, default='.', type=str, help="Root project directory where all your repositories are")
parser.add_argument("-a", "--author", required=True, type=str, help="Your name as configured in git")
parser.add_argument("-s", "--since", required=True, type=str, help="Since date. For example 2019-02-11.")
args = parser.parse_args()

out = check_output(("find %s -name .git" % args.directory).split())
repos = filter(lambda repo : repo, out.decode("UTF-8").split("\n"))

def build_log_command():
    global command
    command = (
            'git --no-pager --git-dir %s log %s --author "%s" --pretty="format:{\\\'time\\\':\\\'%%ai\\\',\\\'message\\\':\\\'%%s\\\'}" --since="%s" --no-merges' % (
        repo, branch, args.author, args.since))

def merge(x, y):
    for k,v in x.items():
        if k in y:
            y[k] += v
        else:
            y[k] = v
    return y

commit_objects = []
for repo in repos:
    out = check_output(("git --git-dir %s branch --sort=-committerdate" % repo).split())
    out = out.decode("UTF-8")
    out = out.split("\n")
    branches = list(map(lambda s: s[2:], out))
    got_master = False
    got_dev = 'development' not in branches
    for branch in branches:
        if not branch:
            continue
        if branch == 'development':
            got_dev = True
        if branch == 'master':
            got_master = True
        build_log_command()
        p = Popen(command, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        out, err = p.communicate()
        commits = out.decode("UTF-8").split("\n")
        for commit in commits:
            if not commit:
                break
            escaped = commit.replace('"', '__||__').replace("\\'",'"').replace('__||__','\\"')
            try:
                commit_objects.append(json.loads(escaped))
            except:
                print("Failed to parse %s" % commit)
        if got_master and got_dev:
            break

mapped = map(lambda c : {dateutil.parser.parse(c['time']).date().isoformat(): [c['message']]}, commit_objects)
reduced = reduce(lambda x,y: merge(x,y), mapped)

reduced = collections.OrderedDict(sorted(reduced.items()))

for k,v in reduced.items():
    print('On date %s you did:' % k)
    print('------------------------------------------------------------------------------------------------')
    for message in sorted(set(v)):
        indent = ''.join(map(lambda x : '\t', range(4)))
        print(indent + message)

