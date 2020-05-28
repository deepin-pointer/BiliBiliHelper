import os
import sys
sys.path.append(sys.path[0] + "/Src")
import asyncio
import signal
import Console
import threading
import Danmu_Monitor
from Raffle_Handler import RaffleHandler
import platform
if platform.system() == "Windows":
    from Windows_Log import Log
else:
    from Unix_Log import Log
from Auth import Auth
from Capsule import Capsule
from Coin2Silver import Coin2Silver
from DailyBag import DailyBag
from GiftSend import GiftSend
from Group import Group
from Heart import Heart
from Silver2Coin import Silver2Coin
from SilverBox import SilverBox
from Statistics import Statistics
from Task import Task
from Sentence import Sentence
from Timer import Timer
from Config import *
from configcheck import ConfigCheck
from optparse import OptionParser
from API import API
from Monitor_Server import MonitorServer
from Version import version
from CaseJudger import CaseJudger
from MainDailyTask import MainDailyTask
from MatchTask import MatchTask

# 初始化所有class
API = API()
Auth = Auth()
Capsule = Capsule()
CaseJudger = CaseJudger()
Coin2Silver = Coin2Silver()
DailyBag = DailyBag()
GiftSend = GiftSend()
Group = Group()
Heart = Heart()
Silver2Coin = Silver2Coin()
SilverBox = SilverBox()
Task = Task()
rafflehandler = RaffleHandler()
MainDailyTask = MainDailyTask()
MatchTask = MatchTask()
MonitorServer = MonitorServer(config["Server"]["ADDRESS"], config["Server"]["PASSWORD"])

parser = OptionParser()
parser.add_option("-d", "--disable-console",
                  action="store_true", dest="disable_console", default=False,
                  help="disable console")
(options, args) = parser.parse_args()

# 开启时清理日志
Log.clean_log(startup=True)

def signal_handler(signal, frame):
    os._exit(0)

print("""\033[32;1m
 ______     __     __         __     ______     __     __         __     __  __     ______     __         ______   ______     ______    
/\  == \   /\ \   /\ \       /\ \   /\  == \   /\ \   /\ \       /\ \   /\ \_\ \   /\  ___\   /\ \       /\  == \ /\  ___\   /\  == \   
\ \  __<   \ \ \  \ \ \____  \ \ \  \ \  __<   \ \ \  \ \ \____  \ \ \  \ \  __ \  \ \  __\   \ \ \____  \ \  _-/ \ \  __\   \ \  __<   
 \ \_____\  \ \_\  \ \_____\  \ \_\  \ \_____\  \ \_\  \ \_____\  \ \_\  \ \_\ \_\  \ \_____\  \ \_____\  \ \_\    \ \_____\  \ \_\ \_\ 
  \/_____/   \/_/   \/_____/   \/_/   \/_____/   \/_/   \/_____/   \/_/   \/_/\/_/   \/_____/   \/_____/   \/_/     \/_____/   \/_/ /_/ 
\033[0m""")

if config["Other"]["INFO_MESSAGE"] != "False":
    Log.info("BiliBiliHelper Python " + version)

Log.info("Powered By TheWanderingCoel, kotoriのねこ and 洛水.山岭居室️")

if config["Other"]["SENTENCE"] != "False":
    Log.info(Sentence().get_sentence())

# 检查Config
ConfigCheck()

# 注册信号
signal.signal(signal.SIGINT, signal_handler)

loop = asyncio.get_event_loop()

timer = Timer(loop)
console = Console.Console(loop)

area_ids = [1,2,3,4,5,6,]
Statistics(len(area_ids))

daily_tasks = [
    Capsule.work(),
    CaseJudger.work(),
    Coin2Silver.work(),
    DailyBag.work(),
    GiftSend.work(),
    Group.work(),
    Heart.work(),
    Silver2Coin.work(),
    SilverBox.work(),
    Task.work(),
    MainDailyTask.work(),
    MatchTask.work(),
    Walker.work()
]
server_tasks = [
    MonitorServer.run_forever()
]
danmu_tasks = [Danmu_Monitor.run_Danmu_Raffle_Handler(i) for i in area_ids]
other_tasks = [
    rafflehandler.run()
]

api_thread = threading.Thread(target=API.work)
api_thread.start()

if not options.disable_console:
    console_thread = threading.Thread(target=console.cmdloop)
    console_thread.start()

# 先登陆一次,防止速度太快导致抽奖模块出错
Auth.work()

if config["Function"]["RAFFLE_HANDLER"] != "False":
    if config["Server"]["PERFER_SERVER"] != "False":
        loop.run_until_complete(asyncio.wait(daily_tasks+server_tasks+other_tasks))
    else:
        loop.run_until_complete(asyncio.wait(daily_tasks+danmu_tasks+other_tasks))
else:
    loop.run_until_complete(asyncio.wait(daily_tasks))

api_thread.join()

if not options.disable_console:
    console_thread.join()

loop.close()
