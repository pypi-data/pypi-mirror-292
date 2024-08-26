import importlib
import threading
import os, time
import traceback
from typing import Callable
from io import StringIO
from faliceqbot import logger
from faliceqbot.matcher import Matcher
from faliceqbot.segments import Config, Message, Base_Adapter, Sender, Plugin, PluginList

class QBot:
    def __init__(self,
            adapter: str = 'console',
            token: str = '',
            wsbase: str = '',
            httpbase: str = '',
            prefix: str = '/',
            permission: dict[str, StringIO] = {},
            plugins: list[Plugin] = [],
            plugin_folder: str = '',
            breath: float = 0.1,
            delay: float = 0.1,
            log_to_console: bool = True,
            log_to_file: bool = False,
        ) -> None:
        """
        Falice's main class. Easy to use.

        :param adapter: Choose the adapter you want to use, such as 'console'.
        :param token: If your adapter need a token, you should put it here.
        :param wsbase: If your adapter need a websocket connection, you should put the link here.
        :param httpbase: If your adapter need a http link to request, you should put it here.
        :param prefix: The prefix of your command.
        :param permission: The permission dictionary for plugins. Stores permissions for special users as a dict[str, int] : {'<user_id>': <level>}
        :param plugins: Your plugins which you'd like to pass it directly in the parameter.
        :param plugin_folder: The folder where your plugins file are located.
        :param breath: Each time the bot dealed with current messages, it will sleep for a while.
        :param delay: When you respond to a message(by Message.respond), the bot will have to wait for a while before sending the message.
        :param log_to_console: Will print each message to console.
        :param log_to_file: Will save each message to a file.
        """
        self.config: Config = Config(token, wsbase, httpbase, prefix, permission, delay)
        adapter_name = adapter.lower()
        self.adapter: Base_Adapter = importlib.import_module(f'faliceqbot.adapters.{adapter_name}').Adapter(self.config)
        self.adapter.platform = adapter
        self.plugin_folder: str = plugin_folder
        self.breath: float = breath
        self.log_to_console: bool = log_to_console
        self.log_to_file: bool = log_to_file
        logger.runtime(f'Using adapter: {adapter_name}...')
        self.Formatter: Base_Adapter.Formatter = self.adapter.Formatter()
        self.API: Base_Adapter.API = self.adapter.API(self.adapter)
        self.Listener: Base_Adapter.Listener = self.adapter.Listener(self.adapter, self.Formatter, self.API)
        self.Sender: Sender = Sender(self.Formatter, self.API)
        self.matcher: Matcher
        
        self.MESSAGES: list[Message] = []
        self.PLUGINS: list[Plugin] = plugins
        for parameter_plugin in self.PLUGINS:
            logger.runtime(f'Loaded: {parameter_plugin}')
        self.log_files: dict = {}
        self.exceptions: list[tuple[Exception, str, float, str]] = []

        self.STATUS: bool = True

    def exception_catcher(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
                logger.debug(f'Finished Function: {func.__name__}')
            except Exception as e:
                self.exceptions.append((e, func.__name__, time.time(), traceback.format_exc()))
                logger.error(f'Error in Func: {e}')
                logger.error(f'{traceback.format_exc()}')
        return wrapper

    class BotFinishException(Exception): pass

    def run(self) -> None:
        """
        Run your bot: Start Listener, load plugins, and start responding to messages.
        """
        if self.log_to_file and not os.path.exists('logs'): os.mkdir('logs')
        threading.Thread(target=self.Listener.listen, args=(self.MESSAGES,)).start()
        if self.plugin_folder:
            plugins_folder: list = os.listdir(self.plugin_folder)
            for plugin_file_name in plugins_folder:
                if plugin_file_name.endswith('.py'):
                    try:
                        logger.runtime(f'Loading plugin {plugin_file_name}...')
                        plugin_file = importlib.import_module(f'plugins.{plugin_file_name[:-3]}')
                        plugin: Plugin = plugin_file.load()
                        self.PLUGINS.append(plugin)
                        logger.runtime(f'Loaded from file: {plugin}')
                    except AttributeError as e:
                        logger.error(f'Error loading plugin {plugin_file_name}: {e} ( May you have not write "load" function? )')
                    except Exception as e:
                        logger.error(f'Unknown Error loading plugin {plugin_file_name}: {e}')
        
        # StackTrace
        StackTrace = Plugin('StackTrace', '1.0', 'Falice', 'Track Exceptions', True)
        def stack_trace(msg: Message) -> None:
            args = message.get_args()
            if len(self.exceptions) == 0:
                msg.respond('No exceptions. Good job!')
                return
            if len(args) == 0:
                msg.respond('Usage: exception <last/count/list/clear/show>')
                return
            if args[0] == 'last':
                msg.respond(f'Last exception: {self.exceptions[-1][0]}')
            if args[0] == 'count':
                msg.respond(f'Number of exceptions: {len(self.exceptions)}')
            elif args[0] == 'list':
                msg.respond('Exceptions:\n' + '\n'.join([f'{i}. {self.exceptions[-i][0]}' for i in range(1, len(self.exceptions) + 1)]))
            elif args[0] == 'clear':
                if msg.get_permission() > 1:
                    self.exceptions = []
                    msg.respond('Exceptions cleared.')
            elif args[0] == 'show':
                if len(args) < 2:
                    msg.respond('Usage: exception show <index>')
                    return
                try:
                    index = int(args[1])
                    exceptiontuple = self.exceptions[-index]
                    msg.respond(f'An exception( {exceptiontuple[0]} ) occurred at function {exceptiontuple[1]}, at time {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(exceptiontuple[2]))}.\n{exceptiontuple[3]}')
                except ValueError:
                    msg.respond('Index must be a number.')
                except IndexError:
                    msg.respond(f'Index out of range ( Should be between 1 and {len(self.exceptions)} but {args[1]} was given )')
        StackTrace.onCommand(stack_trace, 'exception')
        self.PLUGINS.append(StackTrace)

        self.matcher = Matcher(PluginList(self.PLUGINS))
        try:
            while self.STATUS:
                if self.MESSAGES:
                    message: Message = self.MESSAGES.pop(0)
                    message.Sender = self.Sender
                    message.PLuginList = self.matcher.plugin_list
                    if self.log_to_console: logger.chat('{} in {} : {}'.format(message.user.id, 'Private' if message.private else message.group_id, message.content))
                    if self.log_to_file:
                        chat_name = f'Private{message.user.id}' if message.private else f'Group{message.group_id}'
                        try:
                            self.log_files[chat_name].write(f'\n{message.user.id} : {message.content}')
                        except KeyError:
                            self.log_files[chat_name] = open(f'logs/{chat_name}.log', 'a', encoding='utf-8')
                            try:
                                self.log_files[chat_name].write(f'Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}')
                                self.log_files[chat_name].write(f'\n{message.user.id} : {message.content}')
                            except Exception as e:
                                logger.error(f'Error writing to log file: {e}')
                        except Exception as e:
                            logger.error(f'Error writing to log file: {e}')
                    functions = self.matcher.match(message)
                    for function in functions:
                        threading.Thread(target=self.exception_catcher(func=function), args=(message,)).start()
                time.sleep(self.breath)
            raise self.BotFinishException()
        except self.BotFinishException:
            logger.info('Bot stopped, exiting...')
            exit(0)
        except KeyboardInterrupt:
            logger.info('Ctrl+C pressed, exiting...')
            exit(0)
        except Exception as e:
            logger.error('Error: {}'.format(e))
            logger.error('{}'.format(traceback.format_exc()))
        finally:
            self.Listener.STATUS = False
            for file in self.log_files.values():
                file.write(f'\nEnd Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n\n')
                file.close()