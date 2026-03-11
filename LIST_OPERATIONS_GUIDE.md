# リスト操作機能ガイド

## 📋 機能概要

ページにリスト（一覧）が表示される場合、アカウントによって表示内容が異なる場合があります。FamilyReset はリストを自動的に読み取り、操作を選択するソリューションを提供します。

---

## 🎯 主な機能

### 1. `get_list_items()` - リストの自動読み取り
ページのリスト構造（ul/ol/table/divなど）を自動認識し、すべてのリスト項目を返します。

```python
items = fr.get_list_items()

# 返却形式:
# [
#   {'index': 0, 'text': '項目1', 'element': <WebElement>},
#   {'index': 1, 'text': '項目2', 'element': <WebElement>},
#   ...
# ]
```

### 2. `select_and_click_list()` - インタラクティブ選択
リストを表示してユーザーに選択させ、選択された項目を自動クリックします。

```python
fr.select_and_click_list(
    list_selector=None,  # オプション: リストセレクターを指定
    prompt="操作する項目を選択してください"
)
```

### 3. `click_list_item()` - 指定インデックスをクリック
リストのN番目の項目を直接クリックします。

```python
fr.click_list_item(0)  # 1番目の項目をクリック
fr.click_list_item(2)  # 3番目の項目をクリック
```

### 4. `find_all_by_text()` - すべての一致要素を検索
ページ上の指定した文字を含むすべての要素を検索します。

```python
elements = fr.find_all_by_text('確認', exact_match=False)
```

### 5. `get_text_list()` - すべてのテキストを取得
ページのすべてのテキストコンテンツを取得します。

```python
texts = fr.get_text_list()
for text in texts:
    print(text)
```

---

## 💡 使用シナリオ

### シナリオ1: ログイン後に項目を選択

```python
from familyreset import FamilyReset

fr = FamilyReset()

# 1. ログイン
fr.open('https://example.com/login')
fr.input_text('ユーザー名', 'admin')
fr.input_text('パスワード', '123456')
fr.click_text('ログイン')
fr.wait(3)

# 2. リストを読み取り
items = fr.get_list_items()
print(f"{len(items)} 個の項目が見つかりました")

# 3. ユーザーに選択させる
fr.select_and_click_list(prompt="確認する項目を選択してください")
```

### シナリオ2: N番目の項目を直接クリック

```python
fr.click_list_item(0)  # 1番目をクリック
fr.wait(2)
fr.screenshot()
```

### シナリオ3: カスタムセレクターを使用

```python
# 自動認識が失敗した場合、セレクターを指定可能
items = fr.get_list_items(list_selector='//div[@id="item-list"]//li')

# または
fr.click_list_item(0, list_selector='//div[@class="data-list"]//tr')
```

### シナリオ4: 特定の文字を含む項目を検索してクリック

```python
# "確認"を含むすべての要素を検索
elements = fr.find_all_by_text('確認', exact_match=False)

# 最初のものをクリック
if elements:
    elements[0].click()
```

---

## 🔧 サポートされるリスト構造

`get_list_items()` は以下のリスト構造を自動的に認識しようとします：

1. **順不同リスト** - `<ul><li>`
2. **順序リスト** - `<ol><li>`
3. **テーブル** - `<table><tr><td>`
4. **カスタムリスト** - `<div class="list">` または `<div class="item">`
5. **カスタムセレクター** - `list_selector` パラメーターで指定

---

## 📝 完全な例

### 例1: タスク3（config.py に含まれています）

```python
def task_with_list():
    """ログイン後にリストを処理"""
    fr = FamilyReset()

    # ログイン
    fr.open('https://family.tone.ne.jp/v2/manager/signIn')
    fr.wait(2)
    fr.input_text('メールアドレス', 'your@email.com')
    fr.input_text('パスワード', 'password')
    fr.click_text('ログイン')
    fr.wait(3)

    # リストを読み取り
    items = fr.get_list_items()

    # リストを表示
    for item in items:
        print(f"[{item['index']}] {item['text']}")

    # ユーザー選択
    choice = input("選択肢を入力してください: ")
    fr.click_list_item(int(choice))

    fr.wait(2)
    fr.screenshot()
```

