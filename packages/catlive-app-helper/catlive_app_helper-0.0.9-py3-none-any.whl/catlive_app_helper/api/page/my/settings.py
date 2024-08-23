# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  catlive-app-helper
# FileName:     settings.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/08/19
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from poco.proxy import UIObjectProxy
from airtest_helper.platform import ANDROID_PLATFORM
from catlive_app_helper.api.page.my.my import UiMyApi
from airtest_helper.libs.extend import get_poco_factory


class UiSettingsApi(UiMyApi):

    def get_settings_menu(self, menu_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "android.widget.TextView"
        options = dict(d_type=d_type, name=name, text=menu_name)
        return get_poco_factory(poco=self.poco, options=options, loop=loop, peroid=peroid, **kwargs)

    def touch_settings_menu(self, menu_name: str, loop: int = 20, peroid: float = 0.5, **kwargs) -> bool:
        settings_menu_poco = self.get_settings_menu(menu_name=menu_name, loop=loop, peroid=peroid, **kwargs)
        if settings_menu_poco:
            settings_menu_poco.click()
            return True
        return False
