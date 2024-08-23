# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  catlive-app-helper
# FileName:     emoji.py
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
from catlive_app_helper.api.page.portal import UiLivePortalApi, UiRoomPortalApi, UiMessagePortalApi


class UiHallEmojiApi(UiRoomPortalApi, UiLivePortalApi):

    def __init__(self, device: DeviceProxy):
        UiRoomPortalApi.__init__(self, device)
        UiLivePortalApi.__init__(self, device)

    def get_hall_emoji_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/live_pub_expression"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_hall_emoji_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        emoji_enter_poco = self.get_hall_emoji_enter(loop=loop, peroid=peroid, **kwargs)
        if emoji_enter_poco:
            emoji_enter_poco.click()
            return True
        return False

    def get_hall_emoji(self, emoji_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/tv_name"
        options = dict(d_type=d_type, name=name, text=emoji_name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_hall_emoji(self, emoji_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        emoji_poco = self.get_hall_emoji(emoji_name=emoji_name, loop=loop, peroid=peroid, **kwargs)
        if emoji_poco:
            emoji_poco.click()
            return True
        return False

    def get_hall_emoji_icon(self, emoji_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/tv_name"
        options = dict(d_type=d_type, name=name, text=emoji_name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_hall_emoji_icon(self, emoji_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        hall_emoji_icon_poco = self.get_hall_emoji_icon(emoji_name=emoji_name, loop=loop, peroid=peroid, **kwargs)
        if hall_emoji_icon_poco:
            hall_emoji_icon_poco.click()
            return True
        return False


class UiPrivateChatEojiApi(UiMessagePortalApi):
    pass
