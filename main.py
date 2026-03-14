import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# 1. 完整的球隊與資料
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉"], "B": ["王威晨", "江坤宇"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈"], "B": ["張育成", "王正棠"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士"], "B": ["陳傑憲", "蘇智傑"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍"], "B": ["吉力吉撈", "郭天信"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂"], "B": ["林立", "朱育賢"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺"], "B": ["魔鷹", "王柏融"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志"], "B": ["陳金鋒", "彭政閔"]}
}

PITCH_TYPES = {"1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球", "6": "速球", "7": "伸卡球", "8": "指岔球", "9": "卡特球"}

# 2. 遊戲核心狀態 (使用 dictionary 避免重置失敗)
game = {
    "active": False, "score": [0, 0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0,
    "stamina": 100, "bases": [False, False, False], "last_event": "等待開球...", "is_over": False
}

@app.get("/", response_class=HTMLResponse)
async def index():
    # 規則：如果還沒選隊伍，顯示選單
    if not game.get("my_team"):
        team_btns = "".join([f'<a href="/select?id={k}"><button style="margin:5px; padding:10px;">{k}.{v["name"]}</button></a>' for k,v in TEAMS.items()])
        return render_ui(f"<h1>🏟️ 選擇隊伍開始比賽</h1><div style='background:rgba(0,0,0,0.6); padding:20px;'>{team_btns}</div>")

    # 比賽結束畫面
    if game["is_over"]:
        return render_ui(f"""
            <h1>比賽結束</h1>
            <h2>{game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2>
            <p>要比下一場嗎？</p>
            <a href="/select?id=1"><button>1. 要，比下一場</button></a>
            <a href="/quit"><button>2. 不玩了</button></a>
        """, stop_music=True)

    # 球種排版與換行 (每3個換一行)
    pitch_btns = ""
    for i, (k, v) in enumerate(PITCH_TYPES.items(), 1):
        pitch_btns += f'<a href="/pitch?id={k}"><button style="width:100px; margin:5px;">{v}</button></a>'
        if i % 3 == 0: pitch_btns += "<br>"

    # 體力換投系統
    stamina_ui = f"<p>投手: {game['pitcher']} (🔋體力: {game['stamina']})</p>"
    if game["stamina"] < 50:
        stamina_ui += '<div style="background:red;">體力偏低！ <a href="/keep">1.繼續投</a> | <a href="/change">2.換投</a></div>'

    content = f"""
        <div style="background: rgba(0,0,0,0.7); padding: 20px; border-radius: 15px; display: inline-block;">
            <h1>{game['inning']}局上 | {game['my_team']} VS {game['opp_team']}</h1>
            <h2 style="color:yellow;">比分 {game['score'][0]} : {game['score'][1]}</h2>
            <hr>
            {stamina_ui}
            <p>{'🏃' if game['bases'][0] else '◯'}一壘 {'🏃' if game['bases'][1] else '◯'}二壘 {'🏃' if game['bases'][2] else '◯'}三壘</p>
            <p style="font-size:1.5em;">🔴 OUT: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</p>
            <div style="border:1px solid white; padding:5px;">{game['last_event']}</div>
            <div style="margin:20px;">{pitch_btns}</div>
            <br><a href="/surrender" style="color:red;">🏳️ 投降系統</a>
        </div>
    """
    return render_ui(content)

def render_ui(content, stop_music=False):
    # 背景使用 images.jpg，音樂使用 bgm.mp3
    music_tag = '<audio id="aud" autoplay loop><source src="bgm.mp3" type="audio/mpeg"></audio>' if not stop_music else ""
    return f"""
    <html><head><style>
        body {{ background: url('images.jpg') no-repeat center center fixed; background-size: cover; color: white; text-align: center; font-family: sans-serif; }}
        button {{ cursor: pointer; padding: 10px; font-weight: bold; border-radius: 5px; }}
    </style></head>
    <body onclick="document.getElementById('aud').play();">
        <div style="min-height:100vh; background:rgba(0,0,0,0.3); padding-top:50px;">
            {music_tag}
            {content}
        </div>
    </body></html>
    """

@app.get("/select")
async def select(id: str):
    game.update({
        "my_team": TEAMS[id]["name"], "score": [0,0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0, "stamina": 100, "is_over": False,
        "opp_team": random.choice([v["name"] for k,v in TEAMS.items() if v["name"] != TEAMS[id]["name"]]),
        "pitcher": random.choice(TEAMS[id]["P"]), "batter": "強打者", "last_event": "比賽開始！"
    })
    return RedirectResponse("/")

@app.get("/pitch")
async def pitch(id: str):
    game["stamina"] -= random.randint(3, 6)
    res = random.random()
    
    if res < 0.35: # 好球
        game["strikes"] += 1
        game["last_event"] = f"好球！({PITCH_TYPES[id]})"
        if game["strikes"] >= 3:
            game["outs"] += 1
            game["strikes"], game["balls"] = 0, 0
            game["last_event"] = "三振出局！"
    elif res < 0.65: # 壞球
        game["balls"] += 1
        game["last_event"] = f"壞球。({PITCH_TYPES[id]})"
        if game["balls"] >= 4:
            game["last_event"] = "四壞球保送！"
            game["strikes"], game["balls"] = 0, 0
            game["bases"][0] = True 
    else: # 擊球
        if random.random() > 0.7:
            game["score"][1] += 1
            game["last_event"] = "安打！失一分"
        else:
            game["outs"] += 1
            game["last_event"] = "接殺出局！"
        game["strikes"], game["balls"] = 0, 0

    if game["outs"] >= 3:
        game["inning"] += 1
        game["outs"], game["strikes"], game["balls"] = 0, 0, 0
        game["last_event"] = "三出局，換局！"
        if game["inning"] > 9: game["is_over"] = True
    
    return RedirectResponse("/")

@app.get("/surrender")
async def surrender(): game["is_over"] = True; return RedirectResponse("/")

@app.get("/change")
async def change(): game["stamina"] = 100; game["last_event"] = "已更換投手"; return RedirectResponse("/")

@app.get("/keep")
async def keep(): return RedirectResponse("/")

@app.get("/quit")
async def quit(): game.clear(); return RedirectResponse("/")    
