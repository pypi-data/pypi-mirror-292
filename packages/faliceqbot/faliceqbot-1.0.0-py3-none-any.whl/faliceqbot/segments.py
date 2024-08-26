from faliceqbot import logger
from typing import Callable, Union, Any, Optional
import re
import time


class Config:
    def __init__(self,
        token: str = '',
        wsbase: str = '',
        httpbase: str = '',
        prefix: str = '/',
        permission: dict = {},
        delay: float = 0.1
    ) -> None:
        self.token: str = token
        self.wsbase: str = wsbase
        self.httpbase: str = httpbase
        self.prefix: str = prefix
        self.permission: dict = permission
        self.delay: float = delay


class Group:
    def __init__(self, group_id: int, group_avatar: str = '', group_name: str = '') -> None:
        self.id: int = group_id
        self.avatar: str = group_avatar
        self.name: str = group_name


class User:
    def __init__(self, user_id: int, group: Group = Group(-1), user_avatar: str = '', user_name: str = '', is_bot: bool = False) -> None:
        self.id: int = user_id
        self.group: Group = group
        self.avatar: str = user_avatar
        self.name: str = user_name
        self.is_bot: bool = is_bot


class Base_Adapter:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.authorization = self.Authorize()
        self.platform = 'Base'
    
    class Authorization:
        def __init__(self, platform: str, bot_id: str, bot_status: int) -> None:
            self.platform = platform
            self.bot_id = bot_id
            self.bot_status = bot_status

    def Authorize(self) -> Authorization:
        return self.Authorization('Base', 'Base_id', 0)

    class Formatter:
        def encode(self, message: str) -> str:
            return f"[Base encode]: {message}"
        
        def decode(self, message: str) -> str:
            return f'[Base decode]: {message}'
    
    class API:
        def __init__(self, adapter) -> None:
            self.authorization = adapter.authorization
            self.config = adapter.config
        
        def send_message(self, group_id: int, message: str) -> None:
            ...
        
        def send_private_message(self, user_id: int, message: str) -> None:
            ...

        def get_user(self, user_id: int) -> User | None:
            ...

        def get_group(self, group_id: int) -> Group | None:
            ...

        def get_friends(self) -> list[User] | None:
            ...

        def get_group_list(self) -> list[Group] | None:
            ...
        
        def get_members(self, group_id: int) -> list[User] | None:
            ...
    
    class Listener:
        def __init__(self, adapter, Formatter, API) -> None:
            self.authorization = adapter.authorization
            self.config = adapter.config
            self.Formatter = Formatter
            self.API = API
            self.STATUS = True
            
        def listen(self, message_list: list) -> None:
            logger.success('Base Listener Started')
            while self.STATUS:
                ...
            logger.success('Base Listener Stopped')
        
        def respond(self, group_id: int) -> Callable[[str], None]:
            def wrapper(message: str) -> None:
                time.sleep(self.config.delay)
                self.API.send_message(group_id, self.Formatter.encode(message))
            return wrapper
        
        def respond_private(self, user_id: int) -> Callable[[str], None]:
            def wrapper(message: str) -> None:
                self.API.send_private_message(user_id, self.Formatter.encode(message))
            return wrapper


class Sender:
    def __init__(self, Formatter: Base_Adapter.Formatter, API: Base_Adapter.API) -> None:
        self.Formatter: Base_Adapter.Formatter = Formatter
        self.API: Base_Adapter.API = API
    
    def image(self, url: str) -> str:
        return '<<IMAGE:{}>>'.format(url)
    
    def file(self, url: str) -> str:
        return '<<FILE:{}>>'.format(url)
    
    def at(self, user_id: int) -> str:
        return '<<AT:{}>>'.format(user_id)
    
    def lis(self, items: list[str], name: str = '', dot: str = ' - ', colon: str = ':') -> str:
        result = f'{name}{colon}\n' if name else ''
        for item in items:
            result += f'{dot}{item}\n'
        return result.strip('\n').strip(' ')

    def send_message(self, group_id: int, message: str) -> None:
        self.API.send_message(group_id, self.Formatter.encode(message).strip('\n').strip(' '))
    
    def send_private_message(self, user_id: int, message: str) -> None:
        self.API.send_private_message(user_id, self.Formatter.encode(message).strip('\n').strip(' '))
    
    def get_user(self, user_id: int) -> User | None:
        return self.API.get_user(user_id)
    
    def get_group(self, group_id: int) -> Group | None:
        return self.API.get_group(group_id)
    
    def get_friends(self) -> list[User] | None:
        return self.API.get_friends()
    
    def get_groups(self) -> list[Group] | None:
        return self.API.get_group_list()

    def get_members(self, group_id: int) -> list[User] | None:
        return self.API.get_members(group_id)


