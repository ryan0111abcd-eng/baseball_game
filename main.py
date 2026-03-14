import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# 使用一個全域字典來維護遊戲狀態
game_state = {
    "active": False,
    "team": "",
    "inning": 1,
    "outs": 0,
    "strikes": 0,
    "balls": 0,
    "last_event": "遊戲開始"
}

@app.get("/", response_class=HTMLResponse)
async def index():
    # 判斷是否為開始狀態
    if not game_state["active"]:
        return """
        <body style='text-align:center; font-family:sans-serif;'>
            <h1 style='color:black;'>⚾ CPBL中華職棒傳奇 測試版</h1>
            <a href='/select?team=兄弟'><button>中信兄弟</button></a>
            <a href='/select?team=富邦'><button>富邦悍將</button></a>
        </body>
        """
    
    # 比賽畫面
    return f"""
    <body style='text-align:center; font-family:sans-serif; background-color:#f4f4f4;'>
        <div style='background:white; padding:20px; display:inline-block; border-radius:15px; border:1px solid #ccc;'>
            <h1 style='color:black;'>{game_state['team']} 進攻中</h1>
            <h3>第 {game_state['inning']} 局</h3>
            <p style='font-size:24px;'>🔴 OUT: {game_state['outs']} | S: {game_state['strikes']} | B: {game_state['balls']}</p>
            <p>最後事件: {game_state['last_event']}</p>
            <a href='/pitch?type=直球'><button>投直球</button></a>
            <a href='/pitch?type=變化球'><button>投變化球</button></a>
            <br><br>
            <a href='/reset'><button>結束比賽</button></a>
        </div>
    </body>
    """

@app.get("/select")
async def select(team: str):
    game_state.update({"active": True, "team": team, "inning": 1, "outs": 0, "strikes": 0, "balls": 0, "last_event": "比賽開始"})
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(type: str):
    # 核心邏輯
    r = random.random()
    if r < 0.4: # 好球
        game_state["strikes"] += 1
        game_state["last_event"] = f"投出{type}，好球！"
        if game_state["strikes"] == 3:
            game_state["outs"] += 1
            game_state["strikes"] = 0
            game_state["balls"] = 0
            game_state["last_event"] = "三振出局！"
    elif r < 0.7: # 壞球
        game_state["balls"] += 1
        game_state["last_event"] = "壞球"
        if game_state["balls"] == 4:
            game_state["last_event"] = "四壞保送！"
            game_state["strikes"] = 0
            game_state["balls"] = 0
    else: # 出局
        game_state["outs"] += 1
        game_state["last_event"] = "打擊出局！"
        game_state["strikes"] = 0
        game_state["balls"] = 0

    # 換局判斷
    if game_state["outs"] >= 3:
        game_state["inning"] += 1
        game_state["outs"] = 0
        game_state["last_event"] = "三出局，換局！"
        
    return RedirectResponse(url="/")

@app.get("/reset")
async def reset():
    game_state["active"] = False
    return RedirectResponse(url="/")
