import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 資料庫 ---
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉"], "B": ["王威晨", "江坤宇"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈"], "B": ["張育成", "王正棠"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士"], "B": ["陳傑憲", "蘇智傑"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍"], "B": ["吉力吉撈", "郭天信"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂"], "B": ["林立", "朱育賢"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺"], "B": ["魔鷹", "王柏融"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志"], "B": ["陳金鋒", "彭政閔"]}
}

PITCH_TYPES = {"1": "直球", "2": "曲球", "3": "變化球", "4": "滑球"}

# --- 2. 遊戲全域狀態 (確保狀態不會丟失) ---
game = {
    "active": False, "my_team": None, "opp_team": None,
    "score": [0, 0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0,
    "last_event": "遊戲開始！"
}

# --- 3. 網頁渲染 ---
@app.get("/", response_class=HTMLResponse)
async def index():
    if not game["active"]:
        team_btns = "".join([f'<a href="/select?id={k}"><button>{v["name"]}</button></a>' for k,v in TEAMS.items()])
        return f"<body style='color:black; text-align:center;'><h1>⚾ CPBL中華職棒傳奇 測試版</h1>{team_btns}</body>"

    return f"""
    <body style='color:black; text-align:center; background: #f0f0f0;'>
        <div style='background:white; padding:20px; border-radius:10px; display:inline-block;'>
            <h1>{game['my_team']} vs {game['opp_team']}</h1>
            <h2>第 {game['inning']} 局 | 比分 {game['score'][0]} : {game['score'][1]}</h2>
            <p style='font-size:20px;'>🔴 OUT: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</p>
            <p>事件: {game['last_event']}</p>
            {"".join([f'<a href="/pitch?id={k}"><button>{v}</button></a>' for k,v in PITCH_TYPES.items()])}
            <br><br><a href="/quit"><button>結束比賽</button></a>
        </div>
    </body>
    """

@app.get("/select")
async def select(id: str):
    game.update({
        "active": True, "my_team": TEAMS[id]["name"], "opp_team": "對手",
        "score": [0,0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0, "last_event": "比賽開始"
    })
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(id: str):
    # 邏輯核心
    res = random.random()
    if res < 0.4: # 好球
        game["strikes"] += 1
        game["last_event"] = f"投出{PITCH_TYPES[id]}，好球！"
        if game["strikes"] >= 3:
            game["outs"] += 1
            game["strikes"] = 0
            game["balls"] = 0
            game["last_event"] = "三振出局！"
    elif res < 0.7: # 壞球
        game["balls"] += 1
        game["last_event"] = "壞球。"
        if game["balls"] >= 4:
            game["last_event"] = "四壞球保送！"
            game["strikes"] = 0
            game["balls"] = 0
    else: # 出局
        game["outs"] += 1
        game["strikes"] = 0
        game["balls"] = 0
        game["last_event"] = "擊球出局！"

    if game["outs"] >= 3:
        game["inning"] += 1
        game["outs"] = 0
        game["last_event"] = "三出局，換局！"
        
    return RedirectResponse(url="/")

@app.get("/quit")
async def quit():
    game["active"] = False
    return RedirectResponse(url="/")
