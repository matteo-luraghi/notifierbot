import telebot
import json
import time
import requests
import config

API_KEY = config.API_KEY
PALINSESTO = config.PALINSESTO

bot = telebot.TeleBot(API_KEY)

notification = {}
annulla = {}

def sendAlert(program: str, speakers: list):
    print("Sending alert for:", program)
    with open("utils/users.json", "r") as f:
        dbUsers = json.load(f)

    speakersStr = ""
    if len(speakers) > 1:
        for i in range(len(speakers)):
            if i == len(speakers) - 1:
                speakersStr += "e " + speakers[i]
            else:
                speakersStr += speakers[i] + ", "

    for user in dbUsers:
        bot.send_message(user, "https://www.poliradio.it/")
        bot.send_message(user, "https://www.twitch.tv/poliradioit")
        bot.send_message(user, "Ricorda che puoi scrivere agli speaker tramite @poliradiobot")
        if len(speakers) > 1:
            bot.send_message(user, f"{speakersStr} sono in diretta ora con {program}, corri ad ascoltarli!")
        else:
            bot.send_message(user, f"{speakers[0]} è in diretta ora con {program}!")


@bot.message_handler(commands=["start"])
def init(message):
    bot.send_message(message.chat.id, "Saluti! Per iniziare dai un'occhiata ai comandi disponibili")
    with open("utils/users.json", "r") as f:
        dbUsers = json.load(f)
    dbUsers[message.chat.id] = message.chat.username
    print(f"Added user {message.chat.username}")
    with open("utils/users.json", "w") as f:
        json.dump(dbUsers, f)
    sendHelp(message)

@bot.message_handler(commands=["notifica"])
def notify(message):
    annulla[message.chat.id] = False
    notification[message.chat.id] = {}
    bot.send_message(message.chat.id, "Manda il nome del programma")
    bot.register_next_step_handler(message, saveProgram)

def saveProgram(message: telebot.types.Message):
    if annulla[message.chat.id] == True:
        return 

    program = message.text
    if program == None or program == "":
        bot.send_message(message.chat.id, "Errore, nessun nome del programma trovato")
        notify(message)
        return
    
    notification[message.chat.id]["program"] = program
    bot.send_message(message.chat.id, "Manda i nomi degli speaker separati da uno spazio (es. Giovanni Luca Marco)")
    bot.register_next_step_handler(message, saveSpeakers)

def saveSpeakers(message: telebot.types.Message):
    if annulla[message.chat.id] == True:
        return 

    speakers = str(message.text).split(" ")
    speakers = [speaker.capitalize() for speaker in speakers]
    if speakers == [] or len(speakers) < 1:
        bot.send_message(message.chat.id, "Errore, nessun nome di speaker trovato")
        notify(message)
        return
    
    notification[message.chat.id]["speakers"] = speakers
    bot.send_message(message.chat.id, "Perfetto, il messaggio verrà inviato tra 10 secondi (puoi usare /annulla per cancellare l'operazione)")
    
    count = 0
    while count < 10 and annulla[message.chat.id] == False:
        time.sleep(1)
        count += 1
    if annulla[message.chat.id] == False:
        sendAlert(notification[message.chat.id]["program"], notification[message.chat.id]["speakers"])

    del annulla[message.chat.id]
    del notification[message.chat.id]
    
@bot.message_handler(commands=["annulla"])
def cancel(message):
    annulla[message.chat.id] = True

@bot.message_handler(commands=["palinsesto"])
def sendPalinsesto(message):
    try:
        res = requests.get(PALINSESTO).json()
    except:
        res = None

    if res != None:
        palinsestoStr = ""
        for program in res:
            palinsestoStr += f"{program['name']} il {program['day']} alle {program['hour']}:00\n"

        bot.send_message(message.chat.id, palinsestoStr)
            
    else:
        bot.send_message(message.chat.id, "Errore, riprova più tardi")

@bot.message_handler(commands=["help"])
def sendHelp(message):
    userId = str(message.chat.id)
    with open("utils/commands.txt", "r") as f:
        commands = f.read()
    bot.send_message(userId, commands)

if __name__ == "__main__":
    print("Bot started")
    bot.infinity_polling()
