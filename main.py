import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 豐富的資料庫 ---
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉", "呂彥青", "鄭凱文"], "B": ["王威晨", "江坤宇", "陳子豪", "許基宏"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈", "曾峻岳", "張奕"], "B": ["張育成", "王正棠", "范國宸", "申皓瑋"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士", "陳韻文", "胡智為"], "B": ["陳傑憲", "蘇智傑", "林安可", "邱智呈"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍", "陳冠偉", "林凱威"], "B": ["吉力吉撈", "郭天信", "李凱威", "劉基鴻"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂", "陳冠宇", "陳柏豪"], "B": ["林立", "朱育賢", "陳晨威", "梁家榮"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺", "後勁", "陳柏清"], "B": ["魔鷹", "王柏融", "曾子祐", "陳文杰"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志", "陳偉殷", "潘威倫"], "B": ["陳金鋒", "彭政閔", "林智勝", "張泰山"]}
}

STADIUMS = ["台北大巨蛋", "台中洲際球場", "桃園國際球場", "台南市立球場", "新莊棒球場", "天母棒球場", "澄清湖球場"]
PITCH_TYPES = {"1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球", "6": "速球", "7": "伸卡球", "8": "指岔球", "9": "卡特球"}

# --- 2. 遊戲狀態 ---
game = {
    "active": False, "my_team": None, "opp_team": None, "stadium": "",
    "score": [0, 0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0,
    "bases": [False, False, False], "stamina": 100,
    "pitcher": "", "batter": "", "last_event": "遊戲開始！請投球", "is_over": False
}

def reset_game():
    game.update({
        "active": False, "score": [0, 0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0,
        "bases": [False, False, False], "stamina": 100, "is_over": False, "last_event": "遊戲已重置"
    })

# --- 3. 網頁渲染 ---
@app.get("/", response_class=HTMLResponse)
async def index():
    if not game["active"]:
        reset_game()
        team_btns = "".join([f'<a href="/select?id={k}"><button style="padding:10px; margin:5px;">{k}.{v["name"]}</button></a>' for k,v in TEAMS.items()])
        # 標題已更新
        return render_ui(f"<h1>⚾ CPBL中華職棒傳奇 測試版</h1><div style='background:rgba(0,0,0,0.6); padding:20px;'>{team_btns}</div>")

    if game["is_over"]:
        return render_ui(f"""
            <div style='background:rgba(0,0,0,0.8); padding:30px;'>
                <h1>比賽結束！</h1>
                <h2>比分 {game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2>
                <a href="/select?id=1"><button>再比下一場</button></a>
                <a href="/quit"><button>結束遊戲</button></a>
            </div>
        """, stop_music=True)

    stamina_html = ""
    if game["stamina"] < 50:
        stamina_html = f'<div style="background:red; padding:10px;">⚠️ 體力剩餘 {game["stamina"]}！<br><a href="/keep"><button>繼續投</button></a> <a href="/change"><button>換投</button></a></div>'

    pitch_btns = ""
    for i, (k, v) in enumerate(PITCH_TYPES.items(), 1):
        pitch_btns += f'<a href="/pitch?id={k}"><button style="width:80px; margin:5px;">{v}</button></a>'
        if i % 3 == 0: pitch_btns += "<br>"

    bases_ui = f"{'🏃' if game['bases'][0] else '◯'}一壘 {'🏃' if game['bases'][1] else '◯'}二壘 {'🏃' if game['bases'][2] else '◯'}三壘"

    content = f"""
        <div style="background: rgba(0,0,0,0.7); padding: 20px; border-radius: 20px; display: inline-block;">
            <h1>🏟️ {game['stadium']} (第 {game['inning']} 局)</h1>
            <h2>{game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2>
            <p>👤 投手: {game['pitcher']} (🔋{game['stamina']}) | 打者: {game['batter']}</p>
            <p>{bases_ui}</p>
            <p style="font-size: 1.5em; color: yellow;">🔴 OUT: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</p>
            <div style="border: 1px solid #555; padding: 10px;">最後事件: {game['last_event']}</div>
            <div style="margin:20px;">{pitch_btns}</div>
            {stamina_html}
            <br><a href="/surrender" style="color:red;">🏳️ 投降</a>
        </div>
    """
    return render_ui(content)

def render_ui(content, stop_music=False):
    music_tag = '<audio id="bgm" autoplay loop><source src="bgm.mp3" type="audio/mpeg"></audio>' if not stop_music else ""
    return f"""
    <html><head><style>
        body {{ background: url('images.jpg') no-repeat center center fixed; background-size: cover; color: white; font-family: sans-serif; text-align: center; margin-top: 50px; }}
        button {{ padding: 10px; cursor: pointer; border-radius: 5px; border: none; background: #fff; font-weight: bold; }}
    </style></head>
    <body onclick="document.getElementById('bgm').play();">
        {music_tag}
        {content}
    </body></html>
    """

# --- 4. 遊戲邏輯 ---
@app.get("/select")
async def select(id: str):
    reset_game()
    game.update({"my_team": TEAMS[id]["name"], "opp_team": random.choice([v["name"] for k,v in TEAMS.items() if k != id]),
                 "stadium": random.choice(STADIUMS), "pitcher": random.choice(TEAMS[id]["P"]),
                 "batter": random.choice(TEAMS[random.choice(list(TEAMS.keys()))]["B"]), "active": True})
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(id: str):
    game["stamina"] -= random.randint(3, 7)
    res = random.random()
    if res < 0.4:
        game["strikes"] += 1
        game["last_event"] = f"投出 {PITCH_TYPES[id]}，好球！"
        if game["strikes"] >= 3:
            game["outs"] += 1; game["strikes"] = 0; game["balls"] = 0; game["last_event"] = "三振出局！"
    elif res < 0.7:
        game["balls"] += 1
        game["last_event"] = f"投出 {PITCH_TYPES[id]}，壞球。"
        if game["balls"] >= 4:
            game["last_event"] = "四壞球保送！"; game["strikes"] = 0; game["balls"] = 0; game["bases"][0] = True
    else:
        if random.random() > 0.6: game["score"][1] += 1; game["last_event"] = "被打安打，失分！"
        else: game["outs"] += 1; game["last_event"] = "接殺出局！"
        game["strikes"] = 0; game["balls"] = 0

    if game["outs"] >= 3:
        game["inning"] += 1; game["outs"] = 0; game["last_event"] = "三出局，換局！"
        if game["inning"] > 3: game["is_over"] = True
    return RedirectResponse(url="/")

@app.get("/surrender")
async def surrender(): game["is_over"] = True; return RedirectResponse(url="/")
@app.get("/change")
async def change(): game["stamina"] = 100; return RedirectResponse(url="/")
@app.get("/keep")
async def keep(): return RedirectResponse(url="/")
@app.get("/quit")
async def quit(): reset_game(); return RedirectResponse(url="/")
