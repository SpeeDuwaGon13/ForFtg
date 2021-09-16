import asyncio
import logging
import telethon
from .. import loader, utils
from telethon import TelegramClient
from telethon.tl.custom.message import Message

logger = logging.getLogger(__name__)


@loader.tds
class SendMessageGamePlayActionMod(loader.Module):
    strings = {
        "name": "sendMessageGamePlayAction to chat",
    }
    _game_tasks: {int, asyncio.Task} = {}

    async def client_ready(self, client: TelegramClient, db):
        self.db = db
        self.client = client

        _tasks = self._game_tasks

        if "setGamingStatus" not in self.db:
            self.db["setGamingStatus"] = {"CHATS": []}

        for chat in self.db["setGamingStatus"]["CHATS"]:
            if chat in _tasks:
                continue
            _tasks[chat] = client.loop.create_task(
                self.actioner(chat, _tasks)
            )

            logger.info(f"Setting sendMessageGamePlayAction task to {chat}")

    # stopga
    async def stopgacmd(self, message: Message):
        """stop game action"""
        args = utils.get_args(message)

        if args:
            stop_action_chat = args[0]
        else:
            stop_action_chat = str(abs(message.chat_id))

        client: TelegramClient = message.client
        _tasks = self._game_tasks

        if stop_action_chat.isdigit():
            stop_action_chat = int(stop_action_chat)

        try:
            entity = await client.get_input_entity(stop_action_chat)
        except ValueError:
            await message.edit(f"<b>Cannot find any entity corresponding to {stop_action_chat}</b>\n" +
                               "<b>Try to use username</b>" if stop_action_chat.isdigit() else ""
                               )
            return

        _chat_id = abs(telethon.utils.get_peer_id(entity))

        if _chat_id not in _tasks.keys():
            await message.edit(f"<b><code>{stop_action_chat}</code> not in list</b>")
            return

        _tasks[_chat_id].cancel()
        del _tasks[_chat_id]
        self.del_chat_id(_chat_id)

        # await message.edit("<b>Stopped</b>")
        # await asyncio.sleep(.5)
        # await message.delete()

        await message.edit(f"<b>{stop_action_chat} was stopped</b>")

    # startga
    async def startgacmd(self, message: Message):
        """start game action"""
        args = utils.get_args(message)

        if args:
            start_action_chat = args[0]
        else:
            start_action_chat = str(abs(message.chat_id))

        client: TelegramClient = self.client
        _tasks = self._game_tasks

        if start_action_chat.isdigit():
            start_action_chat = int(start_action_chat)

        try:
            entity = await client.get_input_entity(start_action_chat)
        except ValueError:
            await message.edit(f"<b>Cannot find any entity corresponding to {start_action_chat}</b>\n" +
                               "<b>Try to use username</b>" if start_action_chat.isdigit() else ""
                               )
            return

        _chat_id = abs(telethon.utils.get_peer_id(entity))

        if _chat_id in _tasks.keys():
            await message.edit(f"<b>Chat <code>{start_action_chat}</code> already started</b>")
            return

        _tasks[_chat_id] = client.loop.create_task(self.actioner(entity, _tasks))
        self.db["setGamingStatus"]["CHATS"].append(_chat_id)
        try:
            _command_prefix = self.db["friendly-telegram.main"]['command_prefix'][0]
        except:
            _command_prefix = "."

        await message.edit(f"<b>Chat {start_action_chat} was started. "
                           f"To remove it, enter <code>{_command_prefix}stopga {_chat_id}</code></b>")

    # getga
    async def getgacmd(self, message: Message):
        """get game actions"""
        _names: list[str] = ["<b>Sending sendMessageGamePlayAction to:</b>"]

        if self._game_tasks.keys():
            for _num, user_id in enumerate(self._game_tasks.keys(), 1):
                _sql_req = message.client.session._cursor().execute('select name, username from entities where id=:id',
                                                                    {"id": user_id}).fetchall()
                if _sql_req:
                    _name, _username = _sql_req[0]
                    additional_user_information = f"(name: {_name}"
                    additional_user_information += f"; username: @{_username})" if _username else ")"
                else:
                    additional_user_information = ""
                _names.append(f"<b>{_num}:</b> <code>{user_id}</code> {additional_user_information}")

            await message.edit("\n".join(_names))
        else:
            await message.edit("<b>Notning...</b>")

    async def actioner(self, entity, _tasks):
        client = self.client
        if isinstance(entity, int):
            try:
                entity = await client.get_input_entity(entity)
            except ValueError as err:
                logger.error(err)
                return

        try:
            async with client.action(entity, 'game'):
                while True:
                    await asyncio.sleep(1337)
        except Exception as err:
            del _tasks[entity]
            self.del_chat_id(abs(telethon.utils.get_peer_id(entity)))
            logger.error(f"Error while sending sendMessageGamePlayAction to {entity}: {err}")

    def del_chat_id(self, chat_id):
        while True:
            try:
                self.db["setGamingStatus"]["CHATS"].remove(chat_id)
            except:
                break
