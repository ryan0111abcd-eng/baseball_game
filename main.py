import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# 遊戲狀態：將所有變數集中在這裡，避免跳回選單
game = {
    "active": False, "my_team": None, "opp_team": None,
    "score": [0, 0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0
}

@app.get("/", response_class=HTMLResponse)
async def index():
    # 判斷遊戲是否開始
    if not game["active"]:
        return """
        <h1>歡迎來到棒球模擬器</h1>
        <p>請選擇你的隊伍：</p>
        <a href="/select?id=兄弟"><button>中信兄弟</button></a>
        <a href="/select?id=悍將"><button>富邦悍將</button></a>
        """
    
    return f"""
    <body style="background: url('images.jpg'); background-size: cover; color: white; text-align: center;">
        <div style="background: rgba(0,0,0,0.6); padding: 20px;">
            <h1>{game['my_team']} VS {game['opp_team']}</h1>
            <h2>第 {game['inning']} 局 | 比分 {game['score'][0]} : {game['score'][1]}</h2>
            <p>🔴 出局: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</p>
            <a href="/pitch?type=直球"><button>投出直球</button></a>
            <a href="/pitch?type=變化球"><button>投出變化球</button></a>
        </div>
    </body>
    """

@app.get("/select")
async def select(id: str):
    game.update({"my_team": id, "opp_team": "對手", "active": True, "score": [0,0], "outs": 0, "strikes": 0, "balls": 0, "inning": 1})
    return RedirectResponse("/")

@app.get("/pitch")
async def pitch(type: str):
    # 核心邏輯：三好球=出局，四壞球=保送，三出局=換局
    res = random.random()
    if res < 0.4: # 好球
        game["strikes"] += 1
        if game["strikes"] >= 3:
            game["outs"] += 1
            game["strikes"] = 0
            game["balls"] = 0
    elif res < 0.7: # 壞球
        game["balls"] += 1
        if game["balls"] >= 4:
            game["strikes"] = 0
            game["balls"] = 0
            # 這裡可以加入保送邏輯
    else: # 安打或接殺
        if random.random() > 0.5:
            game["score"][1] += 1
        else:
            game["outs"] += 1
        game["strikes"] = 0
        game["balls"] = 0
    
    # 三出局換局
    if game["outs"] >= 3:
        game["inning"] += 1
        game["outs"] = 0
        
    return RedirectResponse("/")
