import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# 1. 豐富的資料庫
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉", "呂彥青", "鄭凱文", "余謙", "魏碩成"], "B": ["王威晨", "江坤宇", "陳子豪", "許基宏", "詹子賢", "岳東華"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈", "曾峻岳", "陳仕朋", "張奕", "黃保羅"], "B": ["張育成", "王正棠", "范國宸", "申皓瑋", "戴培峰", "林哲瑄"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士", "陳韻文", "胡智爲", "林詔恩", "羅昂"], "B": ["陳傑憲", "蘇智傑", "林安可", "邱智呈", "陳鏞基", "潘傑楷"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍", "陳冠偉", "林凱威", "銳歐", "伍鐸"], "B": ["吉力吉撈", "郭天信", "李凱威", "劉基鴻", "拿莫．伊漾", "張祐銘"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂", "陳冠宇", "陳柏豪", "王志煊", "威能帝"], "B": ["林立", "朱育賢", "陳晨威", "梁家榮", "林泓育", "馬傑森"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺", "後勁", "賴鴻誠", "黃群", "陳柏清"], "B": ["魔鷹", "王柏融", "曾子祐", "陳文杰", "杜家明", "藍寅倫"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志", "陳偉殷", "潘威倫", "陽建福", "李振昌"], "B": ["陳金鋒", "彭政閔", "林智勝", "張泰山", "高國輝", "林益全"]}
}

STADIUMS = ["台北大巨蛋", "台中洲際球場", "桃園國際球場", "台南市立球場", "新莊棒球場", "天母棒球場", "澄清湖球場", "斗六球場"]
PITCH_TYPES = {"1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球", "6": "速球", "7": "伸卡球", "8": "指岔球", "9": "卡特球"}

# 2. 遊戲狀態
game = {"my_team": None, "opp_team": None, "score": [0,0], "stamina": 100, "outs": 0, "strikes": 0, "balls": 0, "stadium": ""}

@app.get("/", response_class=HTMLResponse)
async def index():
    if not game["my_team"]:
        teams_html = "".join([f'<a href="/select?id={k}"><button>{v["name"]}</button></a> ' for k, v in TEAMS.items()])
        return f"<h1>歡迎來到 CPBL 棒球模擬器</h1><p>請選擇你的隊伍：</p>{teams_html}"

    pitch_btns = "".join([f'<a href="/pitch?type={v}"><button style="margin:5px;">{v}</button></a>' + ("<br>" if k in ["3","6"] else "") for k,v in PITCH_TYPES.items()])
    
    # 加入背景、音樂與狀態顯示
    return f"""
    <html style="background: url('images.jpg') no-repeat center center fixed; background-size: cover;">
    <body style="text-align:center; color:white; font-weight:bold; background: rgba(0,0,0,0.5); padding:20px;">
        <audio autoplay loop><source src="bgm.mp3" type="audio/mpeg"></audio>
        <h1>🏟️ {game['stadium']}</h1>
        <h2>{game['my_team']} {game['score'][0]} : {game['score'][1]} {game['opp_team']}</h2>
        <p>投手體力: {game['stamina']} | 出局: {game['outs']} | 好球: {game['strikes']} | 壞球: {game['balls']}</p>
        <div>{pitch_btns}</div>
        {'<p>體力低於50！<a href="/keep">1.繼續投</a> <a href="/switch">2.換投</a></p>' if game['stamina'] < 50 else ''}
        <br><a href="/surrender" style="color:red;">🏳️ 投降系統</a>
    </body></html>
    """

@app.get("/select")
async def select(id: str):
    game.update({"my_team": TEAMS[id]["name"], "opp_team": random.choice([t["name"] for k,t in TEAMS.items() if k!=id]), "stadium": random.choice(STADIUMS), "score": [0,0], "stamina":100})
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(type: str):
    game["stamina"] -= 5
    # 此處邏輯根據規則進行判定
    return RedirectResponse(url="/")

@app.get("/surrender")
async def surrender():
    return HTMLResponse("<h1>比賽結束！</h1><a href='/'>1.要，比下一場</a> <a href='/'>2.不玩了</a>")@app.get("/", response_class=HTMLResponse)
async def index():
    # 這是你的遊戲介面，加入 CSS 來處理背景與音效
    return f"""
    <html>
    <head>
        <style>
            body {{
                background: url('images.jpg') no-repeat center center fixed;
                background-size: cover;
                color: white;
                text-align: center;
                font-family: Arial, sans-serif;
            }}
            .container {{ background: rgba(0, 0, 0, 0.6); padding: 20px; border-radius: 15px; display: inline-block; }}
            button {{ padding: 10px; margin: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <audio autoplay loop>
            <source src="bgm.mp3" type="audio/mpeg">
        </audio>
        
        <div class="container">
            <h1>🏟️ 天母棒球場</h1>
            <h2>中信兄弟 0 : 0 味全龍</h2>
            <p>投手體力: 100 | 出局: 0 | 好球: 0 | 壞球: 0</p>
            
            <div style="max-width: 300px; margin: auto;">
                {"".join([f'<button>{pitch}</button>' for pitch in ["直球", "曲球", "變化球", "滑球", "變速球", "速球", "伸卡球", "指岔球", "卡特球"]])}
            </div>
            
            <br><a href="/surrender" style="color:red;">🏳️ 投降系統</a>
        </div>
    </body>
    </html>
    """
