# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  catlive-app-helper
# FileName:     chat.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/08/19
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from poco.proxy import UIObjectProxy
from airtest_helper.core import DeviceProxy
from airtest_helper.platform import ANDROID_PLATFORM
from airtest_helper.libs.extend import get_poco_factory
from catlive_app_helper.api.page.portal import UiRoomPortalApi, UiLivePortalApi, UiMessagePortalApi


class UiHallChatApi(UiRoomPortalApi, UiLivePortalApi):

    def __init__(self, device: DeviceProxy):
        UiRoomPortalApi.__init__(self, device)
        UiLivePortalApi.__init__(self, device)

    def get_hall_chat_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/iv_anchor_im"
        options = dict(d_type=d_type, name=name, text="来聊聊天...")
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_hall_chat_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        hall_chat_enter_poco = self.get_hall_chat_enter(loop=loop, peroid=peroid, **kwargs)
        if hall_chat_enter_poco:
            hall_chat_enter_poco.click()
            return True
        return False

    def get_hall_input_box(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.EditText"
            name = "com.catlive.app:id/msg_live_send_edt_input"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def input_hall_chat_content(self, content: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        input_box_poco = self.get_hall_input_box(loop=loop, peroid=peroid, **kwargs)
        if input_box_poco:
            input_box_poco.click()
            input_box_poco.set_text(content)
            return True
        return False

    def get_send_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/msg_live_send_tv_send"
        options = dict(d_type=d_type, name=name, text="发送")
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_send_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        button_poco = self.get_send_button(loop=loop, peroid=peroid, **kwargs)
        if button_poco:
            button_poco.click()
            return True
        return False


class UiPrivateChatApi(UiMessagePortalApi):
    pass
