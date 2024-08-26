from faliceqbot.segments import Message, Plugin, PluginList
from faliceqbot.segments import PluginFuncType, PluginTriggerListType

class Matcher:
    def __init__(self, PluginList: PluginList) -> None:
        self.PLuginList = PluginList
        self.plugin_list: list[Plugin] = []
        self.on_message_list: PluginTriggerListType = []
        self.on_command_list: PluginTriggerListType = []
        self.on_starts_with_list: PluginTriggerListType = []
        self.on_ends_with_list: PluginTriggerListType = []
        self.on_keywords_list: PluginTriggerListType = []
        self.on_full_match_list: PluginTriggerListType = []

        self.sorted_list: PluginTriggerListType = []
        self.function_list: list[PluginFuncType] = []

    def _match_content(self, message: Message) -> None:
        self.on_command_list = [plugin_trigger for plugin_trigger in self.on_command_list if plugin_trigger.content == message.get_command()] if self.on_command_list else []
        self.on_starts_with_list = [plugin_trigger for plugin_trigger in self.on_starts_with_list if message.get_text().startswith(plugin_trigger.content)] if self.on_starts_with_list else []
        self.on_ends_with_list = [plugin_trigger for plugin_trigger in self.on_ends_with_list if message.get_text().endswith(plugin_trigger.content)] if self.on_ends_with_list else []
        self.on_keywords_list = [plugin_trigger for plugin_trigger in self.on_keywords_list if plugin_trigger.content in message.get_text()] if self.on_keywords_list else []
        self.on_full_match_list = [plugin_trigger for plugin_trigger in self.on_full_match_list if message.get_text() == plugin_trigger.content] if self.on_full_match_list else []
    
    def _match_permission_line(self, on_list: PluginTriggerListType, message: Message) -> PluginTriggerListType:
        return [plugin_trigger for plugin_trigger in on_list if int(plugin_trigger.permission) <= message.get_permission()]

    def _match_permission(self, message: Message) -> None:
        self.on_message_list = self._match_permission_line(on_list=self.on_message_list, message=message) if self.on_message_list else []
        self.on_command_list = self._match_permission_line(on_list=self.on_command_list, message=message) if self.on_command_list else []
        self.on_starts_with_list = self._match_permission_line(on_list=self.on_starts_with_list, message=message) if self.on_starts_with_list else []
        self.on_ends_with_list = self._match_permission_line(on_list=self.on_ends_with_list, message=message) if self.on_ends_with_list else []
        self.on_keywords_list = self._match_permission_line(on_list=self.on_keywords_list, message=message) if self.on_keywords_list else []
        self.on_full_match_list = self._match_permission_line(on_list=self.on_full_match_list, message=message) if self.on_full_match_list else []

    def _sort(self) -> None:
        self.sorted_list = [
            *self.on_message_list,
            *self.on_command_list,
            *self.on_starts_with_list,
            *self.on_ends_with_list,
            *self.on_keywords_list,
            *self.on_full_match_list
        ]
        self.sorted_list.sort(key = lambda x: (-x.priority, -x.permission))
        

    def _functions(self) -> None:
        self.function_list = []
        if self.sorted_list:
            for plugin_trigger in self.sorted_list:
                self.function_list.append(plugin_trigger.function)
                if plugin_trigger.block:
                    break


    def match(self, message: Message) -> list[PluginFuncType]:
        self.plugin_list = self.PLuginList.plugin_list
        self.on_message_list = [plugin_trigger for plugin in self.plugin_list for plugin_trigger in plugin.onMessageList if plugin.enable and not plugin.get_disabled(message.user, message.private)]
        self.on_command_list = [plugin_trigger for plugin in self.plugin_list for plugin_trigger in plugin.onCommandList if plugin.enable and not plugin.get_disabled(message.user, message.private)]
        self.on_starts_with_list = [plugin_trigger for plugin in self.plugin_list for plugin_trigger in plugin.onStartsWithList if plugin.enable and not plugin.get_disabled(message.user, message.private)]
        self.on_ends_with_list = [plugin_trigger for plugin in self.plugin_list for plugin_trigger in plugin.onEndsWithList if plugin.enable and not plugin.get_disabled(message.user, message.private)]
        self.on_keywords_list = [plugin_trigger for plugin in self.plugin_list for plugin_trigger in plugin.onKeywordsList if plugin.enable and not plugin.get_disabled(message.user, message.private)]
        self.on_full_match_list = [plugin_trigger for plugin in self.plugin_list for plugin_trigger in plugin.onFullMatchList if plugin.enable and not plugin.get_disabled(message.user, message.private)]

        self._match_content(message=message)
        self._match_permission(message=message)
        self._sort()
        self._functions()
        return self.function_list