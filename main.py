import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 擴充資料庫 ---
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉", "呂彥青", "鄭凱文", "余謙"], "B": ["王威晨", "江坤宇", "陳子豪", "許基宏", "詹子賢"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈", "曾峻岳", "陳仕朋", "張奕"], "B": ["張育成", "王正棠", "范國宸", "申皓瑋", "戴培峰"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士", "陳韻文", "胡智爲", "林詔恩"], "B": ["陳傑憲", "蘇智傑", "林安可", "邱智呈", "陳鏞基"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍", "陳冠偉", "林凱威", "銳歐"], "B": ["吉力吉撈", "郭天信", "李凱威", "劉基鴻", "拿莫．伊漾"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂", "陳冠宇", "陳柏豪", "王志煊"], "B": ["林立", "朱育賢", "陳晨威", "梁家榮", "林泓育"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺", "後勁", "賴鴻誠", "黃群"], "B": ["魔鷹", "王柏融", "曾子祐", "陳文杰", "杜家明"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志", "陳偉殷", "潘威倫", "陽建福"], "B": ["陳金鋒", "彭政閔", "林智勝", "張泰山", "高國輝"]}
}

PITCH_TYPES = {
    "1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球",
    "6": "速球", "7": "伸卡球", "8": "指岔球", "9": "卡特球"
}

STADIUMS = ["台北大巨蛋", "台中洲際球場", "桃園國際球場", "台南市立球場", "新莊棒球場", "天母棒球場", "澄清湖球場", "斗六棒球場"]

# --- 2. 遊戲狀態 ---
game = {
    "my_team": "", "opp_team": "", "stadium": "",
    "score": [0, 0], "outs": 0, "strikes": 0, "balls": 0,
    "bases": [False, False, False], "stamina": 100,
    "pitcher": "", "batter": "", "message": "請選擇隊伍編號開始比賽："
}

# --- 3. 網頁介面 ---
@app.get("/", response_class=HTMLResponse)
async def index():
    if not game["my_team"]:
        teams_html = "".join([f'<a href="/select?id={k}"><button>{v["name"]}</button></a> ' for k, v in TEAMS.items()])
        return f"<h1>歡迎進入 CPBL 棒球模擬器</h1><p>請選擇你的隊伍：</p>{teams_html}"

    bases_ui = f"{'🏃' if game['bases'][0] else '◯'}一壘 {'🏃' if game['bases'][1] else '◯'}二壘 {'🏃' if game['bases'][2] else '◯'}三壘"
    pitch_btns = "".join([f'<a href="/pitch?type={v}"><button style="margin:5px;">{v}</button></a>' + ("<br>" if k in ["3","6"] else "") for k,v in PITCH_TYPES.items()])
    
    stamina_ui = ""
    if game["stamina"] < 50:
        stamina_ui = "<div style='color:red;'>體力低於50！請選：<a href='/keep'>1.繼續投</a> <a href='/switch'>2.換投</a></div>"

    return f"""
    <html><body style="text-align:center;">
        <h1>🏟️ {game['stadium']}</h1>
        <h2>{game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2>
        <p>投手: {game['pitcher']} | 打者: {game['batter']}</p>
        <p>體力: {game['stamina']} | 壘包: {bases_ui}</p>
        <p>出局: {game['outs']} | 好球: {game['strikes']} | 壞球: {game['balls']}</p>
        <hr>
        <p>{game['message']}</p>
        <div>{pitch_btns}</div>
        {stamina_ui}
        <br><a href="/surrender">🏳️ 投降系統</a>
    </body></html>
    """

@app.get("/select")
async def select(id: str):
    # 初始化遊戲與重置
    game.update({
        "my_team": TEAMS[id]["name"], "opp_team": random.choice([t["name"] for k,t in TEAMS.items() if k!=id]),
        "stadium": random.choice(STADIUMS), "score": [0,0], "outs":0, "stamina":100,
        "pitcher": random.choice(TEAMS[id]["P"]), "batter": random.choice(random.choice(list(TEAMS.values()))["B"]),
        "message": "比賽開始！請選擇投球球種。"
    })
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(type: str):
    game["stamina"] -= 5
    # 簡化模擬判定
    res = random.choices(["S", "B", "H"], weights=[40, 30, 30])[0]
    if res == "S":
        game["strikes"] += 1
        if game["strikes"] >= 3: 
            game["outs"] += 1
            game["strikes"] = 0
            game["message"] = "三振出局！"
    elif res == "B":
        game["balls"] += 1
        if game["balls"] >= 4:
            game["message"] = "四壞保送！"
            game["balls"] = 0
    if game["outs"] >= 3:
        game["outs"] = 0
        game["message"] = "攻守交換！"
    return RedirectResponse(url="/")

@app.get("/surrender")
async def surrender():
    return HTMLResponse("<h1>比賽結束</h1><a href='/'>1.要，比下一場</a> <a href='/'>2.不玩了</a>")
