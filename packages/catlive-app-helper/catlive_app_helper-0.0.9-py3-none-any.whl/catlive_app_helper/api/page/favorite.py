# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  catlive-app-helper
# FileName:     favorite.py
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
from catlive_app_helper.api.page.portal import UiRoomPortalApi, UiLivePortalApi


class UiFavoriteApi(UiRoomPortalApi, UiLivePortalApi):

    def __init__(self, device: DeviceProxy):
        UiRoomPortalApi.__init__(self, device)
        UiLivePortalApi.__init__(self, device)

    def get_favorite_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/ivHomeTopHeart"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_favorite_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        favorites_enter_poco = self.get_favorite_enter(loop=loop, peroid=peroid, **kwargs)
        if favorites_enter_poco:
            favorites_enter_poco.click()
            return True
        return False

    def get_favorite_room_by_name(self, room_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/tvLiveName"
        options = dict(d_type=d_type, name=name, text=room_name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_favorite_room(self, room_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        room_poco = self.get_favorite_room_by_name(room_name=room_name, loop=loop, peroid=peroid, **kwargs)
        if room_poco:
            room_poco.click()
            return True
        return False
