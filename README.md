# FamilyReset

自動化操作ツール - Seleniumベースのブラウザ自動化と画像認識

## プロジェクト構造

```
FamilyReset/
├── requirements.txt       # プロジェクトの依存関係
├── README.md             # プロジェクトの説明
├── src/
│   └── core/
│       ├── __init__.py
│       ├── browser.py     # ブラウザ制御モジュール
│       ├── recognizer.py  # 画像認識モジュール
│       └── controller.py  # マウスキーボード制御モジュール
└── images/
    └── 58/
        ├── templates/    # テンプレート画像保存ディレクトリ
        └── screenshots/  # スクリーンショット保存ディレクトリ
```

## 依存関係のインストール

1. 仮想環境の作成（推奨）：
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または venv\Scripts\activate  # Windows
```

2. 依存関係のインストール：
```bash
pip install -r requirements.txt
```

## コアモジュールの説明

### 1. BrowserController (browser.py)
Seleniumベースのブラウザコントローラー、以下をサポート：
- Chrome、Firefox、Edgeブラウザ
- 要素の検索と操作
- ページのスクリーンショット
- JavaScriptの実行

### 2. ImageRecognizer (recognizer.py)
OpenCVベースの画像認識モジュール、以下をサポート：
- テンプレートマッチング
- 特徴量マッチング
- 複数テンプレートの同時検索

### 3. MouseController (controller.py)
pyautoguiベースのマウスキーボード制御、以下をサポート：
- マウスの移動とクリック
- キーボード入力
- ホットキー監視

## 使用方法

`58_bot_v2.py` の `OPERATIONS` リストを編集して操作フローを定義します：

```python
OPERATIONS = [
    # URLを開く
    {'type': 'open_url', 'url': 'https://example.com'},

    # 待機
    {'type': 'wait', 'seconds': 2},

    # テキストをクリック
    {'type': 'click_text', 'text': 'ボタン文字'},

    # XPathでクリック
    {'type': 'click_xpath', 'xpath': '//button[@class="btn"]'},

    # ページをまたいで全要素をクリック
    {'type': 'click_xpath_all_pages',
     'xpath': '//ul/li',
     'next_page_text': '次のページ'},
]
```


## 操作タイプの説明

| タイプ | 説明 | パラメータ |
|------|------|------|
| `open_url` | URLを開く | `url` |
| `wait` | 待機 | `seconds` |
| `click_text` | テキストを含む要素をクリック | `text`, `exact_match` |
| `click_xpath` | XPathでクリック | `xpath`, `index` |
| `click_xpath_all` | XPathで全てクリック | `xpath`, `wait_after_each` |
| `click_xpath_all_pages` | ページをまたいで全てクリック | `xpath`, `next_page_text`, `max_pages` |
| `click_image` | 画像認識でクリック | `template` |
| `switch_tab` | タブを切り替え | - |
| `screenshot` | スクリーンショットを保存 | `filename` |

## 注意事項

1. Chromeブラウザ（またはFirefox/Edge）のインストールが必要
2. 初回実行時に対応するWebDriverが自動ダウンロードされます
3. 画像認識にはテンプレート画像を `images/58/templates/` ディレクトリに配置する必要があります

## License

MIT
