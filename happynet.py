"""Finger / Happy Net Box Client for Python"""
import hashlib
import re
import sys
from json import dump, load
from os import getenv
from os.path import dirname, exists, join
from socket import create_connection

from blessed import Terminal

HOMEDIR = getenv("HOME", ".")
SERVER = "happynetbox.com"
PORT = 79


SUBSCRIPTION_FILE = join(HOMEDIR, ".happynetbox")
CACHE_FILE = join(HOMEDIR, ".happynetbox.cache.json")


class Finger:
    def __init__(self, handle, post):
        self.handle = handle
        self.post = post
        self.is_new = False

    def __lt__(self, b):
        return self.is_new and not b.is_new

    def __gt__(self, b):
        return not self.is_new and b.is_new

    def __eq__(self, b):
        return self.is_new == b.is_new


def fingerUser(user: str):
    try:
        handle, host = user.split(r"@")
    except ValueError:
        handle, host = user, SERVER

    text = ""
    with create_connection((host, PORT)) as con:
        con.send(f"{handle}\r\n".encode("utf-8"))
        while True:
            raw = con.recv(1024)
            if not raw:
                break
            text += raw.decode()
    return text


def beep():
    sys.stdout.write("\a")
    sys.stdout.flush()


subscriptions = []
cache = {}
try:
    if not exists(SUBSCRIPTION_FILE):
        with open(SUBSCRIPTION_FILE, "w", encoding="utf-8") as fp:
            fp.write("# This is your Happy Net Box subscription list.\n")
    else:
        with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as fp:
            raw = [l.strip() for l in fp.readlines()]
            subscriptions.extend([l for l in raw if l[0] != "#"])
except OSError:
    print(f"Could not read {SUBSCRIPTION_FILE}")
    sys.exit(1)

try:
    if not exists(CACHE_FILE):
        with open(CACHE_FILE, "w", encoding="utf-8") as fp:
            dump(fp, cache)
    else:
        with open(CACHE_FILE, "r", encoding="utf-8") as fp:
            cache = load(fp)
except OSError:
    print(f"Could not read {CACHE_FILE}")
    sys.exit(1)


with open(join(dirname(__file__), "logo.txt"), "r", encoding="utf-8") as fp:
    logo = fp.read()

posts = []
if len(subscriptions) > 0:
    for handle in subscriptions:
        text = re.sub(r"---\nwant another.*?$", "", fingerUser(handle))
        posts.append(Finger(handle, text))
else:
    print(">> Your .happynetbox file is empty")
    print(f">> To subscribe to a handle, add it to {SUBSCRIPTION_FILE}")
    sys.exit()


for idx, post in enumerate(posts):
    newhash = hashlib.new(
        name="md5",
        data=post.post.encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()
    if cache.get(post.handle) != newhash:
        print(post.handle, cache.get(post.handle), newhash)
        posts[idx].is_new = True
        cache[post.handle] = newhash
with open(CACHE_FILE, "w+", encoding="utf-8") as fp:
    dump(cache, fp)


posts.sort()
term = Terminal()

pid = 0
num_posts = len(posts)

new_text = term.black_on_yellow("* NEW *")

with term.cbreak():
    print(term.green(logo))
    while pid < num_posts:
        post = posts[pid]
        title = f"| Latest post from ${post.handle}  |"
        len_title = len(title)
        new = f"{' '.rjust(91-len_title-6)}{new_text}" if post.is_new else ""
        print(term.bold("-=" * 46))
        print(f"{term.bold(title)}{new}")
        print("*" * len_title)
        print(post.post)
        if pid < num_posts - 1:
            print("Press [anykey] to continue")
            char = term.inkey()
            val = char.name if char.is_sequence else char.lower()
            if val in ("KEY_ESCAPE", "q"):
                sys.exit()
            elif val in ("KEY_LEFT", "KEY_UP", "a", "w"):
                pid -= 1
                if pid < 0:
                    pid = 0
                    beep()
            else:
                pid += 1
            print(term.clear())
        else:
            pid += 1
