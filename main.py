import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 擴充後的龐大資料庫 ---
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉", "呂彥青", "鄭凱文", "艾士特", "王凱程"], "B": ["王威晨", "江坤宇", "陳子豪", "許基宏", "曾頌恩", "岳政華"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈", "曾峻岳", "張奕", "陳仕朋", "黃保羅"], "B": ["張育成", "王正棠", "范國宸", "申皓瑋", "戴培峰", "王苡丞"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士", "陳韻文", "胡智為", "布雷克", "羅昂"], "B": ["陳傑憲", "蘇智傑", "林安可", "邱智呈", "潘傑楷", "林益全"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍", "陳冠偉", "林凱威", "王維中", "艾璞樂"], "B": ["吉力吉撈", "郭天信", "李凱威", "劉基鴻", "張祐銘", "拿莫伊漾"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂", "陳冠宇", "陳柏豪", "王志煊", "威能帝"], "B": ["林立", "朱育賢", "陳晨威", "梁家榮", "林泓育", "成晉"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺", "後勁", "陳柏清", "黃群", "伍祐城"], "B": ["魔鷹", "王柏融", "曾子祐", "陳文杰", "杜家明", "葉保弟"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志", "陳偉殷", "潘威倫", "江少慶", "李振昌"], "B": ["陳金鋒", "彭政閔", "林智勝", "張泰山", "高國輝", "林哲瑄"]}
}
STADIUMS = ["台北大巨蛋", "台中洲際球場", "桃園國際球場", "台南市立球場", "新莊棒球場", "天母棒球場", "澄清湖球場", "斗六球場", "嘉義市立球場", "花蓮球場"]
PITCH_TYPES = {"1":"直球", "2":"曲球", "3":"變化球", "4":"滑球", "5":"變速球", "6":"速球", "7":"伸卡球", "8":"指岔球", "9":"卡特球"}
SWING_LOCATIONS = {"1":"內角高", "2":"內角低", "3":"中間", "4":"外角高", "5":"外角低"}

# --- 2. 遊戲狀態 ---
game = {"active":False, "my_team":None, "opp_team":None, "stadium":"", "score":[0,0], "inning":1, "outs":0, "strikes":0, "balls":0, "stamina":100, "pitcher":"", "batter":"", "last_event":"歡迎來到 CPBL！", "is_batting":False, "is_over":False}

def reset_game():
    game.update({"active":False, "score":[0,0], "inning":1, "outs":0, "strikes":0, "balls":0, "stamina":100, "is_over":False, "last_event":"新比賽開始！"})

# --- 3. 介面渲染 ---
def render_page(content):
    return f"""<html><head><style>
        body {{ background: url('images.jpg') no-repeat center center fixed; background-size: cover; color: black; font-family: sans-serif; text-align: center; }}
        .box {{ background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 20px; display: inline-block; margin-top: 30px; width: 90%; max-width: 600px; }}
        button {{ padding: 10px; margin: 5px; cursor: pointer; border-radius: 5px; border: 1px solid #333; font-weight: bold; background: #fff; }}
    </style></head>
    <body onclick="document.getElementById('bgm').play();">
        <audio id='bgm' loop><source src='bgm.mp3' type='audio/mpeg'></audio>
        <div class="box"><h1>⚾ CPBL中華職棒傳奇</h1>{content}</div>
    </body></html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    if not game["active"]:
        btns = "".join([f'<a href="/select?id={k}"><button>{k}.{v["name"]}</button></a>' for k,v in TEAMS.items()])
        return render_page(f"<h3>請選擇你的球隊：</h3>{btns}")
    
    if game["is_over"]:
        return render_page(f"<h1>比賽結束</h1><h2>比分 {game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2><a href='/select?id=1'><button>1. 再比一場</button></a> <a href='/quit'><button>2. 不玩了</button></a>")

    mode = "打擊區" if game["is_batting"] else "投球區"
    btns = "".join([f'<a href="/{"swing" if game["is_batting"] else "pitch"}?id={k}"><button>{v}</button></a>' + ("<br>" if i%3==0 else "") for i, (k, v) in enumerate((SWING_LOCATIONS if game["is_batting"] else PITCH_TYPES).items(), 1)])
    stamina_ui = f"<div style='color:red;'>⚠️ 體力 {game['stamina']} <a href='/change'><button>換投</button></a></div>" if game['stamina'] < 50 else f"<div>體力: {game['stamina']}</div>"

    content = f"""
        <h3>🏟️ {game['stadium']} | 第 {game['inning']} 局</h3>
        <p>👤 投: {game['pitcher']} | 👤 打: {game['batter']}</p>
        <h2 style='font-size:28px;'>🔴 OUT: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</h2>
        <div style='background:#eee; padding:10px; margin:10px;'>{game['last_event']}</div>
        <h4>現在是 {mode}</h4><div>{btns}</div>{stamina_ui}<br><a href='/surrender'><button>🏳️ 投降</button></a>
    """
    return render_page(content)

@app.get("/select")
async def select(id: str):
    team = TEAMS[id]
    opp = TEAMS[random.choice([k for k in TEAMS if k != id])]
    game.update({"active":True, "my_team":team["name"], "opp_team":opp["name"], "stadium":random.choice(STADIUMS), "pitcher":random.choice(team["P"]), "batter":random.choice(opp["B"])})
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(id: str):
    game["stamina"] -= random.randint(3, 7)
    if random.random() < 0.3: game["is_batting"] = True
    game["last_event"] = f"投出了{PITCH_TYPES[id]}"
    return RedirectResponse(url="/")

@app.get("/swing")
async def swing(id: str):
    game["strikes"] += 1
    game["last_event"] = f"揮棒向{SWING_LOCATIONS[id]}，結果揮空！"
    if game["strikes"] >= 3: game["outs"]+=1; game["strikes"]=0; game["is_batting"]=False
    return RedirectResponse(url="/")

@app.get("/change")
async def change(): game["stamina"]=100; return RedirectResponse(url="/")
@app.get("/surrender")
async def surrender(): game["is_over"]=True; return RedirectResponse(url="/")
@app.get("/quit")
async def quit(): reset_game(); return RedirectResponse(url="/")
