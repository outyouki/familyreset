# FamilyReset 機能ガイド

## 📋 目次
- [基本操作](#基本操作)
- [文字で要素を操作](#文字で要素を操作)
- [要素情報の取得](#要素情報の取得)
- [クリック操作](#クリック操作)
- [入力操作](#入力操作)
- [チェックボックス/ラジオボタン](#チェックボックスラジオボタン)
- [スクロール操作](#スクロール操作)
- [ページ操作](#ページ操作)
- [タブ操作](#タブ操作)
- [待機操作](#待機操作)

---

## 基本操作

### URLを開く
```python
fr.open('https://example.com')
```

### 待機
```python
fr.wait(3)  # 3秒待機
```

### スクリーンショット
```python
fr.screenshot('filename')  # スクリーンショットを保存
fr.screenshot()            # ファイル名を自動生成
```

---

## 文字で要素を操作

### 文字をクリック
```python
fr.click_text('ログイン')                    # 完全一致
fr.click_text('ログイン', exact_match=True)
fr.click_text('登', exact_match=False)       # 部分一致
fr.click_text('送信', wait_after=2)          # クリック後2秒待機
```

### テキストを入力
```python
# ラベル文字に基づいて入力
fr.input_text('ユーザー名', 'admin')
fr.input_text('パスワード', '123456')

# ラベル自体が入力欄の場合
fr.input_text('検索', 'キーワード', find_input=False)
```

### 入力後にエンター
```python
fr.input_and_enter('検索', 'キーワード')
```

### ドロップダウンを選択
```python
fr.select_option('国', '日本')
fr.select_option('都市', '東京')
```

---

## 要素情報の取得

### 要素のテキストを取得
```python
text = fr.get_text('タイトル')
print(text)  # 出力: タイトルのテキスト内容
```

### 要素の属性を取得
```python
href = fr.get_attr('リンク', 'href')
class_name = fr.get_attr('ボタン', 'class')
id_value = fr.get_attr('要素', 'id')
```

### 要素が存在するかチェック
```python
if fr.exists('ログインボタン'):
    print('ボタンが存在します')
```

### 要素が出現するのを待機
```python
# 最大30秒待機
if fr.wait_for_text('読み込み完了', timeout=30):
    print('読み込み完了')
```

---

## クリック操作

### 文字をクリック（基本）
```python
fr.click_text('ログイン')
```

### XPathでクリック
```python
fr.click_xpath('//div[@id="submit"]')
fr.click_xpath('//button', index=1)  # 2番目のボタンをクリック
```

### ダブルクリック
```python
fr.double_click_text('ファイル')
```

### マウスホバー
```python
fr.hover_text('メニュー')
```

---

## 入力操作

### テキストを入力
```python
fr.input_text('ユーザー名', 'admin')
```

### 入力後にエンター
```python
fr.input_and_enter('検索', 'キーワード')
```

### 入力欄をクリア
```python
fr.clear_input('ユーザー名')
```

---

## チ�クボックス/ラジオボタン

### チェックを入れる
```python
fr.check_element('利用規約に同意', check=True)
fr.check_element('パスワードを保存')
```

### チェックを外す
```python
fr.check_element('利用規約に同意', check=False)
```

---

## スクロール操作

### 指定ピクセル分スクロール
```python
fr.scroll(500)    # 下に500ピクセルスクロール
fr.scroll(-500)   # 上に500ピクセルスクロール
```

### 指定した文字までスクロール
```python
fr.scroll_to_text('下部')
```

### トップ/ボトムへスクロール
```python
fr.scroll_to_top()
fr.scroll_to_bottom()
```

---

## ページ操作

### 戻る/進む/更新
```python
fr.back()
fr.forward()
fr.refresh()
```

### 現在の情報を取得
```python
url = fr.get_url()
title = fr.get_title()
html = fr.get_page_source()
```

### JavaScriptを実行
```python
fr.execute_js('alert("Hello")')
fr.execute_js('window.scrollTo(0, 1000)')

# 戻り値を取得
height = fr.execute_js('return document.body.scrollHeight')
```

---

## タブ操作

### タブを切り替え
```python
fr.switch_tab()        # 最新のタブに切り替え
fr.switch_tab(0)       # 最初のタブに切り替え
fr.switch_tab(-1)      # 最後のタブに切り替え
```

---

## 待機操作

### 固定待機
```python
fr.wait(3)  # 3秒待機
```

### 要素が出現するのを待機
```python
fr.wait_for_text('読み込み完了', timeout=30)
```

---

## 完全な例

### 例1: 自動ログイン
```python
from familyreset import FamilyReset

fr = FamilyReset()
fr.open('https://example.com/login')
fr.wait(2)
fr.input_text('ユーザー名', 'admin')
fr.input_text('パスワード', '123456')
fr.check_element('ログイン状態を保持')
fr.click_text('ログイン')
fr.wait(3)
fr.screenshot('login_success')
```

### 例2: 検索して閲覧
```python
from familyreset import FamilyReset

fr = FamilyReset()
fr.open('https://example.com')
fr.input_and_enter('検索', 'Pythonチュートリアル')
fr.wait(2)
fr.scroll_to_text('関連結果')
fr.click_text('最初の結果')
fr.wait(3)
fr.screenshot()
```

### 例3: フォーム記入
```python
from familyreset import FamilyReset

fr = FamilyReset()
fr.open('https://example.com/form')
fr.wait(1)

# テキスト記入
fr.input_text('名前', '田中')
fr.input_text('メールアドレス', 'test@example.com')
fr.input_and_enter('携帯電話番号', '09012345678')

# ドロップダウンを選択
fr.select_option('性別', '男')
fr.select_option('都市', '東京')

# チェックボックスにチェック
fr.check_element('利用規約に同意')

# 送信
fr.click_text('送信')
fr.wait(3)
```

### 例4: チェックと待機
```python
from familyreset import FamilyReset

fr = FamilyReset()
fr.open('https://example.com')

# ページ読み込み完了を待機
if fr.wait_for_text('読み込み完了', timeout=30):
    print('ページ読み込み成功')
else:
    print('読み込みタイムアウト')

# 要素が存在するかチェック
if fr.exists('ログインボタン'):
    fr.click_text('ログインボタン')
else:
    print('既にログイン済みです')
```

---

## ヒント

1. **完全一致 vs 部分一致**
   - `exact_match=True`: テキストが完全に一致する必要がある（デフォルト）
   - `exact_match=False`: テキストが含まれていればよい

2. **メソッドチェーン**
   - すべてのメソッドが `self` を返すため、チェーン呼び出しが可能
   - 例: `fr.open('url').wait(2).click_text('ログイン')`

3. **エラー処理**
   - 要素が見つからない場合、エラーログを記録しますが、プログラムは中断しません
   - `exists()` で要素が存在するかチェックすることを推奨

4. **待機時間**
   - `wait()`: 固定待機
   - `wait_for_text()`: スマート待機、指定した時間まで待機
