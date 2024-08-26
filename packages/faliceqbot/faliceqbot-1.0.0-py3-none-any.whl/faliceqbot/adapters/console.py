"""
It's a user '114514' in a group '1919810'.
And the user is in bot's friends list.
The bot is '2333333'.
Type in console to send message to '1919810'.
Type in console with a start of 'private:' to send message in private.
"""
from faliceqbot import logger
from faliceqbot.segments import Group, User, Message, Base_Adapter
import time, os, platform, sys
import re

if platform.system() == 'Windows':
    ICONPATH = 'file:///' + os.path.join(os.path.dirname(__file__), 'console_icons').capitalize().replace('\\', '/')
else:
    ICONPATH = 'file://' + os.path.join(os.path.dirname(__file__), 'console_icons').capitalize().replace('\\', '/')

class Adapter(Base_Adapter):
    def Authorize(self) -> Base_Adapter.Authorization:
        return self.Authorization('Console', 'ConsoleBot_id', 1)
    
    class Formatter(Base_Adapter.Formatter):
        def encode(self, message: str) -> str:
            message = re.sub(r'<<IMAGE:(.*?)>>', r'[CONSOLE_IMAGE:\1]', message)
            message = re.sub(r'<<FILE:(.*?)>>', r'[CONSOLE_FILE:\1]', message)
            message = re.sub(r'<<AT:(.*?)>>', r'[CONSOLE_AT:\1]', message)
            return message
        
        def decode(self, message: str) -> str:
            message = re.sub(r'\[CONSOLE_IMAGE:(.*?)\]', r'<<IMAGE:\1>>', message)
            message =  re.sub(r'\[CONSOLE_FILE:(.*?)\]', r'<<FILE:\1>>', message)
            message =  re.sub(r'\[CONSOLE_AT:(.*?)\]', r'<<AT:\1>>', message)
            return message
    
    class API(Base_Adapter.API):
        def send_message(self, group_id: int, message: str) -> None:
            if group_id == 1919810:
                logger.chat(f'ConsoleBot: {message}')

        def send_private_message(self, user_id: int, message: str) -> None:
            if user_id == 114514:
                logger.chat(f'ConsoleBot(private): {message}')

        def get_user(self, user_id: int) -> User | None:
            if user_id == 114514:
                return User(user_id=user_id, user_avatar=ICONPATH + '/user.png', user_name='Console')
            else:
                return None
            
        def get_group(self, group_id: int) -> Group | None:
            if group_id == 1919810:
                return Group(group_id=group_id, group_avatar=ICONPATH + '/group.png', group_name='ConsoleGroup')
            else:
                return None
        
        def get_friends(self) -> list[User]:
            return [User(114514, user_avatar=ICONPATH + '/user.png', user_name='Console')]
        
        def get_group_list(self) -> list[Group]:
            return [Group(group_id=1919810, group_avatar=ICONPATH + '/group.png', group_name='ConsoleGroup')]

        def get_members(self, group_id: int) -> list[User] | None:
            if group_id == 1919810:
                return [User(114514, user_avatar=ICONPATH + '/user.png', user_name='Console')]
            else:
                return None
    class Listener(Base_Adapter.Listener):
            def listen(self, message_list: list) -> None:
                logger.success('Console Listener Started')
                try:
                    while self.STATUS:
                        message = input()
                        if message.startswith('private:'):
                            message_list.append(Message(config=self.config, message_id=str(time.time()), content=self.Formatter.decode(message[8:]), user=User(user_id=114514, user_avatar=ICONPATH + '/user.png', user_name='ConsoleUser'), private=True, respond_function=self.respond_private(114514)))
                        else:
                            message_list.append(Message(config=self.config, message_id=str(time.time()), content=self.Formatter.decode(message), user=User(user_id=114514, group=Group(1919810), user_avatar=ICONPATH + '/user.png', user_name='ConsoleUser'), private=False, respond_function=self.respond(1919810)))
                except (EOFError, KeyboardInterrupt):
                    logger.success('Console Listener Stopped')
                    exit(0)
                logger.success('Console Listener Stopped')
                exit(0)