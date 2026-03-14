import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# --- 1. 資料庫 ---
TEAMS = {
    "1": {"name": "中信兄弟", "P": ["德保拉", "吳俊偉", "呂彥青", "鄭凱文"], "B": ["王威晨", "江坤宇", "陳子豪", "許基宏"]},
    "2": {"name": "富邦悍將", "P": ["江少慶", "富藍戈", "曾峻岳", "張奕"], "B": ["張育成", "王正棠", "范國宸", "申皓瑋"]},
    "3": {"name": "統一獅", "P": ["古林睿煬", "勝騎士", "陳韻文", "胡智為"], "B": ["陳傑憲", "蘇智傑", "林安可", "邱智呈"]},
    "4": {"name": "味全龍", "P": ["徐若熙", "鋼龍", "陳冠偉", "林凱威"], "B": ["吉力吉撈", "郭天信", "李凱威", "劉基鴻"]},
    "5": {"name": "樂天桃猿", "P": ["黃子鵬", "魔神樂", "陳冠宇", "陳柏豪"], "B": ["林立", "朱育賢", "陳晨威", "梁家榮"]},
    "6": {"name": "台鋼雄鷹", "P": ["哈瑪星", "江承諺", "後勁", "陳柏清"], "B": ["魔鷹", "王柏融", "曾子祐", "陳文杰"]},
    "7": {"name": "中華隊", "P": ["王建民", "郭泓志", "陳偉殷", "潘威倫"], "B": ["陳金鋒", "彭政閔", "林智勝", "張泰山"]}
}
PITCH_TYPES = {"1": "直球", "2": "曲球", "3": "變化球", "4": "滑球", "5": "變速球"}

# --- 2. 狀態管理 ---
game = {"active": False, "my_team": None, "opp_team": None, "score": [0,0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0, "stamina": 100, "last_event": "遊戲開始！", "pitcher": "", "batter": ""}

def reset_game():
    game.update({"active": False, "score": [0,0], "inning": 1, "outs": 0, "strikes": 0, "balls": 0, "stamina": 100, "last_event": "比賽開始！"})

# --- 3. UI 渲染 ---
def render_page(content):
    return f"""<html><head><style>
        body {{ background: url('images.jpg') no-repeat center center fixed; background-size: cover; color: black; font-family: sans-serif; text-align: center; }}
        .box {{ background: rgba(255, 255, 255, 0.9); padding: 25px; border-radius: 20px; display: inline-block; margin-top: 50px; border: 2px solid #000; width: 80%; max-width: 500px; }}
        button {{ padding: 10px 15px; margin: 5px; cursor: pointer; border-radius: 5px; border: 1px solid #000; font-weight: bold; background: #fff; }}
    </style></head>
    <body onclick="document.getElementById('bgm').play();">
        <audio id="bgm" loop><source src="bgm.mp3" type="audio/mpeg"></audio>
        <div class="box"><h1 style='color:black;'>⚾ CPBL中華職棒傳奇 測試版</h1>{content}</div>
    </body></html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    if not game["active"]:
        btns = "".join([f'<a href="/select?id={k}"><button>{v["name"]}</button></a>' for k,v in TEAMS.items()])
        return render_page(f"<h3>請選擇你的球隊：</h3>{btns}")
    
    pitch_btns = "".join([f'<a href="/pitch?id={k}"><button>{v}</button></a>' for k,v in PITCH_TYPES.items()])
    stamina_color = "red" if game['stamina'] < 30 else "black"
    stamina_ui = f"<div style='color:{stamina_color}; margin:10px;'>⚡ 投手體力：{game['stamina']} <a href='/change'><button>更換投手</button></a></div>"
    
    content = f"""
        <h3>{game['my_team']} vs {game['opp_team']} | 第 {game['inning']} 局</h3>
        <p>投手: {game['pitcher']} | 打者: {game['batter']}</p>
        <h2 style='font-size:32px;'>🔴 OUT: {game['outs']} | S: {game['strikes']} | B: {game['balls']}</h2>
        <div style='background:#eee; padding:10px; border-radius:10px;'>{game['last_event']}</div>
        <div style='margin-top:15px;'>{pitch_btns}</div>
        {stamina_ui}
        <br><a href='/quit'><button style='background:#fdd;'>結束比賽</button></a>
    """
    return render_page(content)

@app.get("/select")
async def select(id: str):
    game.update({"active": True, "my_team": TEAMS[id]["name"], "opp_team": "對手球隊", "pitcher": random.choice(TEAMS[id]["P"]), "batter": "強打者"})
    return RedirectResponse(url="/")

@app.get("/pitch")
async def pitch(id: str):
    game["stamina"] -= random.randint(4, 10)
    if game["stamina"] < 0: game["stamina"] = 0
    r = random.random()
    if r < 0.4:
        game["strikes"] += 1
        game["last_event"] = f"投出{PITCH_TYPES[id]}，好球！"
        if game["strikes"] >= 3: game["outs"]+=1; game["strikes"]=0; game["balls"]=0; game["last_event"]="三振出局！"
    elif r < 0.7:
        game["balls"] += 1
        game["last_event"] = "壞球。"
        if game["balls"] >= 4: game["last_event"]="四壞球保送！"; game["strikes"]=0; game["balls"]=0
    else:
        game["outs"]+=1; game["strikes"]=0; game["balls"]=0; game["last_event"]="擊球被接殺！"
    
    if game["outs"] >= 3: game["inning"]+=1; game["outs"]=0; game["last_event"]="三出局，換局！"
    return RedirectResponse(url="/")

@app.get("/change")
async def change(): game["stamina"] = 100; return RedirectResponse(url="/")
@app.get("/quit")
async def quit(): reset_game(); return RedirectResponse(url="/")
