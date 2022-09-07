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
    'TA': [os.environ["TA_CN"], os.environ["TA"]],
    'TR': [os.environ["VIVIAN_TRADE_CN"], os.environ["VIVIAN_TRADE"]],
    'DAILY': [os.environ["VIVIAN_DAILY_CN"], os.environ["VIVIAN_DAILY"]],
    # 'KUO': [os.environ['FUPAN_HOOK'] + '?thread_id=998336868913528944'],
    # 'SKRRA': [os.environ['FUPAN_HOOK'] + '?thread_id=1006216000586403981'],
    # 'QIE': [os.environ['FUPAN_HOOK'] + '?thread_id=1006216102856118362'],
    # 'DORCAS': [os.environ['FUPAN_HOOK'] + '?thread_id=1006215829114851328']
}

CHANNELS = {
    # bc sniper
    '917568228367171614': {'description': "TA-eazy12k", 'hooks': hooks['TA']},
    '912549044805566584': {'description': "TA-pulkit", 'hooks': hooks['TA']},
    '912549119023792128': {'description': "TA-asad", 'hooks': hooks['TA']},
    '914234223248932894': {'description': "TA-surja", 'hooks': hooks['TA']},
    '945769733729452122': {'description': "TA-moussa", 'hooks': hooks['TA']},
    '957322015671484456': {'description': "TA-lucifer", 'hooks': hooks['TA']},
    '966717040989708398': {'description': "TA-kayler", 'hooks': hooks['TA']},
    '996773096587526225': {'description': "TA-kingpincrypto", 'hooks': hooks['TA']},
    '970807197758005298': {'description': "TR-swing", 'hooks': hooks['TR']},
    '970807236203003905': {'description': "TR-scalp", 'hooks': hooks['TR']},
    '922210237337960489': {'description': "TR-idea", 'hooks': hooks['TR']},
    '938996765921792050': {'description': "TR-lesson", 'hooks': hooks['TR']},
    '898579005232521286': {'description': "DAILY-BTC", 'hooks': hooks['DAILY']},
    '899394668662505502': {'description': "DAILY-ETH", 'hooks': hooks['DAILY']},
    '930970372726222898': {'description': "DAILY-NEWS", 'hooks': hooks['DAILY']},
    # coop
    # '1004963672826847313': {'description': 'KUO', 'hooks': hooks['KUO']},
    # '913054223460102205': {'description': "SILVERBAY_ANNOUNCE", 'hooks': hooks['SILVERBAY_ANNOUNCE']},
    # '1000276250255949844': {'description': 'SKRRA', 'hooks': hooks['SKRRA']},
    # '992093748278341672': {'description': 'QIE', 'hooks': hooks['QIE']},
    # '1006214862151635006': {'description': 'DORCAS', 'hooks': hooks['DORCAS']}
}

bot = discum.Client(token=os.getenv('USER'))


@bot.gateway.command
def on_message(resp):
    # ready_supplemental is sent after ready
    if resp.event.ready_supplemental:
        user = bot.gateway.session.user
        print("Logged in as {}#{}".format(user["username"],
                                          user["discriminator"]))
    if resp.event.message:
        m = resp.raw['d']
        guildID = m["guild_id"] if "guild_id" in m else None
        if guildID == "895412557668548608":
            blockchain_sniper(m)
        # elif guildID == '913012487841001502':
        #     silverbay(m)
        # elif guildID == '965110788618588200':
        #     kolunite(m)


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
        wb.content = content
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
