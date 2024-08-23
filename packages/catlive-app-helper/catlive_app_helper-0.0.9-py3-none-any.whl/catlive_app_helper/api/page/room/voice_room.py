# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  catlive-app-helper
# FileName:     voice_room.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/08/19
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from poco.proxy import UIObjectProxy
from airtest_helper.platform import ANDROID_PLATFORM
from airtest_helper.libs.extend import get_poco_factory
from catlive_app_helper.api.page.portal import UiRoomPortalApi


class UiVoiceRoomApi(UiRoomPortalApi):

    def get_randomly_idle_seat(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/addImg"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_randomly_idle_seat(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        idle_seat_poco = self.get_randomly_idle_seat(loop=loop, peroid=peroid, **kwargs)
        if idle_seat_poco:
            idle_seat_poco.click()
            return True
        return False

    def get_three_point_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.ImageView"
            name = "com.catlive.app:id/live_leave_img"
        options = dict(d_type=d_type, name=name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_three_point_enter(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        three_point_enter_poco = self.get_three_point_enter(loop=loop, peroid=peroid, **kwargs)
        if three_point_enter_poco:
            three_point_enter_poco.click()
            return True
        return False

    def get_leave_voice_room(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = name = "android.widget.TextView"
        options = dict(d_type=d_type, name=name, text="退出房间")
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_leave_voice_room(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        leave_voice_room_poco = self.get_leave_voice_room(loop=loop, peroid=peroid, **kwargs)
        if leave_voice_room_poco:
            leave_voice_room_poco.click()
            return True
        return False

    def get_voice_room_id(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> int:
        d_type = name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/tvShortId"
        options = dict(d_type=d_type, name=name)
        poco_proxy = get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)
        if poco_proxy:
            text = poco_proxy.get_text().strip()
            return int(text.replace("ID:", ""))
        return 0

    def get_user_msc_seat_number(self, uname: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/setNameTv"
        options = dict(d_type=d_type, name=name, text=uname)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_user_msc_seat_number(self, uname: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        seat_number_poco = self.get_user_msc_seat_number(uname=uname, loop=loop, peroid=peroid, **kwargs)
        if seat_number_poco:
            seat_number_poco.click()
            return True
        return False

    def get_off_msc_menu(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/valueTv"
        options = dict(d_type=d_type, name=name, text="下麦旁听")
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_off_msc_menu(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        off_msc_poco = self.get_off_msc_menu(loop=loop, peroid=peroid, **kwargs)
        if off_msc_poco:
            off_msc_poco.click()
            return True
        return False

    def get_on_msc_menu(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.catlive.app:id/valueTv"
        options = dict(d_type=d_type, name=name, text="上麦")
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_on_msc_menu(self, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        on_msc_poco = self.get_on_msc_menu(loop=loop, peroid=peroid, **kwargs)
        if on_msc_poco:
            on_msc_poco.click()
            return True
        return False
