from ocr import rotationCorrect, prepareText, printText
import discord
import re
import subprocess
import os
import random
import aiohttp
import json
import asyncio
import sikhgenerator
import googletrans
import praw
import numpy as np
import pytesseract
import cv2

TOKEN = open("privatekey.txt", "r").read().split("\n")[0]
CLIENT_ID, CLIENT_SECRET, USER_AGENT = tuple(filter(None, open("reddit.txt", "r").read().split("\n")))

client = discord.Client()
translator = googletrans.Translator() # Uses Google trans, may switch to Apertium

reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

repeated_post = dict({0 : 0})
messages = dict()
custom_commands = dict()
markov = dict()
cached = dict()
extensions = ['png', 'jpg', 'jpeg', 'gif']
langs = dict(zip(open("iso639-1-names.txt", "r").read().split("\n"), \
        open("iso639-1-codes.txt", "r").read().split("\n")))
commands = ['!generatesikh', '!lastmessage', '!markovmessage', '!randomimage', '!help', '!seamcarve', \
        '!translate', '!ocr', '!anime', '!cachedimage', '!thanos', '!customcommand', '!ayuda', '!figlet']


def mark(server):
    corpus = markov[server]

    def make_pairs(corpus):
        for i in range(len(corpus)-1):
            yield (corpus[i], corpus[i+1])

    pairs = make_pairs(corpus)

    word_dict = {}

    for word_1, word_2 in pairs:
        if word_1 in word_dict.keys():
            word_dict[word_1].append(word_2)
        else:
            word_dict[word_1] = [word_2]
    first_word = np.random.choice(corpus)

    while first_word.islower():
        first_word = np.random.choice(corpus)

    chain = [first_word]

    n_words = random.randint(10, 30)

    for i in range(n_words):
        chain.append(np.random.choice(word_dict[chain[-1]]))

    for i in range(len(chain) - 1):
        if chain[i + 1].istitle() and chain[i][-1].isalnum():
            chain[i] = chain[i] + "."

    return ' '.join(chain)

