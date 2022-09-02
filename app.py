import os
import re
import deepl
import discum
import requests
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook

load_dotenv()

prefix = 'https://cdn.discordapp.com/'
avatar = 'avatars/{user_id}/{user_avatar}.png'
hooks = {
    'TA': [os.environ["TA_HOOK"], os.environ["ORI_TA"]],
    'TR': [os.environ["TRADING_HOOK"], os.environ["ORI_TRADING"]],
    'DAILY': [os.environ["DAILY_HOOK"], os.environ["ORI_DAILY"]],
    'PUBLIC': [os.environ["PUBLIC_HOOK"], os.environ["ORI_PUB"]],
    'SILVERBAY_ANNOUNCE': [os.environ['SILVERBAY_HOOK']],
    'KUO': [os.environ['FUPAN_HOOK'] + '?thread_id=998336868913528944'],
    'SKRRA': [os.environ['FUPAN_HOOK'] + '?thread_id=1006216000586403981'],
    'QIE': [os.environ['FUPAN_HOOK'] + '?thread_id=1006216102856118362'],
    'DORCAS': [os.environ['FUPAN_HOOK'] + '?thread_id=1006215829114851328']
}

CHANNELS = {
    '917568228367171614': {
        'name': "TA-pablo-on-chain",
        'hooks': hooks['TA']
    },
    '912549044805566584': {
        'name': "TA-pulkit",
        'hooks': hooks['TA']
    },
    '912549119023792128': {
        'name': "TA-asad",
        'hooks': hooks['TA']
    },
    '914234223248932894': {
        'name': "TA-surja",
        'hooks': hooks['TA']
    },
    '945769733729452122': {
        'name': "TA-moussa",
        'hooks': hooks['TA']
    },
    '957322015671484456': {
        'name': "TA-lucifer",
        'hooks': hooks['TA']
    },
    '966717040989708398': {
        'name': "TA-kayler",
        'hooks': hooks['TA']
    },
    '996773096587526225': {
        'name': "TA-kingpincrypto",
        'hooks': hooks['TA']
    },
    '970807197758005298': {
        'name': "TR-swing",
        'hooks': hooks['TR']
    },
    '970807236203003905': {
        'name': "TR-scalp",
        'hooks': hooks['TR']
    },
    '922210237337960489': {
        'name': "TR-idea",
        'hooks': hooks['TR']
    },
    '938996765921792050': {
        'name': "TR-lesson",
        'hooks': hooks['TR']
    },
    '898579005232521286': {
        'name': "DAILY-BTC",
        'hooks': hooks['DAILY']
    },
    '899394668662505502': {
        'name': "DAILY-ETH",
        'hooks': hooks['DAILY']
    },
    '930970372726222898': {
        'name': "DAILY-NEWS",
        'hooks': hooks['DAILY']
    },
    '919228190097043476': {
        'name': "chat",
        'hooks': hooks['PUBLIC']
    },
    '1004963672826847313': {
        'name': 'KUO',
        'hooks': hooks['KUO']
    },
    '913054223460102205': {
        'name': "SILVERBAY_ANNOUNCE",
        'hooks': hooks['SILVERBAY_ANNOUNCE']
    },
    '1000276250255949844': {
        'name': 'SKRRA',
        'hooks': hooks['SKRRA']
    },
    '992093748278341672': {
        'name': 'QIE',
        'hooks': hooks['QIE']
    },
    '1006214862151635006': {
        'name': 'DORCAS',
        'hooks': hooks['DORCAS']
    }
}

bot = discum.Client(token=os.getenv("USER"), log=False)


@bot.gateway.command
def on_message(resp):
    # ready_supplemental is sent after ready
    if resp.event.ready_supplemental:
        user = bot.gateway.session.user
        print("Logged in as {}#{}".format(user["username"],
                                          user["discriminator"]))
    if resp.event.message:
        m = resp.raw['d']
        # because DMs are technically channels too
        guildID = m["guild_id"] if "guild_id" in m else None
        if guildID == "895412557668548608":
            blockchain_sniper(m)
        if guildID == '913012487841001502':
            silverbay(m)
        if guildID == '965110788618588200':
            kolunite(m)


def kolunite(m):
    guildID = m["guild_id"]
    channelID = m["channel_id"]
    username = m["author"]["username"]
    discriminator = m["author"]["discriminator"]
    content = m["content"]
    print(">Kolunite guild {} channel {} | {}#{}: {}".format(
        guildID, channelID, username, discriminator, content))

    w = get_webhook(channelID)
    if w is not None:
        w.username, w.avatar_url = get_user_info(m)
        w.embeds, attach = add_attachments(m)
        w.content = m['content']
        w.content += attach
        w.execute()


def silverbay(m):
    guildID = m["guild_id"]
    channelID = m["channel_id"]
    username = m["author"]["username"]
    discriminator = m["author"]["discriminator"]
    content = m["content"]
    print(">Silverbay guild {} channel {} | {}#{}: {}".format(
        guildID, channelID, username, discriminator, content))
    w = get_webhook(channelID)
    if w is not None:
        w.username, w.avatar_url = get_user_info(m)
        w.content = re.sub(r'@(\w+|&\d+)', '<@&1006662849587855401>',
                           m['content'])
        w.embeds, attach = add_attachments(m)
        w.content += attach
        w.execute()


def blockchain_sniper(m):
    EN_MENTION = '998715559418011769'
    guildID = m["guild_id"]
    channelID = m["channel_id"]
    username = m["author"]["username"]
    discriminator = m["author"]["discriminator"]
    content = m["content"]
    print(">Blockchain_sniper guild {} channel {} | {}#{}: {}".format(
        guildID, channelID, username, discriminator, content))

    wb = get_ori_webhook(channelID)
    if wb:
        wb.username, wb.avatar_url = get_user_info(m)
        wb.content = re.sub(r"@everyone", f"<@&{EN_MENTION}>", content)
        wb.embeds, attach = add_attachments(m)
        wb.content += attach
        wb.execute()

    w = get_webhook(channelID)
    if w:
        w.username, w.avatar_url = get_user_info(m)
        w.content = translate(re.sub(r"@everyone", "everyone", content))
        w.embeds, attach = add_attachments(m)
        w.content += attach
        w.execute()


def get_webhook(cid):
    if cid in CHANNELS:
        return DiscordWebhook(CHANNELS[cid]['hooks'][0], rate_limit_retry=True)
    return None


def get_ori_webhook(cid):
    if cid in CHANNELS:
        return DiscordWebhook(CHANNELS[cid]['hooks'][1], rate_limit_retry=True)
    return None


def translate(message):
    try:
        return deepl.translate(source_language="EN",
                               target_language="ZH",
                               text=message)
    except requests.exceptions.HTTPError as e:
        print(e)
    return message


def get_user_info(msg):
    return msg["author"]["username"], prefix + avatar.format(
        user_id=msg["author"]["id"], user_avatar=msg["author"]["avatar"])


def add_attachments(msg):
    embeds = []
    attachments = ''
    if len(msg["embeds"]) > 0:
        embeds = msg["embeds"]
    if len(msg["attachments"]) > 0:
        for att in msg["attachments"]:
            attachments += "\n" + att["url"]
    return embeds, attachments

bot.gateway.run()