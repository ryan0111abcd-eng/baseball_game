import random
import time

# --- 1. 大量球員與球隊資料庫 ---
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

HIT_DIRECTIONS = {"1": "左外野", "2": "中外野", "3": "右外野", "4": "內野防區"}
STADIUMS = ["台北大巨蛋", "台中洲際球場", "桃園國際球場", "台南市立球場", "新莊球場", "天母球場"]

class BaseballGame:
    def __init__(self, my_id, opp_id):
        self.my_team = TEAMS[my_id]
        self.opp_team = TEAMS[opp_id]
        self.stadium = random.choice(STADIUMS)
        self.scores = {self.my_team['name']: 0, self.opp_team['name']: 0}
        self.inning = 1
        self.is_player_attacking = False # 規則：先守
        self.surrender = False
        self.reset_inning_state()

    def reset_inning_state(self):
        self.outs = 0
        self.strikes = 0
        self.balls = 0
        self.bases = [None, None, None] # 一二三壘跑者

    def show_status(self, p, b, last_p=""):
        bs = ["●" if x else "○" for x in self.bases]
        print(f"\n{'═'*60}\n🏟️  球場：{self.stadium} | 第 {self.inning} 局 {'下(進攻)' if self.is_player_attacking else '上(防守)'}")
        print(f"📊  比分：{self.my_team['name']} {self.scores[self.my_team['name']]} : {self.scores[self.opp_team['name']]} {self.opp_team['name']}")
        print(f"🏃  壘包：[2 {bs[1]}] [3 {bs[2]}] [1 {bs[0]}]")
        print(f"🔴  出局: {self.outs} | S: {self.strikes} B: {self.balls}")
        print(f"👤  投手: {p} | 打者: {b}")
        if last_p: print(f"⚾  球種：{last_p}")
        print(f"📢  (輸入 0 投降)\n{'═'*60}")

    def play_at_bat(self):
        p = random.choice(self.my_team['P']) if not self.is_player_attacking else random.choice(self.opp_team['P'])
        b = random.choice(self.opp_team['B']) if not self.is_player_attacking else random.choice(self.my_team['B'])
        atk_team = self.my_team['name'] if self.is_player_attacking else self.opp_team['name']

        while self.outs < 3:
            self.show_status(p, b)
            if not self.is_player_attacking:
                print("請選擇投球球種編號：", " ".join([f"[{k}]{v}" for k,v in PITCH_TYPES.items()]))
                cmd = input("投球選擇: ")
                if cmd == "0": self.surrender = True; return
                pitch_name = PITCH_TYPES.get(cmd, "直球")
            else:
                print("請選擇打擊方向編號：", " ".join([f"[{k}]{v}" for k,v in HIT_DIRECTIONS.items()]))
                cmd = input("打擊選擇: ")
                if cmd == "0": self.surrender = True; return
                pitch_name = random.choice(list(PITCH_TYPES.values()))

            # 判定邏輯
            res = random.choices(["S", "B", "H"], weights=[35, 35, 30])[0]
            if res == "S":
                self.strikes += 1; print(f"❌ 好球！({pitch_name})")
                if self.strikes >= 3:
                    print(f"⚡ 三振出局！"); self.outs += 1; self.strikes, self.balls = 0, 0
                    if self.outs < 3: break
            elif res == "B":
                self.balls += 1; print(f"🟡 壞球。({pitch_name})")
                if self.balls >= 4:
                    print(f"🚶 四壞球保送！"); self.advance(b, atk_team); break
            else:
                print(f"🔥 擊出安打！"); self.advance(b, atk_team); break

    def advance(self, batter, team):
        if self.bases[2]: self.scores[team] += 1; print(f"🎉 {self.bases[2]} 回本壘得分！")
        self.bases = [batter, self.bases[0], self.bases[1]]
        self.strikes, self.balls = 0, 0

def start_game():
    print("=== 中華職棒傳奇：終極連賽對決測試版 ===")
    for k, v in TEAMS.items(): print(f"[{k}] {v['name']}")
    my_id = input("請選擇你的隊伍編號: ")
    if my_id not in TEAMS: my_id = "1"

    while True: # 遊戲主循環
        opp_id = random.choice([k for k in TEAMS.keys() if k != my_id])
        game = BaseballGame(my_id, opp_id)
        print(f"\n🚀 新手戰開打！ {game.my_team['name']} VS {game.opp_team['name']}")

        for i in range(1, 10):
            if game.surrender: break
            game.inning = i
            # 上半局 (守備)
            game.is_player_attacking = False; game.reset_inning_state()
            while game.outs < 3 and not game.surrender: game.play_at_bat()
            if game.surrender: break
            print("\n🔄 三出局，攻守交換！")
            # 下半局 (進攻)
            game.is_player_attacking = True; game.reset_inning_state()
            while game.outs < 3 and not game.surrender: game.play_at_bat()

        if game.surrender:
            print(f"\n🏳️  你選擇了投降。比賽提前結束，判定 {game.my_team['name']} 敗北。")
        else:
            print(f"\n🏆 九局比賽結束！最終比分: {game.my_team['name']} {game.scores[game.my_team['name']]} : {game.scores[game.opp_team['name']]} {game.opp_team['name']}")

        # 賽後續戰選單
        print("\n" + "═"*40)
        print("1. 要，比下一場 (繼續遊戲)")
        print("2. 不玩了 (遊戲結束)")
        choice = input("你的選擇: ")
        if choice != "1":
            print("\n⚾ 感謝遊玩，下次再見！")
            break
        print("\n🏟️  球探正在尋找下一個對手...")
        time.sleep(1)


















































if __name__ == "__main__":
    start_game()