class Message:
    def __init__(self, config: Config, message_id: str, content: str, user: User, private: bool, respond_function: Optional[Callable] = None) -> None:
        self.config = config
        self.id = message_id
        self.content: str = content
        self.private: bool = private
        self.user: User = user
        self.group_id: int = self.user.group.id
        self._respond: Callable[[str], None] = respond_function if respond_function is not None else self._empty_respond
        self.tag: Optional[str] = None
        self.Sender: Sender
        self.PLuginList: list[Plugin] = []
    
    def _empty_respond(self, *args, **kwargs) -> None:
        logger.fail("Response function is not defined (may be a service) but you tried to pass a content to it!")

    def respond(self, content: str) -> None:
        self._respond((content if self.tag is None else '[{}]\n{}'.format(self.tag, content)).strip('\n').strip(' '))
    
    def reply(self, content: str) -> None:
        if not self.private:
            content = f'<<AT:{self.user.id}>> ' + content
        self.respond(content)

    def get_permission(self) -> int:
        return self.config.permission[str(self.user.id)] if str(self.user.id) in self.config.permission else 0

    def get_text(self) -> str:
        return self.content
    
    def get_command(self) -> str:
        return self.content.split(" ")[0][len(self.config.prefix):]

    def get_args(self) -> list:
        args = self.content.split(" ")
        args.pop(0)
        args = [arg.strip(' ') for arg in args if arg.strip(' ')]
        return args
    
    def get_args_string(self) -> str:
        return " ".join(self.get_args())
    
    def get_images(self) -> list:
        return re.findall(r'<<IMAGE:(.*?)>>', self.content)
    
    def get_files(self) -> list:
        return re.findall(r'<<FILE:(.*?)>>', self.content)
    
    def get_ats(self) -> list:
        return re.findall(r'<<AT:(.*?)>>', self.content)


PluginFuncType = Callable[[Message], None]
class PluginTriggerType:
    def __init__(self, function: PluginFuncType, content: str, permission: int, priority: int, block: bool) -> None:
        self.function: PluginFuncType = function
        self.content: str = content
        self.permission: int = permission
        self.priority: int = priority
        self.block: bool = block
PluginTriggerListType = list[PluginTriggerType]


class Plugin:
    def __init__(self, name: str, version: str | None = None, author: str | None = None, description: str | None = None, load_on_launch: bool = True) -> None:
        """
        To make a plugin, you must inherit this class and make a function named `load` which returns the inherited class in your .py file.

        :param name: The name of your plugin, doesn't need to be the same as the file name. (It's important)
        :param version: The version of your plugin. (Not important)
        :param author: The author of your plugin. (Not important)
        :param description: The description of your plugin. (Sometimes important)
        :param load_on_launch: Bot will always load your Plugin class. But if you set this to False, you need to /load you plugin to enable it. (Simply, enable or disable whole plugin at first.)
        """
        self.name: str = name
        self.version: str | None = version
        self.author: str | None = author
        self.description: str | None = description
        self.enable: bool = load_on_launch
        self.disabled_list = self.Disabled_list()

        self.onMessageList: PluginTriggerListType = []
        self.onCommandList: PluginTriggerListType = []
        self.onStartsWithList: PluginTriggerListType = []
        self.onEndsWithList: PluginTriggerListType = []
        self.onKeywordsList: PluginTriggerListType = []
        self.onFullMatchList: PluginTriggerListType = []

    def __str__(self) -> str:
        return self.name + '{' + '{}{}{}{}{}{}'.format(
            f'onMessage:{[i.content for i in self.onMessageList]};' if self.onMessageList else '',
            f'onCommand:{[i.content for i in self.onCommandList]};' if self.onCommandList else '',
            f'onStartsWith:{[i.content for i in self.onStartsWithList]}; ' if self.onStartsWithList else '',
            f'onEndsWith:{[i.content for i in self.onEndsWithList]};' if self.onEndsWithList else '',
            f'onKeywords:{[i.content for i in self.onKeywordsList]};' if self.onKeywordsList else '',
            f'onFullMatch:{[i.content for i in self.onFullMatchList]};' if self.onFullMatchList else ''
        ) + '}'

    class Disabled_list:
        def __init__(self) -> None:
            self.friends: list[int] = []
            self.groups: list[int] = []
    
    def get_disabled(self, user: User, private: bool) -> bool:
        if private:
            if user.id in self.disabled_list.friends:
                return True
            else:
                return False
        else:
            if user.group.id in self.disabled_list.groups:
                return True
            else:
                return False

    def onMessage(self, function: PluginFuncType, permission: int = 0, priority: int = 0) -> None:
        self.onMessageList.append(PluginTriggerType(function, 'on_message', permission, priority, False))
    
    def _ensure_list(self, value: Any) -> list:
        if isinstance(value, str):
            return [value]
        elif isinstance(value, list):
            return value
        else:
            raise TypeError(f"Expected a list or a string, got {type(value)}")

    def onCommand(self, function: PluginFuncType, commands: Union[list[str], str], permission: int = 0, priority: int = 0, block: bool = False) -> None:
        """
        Load a trigger responds to a message like '/test' (The prefix depends on you.)
        """
        for content in self._ensure_list(commands):
            self.onCommandList.append(PluginTriggerType(function, content, permission, priority, block))
    
    def onStartsWith(self, function: PluginFuncType, commands: Union[list[str], str], permission: int = 0, priority: int = 0, block: bool = False) -> None:
        """
        Load a trigger responds to a message like 'testing before using is a good habit.'

        """
        for content in self._ensure_list(commands):
            self.onStartsWithList.append(PluginTriggerType(function, content, permission, priority, block))
    
    def onEndsWith(self, function: PluginFuncType, commands: Union[list[str], str], permission: int = 0, priority: int = 0, block: bool = False) -> None:
        """
        Load a trigger respond to a message like 'you even have NOT had a test'
        """
        for content in self._ensure_list(commands):
            self.onEndsWithList.append(PluginTriggerType(function, content, permission, priority, block))
    
    def onKeywords(self, function: PluginFuncType, commands: Union[list[str], str], permission: int = 0, priority: int = 0, block: bool = False) -> None:
        """
        Load a trigger respond to a message like 'if i type "test" in my message...'
        """
        for content in self._ensure_list(commands):
            self.onKeywordsList.append(PluginTriggerType(function, content, permission, priority, block))
    
    def onFullMatch(self, function: PluginFuncType, commands: Union[list[str], str], permission: int = 0, priority: int = 0, block: bool = False) -> None:
        """
        Load a trigger respond to a message equals to 'test'.
        """
        for content in self._ensure_list(commands):
            self.onFullMatchList.append(PluginTriggerType(function, content, permission, priority, block))


