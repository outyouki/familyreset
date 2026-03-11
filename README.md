# FamilyReset

ファミリー設定をデフォルトに戻すための自動化ツール - Seleniumベースのブラウザ自動化

## プロジェクト構造

```
FamilyReset/
├── config.py             # 設定ファイル（ログイン情報・各種パラメータ）
├── familyreset.py        # メインプログラム
├── familyreset_ja.py     # 日本語版メインプログラム
├── requirements.txt      # プロジェクトの依存関係
├── README.md            # プロジェクトの説明
├── src/
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       ├── browser.py    # ブラウザ制御モジュール
│       ├── recognizer.py # 画像認識モジュール
│       └── controller.py # マウスキーボード制御モジュール
└── images/
    └── screenshots/      # スクリーンショット保存ディレクトリ
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

## 設定ファイル (config.py)

`config.py` はファミリー設定をリセットするための全ての設定を管理します。

### 基本設定

| 設定項目 | 説明 | デフォルト値 |
|---------|------|------------|
| `browser_type` | 使用するブラウザ | `'chrome'` |
| `headless` | ヘッドレスモード（ブラウザ非表示） | `False` |
| `target_url` | ログインページのURL | `'#{ログインURL}'` |

### ログイン情報

| 設定項目 | 説明 |
|---------|------|
| `login_email_label` | メールアドレス入力フィールドのラベル |
| `login_email` | ログイン用メールアドレス |
| `login_password_label` | パスワード入力フィールドのラベル |
| `login_password` | ログイン用パスワード |

### URL保存キー

| 設定項目 | 説明 |
|---------|------|
| `url_save_key` | URLを保存・復元するための識別キー（ニックネームなど） |

### アプリ制限設定の削除

| 設定項目 | 説明 |
|---------|------|
| `delete_target_xpath` | 削除対象要素のXPath |
| `delete_button_text` | 削除ボタンのテキスト |
| `confirm_button_text` | 削除確認ボタンのテキスト |
| `max_delete_iterations` | 最大削除回数 |

### ジオフェンス設定

| 設定項目 | 説明 |
|---------|------|
| `container_xpath` | ジオフェンス一覧のコンテナXPath |
| `container_delete_button_text` | コンテナ内の削除ボタンテキスト |
| `container_confirm_button_text` | 削除確認ダイアログのボタンテキスト |
| `container_confirm_button_xpath` | 削除確認ダイアログのボタンXPath |
| `max_container_delete_iterations` | 最大削除回数 |

### 端末ロック設定

| 設定項目 | 説明 |
|---------|------|
| `container_xpath1` | ロック一覧のコンテナXPath |
| `container_delete_button_text1` | コンテナ内の削除ボタンテキスト |
| `container_confirm_button_text1` | 削除確認ダイアログのボタンテキスト |
| `container_confirm_button_xpath1` | 削除確認ダイアログのボタンXPath |
| `max_container_delete_iterations1` | 最大削除回数 |

### 使用例

```python
# config.py の設定を変更して実行
python config.py
```

設定を変更する場合は、`config.py` の `CONFIG` ディクショナリの値を編集してください。

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

### 基本的な実行

```bash
# 設定ファイルを実行
python config.py
```

### カスタマイズ

1. `config.py` を開き、`CONFIG` ディクショナリの値を変更します
2. 主に変更する設定：
   - **ログイン情報**: `login_email`, `login_password`
   - **ニックネーム**: `url_save_key`
   - **ブラウザ設定**: `browser_type`, `headless`
3. 設定変更後、`python config.py` を実行します

## 自動化される操作

`task_login_and_delete()` 関数は以下の操作を自動的に実行します：

1. **ログイン** - ファミリー管理サイトにログイン
2. **ホームページ** - アプリの制限を有効化
3. **アプリ制限** - 全設定を一括削除
4. **ジオフェンス設定** - 全項目を削除
5. **通知設定** - Oneファミリー通知・メール通知の設定
6. **端末ロック** - 全ロック設定を削除
7. **TONEカメラ** - カメラ設定を構成
8. **GPS** - 位置情報記録を有効化
9. **ブラウザアプリ制限** - 制限を有効化
10. **歩きスマホ警告** - 設定を構成
11. **その他** - 動画チケット購入時の承認を有効化

## 注意事項

1. Chromeブラウザ（またはFirefox/Edge）のインストールが必要です
2. 初回実行時に対応するWebDriverが自動的にダウンロードされます
3. `headless: True` に設定すると、ブラウザが非表示で実行されます
4. スクリーンショットは `images/screenshots/` ディレクトリに保存されます

## License

MIT
