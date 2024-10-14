import discord
import os
from discord.message import MessageInteractionMetadata
from dotenv import load_dotenv
import requests  #allows http req to get data from api
import json  #data will be in json format
import random
from replit import db
from keep_alive import keep_alive

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]
starter_encouragements = [
    "Cheer up!", "Hang in there.", "You are a great person / bot!"
]

if "responding" not in db.keys():
  db["responding"] = True


#get quotes from the api
def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return (quote)


#update encouraagements
def update_encouragements(encouraging_message):
  if 'encouragements' in db.keys():
    encouragements = db['encouragements']
    encouragements.append(encouraging_message)
    db['encouragements'] = encouragements
  else:
    db['encouragements'] = [encouraging_message]


#delete encouragement
def delete_encouragement(index):
  encouragements = db['encouragements']
  if len(encouragements) > index:  #index greater than list
    del encouragements[index]
  db['encouragements'] = encouragements


# Load environment variables from the .env file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


#ifbot receives a message if message is from ourselves don't do anything. If hello reply with hello
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)
  #if respomding-true then only respond to the sad words
  if (db["responding"]):
    options = starter_encouragements
    if "encouragements" in db.keys():
      options = options + list(db['encouragements'])

    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))

  #$new - new message(add new message)
  if msg.startswith('$new'):
    encouraging_message = msg.split('$new ', 1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added.")

  if msg.startswith('$del'):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(msg.split('$del', 1)[1])
      delete_encouragement(index)
      encouragements = db['encouragements']
    await message.channel.send(encouragements)

  if msg.startswith('$list'):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db['encouragements']
    await message.channel.send(encouragements)

  if msg.startswith('$responding'):
    value = msg.split('$responding ', 1)[1]
    if value.lower() == "true":
      db['responding'] = True
      await message.channel.send("Responding is on.")
    if value.lower() == "false":
      db['responding'] = False
      await message.channel.send("Responding is off.")


#by deafult replit are public and tokens are public so we need to keep it private
keep_alive()
client.run(os.getenv('TOKEN'))
