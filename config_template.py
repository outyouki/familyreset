"""
FamilyReset 設定

ファミリー設定をデフォルトに戻すスクリプト
"""

from familyreset import FamilyReset


# ============================================================================
# 設定
# ============================================================================

# 環境・エントリファイル設定
CONFIG = {
    'browser_type': 'chrome',  # ブラウザ: 'chrome', 'firefox', 'edge'
    'headless': False,         # False：ブラウザリストデモ　True：ブラウザ非リストデモ
    'target_url': '#{ログインURL}',

    # ログイン情報
    'login_email_label': 'メールアドレス',
    'login_email': '#{アカウント}',
    'login_password_label': 'パスワード',
    'login_password': '#{パスワード}',

    # ニックネーム
    'url_save_key': '#{ニックネーム}',

    # アプリ制制限設定の削除
    'delete_target_xpath': '//*[@id="__nuxt"]/section/div/a[1]',  # 純粋なXPath
    'delete_button_text': '設定を削除する',                      # 削除ボタン
    'confirm_button_text': '削除',                              # 削除確定ボタン
    'max_delete_iterations': 100,                               # 削除回関数

    # ジオフェス
    'container_xpath': '//*[@id="__nuxt"]/section/div/div[3]',   # コンテナXPath
    'container_delete_button_text': '削除',                     # コンテナ内の削除
    'container_confirm_button_text': '削除',                    # ダイアログの削除（Noneならしないで）
    'container_confirm_button_xpath': '//*[@id="__nuxt"]/div/div[2]/div/a[1]',            #ダイアログの削除取れない場結合、xpathで
    'max_container_delete_iterations': 100,

    # ロック
    'container_xpath1': '//*[@id="__nuxt"]/section/div/div[2]',  # コンテナXPath
    'container_delete_button_text1': '削除',  # コンテナ内の削除
    'container_confirm_button_text1': '削除',  # ダイアログの削除（Noneならしないで）
    'container_confirm_button_xpath1': '//*[@id="__nuxt"]/div/div[2]/div/a[1]',  # ダイアログの削除取れない場結合、xpathで
    'max_container_delete_iterations1': 100,
}


# ============================================================================
# タスク自動定義
# ============================================================================
#


