import os
import config

#installs python libraries needed to run the bot
print("Installing libraries")
os.system("pip install -r requirements.txt")

#creates the utility files needed to run the bot
print("Creating files")
os.system("touch utils/users.json")
os.system("echo {} > utils/users.json")

#asks the user for the telegram api key and api website for the programs
api = input("Inserisci la chiave api per il bot: ")

config.API_KEY = api

print("Setup completed!")
