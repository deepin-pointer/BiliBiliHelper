from Config import *
from BasicRequest import BasicRequest
from AsyncioCurl import AsyncioCurl
from Utils import Utils
from Raffle_Handler import RaffleHandler
from Guard_Raffle_Handler import GuardRaffleHandler
from Tv_Raffle_Handler import TvRaffleHandler
from Pk_Raffle_Handler import PkRaffleHandler
import asyncio
import platform
import random

if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log


class Walker:
    def __init__(self):
        self.area = 0
        self.queue = []
        self.arealist = []

    async def work(self):
        if config["Function"]["Walker"] == "False":
            return

        while True:
            if self.arealist.count < 1:
                self.getList()
            else:
                if self.queue.count < 1:
                    self.getRooms()
                else:
                    self.inspectRoom()

            await asyncio.sleep(random.randint(2, 8))

    async def getList(self):
        url = "https://api.live.bilibili.com/room/v1/Area/getList"
        data = await AsyncioCurl().request_json("GET", url, headers=config["pcheaders"])
        if data["code"] != 0:
            Log.error("获取分区列表失败")
        else:
            for item in data["data"]:
                self.arealist.append(item["id"])

    async def getRooms(self):
        url = "https://api.live.bilibili.com/room/v3/Area/getRoomList?page={}&page_size=99&parent_area_id={}"
        page = 0
        while True:
            data = await AsyncioCurl().request_json("GET", url.format(page, self.arealist[self.area]), headers=config["pcheaders"])
            if data["code"] != 0:
                Log.error("获取房间列表出错")
                break
            else:
                try:
                    for item in data["data"]["list"]:
                        if "lottery" in item["web_pendent"]:
                            self.queue.append(item["roomid"])
                except:
                    Log.error("遍历房间出错")
                page = page+1
                if page*99 >= data["data"]["count"]:
                    break
            await asyncio.sleep(random.randint(1, 3))
        self.area = self.area+1
        if self.area >= self.arealist.count:
            self.area = 0
    
    async def inspectRoom(self):
        room=self.queue.pop()
        if not await Utils.is_normal_room(room):
            return
        
        data = await BasicRequest.gift_req_check(room)
        if data["data"]["guard"]:
            Log.raffle("遍历到%s房间的大航海" % (room))
            RaffleHandler.push2queue((room,), GuardRaffleHandler.check)
        if data["data"]["pk"]:
            Log.raffle("遍历到%s房间的大乱斗" % (room))
            RaffleHandler.push2queue((room), PkRaffleHandler.check)
        if data["data"]["gift"]:
            Log.raffle("遍历到%s房间的抽奖" % (room))
            RaffleHandler.push2queue((room,""), TvRaffleHandler.check)