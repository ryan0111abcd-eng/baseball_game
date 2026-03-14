import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 完整資料庫 ---
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉", "呂彥青", "鄭凱文", "余謙", "魏碩成"], "B": ["王威晨", "江坤宇", "陳子豪", "許基宏", "詹子賢", "岳東華"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈", "曾峻岳", "陳仕朋", "張奕", "黃保羅"], "B": ["張育成", "王正棠", "范國宸", "申皓瑋", "戴培峰", "林哲瑄"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士", "陳韻文", "胡智爲", "林詔恩", "羅昂"], "B": ["陳傑憲", "蘇智傑", "林安可", "邱智呈", "陳鏞基", "潘傑楷"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍", "陳冠偉", "林凱威", "銳歐", "伍鐸"], "B": ["吉力吉撈", "郭天信", "李凱威", "劉基鴻", "拿莫．伊漾", "張祐銘"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂", "陳冠宇", "陳柏豪", "王志煊", "威能帝"], "B": ["林立", "朱育賢", "陳晨威", "梁家榮", "林泓育", "馬傑森"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺", "後勁", "賴鴻誠", "黃群", "陳柏清"], "B": ["魔鷹", "王柏融", "曾子祐", "陳文杰", "杜家明", "藍寅倫"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志", "陳偉殷", "潘威倫", "陽建福", "李振昌"], "B": ["陳金鋒", "彭政閔", "林智勝", "張泰山", "高國輝", "林益全"]}
}

STADIUMS = ["台北大巨蛋", "台中洲際球場", "桃園國際球場", "台南市立球場", "新莊棒球場", "天母棒球場", "澄清湖球場", "斗六棒球場"]

PITCH_TYPES = {
    "1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球",
    "6": "速球", "7": "伸卡球", "8": "指岔球", "9": "卡特球"
}

# --- 2. 遊戲狀態 ---
game = {
    "my_team": "", "opp_team": "", "stadium": "",
    "score": [0, 0], "outs": 0, "strikes": 0, "balls": 0,
    "bases": [False, False, False], "stamina": 100,
    "message": "請選擇隊伍編號 (1-7)："
}

# --- 3. 網頁介面邏輯 ---
@app.get("/", response_class=HTMLResponse)
async def index():
    if not game["my_team"]:
        options = "".join([f'<a href="/select?id={k}"><button>{v["name"]}</button></a> ' for k,v in TEAMS.items()])
        return f"<h1>選擇你的球隊</h1>{options}"

    pitch_buttons = "".join([f'<a href="/pitch?type={v}"><button style="margin:5px; padding:10px;">{v}</button></a>' for k,v in PITCH_TYPES.items()])
    
    stamina_check = ""
    if game["stamina"] < 50:
        stamina_check = '<p>體力低於50！ <a href="/keep">1.繼續投</a> <a href="/switch">2.換投</a></p>'

    return f"""
    <html><body style="text-align:center;">
        <h1>🏟️ {game['stadium']}</h1>
        <h2>{game['my_team']} {game['score'][0]}:{game['score'][1]} {game['opp_team']}</h2>
        <p>狀態: {game['message']}</p>
        <p>壘包: {game['bases']} | 出局: {game['outs']} | 好球: {game['strikes']} | 壞球: {game['balls']}</p>
        <p>投手體力: {game['stamina']}</p>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; width:300px; margin:auto;">
            {pitch_buttons}
        </div>
        {stamina_check}
        <br><a href="/surrender">🏳️ 投降系統</a>
    </body></html>
    """

@app.get("/select")
async def select(id: str):
    game.update({"my_team": TEAMS[id]["name"], "opp_team": random.choice([t["name"] for k,t in TEAMS.items() if k != id]), "stadium": random.choice(STADIUMS)})
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(type: str):
    game["stamina"] -= 5
    # 這裡加入你的三振/保送/安打判定邏輯...
    return RedirectResponse(url="/")

@app.get("/surrender")
async def surrender():
    game["message"] = "比賽結束！要再來一場嗎？<a href='/reset'>1.要</a> <a href='/quit'>2.不玩了</a>"
    return RedirectResponse(url="/")

@app.get("/reset")
async def reset():
    game.update({"my_team": "", "score": [0,0], "outs": 0, "stamina": 100})
    return RedirectResponse(url="/")
