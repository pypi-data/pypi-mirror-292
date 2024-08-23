# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  catlive-app-helper
# FileName:     gift.py
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


class UiDailyCheckInApi(DeviceApi):

    def get_signup_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/tv_signup"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_signup_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        signup_button_poco = self.get_signup_button(loop=loop, peroid=peroid, **kwargs)
        if signup_button_poco:
            signup_button_poco.click()
            return True
        return False

    def get_signup_submit_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/tv_ok"
        options = dict(d_type=d_type, name=name, text="好的")
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_signup_submit_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        signup_submit_button_poco = self.get_signup_submit_button(loop=loop, peroid=peroid, **kwargs)
        if signup_submit_button_poco:
            signup_submit_button_poco.click()
            return True
        return False

    def get_live_leave_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/live_leave_img"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_live_leave_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        live_leave_enter_poco = self.get_live_leave_enter(loop=loop, peroid=peroid, **kwargs)
        if live_leave_enter_poco:
            live_leave_enter_poco.click()
            return True
        return False

    def get_close_room_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/tx_close_room"
        options = dict(d_type=d_type, name=name, text="退出房间")
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_close_room_button(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        close_room_button_poco = self.get_close_room_button(loop=loop, peroid=peroid, **kwargs)
        if close_room_button_poco:
            close_room_button_poco.click()
            return True
        return False
