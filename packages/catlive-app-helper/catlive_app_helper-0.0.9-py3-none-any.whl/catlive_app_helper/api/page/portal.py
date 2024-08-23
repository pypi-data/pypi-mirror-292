# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  catlive-app-helper
# FileName:     portal.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/08/19
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from poco.proxy import UIObjectProxy
from airtest_helper.core import DeviceApi
from airtest_helper.platform import ANDROID_PLATFORM
from airtest_helper.libs.extend import get_poco_factory


class UiMyPortalApi(DeviceApi):

    def get_my(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/ivTabItemIcon4"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_my(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        my_poco = self.get_my(loop=loop, peroid=peroid, **kwargs)
        if my_poco:
            my_poco.click()
            return True
        return False


class UiLivePortalApi(DeviceApi):

    def get_live(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/ivTabItemIcon1"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_live(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        live_poco = self.get_live(loop=loop, peroid=peroid, **kwargs)
        if live_poco:
            live_poco.click()
            return True
        return False


class UiRoomPortalApi(DeviceApi):

    def get_room(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/ivTabItemIcon5"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_room(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        room_poco = self.get_room(loop=loop, peroid=peroid, **kwargs)
        if room_poco:
            room_poco.click()
            return True
        return False


class UiSquarePortalApi(DeviceApi):

    def get_square(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/ivTabItemIcon2"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_square(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        my_poco = self.get_square(loop=loop, peroid=peroid, **kwargs)
        if my_poco:
            my_poco.click()
            return True
        return False


class UiMessagePortalApi(DeviceApi):

    def get_message(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/ivTabItemIcon3"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_message(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        my_poco = self.get_message(loop=loop, peroid=peroid, **kwargs)
        if my_poco:
            my_poco.click()
            return True
        return False
