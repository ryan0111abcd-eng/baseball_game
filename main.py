import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 完整資料庫 (球隊、球員、球場) ---
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

PITCH_TYPES = {
    "1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球",
    "6": "速球", "7": "伸卡球", "8": "指岔球", "9": "卡特球"
}

# --- 2. 遊戲狀態控制 ---
game = {
    "active": False, "my_team": None, "opp_team": None, "stadium": "",
    "score": [0, 0], "outs": 0, "strikes": 0, "balls": 0,
    "bases": [False, False, False], "stamina": 100,
    "pitcher": "", "batter": "", "last_pitch": "無", "is_over": False
}

def reset_game():
    game.update({
        "active": False, "my_team": None, "opp_team": None, "score": [0, 0],
        "outs": 0, "strikes": 0, "balls": 0, "bases": [False, False, False],
        "stamina": 100, "last_pitch": "無", "is_over": False
    })

# --- 3. 網頁渲染邏輯 ---
@app.get("/", response_class=HTMLResponse)
async def index():
    # 規則：一進遊戲，遊戲就要重新開始
    if not game["active"]:
        reset_game()
        team_btns = "".join([f'<a href="/select?id={k}"><button style="padding:10px; margin:5px;">{k}.{v["name"]}</button></a>' for k,v in TEAMS.items()])
        return render_ui(f"<h1>請選擇隊伍開始新手戰</h1><div>{team_btns}</div>")

    if game["is_over"]:
        return render_ui(f"""
            <h1>比賽結束！</h1>
            <h2>比分 {game['score'][0]} : {game['score'][1]}</h2>
            <p>要比下一場嗎？</p>
            <a href="/reset"><button>1. 要，比下一場 (繼續遊戲)</button></a>
            <a href="/quit"><button>2. 不玩了 (遊戲結束)</button></a>
        """, stop_music=True)

    # 體力低於 50 的換投機制
    stamina_action = ""
    if game["stamina"] < 50:
        stamina_action = """
            <div style="background:rgba(255,0,0,0.5); padding:10px; margin:10px;">
                <p>⚠️ 投手體力過低！請選擇：</p>
                <a href="/keep"><button>1. 繼續投</button></a>
                <a href="/change_p"><button>2. 換投</button></a>
            </div>
        """

    # 球種換行排版 (每 3 個換一行)
    pitch_btns = ""
    for i, (k, v) in enumerate(PITCH_TYPES.items(), 1):
        pitch_btns += f'<a href="/pitch?id={k}"><button style="padding:10px; margin:5px;">{k}.{v}</button></a>'
        if i % 3 == 0: pitch_btns += "<br>"

    bases_status = f"{'●' if game['bases'][0] else '○'}一壘 {'●' if game['bases'][1] else '○'}二壘 {'●' if game['bases'][2] else '○'}三壘"

    ui_content = f"""
        <h1>🏟️ {game['stadium']}</h1>
        <h2>{game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2>
        <hr>
        <p>投手: {game['pitcher']} (🔋體力: {game['stamina']}) | 打者: {game['batter']}</p>
        <p>壘包: {bases_status} | 最後球種: {game['last_pitch']}</p>
        <p style="font-size:1.2em; color:yellow;">🔴 出局: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</p>
        <div style="margin:20px;">{pitch_btns}</div>
        {stamina_action}
        <br><a href="/surrender" style="color:red;">[ 🏳️ 投降系統 ]</a>
    """
    return render_ui(ui_content)

def render_ui(content, stop_music=False):
    # 背景圖 images.jpg 且音樂 bgm.mp3 無限循環
    music_html = '<audio autoplay loop><source src="bgm.mp3" type="audio/mpeg"></audio>' if not stop_music else ""
    return f"""
    <html>
    <head>
        <style>
            body {{
                background: url('images.jpg') no-repeat center center fixed;
                background-size: cover;
                color: white; font-family: 'Microsoft JhengHei', sans-serif;
                text-align: center; margin: 0; padding: 0;
            }}
            .overlay {{
                background: rgba(0, 0, 0, 0.7);
                min-height: 100vh; padding-top: 50px;
            }}
            button {{ cursor: pointer; border-radius: 5px; border: 1px solid white; background: #333; color: white; }}
            button:hover {{ background: #555; }}
        </style>
    </head>
    <body>
        <div class="overlay">
            {music_html}
            {content}
        </div>
    </body>
    </html>
    """

# --- 4. 遊戲邏輯路徑 ---
@app.get("/select")
async def select(id: str):
    game["my_team"] = TEAMS[id]["name"]
    # 新手戰：對手不能跟自己一樣
    opp_id = random.choice([k for k in TEAMS.keys() if k != id])
    game["opp_team"] = TEAMS[opp_id]["name"]
    game["stadium"] = random.choice(STADIUMS)
    game["pitcher"] = random.choice(TEAMS[id]["P"])
    game["batter"] = random.choice(TEAMS[opp_id]["B"])
    game["active"] = True
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(id: str):
    game["last_pitch"] = PITCH_TYPES[id]
    game["stamina"] -= random.randint(3, 7)
    
    # 簡單模擬：40% 好球, 30% 壞球, 30% 安打/出局
    res = random.random()
    if res < 0.4:
        game["strikes"] += 1
        if game["strikes"] >= 3:
            game["outs"] += 1
            game["strikes"], game["balls"] = 0, 0
    elif res < 0.7:
        game["balls"] += 1
        if game["balls"] >= 4:
            game["strikes"], game["balls"] = 0, 0 # 保送邏輯簡化
    else:
        # 隨機產生安打或出局
        if random.random() > 0.7: game["score"][1] += 1
        else: game["outs"] += 1
        game["strikes"], game["balls"] = 0, 0

    if game["outs"] >= 3:
        game["is_over"] = True # 簡化：三出局即結束或換場
    return RedirectResponse(url="/")

@app.get("/surrender")
async def surrender():
    game["is_over"] = True
    return RedirectResponse(url="/")

@app.get("/reset")
async def reset():
    reset_game()
    return RedirectResponse(url="/")

@app.get("/quit")
async def quit():
    return HTMLResponse("<h1>遊戲已結束，感謝遊玩！</h1>")

@app.get("/keep")
async def keep(): return RedirectResponse(url="/")

@app.get("/change_p")
async def change_p():
    game["stamina"] = 100
    return RedirectResponse(url="/")
