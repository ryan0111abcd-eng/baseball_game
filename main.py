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

PITCH_TYPES = {
    "1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球",
    "6": "速球", "7": "伸卡球", "8": "指岔球", "9": "卡特球"
}

# --- 2. 遊戲狀態 ---
game = {
    "my_team": "", "opp_team": "",
    "score": [0, 0], "outs": 0, "strikes": 0, "balls": 0,
    "stamina": 100, "message": "請先輸入編號選擇你的隊伍 (1-7)："
}

# --- 3. 網頁介面 ---
@app.get("/", response_class=HTMLResponse)
async def index():
    # 建立隊伍選單
    team_options = "".join([f'<a href="/select_team?id={k}"><button>{v["name"]}</button></a> ' for k,v in TEAMS.items()])
    
    # 球種選單 (自動換行)
    pitch_options = "".join([f'<a href="/pitch?type={v}"><button style="margin:5px;">{v}</button></a>' for k,v in PITCH_TYPES.items()])
    
    html = f"""
    <html><body style="text-align:center;">
        <h1>⚾ CPBL 棒球模擬器</h1>
        <p>狀態: {game['message']}</p>
        <p>比分: {game['score'][0]}:{game['score'][1]} | 出局: {game['outs']} | 好: {game['strikes']} | 壞: {game['balls']}</p>
        <p>投手體力: {game['stamina']}</p>
        <hr>
        {team_options if not game['my_team'] else f"<h3>{game['my_team']} vs {game['opp_team']}</h3>" + pitch_options}
        <br><a href="/reset">重新比賽</a>
    </body></html>
    """
    return html

@app.get("/select_team")
async def select_team(id: str):
    game["my_team"] = TEAMS[id]["name"]
    game["opp_team"] = random.choice([t["name"] for k,t in TEAMS.items() if k != id])
    game["message"] = "比賽開始！請投球。"
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(type: str):
    # 邏輯判定
    game["stamina"] -= 5
    res = random.choices(["S", "B", "H"], weights=[40, 30, 30])[0]
    
    if res == "S":
        game["strikes"] += 1
        if game["strikes"] >= 3:
            game["outs"] += 1
            game["strikes"], game["balls"] = 0, 0
            game["message"] = "三振！"
    elif res == "B":
        game["balls"] += 1
        if game["balls"] >= 4:
            game["message"] = "保送！"
            game["strikes"], game["balls"] = 0, 0
    else:
        game["score"][1] += 1
        game["message"] = "被打出安打！"
    
    if game["outs"] >= 3:
        game["message"] = "攻守交換！"
        game["outs"] = 0
    
    return RedirectResponse(url="/")

@app.get("/reset")
async def reset():
    game.update({"score": [0,0], "outs": 0, "strikes": 0, "balls": 0, "stamina": 100, "my_team": ""})
    return RedirectResponse(url="/")