def task_login_and_delete():
    """
    ログインして設定を一含む削除，デフォルトに戻す
    """
    print("\n" + "="*70)
    print("ログインして設定を一含む削除，デフォルトに戻す")
    print("="*70)

    fr = FamilyReset(
        browser_type=CONFIG['browser_type'],
        headless=CONFIG['headless']
    )

    # ログイン
    print("\n--- ログイン ---")
    fr.open(CONFIG['target_url'])
    fr.wait(2)
    fr.input_text(CONFIG['login_email_label'], CONFIG['login_email'])
    fr.input_text(CONFIG['login_password_label'], CONFIG['login_password'])
    fr.click_text('ログイン')
    fr.wait(3)
    fr.screenshot('after_login')

    # ホームページ
    print("\n--- ホームページ ---")
    fr.click_text_and_save_url(CONFIG['url_save_key'])
    fr.wait(1)
    fr.click_text('アプリの制限')
    fr.wait(1)
    fr.check_element('新規ダウンロードアプリを自動で利用禁止する', check=True)
    fr.click_text('閉じる')

    # アプリ制限
    print("\n--- ステップ3: 設定の一括削除 ---")
    count = fr.delete_all_settings(
        target_xpath=CONFIG['delete_target_xpath'],
        delete_button_text=CONFIG['delete_button_text'],
        confirm_button_text=CONFIG['confirm_button_text'],
        max_iterations=CONFIG['max_delete_iterations']
    )
    fr.open_saved_url(CONFIG['url_save_key'])
    fr.click_text('ジオフェンス設定')

    # ジオフェス
    print("\n--- ステップ4: コンテナ内の一含む削除 ---")
    container_count = fr.delete_items_in_container(
        container_xpath=CONFIG['container_xpath'],
        delete_button_text=CONFIG['container_delete_button_text'],
        confirm_button_text=CONFIG['container_confirm_button_text'],
        confirm_button_xpath=CONFIG['container_confirm_button_xpath'],
        max_iterations=CONFIG['max_container_delete_iterations']
    )
    fr.back()
    fr.wait(1)

    #onefamily
    fr.click_text('通知・')
    fr.wait(1)
    fr.click_text(' Oneファミリー通知 ')
    fr.check_element('バッテリー残量低下時（残10%、5%）に通知する', check=True)
    fr.check_element('歩数が設定値未満の場合、通知する', check=False)
    fr.check_element('レポートを通知する', check=True)
    fr.check_element('動画チケットの購入時に通知する', check=True)
    fr.check_element('「ジオフェンス」の出入り検知時に通知する', check=True)
    fr.check_element('アプリのリクエストを通知する', check=True)
    fr.check_element('移動状態が「乗り物」に変わった際に通知する', check=False)
    fr.click_text('設定')
    fr.click_text('閉じる')
    fr.back()
    fr.wait(1)

    #メール
    fr.click_text('メール通知')
    fr.check_element('バッテリー残量低下時（残10%、5%）に通知する', check=False)
    fr.check_element('歩数が設定値未満の場合、通知する', check=False)
    fr.check_element('動画チケットの購入時にメールで通知する', check=False)
    fr.click_text('設定')
    fr.click_text('閉じる')
    fr.back()
    fr.wait(1)

    #ロック
    fr.click_text('端末のロック')
    fr.wait(1)
    container_count1 = fr.delete_items_in_container(
        container_xpath=CONFIG['container_xpath1'],
        delete_button_text=CONFIG['container_delete_button_text1'],
        confirm_button_text=CONFIG['container_confirm_button_text1'],
        confirm_button_xpath=CONFIG['container_confirm_button_xpath1'],
        max_iterations=CONFIG['max_container_delete_iterations1']
    )
    fr.back()
    fr.wait(1)

    #TONEカメラ
    fr.click_text('TONEカメラ')
    fr.wait(1)
    fr.check_element(' 高 (標準)', check=True)
    fr.check_element('TONEカメラ以外のカメラを禁止する', check=False)
    fr.check_element('不適切な撮影が行われた場合、メールで通知する', check=False)
    fr.check_element('不適切な撮影が行われた場合、「Oneファミリー」へ通知する', check=True)
    fr.check_element('通知にサムネイル画像を含める (Oneファミリー限定)', check=True)
    fr.click_text('設定')
    fr.click_text('閉じる')
    fr.back()
    fr.wait(1)

    #GPS
    fr.click_text(' GPS ')
    fr.wait(1)
    fr.check_element('現在地情報を定期的に記録する (約30分毎)',check=True)
    fr.click_text('設定')
    fr.click_text('閉じる')
    fr.back()
    fr.wait(1)

    #ブラウザ制制限
    fr.click_text(' ブラウザアプリ制限 ')
    fr.wait(1)
    fr.check_element('あんしんインターネット以外のブラウザを制限する', check=True)
    fr.click_text('設定')
    fr.click_text('閉じる')
    fr.back()
    fr.wait(1)

    # 歩きスマホ警告
    fr.click_text(' 歩きスマホ警告 ')
    fr.wait(1)
    fr.check_element('利用者が歩きスマホをしているとき、利用端末に警告を表示する', check=False)
    fr.click_text('設定')
    fr.click_text('閉じる')
    fr.back()
    fr.wait(1)

    # その他
    fr.click_text(' その他 ')
    fr.wait(1)
    fr.check_element('動画チケットの購入時に保護者の承認を必須にする', check=True)
    fr.click_text('設定')
    fr.click_text('閉じる')
    fr.back()
    fr.wait(1)



    print(f"\n[OK] 削除完了")


    input("\nEnterでブラウザを閉じる...")
    fr.close()



if __name__ == "__main__":
    task_login_and_delete()
