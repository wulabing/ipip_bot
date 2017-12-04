import telegram
import requests
import json
import re
import socket
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent


TOKEN = "442941270:AAG-PVZHUVxJnbTcPWJz_y8pycf6gFF7qZs"
bot = telegram.Bot(token=TOKEN)
updater = Updater(token=TOKEN)

dispatcher = updater.dispatcher
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a simple ipip bot, please use /ipip ipaddress"
        " commmand to get ip information")



def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)



def caps(bot, update, args):
    text_caps = ''.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)


def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)


def is_ip(ipaddr):
    ip = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if ip.match(ipaddr):
        return True
    else:
        return False


def is_url(urladdr):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if regex.match(urladdr):
        return True
    else:
        return False


def resolve_url(urladdr):
    ip_list = list()
    response = socket.getaddrinfo(urladdr, None)
    for i in response:
        ip_list.append(i[4][0])
    return ip_list


def format_url(urladdr):
    if urladdr[:8] == "https://":
        domain = urladdr[8:]
    elif urladdr[:7] == "http://":
        domain = urladdr[7:]
    else:
        domain = urladdr
    return domain


def format_ipip(ip, text):
    response = "IP: %s\n国家/机构 : %s \n城市 : %s\t%s \n运营商 : %s\t%s " % (
        ip, text[0], text[1], text[2], text[3], text[4])
    return response


def print_inf(ipaddr):
    r = requests.get("http://freeapi.ipip.net/%s" % ipaddr)
    return json.loads(r.text)


def ipip(bot, update, args):
    if is_ip(args[0]):
        text_ipip = print_inf(args[0])
        response = format_ipip(args[0], text_ipip)
        bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        url = args[0]
        domain = format_url(url)
        ip_list = resolve_url(domain)
        for i in ip_list:
            text_ipip = print_inf(i)
            response = format_ipip(i, text_ipip)
            bot.send_message(chat_id=update.message.chat_id, text=response)


inline_caps_handler = InlineQueryHandler(inline_caps)
caps_handler = CommandHandler('caps', caps, pass_args=True)
ipip_handler = CommandHandler('ipip', ipip, pass_args=True)
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(ipip_handler)
dispatcher.add_handler(inline_caps_handler)
updater.start_polling()
