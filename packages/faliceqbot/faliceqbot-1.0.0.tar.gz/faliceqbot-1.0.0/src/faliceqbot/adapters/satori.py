"""
Adapter in satori
"""
from faliceqbot import logger
from faliceqbot.segments import Group, User, Message, Base_Adapter
import re
import requests
import threading, time
import json
from websocket import WebSocketApp, WebSocket

class Adapter(Base_Adapter):
    def Authorize(self) -> Base_Adapter.Authorization:
        def on_message(ws: WebSocket, str_message: str) -> None:
            message: dict = json.loads(str_message)
            op: int = message['op']
            if op == 4:
                body = message['body']['logins'][0]
                platform = body['platform']
                id = body['user']['id']
                status = body['status']
                ws.login = self.Authorization(platform, id, status) # type: ignore
                logger.success('Satori Authorizer Authorized {} - {}({})'.format(platform, id, status))
                ws.close()
            else:
                logger.fail('Satori Authorizer received wrong opcode {}'.format(op))
        
        def on_open(ws: WebSocket) -> None:
            token = self.config.token
            IDENTIFY = {
                "op": 3,
                "body": {
                    "token": token
                }
            }
            ws.send(json.dumps(IDENTIFY, ensure_ascii=False))
            
        authorizer = WebSocketApp(
            url=self.config.wsbase.replace(' ', '').strip('/'),
            on_open=on_open,
            on_message=on_message
        )
        authorizer.run_forever()
        return authorizer.login # type: ignore
    
    class Formatter(Base_Adapter.Formatter):
        def encode(self, message: str) -> str:
            message = re.sub(r'<<IMAGE:(.*?)>>', r'<img src="\1"/>', message)
            message = re.sub(r'<<FILE:(.*?)>>', r'<file src="\1"/>', message)
            message = re.sub(r'<<AT:(.*?)>>', r'<at id="\1"/>', message)
            message.replace('&', '&amp;').replace('"', '&quot;')
            message.replace('<', '&lt;').replace('>', '&gt;')
            return message
    
        def decode(self, message: str) -> str:
            message = re.sub(r'<img src="(.*?)"/>', r'<<IMAGE:\1>>', message)
            message = re.sub(r'<file src="(.*?)"/>', r'<<FILE:\1>>', message)
            message = re.sub(r'<at id="(.*?)"/>', r'<<AT:\1>>', message)
            return message
    
    class API(Base_Adapter.API):
        def _post(self, api: str, data: dict) -> dict:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.config.token,
                "X-Platform": self.authorization.platform,
                "X-Self-ID": self.authorization.bot_id
            }
            return {
                'body': requests.post(self.config.httpbase.replace(' ', '').strip('/') + '/' + api, json=data, headers=headers).json()
            }

        def send_message(self, group_id: int, message: str) -> None:
            self._post('message.create', {
                'channel_id': str(group_id),
                'content': message
            })

        def send_private_message(self, user_id: int, message: str) -> None:
            self._post('message.create', {
                'channel_id': f'private:{str(user_id)}',
                'content': message
            })
        
        def get_user(self, user_id: int) -> User:
            user: dict = self._post('user.get', {
                'user_id': str(user_id)
            })['body']
            return User(user_id=int(user['id']), user_avatar=user['avatar'])
        
        def get_group(self, group_id: int) -> Group:
            group: dict = self._post('channel.get', {
                'channel_id': str(group_id)
            })['body']
            return Group(group_id=int(group['id']), group_avatar=group['avatar'])
        
        def get_friends(self) -> list[User]:
            first_list: dict = self._post('user.list', {})['body']
            result_list: list = first_list['data']
            while 'next' in first_list:
                first_list = self._post('user.list', {
                    'next': first_list['next']
                })['body']
                result_list += first_list['data']
            return [User(user_id=int(user['id']), user_avatar=user['avatar'], user_name=user['name'], is_bot=bool(user['is_bot'])) for user in result_list]
        
        def get_group_list(self) -> list[Group]:
            first_list: dict = self._post('guild.list', {})['body']
            result_list: list = first_list['data']
            while 'next' in first_list:
                first_list = self._post('guild.list', {
                    'next': first_list['next']
                })['body']
                result_list += first_list['data']
            return [Group(group_id=int(group['id']), group_avatar=group['avatar'], group_name=group['name']) for group in result_list]
        
        def get_members(self, group_id: int) -> list[User]:
            first_list: dict = self._post('guild.member.list', {
                'guild_id': str(group_id)
            })['body']
            result_list: list = first_list['data']
            while 'next' in first_list:
                first_list = self._post('guild.member.list', {
                    'guild_id': str(group_id),
                    'next': first_list['next']
                })['body']
                result_list += first_list['data']
            return [User(user_id=guild_member['user']['id'], user_avatar=guild_member['user']['avatar']) for guild_member in result_list]
    
    class Listener(Base_Adapter.Listener):
        def listen(self, message_list: list) -> None:
            def on_open(ws: WebSocketApp):
                INDENTIFY = {
                    "op": 3,
                    "body": {
                        "token": self.config.token
                    }
                }
                ws.pinger = None
                ws.send(json.dumps(INDENTIFY, ensure_ascii=False))
            
            def on_message(ws: WebSocketApp, origin_message: str):
                message: dict = json.loads(origin_message)
                op: int = message['op']
                match op:
                    case 4:
                        logger.success('Satori Listener Started')
                        class pinger:
                            def __init__(self, ws: WebSocketApp) -> None:
                                self.ws = ws
                                self.status = True
                                threading.Thread(target=self.ping).start()

                            def ping(self):
                                while self.status:
                                    time.sleep(10)
                                    self.ws.send(json.dumps({'op': 1}))
                        ws.pinger = pinger(ws)
                        ws.keep_running = True
                    case 0:
                        try:
                            message = message['body']
                            timestamp: str = message['timestamp']
                            id: str = message['message']['id']
                            content: str = message['message']['content']
                            user: User
                            match message['channel']['type']:
                                case 0:
                                    group: Group = Group(group_id=int(message['guild']['id']), group_avatar=message['guild']['avatar'], group_name=message['guild']['name'])
                                    user = User(user_id=int(message["user"]["id"]), group=group, user_avatar=message["user"]["avatar"], user_name=message["user"]["name"] if 'name' in message["user"] else 'Unknow')
                                    message_list.append(Message(config=self.config, message_id=id, content=content, user=user, private=False, respond_function=self.respond(group.id)))
                                case 1:
                                    user = User(user_id=int(message["user"]["id"]), user_avatar=message["user"]["avatar"], user_name=message["user"]["name"] if 'name' in message["user"] else 'Unknow')
                                    message_list.append(Message(config=self.config, message_id=id, content=content, user=user, private=True, respond_function=self.respond_private(user.id)))
                                case _:
                                    logger.fail('Satori Listener unknown channel type: {}'.format(message['channel']['type']))
                        except Exception as e:
                            logger.fail(f'Satori Listener message parse error: {e}')

            def on_error(ws: WebSocketApp, error: Exception):
                logger.error(f'Satori Listener disconnected with error: {error}')
                ws.keep_running = False
                ws.pinger.status = False
            
            def on_close(ws: WebSocketApp, code: int, msg: str):
                logger.error(f'Satori Listener disconnected with code: {code} and message: {msg}')
                ws.keep_running = False
                ws.pinger.status = False

            SatoriListener = WebSocketApp(
                url=self.config.wsbase,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            while self.STATUS:
                logger.debug('Satori Listener is Trying to Connect...')
                SatoriListener.run_forever()
                time.sleep(5)
            SatoriListener.close()
            logger.success('Satori Listener Disconnected.')