### 例2: インタラクティブ選択を使用

```python
fr = FamilyReset()

# ログイン
fr.open('https://example.com')
fr.input_text('ユーザー名', 'admin')
fr.input_text('パスワード', '123456')
fr.click_text('ログイン')
fr.wait(3)

# ユーザーにリスト項目を選択させる
fr.select_and_click_list(prompt="確認する注文を選択してください")
```

### 例3: 複数のリスト項目を処理

```python
fr = FamilyReset()

# ログインしてリストを読み取り
fr.open('https://example.com')
fr.wait(2)

items = fr.get_list_items()

# 各項目を処理
for i in range(len(items)):
    print(f"処理中: {i+1}/{len(items)} 項目...")

    # クリック
    fr.click_list_item(i)
    fr.wait(2)

    # 操作を実行（スクリーンショット、ダウンロードなど）
    fr.screenshot(f'item_{i}')

    # リストに戻る
    fr.back()
    fr.wait(2)
```

---

## ⚠️ トラブルシューティング

### 問題1: リスト項目が見つからない

**解決策：**
1. ページのすべてのテキストを確認: `fr.get_text_list()`
2. カスタムセレクターを使用: `fr.get_list_items(list_selector='//xpath')`
3. ブラウザ開発者ツールで正しい XPath を取得

```python
# ページのすべてのテキストを取得し、リスト内容を確認
texts = fr.get_text_list()
for text in texts:
    if 'キーワード' in text:
        print(text)
```

### 問題2: リスト認識が正しくない

**解決策:** 明確なリストセレクターを指定

```python
# 例: テーブル
fr.get_list_items(list_selector='//table[@id="data-table"]//tr')

# 例: divリスト
fr.get_list_items(list_selector='//div[@class="item-list"]//div[@class="item"]')
```

### 問題3: クリック後にページ遷移し、操作を続けられない

**解決策:** `switch_tab()` を使用するか、新しいタブで操作

```python
fr.click_list_item(0)
fr.wait(2)

# 新しいタブが開いた場合
fr.switch_tab(-1)  # 最新のタブに切り替え

# 操作を続ける...
```

---

## 🚀 高度なテクニック

### テクニック1: リスト項目のフィルタリング

```python
items = fr.get_list_items()

# 特定の文字を含む項目のみ表示
filtered = [item for item in items if '重要' in item['text']]

for item in filtered:
    print(f"[{item['index']}] {item['text']}")
```

### テクニック2: 一括操作

```python
items = fr.get_list_items()

# 最初の5項目をクリック
for i in range(min(5, len(items))):
    fr.click_list_item(i)
    fr.wait(2)
    fr.back()
    fr.wait(1)
```

### テクニック3: 文字で検索してクリック

```python
# "未処理"を含む項目を見つけてクリック
items = fr.get_list_items()

for item in items:
    if '未処理' in item['text']:
        index = item['index']
        fr.click_list_item(index)
        break
```

---

## 📖 クイックリファレンス

| メソッド | 説明 | 例 |
|------|------|------|
| `get_list_items()` | リストを読み取り | `items = fr.get_list_items()` |
| `click_list_item(n)` | N番目の項目をクリック | `fr.click_list_item(0)` |
| `select_and_click_list()` | インタラクティブ選択 | `fr.select_and_click_list()` |
| `find_all_by_text(text)` | すべての一致要素を検索 | `fr.find_all_by_text('確認')` |
| `get_text_list()` | すべてのテキストを取得 | `texts = fr.get_text_list()` |

---

## 💬 ヘルプが必要ですか？

自動認識が動作しない場合：

1. **ページテキストを確認**
   ```python
   texts = fr.get_text_list()
   for i, text in enumerate(texts):
       print(f"{i}: {text}")
   ```

2. **ブラウザ開発者ツールを使用**
   - F12 で開発者ツールを開く
   - 要素セレクターでリスト構造を確認
   - XPath をコピー

3. **カスタムセレクターを使用**
   ```python
   fr.get_list_items(list_selector='コピーしたXPath')
   ```
