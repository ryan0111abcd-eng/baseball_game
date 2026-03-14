import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 資料庫 ---
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉", "呂彥青"], "B": ["王威晨", "江坤宇", "陳子豪"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈", "曾張奕"], "B": ["張育成", "王正棠", "范國宸"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士"], "B": ["陳傑憲", "蘇智傑"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍"], "B": ["吉力吉撈", "郭天信"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂"], "B": ["林立", "朱育賢"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺"], "B": ["魔鷹", "王柏融"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志"], "B": ["陳金鋒", "彭政閔"]}
}

PITCH_TYPES = ["直球", "曲球", "滑球", "變速球", "伸卡球"]

# --- 2. 遊戲狀態儲存 (簡單起見存於記憶體) ---
game_state = {
    "my_team": TEAMS["1"]["name"],
    "opp_team": TEAMS["2"]["name"],
    "outs": 0,
    "strikes": 0,
    "balls": 0,
    "score_me": 0,
    "score_opp": 0,
    "message": "比賽開始！請選擇你要投的球種："
}

# --- 3. 網頁介面 ---
@app.get("/", response_class=HTMLResponse)
async def get_webpage():
    html_content = f"""
    <html>
    <head><title>CPBL 網頁模擬版</title><meta charset="utf-8"></head>
    <body style="font-family: sans-serif; text-align: center; background-color: #f0f0f0; padding-top: 50px;">
        <div style="background: white; width: 400px; margin: auto; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h2>⚾ 中華職棒模擬對戰</h2>
            <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">
                {game_state['my_team']} {game_state['score_me']} : {game_state['score_opp']} {game_state['opp_team']}
            </div>
            
            <div style="background: #222; color: #0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-family: monospace; text-align: left;">
                ● 出局 (OUT): {game_state['outs']} <br>
                ● 好球 (S): {game_state['strikes']} <br>
                ● 壞球 (B): {game_state['balls']}
            </div>
            
            <p style="color: #d32f2f; font-weight: bold; min-height: 50px;">{game_state['message']}</p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                {" ".join([f'<a href="/pitch?type={pt}"><button style="width:100%; padding:10px; cursor:pointer;">投 {pt}</button></a>' for pt in PITCH_TYPES])}
            </div>
            
            <hr style="margin-top: 20px;">
            <a href="/reset"><button style="color: gray; background: none; border: none; cursor: pointer;">重新開始比賽</button></a>
        </div>
    </body>
    </html>
    """
    return html_content

# --- 4. 投球邏輯 ---
@app.get("/pitch")
async def process_pitch(type: str):
    res = random.choices(["S", "B", "H", "HR"], weights=[35, 30, 25, 10])[0]
    
    if res == "S":
        game_state["strikes"] += 1
        game_state["message"] = f"❌ 好球！你的 {type} 讓打者揮空。"
        if game_state["strikes"] >= 3:
            game_state["outs"] += 1
            game_state["message"] = "⚡ 三振出局！"
            game_state["strikes"] = 0
            game_state["balls"] = 0
            
    elif res == "B":
        game_state["balls"] += 1
        game_state["message"] = f"🟡 壞球。這顆 {type} 偏離了打擊區。"
        if game_state["balls"] >= 4:
            game_state["message"] = "🚶 四壞球保送！"
            game_state["strikes"] = 0
            game_state["balls"] = 0
            
    elif res == "H":
        game_state["score_opp"] += 1
        game_state["message"] = f"🔥 擊出安打！打者看穿了你的 {type}。"
        game_state["strikes"], game_state["balls"] = 0, 0
        
    elif res == "HR":
        game_state["score_opp"] += 2
        game_state["message"] = f"🚀 全壘打！這顆 {type} 被掃出了牆外！"
        game_state["strikes"], game_state["balls"] = 0, 0

    if game_state["outs"] >= 3:
        game_state["message"] = "🔄 三出局！攻守交換 (模擬結束)。"
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/reset")
async def reset():
    game_state["outs"], game_state["strikes"], game_state["balls"] = 0, 0, 0
    game_state["score_me"], game_state["score_opp"] = 0, 0
    game_state["message"] = "新局開始，請投球！"
    return RedirectResponse(url="/", status_code=303)
