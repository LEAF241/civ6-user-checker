import os
import re

# ==========================================
# 設定
# ==========================================
WATCH_LIST_FILE = "watchlist.txt"

# ==========================================
# ツール関数
# ==========================================

def extract_steam_id(input_text):
    """
    入力文字列からSteamID(17桁の数字)を抽出する。
    URLが貼り付けられた場合にも対応。
    """
    # 7656から始まる17桁の数字を探す
    match = re.search(r"(7656\d{13})", input_text)
    if match:
        return match.group(1)
    # 単純に17桁の数字があるか探す（7656以外で始まるレアケース対応）
    match_simple = re.search(r"(\d{17})", input_text)
    if match_simple:
        return match_simple.group(1)
    return None

def check_duplicate(filename, target_id):
    """ファイル内にIDが既に存在するかチェック"""
    if not os.path.exists(filename):
        return False
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            if target_id in content:
                return True
    except:
        return False
    return False

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==============================================")
    print(" Civ6 Watchlist Adder")
    print(" リスト追加ツール")
    print("==============================================")
    print(f"対象ファイル: {WATCH_LIST_FILE}\n")

    # ファイル追記モードで開く
    try:
        # ファイルがない場合は作成
        if not os.path.exists(WATCH_LIST_FILE):
            with open(WATCH_LIST_FILE, "w", encoding="utf-8") as f:
                f.write("# 形式: SteamID, [名前] 理由\n")

        while True:
            print("-" * 30)
            
            # 1. ID入力
            while True:
                raw_input = input("Steam ID または URLを入力: ").strip()
                if not raw_input: continue
                
                steam_id = extract_steam_id(raw_input)
                
                if steam_id:
                    # 重複チェック
                    if check_duplicate(WATCH_LIST_FILE, steam_id):
                        print(f"⚠ 警告: このID ({steam_id}) は既にリストに存在します。")
                        confirm = input("それでも追加しますか？ (y/n): ").lower()
                        if confirm != 'y':
                            steam_id = None # ループやり直し
                            continue
                    
                    print(f"OK: ID {steam_id} を認識しました。")
                    break
                else:
                    print("× エラー: 有効なSteam IDが見つかりません。")
                    print("  (17桁の数字、またはプロフィールURLを入力してください)")

            # 2. 名前入力
            name = input("プレイヤー名 (省略可): ").strip()
            if not name:
                name = "Unknown"

            # 3. 理由入力
            reason = input("BAN/注意の理由: ").strip()
            if not reason:
                reason = "理由なし"

            # 4. 書き込み処理
            # 形式: ID, [Name] Reason
            line_to_write = f"{steam_id}, [{name}] {reason}\n"
            
            with open(WATCH_LIST_FILE, "a", encoding="utf-8") as f:
                f.write(line_to_write)
            
            print(f"\n>> 追加しました: [{name}] {reason}")

            # 5. 続行確認
            cont = input("\n続けて追加しますか？ (Enter=はい / n=終了): ").lower()
            if cont == 'n':
                break

    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        input("Enterを押して終了...")

    print("\n終了しました。監視スクリプト(civ6_watch_v2.py)を再起動すると反映されます。")
    time.sleep(2)

if __name__ == "__main__":
    import time
    main()