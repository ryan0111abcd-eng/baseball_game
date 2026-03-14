import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 資料庫設定 ---
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

# --- 2. 遊戲狀態控制 ---
game = {"active": False, "score": [0,0], "outs": 0, "strikes": 0, "balls": 0, "stamina": 100, "is_over": False, "last_msg": "歡迎進入遊戲"}

def reset_game():
    game.update({"active": False, "score": [0,0], "outs": 0, "strikes": 0, "balls": 0, "stamina": 100, "is_over": False, "bases": [False,False,False]})

@app.get("/", response_class=HTMLResponse)
async def index():
    # 規則：一進遊戲，遊戲就要重新開始
    if not game["active"]:
        reset_game()
        team_btns = "".join([f'<a href="/select?id={k}"><button style="margin:5px;">{k}.{v["name"]}</button></a>' for k,v in TEAMS.items()])
        return render_ui(f"<h1>請選擇你的隊伍開始新手戰</h1><div>{team_btns}</div>")

    if game["is_over"]:
        return render_ui(f"""
            <h1>比賽結束！比分 {game['score'][0]}:{game['score'][1]}</h1>
            <p>要比下一場嗎？</p>
            <a href="/reset"><button>1. 要，比下一場</button></a>
            <a href="/quit"><button>2. 不玩了</button></a>
        """, stop_music=True)

    # 體力低於 50 換投機制
    stamina_warning = ""
    if game["stamina"] < 50:
        stamina_warning = '<div style="color:red; background:rgba(255,255,255,0.8);">體力低於50！ <a href="/keep">1.繼續投</a> | <a href="/change">2.換投</a></div>'

    # 球種排版與換行
    pitch_btns = ""
    for i, (k, v) in enumerate(PITCH_TYPES.items(), 1):
        pitch_btns += f'<a href="/pitch?id={k}"><button style="margin:5px;">{k}.{v}</button></a>'
        if i % 3 == 0: pitch_btns += "<br>"

    bases_info = f"{'●' if game['bases'][0] else '○'}一壘 {'●' if game['bases'][1] else '○'}二壘 {'●' if game['bases'][2] else '○'}三壘"

    content = f"""
        <h1>🏟️ {game['stadium']}</h1>
        <h2>{game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2>
        <p>投手: {game['pitcher']} (🔋{game['stamina']}) | 打者: {game['batter']}</p>
        <p>{bases_info}</p>
        <p>🔴 出局: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</p>
        <hr>
        <div style="margin:20px;">{pitch_btns}</div>
        {stamina_warning}
        <br><a href="/surrender" style="color:yellow;">🏳️ 投降系統</a>
    """
    return render_ui(content)

def render_ui(content, stop_music=False):
    # 背景圖 images.jpg 且音樂 bgm.mp3 無限循環
    music = '<audio autoplay loop><source src="bgm.mp3" type="audio/mpeg"></audio>' if not stop_music else ""
    return f"""
    <html><head><style>
        body {{ background: url('images.jpg') no-repeat center center fixed; background-size: cover; color: white; text-align: center; font-family: sans-serif; }}
        .box {{ background: rgba(0,0,0,0.7); min-height: 100vh; padding: 50px; }}
        button {{ padding: 10px 20px; cursor: pointer; }}
    </style></head>
    <body><div class="box">{music}{content}</div></body></html>
    """

@app.get("/select")
async def select(id: str):
    game.update({"my_team": TEAMS[id]["name"], "opp_team": random.choice([v["name"] for k,v in TEAMS.items() if k!=id]),
                 "stadium": random.choice(STADIUMS), "pitcher": random.choice(TEAMS[id]["P"]),
                 "batter": random.choice(TEAMS[random.choice(list(TEAMS.keys()))]["B"]), "active": True})
    return RedirectResponse("/")

@app.get("/pitch")
async def pitch(id: str):
    game["stamina"] -= random.randint(3, 8)
    res = random.random()
    if res < 0.4: game["strikes"] += 1
    elif res < 0.7: game["balls"] += 1
    else: game["score"][1] += 1 # 簡化安打邏輯
    
    if game["strikes"] >= 3: game["outs"] += 1; game["strikes"], game["balls"] = 0, 0
    if game["balls"] >= 4: game["strikes"], game["balls"] = 0, 0
    if game["outs"] >= 3: game["is_over"] = True
    return RedirectResponse("/")

@app.get("/surrender")
async def surrender(): game["is_over"] = True; return RedirectResponse("/")

@app.get("/reset")
async def reset(): reset_game(); return RedirectResponse("/")

@app.get("/quit")
async def quit(): return HTMLResponse("<h1>遊戲結束，謝謝遊玩！</h1>")

@app.get("/keep")
async def keep(): return RedirectResponse("/")

@app.get("/change")
async def change(): game["stamina"] = 100; return RedirectResponse("/")
