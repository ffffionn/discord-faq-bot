import discord
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection


class Bot(discord.Client):
    db: MongoClient
    replies: Collection

    def __init__(self, database: MongoClient, **options):
        super().__init__(**options)
        self.db = database
        self.replies = database.discord_bot.replies

    async def on_ready(self):
        print("Connected to Discord as %s." % self.user.name)
        print("Guilds:" + str([g.name for g in self.guilds]))

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.content.startswith("!"):
            await message.channel.send(await self.parse_message(message))

    async def parse_message(self, message: discord.Message):
        print("Got message: %s " % message.content)
        content = message.content[1:]
        content_parts = content.split(" ")
        msg = ""

        if len(content_parts) == 0:
            return msg

        reply = self.replies.find_one({"trigger": content_parts[0]})
        print("Found:  %s" % reply)

        if content_parts[0].lower() == "no," and (len(content_parts) > 3 and content_parts[2] == "is"):
            # if command is `no, __ is __` -> update reply
            reply = self.replies.find_one({"trigger": content_parts[1]})
            new_content = " ".join(content_parts[3:])
            if reply is not None:
                await self.update_db_row(new_content, message, reply)
            else:
                await self.create_db_row(content_parts[1], message, new_content)
            msg = "OK."
        elif reply is not None:
            # check msgDict for key
            if len(content_parts) > 1:
                user = await self.fetch_user(content_parts[1])
                if user is not None:
                    msg = content_parts[1]
            msg += " " + reply["content"]
        else:
            # else return generic msg
            msg = "Sorry, %s..  I didn't understand that command." % message.author.mention

        # if param 2, read user list and attempt to mention them
        print("\t returning: " + msg)
        return msg

    async def update_db_row(self, new_value: str, discord_message: discord.Message, reply: dict):
        update_set = {
            "content": new_value,
            "updated_by": discord_message.author.name,
            "last_updated": datetime.now()
        }
        self.replies.update_one({"_id": reply["_id"]}, update_set)

    async def create_db_row(self, trigger: str, message: discord.Message, new_content: str):
        reply = {
            "trigger": trigger,
            "content": new_content,
            "updated_by": message.author.name,
            "last_updated": datetime.now()
        }
        self.replies.insert_one(reply)