class PluginList:
    def __init__(self, plugin_list: list[Plugin]) -> None:
        self.plugin_list: list[Plugin] = plugin_list
        PluginManager = Plugin('PluginManager','1.0.0','Falsw','Manage Plugins by enable or disable.')
        PluginManager.onCommand(function=self.plugin_manager, commands=['plugin','pl'], permission=3, priority=10, block=True)
        self.plugin_list.append(PluginManager)
    
    def plugin_status(self, message: Message, act: bool, is_load: bool):
        if args := message.get_args()[1:]:
            abled: list = []
            for i in range(len(self.plugin_list)):
                if self.plugin_list[i].name in args:
                    abled.append(self.plugin_list[i].name)
                    args = [arg for arg in args if arg != self.plugin_list[i].name]
                    if is_load:
                        self.plugin_list[i].enable = act
                    else:
                        if message.private:
                            if act:
                                if message.user.id in self.plugin_list[i].disabled_list.friends:
                                    self.plugin_list[i].disabled_list.friends.remove(message.user.id)
                            else:
                                if message.user.id not in self.plugin_list[i].disabled_list.friends:
                                    self.plugin_list[i].disabled_list.friends.append(message.user.id)
                        else:
                            if act:
                                if message.group_id in self.plugin_list[i].disabled_list.groups:
                                    self.plugin_list[i].disabled_list.groups.remove(message.group_id)
                            else:
                                if message.group_id not in self.plugin_list[i].disabled_list.groups:
                                    self.plugin_list[i].disabled_list.groups.append(message.group_id)
            result = ''
            if abled:
                for plugin_name in abled:
                    result += (f'Enabled {plugin_name}\n' if act else f'Disabled {plugin_name}\n') if is_load else (f'Pardoned {plugin_name} for the chat\n' if act else f'Baned {plugin_name} for the chat\n')
            if args:
                for plugin_name in args:
                    result += f'Could Not Find {plugin_name}\n'
            message.respond(result.strip('\n'))
    
    def plugin_manager(self, message: Message):
        args = message.get_args()
        match len(args):
            case 0:
                show_plugin = 'Plugins'
                for plugin in self.plugin_list:
                    if plugin.enable and not plugin.get_disabled(message.user, message.private):
                        show_plugin += f'\n - {plugin.name}'
                message.respond(show_plugin)
            case 1:
                pass
            case _:
                match args[0]:
                    case 'enable':
                        message.respond('You are about to enable a plugin. Use "Enable" instead of "enable".')
                    case 'disable':
                        message.respond('You are about to disable a plugin. Use "Disable" instead of "disable".')
                    case 'Enable':
                        self.plugin_status(message, True, True)
                    case 'Disable':
                        self.plugin_status(message, False, True)
                    case 'pardon':
                        self.plugin_status(message, True, False)
                    case 'ban':
                        self.plugin_status(message, False, False)


