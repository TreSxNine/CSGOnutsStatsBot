#credit to /u/GoldenSights
import traceback
import praw
import time
import sqlite3
from scraping import *

USERNAME = ""

PASSWORD = ""

USERAGENT = ""

SUBREDDIT = "csgobetting"

KEYWORDS = ["Statbot!"]

MAXPOSTS = 100

WAIT = 30

CLEANCYCLES = 100

try:
    from user_credentials import *
    # This is a file in my python library which contains my
    # Bot's username and password.
    # I can push code to Git without showing credentials
    USERNAME = username
    PASSWORD = password
    USERAGENT = useragent
except ImportError:
    pass

sql = sqlite3.connect('sql.db')
print('Loaded SQL Database')
cur = sql.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')

sql.commit()

print('Logging in...')
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD) 

def replybot():
    print('Searching %s.' % SUBREDDIT)
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = list(subreddit.get_comments(limit=MAXPOSTS))
    posts.reverse()
    for post in posts:
        pid = post.id

        try:
            pauthor = post.author.name
        except AttributeError:
            # Author is deleted.
            continue

        if pauthor.lower() == USERNAME.lower():
            #If user = self
            continue

        cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
        if cur.fetchone():
            # Post is already in database
            continue

        cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
        sql.commit()
        pbody = post.body.lower()
        if any(key.lower() in pbody for key in KEYWORDS):
            print('Replying to %s by %s' % (pid, pauthor))
            REPLYSTRING = bot_reply(pbody)
            post.reply(REPLYSTRING)

cycles = 0
while True:
    try:
        replybot()
        cycles += 1
    except Exception as e:
        traceback.print_exc()
    # if cycles >= CLEANCYCLES:
        # print('Cleaning database')
        # cur.execute('DELETE FROM oldposts WHERE id NOT IN (SELECT id FROM oldposts ORDER BY id DESC LIMIT ?)', [MAXPOSTS * 2])
        # sql.commit()
        # cycles = 0
    print('Running again in %d seconds \n' % WAIT)
    time.sleep(WAIT)
