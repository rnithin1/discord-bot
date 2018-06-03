import discord, sikhgenerator, re

TOKEN = open("privatekey.txt", "r").read().split("\n")[0]

client = discord.Client()
#client.login('452696909375864853')

messages = dict()
markov = list()

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

    if message.author == client.user:
        return

    if message.content.startswith('suck my ass'):
        msg = 'fo shizzle my nizzle {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!generatesikh'):
        msg = sikhgenerator.make_name().format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('last message'):
        msg = '{0.author}, your last message was {1}!'.format(message, messages["{0.author}".format(message)])
        await client.send_message(message.channel, msg)

    if message.content.startswith('markov message'):
        msg = mark()
        msg = msg + "."
        await client.send_message(message.channel, msg)

    messages["{0.author}".format(message)] = message.content
    contents = message.content.lower().replace('\n', ' ')
    contents = re.sub('([a-zA-Z])', \
            lambda x: x.groups()[0].upper(), contents, 1)
    contents = re.sub(" \d+", " ", contents)
    if len(contents) >= 5:
        markov.extend(list(filter(None, contents.split(" "))))
        print(list(filter(None, contents.split(" "))))

@client.event
async def on_ready():
    pass

client.run(TOKEN)
