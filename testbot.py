import discord
import sikhgenerator
import re
import subprocess
import os
import random
import aiohttp
import json
import asyncio

TOKEN = open("privatekey.txt", "r").read().split("\n")[0]

client = discord.Client()

messages = dict()
markov = list()
cache = list()
extensions = ['png', 'jpg', 'jpeg', 'gif']

def mark():
    import numpy as np

    corpus = markov

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

    n_words = 10

    for i in range(n_words):
        chain.append(np.random.choice(word_dict[chain[-1]]))

    return ' '.join(chain)

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself

    print(message.content)
    print(type(message.content))
    if message.attachments:
        print(message.attachments)
        extension = message.attachments[0]['url'].split(".")[-1]
        if extension.lower() in extensions:
            imgList = os.listdir("./cache")[0]
            try:
                os.remove('cache/' + imgList)
            except:
                pass
            with aiohttp.ClientSession() as session:
                async with session.get(message.attachments[0]['url']) as r:
                    print(dir(r))
                    data = await r.read()
                    print(data)
                    with open("cache/cache." + extension, "wb") as f:
                        f.write(data)

    if message.author == client.user:
        return

    if message.content.startswith('suck my ass'):
        msg = 'fo shizzle my nizzle {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!generatesikh'):
        msg = sikhgenerator.make_name().format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!lastmessage'):
        msg = '{0.author}, your last message was {1}!'.format(message, messages["{0.author}".format(message)])
        await client.send_message(message.channel, msg)

    if message.content.startswith('!markovmessage'):
        msg = mark()
        msg = msg + "."
        await client.send_message(message.channel, msg)

    if message.content == "!randomimage":
        imgList = os.listdir("./imgs")
        imgString = random.choice(imgList)
        path = "./imgs/" + imgString
        await client.send_file(message.channel, path)

    if message.content.startswith("!seamcarve"):
        cmd = message.content.split(" ")
        if len(cmd) != 3 or not cmd[1].isdigit() \
                or cmd[2] not in ["horizontal", "y", "vertical", "N"]:
            msg = "Usage: !seamcarve [numPixels] [horizontal | yN]"
            await client.send_message(message.channel, msg)
        else:
            await client.send_message(message.channel, "Calculating...")
            subprocess.call(['java', '-jar', 'seamcarve.jar', 'cache/'\
                    + os.listdir("./cache")[0], cmd[1], cmd[2]])
            await client.send_file(message.channel, "output.png")

    if message.content.startswith("!cachedimage"):
        await client.send_file(message.channel, \
                'cache/' + os.listdir("./cache")[0])

    messages["{0.author}".format(message)] = message.content
    contents = message.content.lower().replace('\n', ' ')
    contents = re.sub('([a-zA-Z])', \
            lambda x: x.groups()[0].upper(), contents, 1)
    contents = re.sub(" \d+", " ", contents)

    if len(contents) >= 5:
        markov.extend(list(filter(None, contents.split(" "))))

@client.event
async def on_ready():
    pass

client.run(TOKEN)
