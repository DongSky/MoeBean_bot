#encoding:utf-8
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,ConversationHandler)
import logging,os,urllib,json
import pixiv_auto_get
import description
import tag
import ocr
import mail
import shortlink
import weatherinfo
import btdiggTop10
import translate
import netease_music_lib
import bingsearch
#initialize logging module

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",level=logging.INFO)
logger=logging.getLogger(__name__)

#    some modules
def start(bot, update):
    update.message.reply_text('Hi!')

def photo(bot, update):
    print("photo in")
    user=update.message.from_user
    photo_file=bot.get_file(update.message.photo[-1].file_id)
    photo_file.download("test_photo.jpg")
    logger.info("Photo of %s: %s" % (user.first_name, 'test_photo.jpg'))
    update.message.reply_text("get")
    update.message.reply_photo(open("test_photo.jpg","rb"))
    return 1

def btdigg_start(bot, update):
    update.message.reply_text("input the content")
    return 1
def btdigg_get(bot,update):
    print("btdigg_get in")
    content=str(update.message.text)
    print(content)
    outputlist=btdiggTop10.btdiggtop10get(content)
    reply_str=""
    if len(outputlist)==0:
        reply_str+="error, no resources"
    else:
        cnt_=0
        for out in outputlist:
            reply_str+=out+"\n"
            cnt_+=1
            if cnt_>=min(10,len(outputlist)):
                break
    update.message.reply_text(reply_str)
    return ConversationHandler.END

def pixivget(bot, update):
    pic_get=pixiv_auto_get.pixiv_auto_get(pixiv_id=update.message.text.split("$")[1])
    for pic_pos in pic_get:
        update.message.reply_photo(open(pic_pos,"rb"))
    return 1
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Cancel',reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

#63738701
def pixiv_id_request(bot, update):
    update.message.reply_text("give me pixiv pic id")
    return 1
def pixiv_id_proc(bot, update):
    update.message.reply_text("searching...")
    pic_get=pixiv_auto_get.pixiv_auto_get(pixiv_id=update.message.text)
    for pic_pos in pic_get:
        update.message.reply_photo(open(pic_pos,"rb"))
    return ConversationHandler.END

def cognitive_description_request(bot,update):
    update.message.reply_text("give me a photo")
    return 1
def cognitive_description_proc(bot,update):
    user=update.message.from_user
    photo_file=bot.get_file(update.message.photo[-1].file_id)
    photo_file.download("test_photo.jpg")
    logger.info("Photo of %s: %s" % (user.first_name, 'test_photo.jpg'))
    output=description.Description('test_photo.jpg')
    update.message.reply_text(output)
    return ConversationHandler.END
def cognitive_category_request(bot,update):
    update.message.reply_text("give me a photo")
    return 1
def cognitive_category_proc(bot,update):
    user=update.message.from_user
    photo_file=bot.get_file(update.message.photo[-1].file_id)
    photo_file.download("test_photo.jpg")
    logger.info("Photo of %s: %s" % (user.first_name, 'test_photo.jpg'))
    output=tag.Tag('test_photo.jpg')
    update.message.reply_text(output)
    return ConversationHandler.END
def cognitive_ocr_request(bot,update):
    update.message.reply_text("give me a photo")
    return 1
def cognitive_ocr_proc(bot,update):
    user=update.message.from_user
    photo_file=bot.get_file(update.message.photo[-1].file_id)
    photo_file.download("test_photo.jpg")
    logger.info("Photo of %s: %s" % (user.first_name, 'test_photo.jpg'))
    output=ocr.OCR('test_photo.jpg')
    update.message.reply_text(output)
    return ConversationHandler.END

def start_mail_request(bot,update):
    print(update.message.from_user.id)
    if not os.path.exists("mail_config"):
        print(1)
        os.makedirs("mail_config")
        os.makedirs("mail_content")
    file_name='mail_config/'+str(update.message.from_user.id)+'.json'
    if os.path.exists(file_name):
        update.message.reply_text("input the content")
        return 2
    else:
        update.message.reply_text("""please setup your mail config\nFormat:\nsmtp_host;pop_host;mail_address;password""")
        return 1

def clear_mail_config(bot,update):
    file_name='mail_config/'+str(update.message.from_user.id)+'.json'
    if not os.path.exists(file_name):
        update.message.reply_text("no config")
    else:
        os.remove(file_name)
        update.message.reply_text("clear")
    return ConversationHandler.END

def setup_mail_config(bot,update):
    file_name='mail_config/'+str(update.message.from_user.id)+'.json'
    print(update.message.text)
    config_list=update.message.text.split(";")
    config_dict={}
    config_dict['smtp_host']=config_list[0]
    config_dict['pop_host']=config_list[1]
    config_dict['mail_address']=config_list[2]
    config_dict['password']=config_list[3]
    config_str=json.dumps(config_dict)
    with open(file_name,'w') as f:
        f.write(config_str)
        f.close()
    update.message.reply_text("config complete, input content")
    return 2
def edit_mail_content(bot,update):
    file_name='mail_content/'+str(update.message.from_user.id)+'_draft.txt'
    f=open(file_name,"w")
    f.write(update.message.text)
    update.message.reply_text("content complete")
    update.message.reply_text("input title and address\nformat:\ntitle;address")
    #update.message.reply_text("add a document, or input /skip to skip")
    return 3
