# BiliBiliHelper Python Version
# Copy right (c) 2019-2020 TheWanderingCoel
# 该代码实现了领取每日任务的功能
# 代码根据metowolf大佬的PHP版本进行改写
# PHP代码地址:https://github.com/metowolf/BilibiliHelper/blob/0.9x/src/plugins/Task.php

import asyncio
import platform

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from AsyncioCurl import AsyncioCurl
from BasicRequest import BasicRequest
from Config import *
from Base import std235959ptm


class Task:

    def __init__(self):
        self.done = []

    async def work(self):
        if config["Function"]["TASK"] == "False":
            return

        while 1:
            Log.info("检查每日任务")

            await self.web_info()
            await self.app_info()
            data = await self.check()

            await self.double_watch_info(data)
            await self.sign_info()

            if len(self.done) >= 2:
                self.done = []
                await asyncio.sleep(std235959ptm())
            else:
                await asyncio.sleep(600)

    async def check(self):
        url = "https://api.live.bilibili.com/i/api/taskInfo"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if data["code"] != 0:
            Log.error("每日任务检查失败")

        return data

    async def sign_info(self):
        if "sign_info" in self.done:
            return

        Log.info("检查任务「每日签到」")

        sign_data = await BasicRequest.req_check_signinfo()
        if not sign_data["code"]:
            info = sign_data["data"]

        if info["status"] == 1:
            Log.warning("「每日签到」奖励已经领取")
            self.done.append("sign_info")
            return

        url = "https://api.live.bilibili.com/sign/doSign"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])

        if data["code"] == 0:
            Log.info("「每日签到」成功，您已连续签到 %s 天，获得%s，%s" % (
            data["data"]["hadSignDays"], data["data"]["text"], data["data"]["specialText"]))
            self.done.append("sign_info")
        elif data["code"] == 1011040:
            Log.warning("「每日签到」今日已签到过")
            self.done.append("sign_info")
        else:
            Log.error("「每日签到」失败")

    async def web_info(self):
        try:
            response = await BasicRequest.web_get_info_by_room()
            if response["code"] != 0:
                Log.warning(f"web getInfoByRoom 返回错误: {response.get('message') or response.get('msg')}")
        except Exception as exc:
            Log.error(f"{exc}")

    async def app_info(self):
        try:
            response = BasicRequest.app_get_info_by_room()
            if response["code"] != 0:
                Log.warning(f"app getInfoByRoom 返回错误: {response.get('message') or response.get('msg')}")
        except Exception as exc:
            Log.error(f"{exc}")

    async def double_watch_info(self, value):
        if len(value["data"]["double_watch_info"]) == 0:
            return
        if "double_watch_info" in self.done:
            return

        Log.info("检查任务「双端观看直播」")

        info = value["data"]["double_watch_info"]

        if info["status"] == 2:
            Log.warning("「双端观看直播」奖励已经领取过")
            self.done.append("double_watch_info")
            return

        if info["mobile_watch"] != 1 or info["web_watch"] != 1:
            Log.warning("「双端观看直播」未完成，请等待")
            return

        url = "https://api.live.bilibili.com/activity/v1/task/receive_award"
        payload = {
            "task_id": "double_watch_task",
            "csrf_token": account["Token"]["CSRF"],
            "csrf": account["Token"]["CSRF"]
        }
        data = await AsyncioCurl().request_json("POST", url, headers=config["pcheaders"], data=payload)

        if data["code"] != 0:
            Log.error("「双端观看直播」奖励领取失败")
        else:
            Log.info("「双端观看直播」奖励领取成功")
            self.done.append("double_watch_info")
