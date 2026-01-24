# FamilyReset

自动化操作工具 - 基于 Selenium 的浏览器自动化和图像识别

## 项目结构

```
FamilyReset/
├── 58_bot_v2.py          # 58同城自动化脚本（主程序）
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明
├── src/
│   └── core/
│       ├── __init__.py
│       ├── browser.py     # 浏览器控制模块
│       ├── recognizer.py  # 图像识别模块
│       └── controller.py  # 鼠标键盘控制模块
└── images/
    └── 58/
        ├── templates/    # 模板图片存放目录
        └── screenshots/  # 截图保存目录
```

## 安装依赖

1. 创建虚拟环境（推荐）：
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 核心模块说明

### 1. BrowserController (browser.py)
基于 Selenium 的浏览器控制器，支持：
- Chrome、Firefox、Edge 浏览器
- 元素查找和交互
- 页面截图
- JavaScript 执行

### 2. ImageRecognizer (recognizer.py)
基于 OpenCV 的图像识别模块，支持：
- 模板匹配
- 特征匹配
- 多模板同时查找

### 3. MouseController (controller.py)
基于 pyautogui 的鼠标键盘控制，支持：
- 鼠标移动和点击
- 键盘输入
- 热键监听

## 使用方法

编辑 `58_bot_v2.py` 中的 `OPERATIONS` 列表来定义操作流程：

```python
OPERATIONS = [
    # 打开网址
    {'type': 'open_url', 'url': 'https://example.com'},

    # 等待
    {'type': 'wait', 'seconds': 2},

    # 点击文本
    {'type': 'click_text', 'text': '按钮文字'},

    # 使用XPath点击
    {'type': 'click_xpath', 'xpath': '//button[@class="btn"]'},

    # 跨页点击所有元素
    {'type': 'click_xpath_all_pages',
     'xpath': '//ul/li',
     'next_page_text': '下一页'},
]
```

运行脚本：
```bash
python 58_bot_v2.py
```

## 操作类型说明

| 类型 | 说明 | 参数 |
|------|------|------|
| `open_url` | 打开网址 | `url` |
| `wait` | 等待 | `seconds` |
| `click_text` | 点击包含文本的元素 | `text`, `exact_match` |
| `click_xpath` | XPath点击 | `xpath`, `index` |
| `click_xpath_all` | XPath点击所有 | `xpath`, `wait_after_each` |
| `click_xpath_all_pages` | 跨页点击所有 | `xpath`, `next_page_text`, `max_pages` |
| `click_image` | 图像识别点击 | `template` |
| `switch_tab` | 切换标签页 | - |
| `screenshot` | 保存截图 | `filename` |

## 注意事项

1. 需要安装 Chrome 浏览器（或 Firefox/Edge）
2. 首次运行会自动下载对应的 WebDriver
3. 图像识别需要将模板图片放到 `images/58/templates/` 目录

## License

MIT
