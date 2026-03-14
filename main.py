from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import random

app = FastAPI()

# 簡化版的遊戲邏輯，專供網頁顯示
@app.get("/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head><title>CPBL Baseball Game</title></head>
        <body style="text-align: center; font-family: sans-serif; background: #f0f0f0;">
            <h1>⚾ 中華職棒模擬對戰 ⚾</h1>
            <div id="game-box" style="background: white; width: 400px; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <p>歡迎來到球場！請選擇你的動作：</p>
                <button onclick="play('投球')" style="padding: 10px 20px; cursor: pointer;">開始投球</button>
                <div id="result" style="margin-top: 20px; font-weight: bold; color: blue;"></div>
            </div>
            <script>
                function play(action) {
                    const results = ["好球", "壞球", "安打", "三振", "全壘打"];
                    const res = results[Math.floor(Math.random() * results.length)];
                    document.getElementById('result').innerText = "結果：" + res;
                }
            </script>
        </body>
    </html>
    """
