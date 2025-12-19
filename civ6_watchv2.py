import os
import time
import re
import winsound
import sys

# ==========================================
# 設定エリア
# ==========================================

# 外部リストファイル名
WATCH_LIST_FILE = "watchlist.txt"

# ログファイルのパス (AppData/Local を参照)
LOCAL_APP_DATA = os.environ.get('LOCALAPPDATA')
LOG_FILE_PATH = os.path.join(LOCAL_APP_DATA, r"Firaxis Games\Sid Meier's Civilization VI\Logs\net_connection_debug.log")

# プレイヤー名を一時保存する辞書 {SteamID: Name}
known_players = {}

# ==========================================
# ファイル読み込み処理
# ==========================================

def load_watchlist(filename):
    """外部ファイルからウォッチリストを読み込む"""
    watch_list = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)

    if not os.path.exists(file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# SteamID, 理由\n")
        except:
            pass
        return watch_list

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                parts = line.split(",", 1)
                if len(parts) == 2:
                    s_id = parts[0].strip()
                    watch_list[s_id] = parts[1].strip()
    except Exception as e:
        print(f"リスト読み込みエラー: {e}")

    return watch_list

# ==========================================
# 通知・表示処理
# ==========================================

def play_alert_sound(is_danger):
    """音を鳴らす (danger=警告音, False=通知音)"""
    try:
        if is_danger:
            # 警告音（高めの音で3回）
            winsound.Beep(1000, 200)
            winsound.Beep(1000, 200)
            winsound.Beep(2000, 500)
        else:
            # 退室時などは少し控えめな音
            winsound.Beep(800, 300)
    except:
        pass

def log_print(message, color_code=""):
    """タイムスタンプ付きでプリント"""
    timestamp = time.strftime("%H:%M:%S")
    # ANSIエスケープシーケンス (Windows 10以降のコンソールで有効)
    reset = "\033[0m"
    print(f"[{timestamp}] {color_code}{message}{reset}")

# ==========================================
# メイン処理
# ==========================================

def follow(file):
    """ファイルの末尾を監視し続ける"""
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==============================================")
    print(" Civ6 Lobby Monitor V3 (Sound Only)")
    print(f" Target Log: {LOG_FILE_PATH}")
    
    watch_list = load_watchlist(WATCH_LIST_FILE)
    print(f" Watch List: {len(watch_list)} IDs loaded")
    print("==============================================")
    print("Waiting for connection logs...")

    # ログファイル待機
    while not os.path.exists(LOG_FILE_PATH):
        print(f"Log file not found. Please start Civ6... ", end="\r")
        time.sleep(3)

    print(f"\nMonitoring started.\n")

    # 正規表現パターンの定義
    regex_join = re.compile(r"Steam ConnectionID Created: \d+ \((.*?) \[(\d{17})\]\)")
    regex_leave = re.compile(r"Steam Connection Closed: (\d{17})")

    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8", errors='ignore') as logfile:
            loglines = follow(logfile)
            
            for line in loglines:
                # --- 入室検知 (JOIN) ---
                match_join = regex_join.search(line)
                if match_join:
                    p_name = match_join.group(1)
                    p_id = match_join.group(2)
                    
                    # 名前を記憶
                    known_players[p_id] = p_name

                    if p_id in watch_list:
                        # ターゲット入室！ (音 + 赤文字)
                        reason = watch_list[p_id]
                        msg = f"!!! WARNING !!! {p_name} ({reason}) が入室しました [ID:{p_id}]"
                        log_print(msg, "\033[31m") # 赤文字
                        play_alert_sound(True)     # 警告音のみ
                    else:
                        # 一般プレイヤー入室 (水色文字)
                        msg = f"[+] Join: {p_name} [ID:{p_id}]"
                        log_print(msg, "\033[96m") 

                # --- 退室検知 (LEAVE) ---
                match_leave = regex_leave.search(line)
                if match_leave:
                    p_id = match_leave.group(1)
                    p_name = known_players.get(p_id, "Unknown")
                    
                    if p_id in watch_list:
                        # ターゲット退室 (音 + 黄色文字)
                        reason = watch_list[p_id]
                        msg = f"!!! LEAVE !!! 警戒対象 {p_name} ({reason}) が退室しました"
                        log_print(msg, "\033[33m") # 黄色文字
                        play_alert_sound(False)    # 退出音
                    else:
                        # 一般プレイヤー退室 (灰色文字)
                        msg = f"[-] Left: {p_name} [ID:{p_id}]"
                        log_print(msg, "\033[90m")

    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()