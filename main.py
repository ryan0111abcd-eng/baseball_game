from fastapi import FastAPI, StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import random

app = FastAPI()

# 啟用靜態檔案服務，讓網頁能抓到你的圖片與音樂
app.mount("/static", StaticFiles(directory="."), name="static")

# 遊戲狀態存在記憶體中
game = {"active": False, "score": [0,0], "outs": 0, "strikes": 0, "balls": 0, "inning": 1}

@app.get("/", response_class=HTMLResponse)
async def index():
    if not game.get("my_team"):
        return """
        <h1>請選擇球隊</h1>
        <a href="/select?id=1"><button>中信兄弟</button></a>
        <a href="/select?id=2"><button>富邦悍將</button></a>
        """
    
    # HTML 模板使用 ./static/ 指向檔案
    return f"""
    <body style="background: url('./static/images.jpg'); background-size: cover;">
        <audio id="bgm" src="./static/bgm.mp3" loop></audio>
        <div style="background:rgba(0,0,0,0.5); color:white;">
            <h1>{game['my_team']} 比賽中</h1>
            <p>🔴 出局: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</p>
            <a href="/pitch"><button>投球</button></a>
        </div>
        <script>document.body.onclick = () => document.getElementById('bgm').play();</script>
    </body>
    """

@app.get("/select")
async def select(id: str):
    game.update({"my_team": "球隊"+id, "active": True})
    return RedirectResponse("/")

@app.get("/pitch")
async def pitch():
    # 邏輯：三好球=一出局，四壞球=保送，三出局=換局
    game["strikes"] += 1
    if game["strikes"] == 3:
        game["outs"] += 1
        game["strikes"] = 0
    if game["outs"] == 3:
        game["inning"] += 1
        game["outs"] = 0
    return RedirectResponse("/")