@client.event
async def on_message(message):
    global repeated_post
    print(message.content)
    print(message.server.id)
    print(type(message.content))
    if message.attachments and not message.author.bot:
        print('{0.author}'.format(message))
        print(message.attachments)
        extension = message.attachments[0]['url'].split(".")[-1]
        directory = "./cache"
        if "cache" not in os.listdir("."):
            os.makedirs("cache")

        if extension.lower() in extensions:
            if str(message.server.id) not in os.listdir(directory):
                os.makedirs(directory + "/" + message.server.id) 

            directory += '/' + message.server.id
            if os.listdir(directory) == list():
                open(directory + '/cache.jpg', 'a').close() 

            os.remove(directory + '/' + os.listdir(directory)[0])

            with aiohttp.ClientSession() as session:
                async with session.get(message.attachments[0]['url']) as r:
                    print(dir(r))
                    data = await r.read()
                    print(data)
                    with open(directory + "/cache." + extension, "wb") as f:
                        f.write(data)

    if message.author == client.user and \
            not message.content.split(" ")[0] in commands:
        return

    if message.content.split(" ")[0] in commands and message.author.bot:
        await client.delete_message(message)

    if message.content.startswith('!generatesikh'):
        msg = sikhgenerator.make_name().format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!markovmessage'):
        if message.server.id not in markov.keys():
            markov[message.server.id] = list()
        if len(markov[message.server.id]) < 40:
            await client.send_message(message.channel, "ERROR: Not enough messages cached")
        else:
            msg = mark(message.server.id)
            msg = msg + "."
            await client.send_message(message.channel, msg)

    """
    if message.content == "!randomimage":
        imgList = os.listdir("./imgs")
        imgString = random.choice(imgList)
        path = "./imgs/" + imgString
        await client.send_file(message.channel, path)
    """
    if message.content == "!ayuda":
        msg = '''
            AVAILABLE COMMANDS:
            !generatesikh -- Generate random Sikh name
            !markovmessage -- Generates random sentence from past messages
            !seamcarve [numPixels] [horizontal | yN] -- Seamcarves last image numPixels
            !translate [source] [dest] [message] -- Translates [message] from [source] to [dest] language
            !cachedimage -- Returns last (cached) image
            !anime -- Posts random anime gif from Reddit
            !thanos -- Were you slain for the good of the Universe? I call that mercy.
            !ocr -- Tries to read text from image provided
            !customcommand -- Creates a custom command
            !listcustom -- Lists current custom commands
            !figlet -- Figlets custom text
            '''
        await client.send_message(message.channel, msg)

    if message.content.startswith("!seamcarve"):
        cmd = message.content.split(" ")
        if len(cmd) != 3 or not cmd[1].isdigit() \
                or cmd[2] not in ["horizontal", "y", "vertical", "N"]:
            msg = "Usage: !seamcarve [numPixels] [horizontal | yN]"
            await client.send_message(message.channel, msg)
        else:
            await client.send_message(message.channel, "Calculating...")
            subprocess.call(['java', '-jar', 'seamcarve.jar', 'cache/' \
                    + message.server.id + '/' \
                    + os.listdir("./cache/" + message.server.id)[0], cmd[1], cmd[2]])
            await client.send_file(message.channel, "output.png")

    if message.content.startswith("!translate"):
        cmd = message.content.split(" ")
        if len(cmd) < 4 or cmd[1].lower().title() not in \
                list(langs.keys()) or cmd[2].lower().title() not in \
                list(langs.keys()):
            msg = "Usage: !translate [source] [dest] [message]"
            await client.send_message(message.channel, msg)
        else:
            msg = " ".join(cmd[3:])
            print(msg)
            msg = msg.lower().replace('\n', ' ')
            msg = re.sub('([a-zA-Z])', \
                    lambda x: x.groups()[0].upper(), msg, 1)
            msg = re.sub(" \d+", " ", msg)
            try:
                print(msg.lower())
                print(langs[cmd[1].title()])
                print(langs[cmd[2].title()])
                msg = translator.translate(msg.lower(), \
                        src=langs[cmd[1].title()], \
                        dest=langs[cmd[2].title()]).text
                print(msg)
            except:
                msg = "ERROR"
            await client.send_message(message.channel, msg)

    if message.content.startswith("!ocr"):
        cachedimage = 'cache/' + message.server.id + '/' + os.listdir("./cache/" \
                + message.server.id)[0]
        try:
            image = cv2.imread(cachedimage)
            msg = rotationCorrect(image)
            if not msg:
                msg = "ERROR: Could not read text from image"
            await client.send_message(message.channel, msg)
        except:
            msg = "Oopsy woopsy! We made a fucky wucky! :3"
            await client.send_message(message.channel, msg)

    if message.content.startswith("!anime"):
        gen = reddit.subreddit('animegifs').top()
        for _ in range(0, random.randint(1, 100)):
            submission = next(x for x in gen if not x.stickied)
        await client.send_message(message.channel, submission.url)

    if message.content.startswith("!figlet"):
        if len(message.content.split(" ")) == 1:
            await client.send_message(message.channel, \
                    "Usage: !figlet [text]")
        else:
            cmd = "echo " + " ".join(list( \
                    map(lambda x : re.escape(x), \
                    message.content.split(" ")[1:]))) + "|figlet"
            ps = subprocess.Popen(cmd, shell=True, \
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()[0].decode('utf-8')
            await client.send_message(message.channel, '```' + \
                    output + '```')

    if message.content.startswith("!cachedimage"):
        await client.send_file(message.channel, \
                'cache/' + message.server.id + '/' \
                + os.listdir("./cache/" + message.server.id)[0])

    if 'suck my ass' in message.content.lower():
        msg = 'fo shizzle my nizzle {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('im not ok'):
        msg = 'pikachu rikachu pee pee in the window {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith("!thanos"):
        if random.randint(0, 1) % 2 == 0:
            msg = "You were spared by Thanos."
        else:
            msg = "You were slain by Thanos, for the good of the Universe."
        await client.send_message(message.channel, msg)

    if message.content.startswith("!customcommand"):
        if len(message.content.split(" ")) >= 3:
            msg = message.content.split(" ")
            cmd = msg[1]
            if cmd[0] == '!' and cmd not in commands:
                cust = " ".join(msg[2:])
                if message.server.id not in custom_commands.keys():
                    custom_commands[message.server.id] = dict()
                custom_commands[message.server.id][cmd] = cust
                await client.send_message(message.channel, "'{}' -> '{}' saved as a custom command!" \
                        .format(cmd, cust))
            else:
                await client.send_message(message.channel, "Usage: !customcommand ![custom] [message]")

        else:
            await client.send_message(message.channel, "Usage: !customcommand ![custom] [message]")

    if message.content.startswith("!listcustom"):
        msg = ""
        if message.server.id not in custom_commands.keys():
            await client.send_message(message.channel, "No custom commands!")
        else:
            keys = custom_commands[message.server.id].keys()
            values = custom_commands[message.server.id].values()
            for k, v in zip(keys, values):
                msg += k + ' -> ' + v + '\n'
            await client.send_message(message.channel, msg)

    if not message.author.bot:
        if message.server.id in custom_commands.keys():
            if message.content in custom_commands[message.server.id].keys():
                await client.send_message(message.channel, custom_commands \
                        [message.server.id][message.content])

        if message.server.id not in messages.keys():
            messages[message.server.id] = dict()
        messages[message.server.id]["{0.author}".format(message)] = message.content
        contents = message.content.lower().replace('\n', ' ')
        contents = re.sub('([a-zA-Z])', \
                lambda x: x.groups()[0].upper(), contents, 1)
        contents = re.sub(" \d+", " ", contents)

    else:
        contents = ""

    if message.server.id not in markov.keys():
        markov[message.server.id] = list()

    if message.server.id not in cached.keys():
        cached[message.server.id] = list()

    if not message.author.bot and contents[0].isalnum() and len(contents.split(" ")) >= 5 and contents[0] != "!":
        markov[message.server.id].extend(list(filter(None, contents.split(" "))))

    cached[message.server.id].append(message.content)
    print(messages)
    print(cached)
    sp = [x for x in messages[message.server.id].values() \
            if x == message.content]
    if message.server.id not in repeated_post.keys():
        repeated_post[message.server.id] = 0

    if len(sp) >= 3 and not message.author.bot \
            and message.content != repeated_post.get(message.server.id, \
            message.content) and message.content[0].isalnum():
        repeated_post[message.server.id] = message.content
        await client.send_message(message.channel, message.content)

@client.event
async def on_ready():
    print("Starting...")
    await client.change_presence(game=discord.Game(name='Help: !ayuda'))

client.run(TOKEN)