def send_mail_proc(bot,update):
    title,address=update.message.text.split(";")
    content=""
    f=open('mail_content/'+str(update.message.from_user.id)+'_draft.txt','r')
    content=f.read()
    f.close()
    config=json.loads(open('mail_config/'+str(update.message.from_user.id)+'.json','r').read())
    try:
        status=mail.send(smtp_host=config['smtp_host'],mail_user=config['mail_address'],mail_pass=config['password'],to_list=[address],subject=title,text=content)
        if status==True:
            update.message.reply_text("sent")
        else:
            update.message.reply_text("failed")
    except Exception as e:
        print(e)
        update.message.reply_text("failed")
    return ConversationHandler.END

def shortlink_request(bot,update):
    update.message.reply_text("give me a link")
    return 1
def shortlink_proc(bot,update):
    update.message.reply_text(shortlink.shortlink(update.message.text))
    return ConversationHandler.END

def weather_request(bot,update):
    update.message.reply_text("give me a city name")
    return 1
def weather_proc(bot,update):
    update.message.reply_text(weatherinfo.weatherinfo(update.message.text))
    return ConversationHandler.END

def translate_request(bot,update):
    if not os.path.exists('translate'):
        os.makedirs('translate')
    update.message.reply_text('input the target language in short')
    update.message.reply_text(translate.lang_list)
    return 1
def lang_proc(bot,update):
    f=open('translate/'+str(update.message.from_user.id)+'.txt','w')
    f.write(update.message.text)
    f.close()
    update.message.reply_text('give me the content to be translated')
    return 2
def content_proc(bot,update):
    content=update.message.text
    lang=open('translate/'+str(update.message.from_user.id)+'.txt','r').read()
    update.message.reply_text(translate.translate(q=content,toLang=lang))
    return ConversationHandler.END

def song_request(bot,update):
    update.message.reply_text('give me the name of song')
    return 1
def song_proc(bot,update):
    Netease=netease_music_lib.NeteaseMusic()
    link=Netease.get_song_info_by_name(update.message.text)[-1]
    if not link==None:
        data=urllib.request.urlopen(link).read()
        update.message.reply_audio(data)
    else:
        update.message.reply_text('could not fetch this song')
    return ConversationHandler.END

def bing_search_request(bot,update):
    update.message.reply_text("input the search content")
    return 1
def bing_search_proc(bot,update):
    reply=bingsearch.search(update.message.text)
    update.message.reply_text(reply)
    return ConversationHandler.END
# def chinese_debug(bot,update):
#     print(update.message.text)

#Main function
def main():
    updater=Updater("your token")
    dp=updater.dispatcher

    btdigg_conv_handler=ConversationHandler(entry_points=[CommandHandler("btdigg",btdigg_start)],
    states={
        1:[MessageHandler(Filters.text,btdigg_get)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    pixiv_get_conv_handler=ConversationHandler(entry_points=[CommandHandler("pixiv",pixiv_id_request)],
    states={
    1:[MessageHandler(Filters.text,pixiv_id_proc)]
    },fallbacks=[CommandHandler('cancel', cancel)])

    description_conv_handler=ConversationHandler(entry_points=[CommandHandler("description",cognitive_description_request)],
    states={
        1:[MessageHandler(Filters.photo,cognitive_description_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    category_conv_handler=ConversationHandler(entry_points=[CommandHandler("category",cognitive_category_request)],
    states={
        1:[MessageHandler(Filters.photo,cognitive_category_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    ocr_conv_handler=ConversationHandler(entry_points=[CommandHandler("ocr",cognitive_ocr_request)],
    states={
        1:[MessageHandler(Filters.photo,cognitive_ocr_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    mail_send_handler=ConversationHandler(entry_points=[CommandHandler("mail",start_mail_request)],
    states={
        1:[MessageHandler(Filters.all,setup_mail_config)],
        2:[MessageHandler(Filters.all,edit_mail_content)],
        3:[MessageHandler(Filters.all,send_mail_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)])

    short_link_handler=ConversationHandler(entry_points=[CommandHandler("shortlink",shortlink_request)],
    states={
    1:[MessageHandler(Filters.text,shortlink_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)])

    weather_info_handler=ConversationHandler(entry_points=[CommandHandler("weather",weather_request)],
    states={
    1:[MessageHandler(Filters.text,weather_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)])

    translate_handler=ConversationHandler(entry_points=[CommandHandler("translate",translate_request)],
    states={
    2:[MessageHandler(Filters.text,content_proc)],
    1:[MessageHandler(Filters.text,lang_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)])

    song_handler=ConversationHandler(entry_points=[CommandHandler("song",song_request)],
    states={
        1:[MessageHandler(Filters.text,song_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    bing_search_handler=ConversationHandler(entry_points=[CommandHandler("search",bing_search_request)],
    states={
        1:[MessageHandler(Filters.text,bing_search_proc)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(mail_send_handler)
    dp.add_handler(btdigg_conv_handler)
    dp.add_handler(pixiv_get_conv_handler)
    dp.add_handler(description_conv_handler)
    dp.add_handler(category_conv_handler)
    dp.add_handler(ocr_conv_handler)
    dp.add_handler(short_link_handler)
    dp.add_handler(weather_info_handler)
    dp.add_handler(translate_handler)
    dp.add_handler(song_handler)
    dp.add_handler(bing_search_handler)
    dp.add_handler(CommandHandler("start",start))
    dp.add_handler(CommandHandler("clearmailconfig",clear_mail_config))
    #dp.add_handler(RegexHandler(r"/cn.+?",chinese_debug))
    #dp.add_handler(RegexHandler(r"/pixiv.+?",pixivget))
    #dp.add_handler(MessageHandler(Filters.photo,photo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()
