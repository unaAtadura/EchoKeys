# EchoKeys

一款专为计算机教学演示设计的键鼠操作可视化工具，让观众能够清晰地看到演示者的每一次按键和鼠标操作。

## 功能特性

### ⌨️ 按键可视化
- **实时显示**：按下的按键即时显示在屏幕上
- **组合键识别**：自动识别并显示 `ctrl + c`、`ctrl + shift + s` 等组合键
- **智能合并**：快速连续输入（1 秒内）的字母、数字、符号键会自动合并显示
- **连续按键计数**：快速重复按同一键（如 space、enter、backspace、方向键、字母数字）会显示 `space x3`、`a x5` 等计数格式
- **历史记录**：最多保留最近 6 条操作记录
- **自动消失**：每条记录 5 秒后自动消失，保持屏幕整洁
- **最新记录高亮**：最新一条记录使用更大字体（18pt）显示，旧记录自动切换为较小字体（14pt）
- **符号键支持**：支持 `!@#$%^&*()_+` 等符号键显示
- **小键盘支持**：支持 NumPad 数字键和运算符（`NumPad 0-9`、`NumPad +-*/.`）
- **特殊按键**：支持 `tab`、`escape`、`insert`、`home`、`end`、`page_up/down`、`f1-f12` 等特殊功能键

### 🖱️ 鼠标高亮
- **左键点击**：黄色圆形跟随光标移动
- **右键点击**：粉色圆形跟随光标移动
- **左右键同时按下**：蓝色圆形显示
- **即时反馈**：释放鼠标键后立即消失
- **移动追踪**：按住鼠标键拖动时，高亮圆形跟随光标移动

### 🎯 位置智能
- **方向选择**：根据圆形窗口位置，自动选择上方或下方空间较大的一侧显示操作记录
- **水平对齐**：靠近屏幕左边缘时左对齐，靠近右边缘时右对齐
- **屏幕边界限制**：圆形窗口移动范围限制在屏幕内

### 🔵 圆形悬浮窗
- **可拖拽**：蓝色圆形窗口始终置顶，可自由拖拽调整位置
- **操作隔离**：点击圆形窗口内部不产生操作记录
- **移动触发提示关闭**：移动圆形窗口会自动关闭启动提示气泡

### 🎈 启动提示气泡
- 首次启动时显示欢迎信息和使用提示
- 包含 3 条关键提示：日志窗口暂停监控、托盘隐藏窗口、移动圆点关闭提示
- 移动蓝色圆形窗口后自动关闭

### 📋 系统托盘
- 支持最小化到系统托盘
- **左键双击托盘图标**：切换圆形窗口的显示/隐藏
- **右键菜单**：显示窗口、隐藏窗口、查看日志、退出程序
- 关闭最后一个窗口时程序不退出，继续在托盘运行

### 📝 日志窗口
- **彩色日志**：不同事件类型使用不同颜色区分
  - 键盘按下：绿色 `#66ff66`
  - 键盘释放：浅蓝色 `#66ccff`
  - 鼠标点击：浅蓝色 `#66ccff`
  - 鼠标释放：浅红色 `#ff9999`
  - 鼠标滚轮：橙色 `#ff9966`
- **暂停监控**：打开日志窗口时自动暂停键鼠监控，关闭后恢复
- **历史记录**：程序运行期间的所有事件都会被记录，打开日志窗口时显示完整历史
- **时间戳**：每条记录包含精确到毫秒的时间戳（`HH:MM:SS.sss`）

### 🖥️ 高 DPI 支持
- 自动启用高 DPI 缩放（`Qt.AA_EnableHighDpiScaling`）
- 使用高 DPI 图标（`Qt.AA_UseHighDpiPixmaps`）
- 坐标自动转换：将物理坐标转换为 Qt 逻辑坐标，确保在高 DPI 屏幕上位置准确

## 安装

### 环境要求
- Python 3.8+
- Windows 系统（推荐）/ Linux / macOS

### 依赖包
- **PyQt5** (5.15.11) - GUI 框架
- **pynput** (1.8.2) - 键鼠监听库

## 使用方法

### 运行程序

**方法一：使用 boot.py 启动器（推荐）**

启动器会自动管理虚拟环境、安装依赖，并在后台静默启动程序（无控制台窗口）。

```bash
python boot.py
```

启动器特性：
- **自动检测目标脚本**：自动查找当前目录下除自身外的唯一 `.py` 主程序
- **虚拟环境管理**：
  - 自动创建 `venv/` 虚拟环境
  - 校验虚拟环境有效性（sys.prefix 校验）
  - 使用 MD5 哈希检测 `requirements.txt` 变更
  - 依赖变更时自动增量更新，失败则重建虚拟环境
- **依赖安装重试**：pip 安装失败时自动重试（最多 3 次），延迟递增
- **日志管理**：
  - 详细日志记录到 `boot.log`
  - 超过 500KB 自动清空
  - 同时输出到文件和控制台
- **后台运行**：Windows 下使用 `CREATE_NO_WINDOW` 标志，目标程序无控制台窗口
  - Linux/macOS 下重定向输入输出到 `DEVNULL`

**方法二：使用全局 Python 解释器**

```bash
pip install -r requirements.txt
python EchoKeys.py
```

### 教学演示使用技巧

1. **准备演示**：启动程序后，将蓝色圆形窗口拖拽到不影响演示内容的位置（如屏幕角落）
2. **首次启动提示**：阅读启动气泡中的 3 条使用提示，移动蓝色圆点即可关闭
3. **开始演示**：正常进行操作，按键和鼠标动作会自动显示
4. **查看日志**：如需回顾操作细节，可在托盘菜单中打开日志窗口（注意：打开日志会暂停监控）
5. **隐藏窗口**：如果蓝色圆点碍事，可通过托盘菜单选择「隐藏窗口」
6. **退出程序**：在系统托盘右键菜单选择「退出」

### 操作说明

| 操作 | 显示效果 |
|------|---------|
| 按下字母/数字键 | 显示按键内容，快速输入（1 秒内）自动合并 |
| 按下符号键 `!@#$%` 等 | 显示符号内容，同样支持合并 |
| 连续快速按同一键 | 显示计数格式，如 `space x3`、`a x5` |
| 按下组合键（如 ctrl+c） | 显示 `ctrl + c` |
| 按下小键盘 | 显示 `NumPad 0-9`、`NumPad +` 等 |
| 按下鼠标左键 | 黄色圆形跟随光标 |
| 按下鼠标右键 | 粉色圆形跟随光标 |
| 同时按下左右键 | 蓝色圆形显示 |
| 滚动鼠标滚轮 | 显示 `[滚轮] 上滚`、`[滚轮] 下滚`，连续滚动显示 `[滚轮] 上滚 x5` |
| 水平滚轮（部分鼠标） | 显示 `[滚轮] 左滚`、`[滚轮] 右滚` |

## 项目结构

```
EchoKeys/
├── EchoKeys.py                   # 主程序入口（CircleWindow + 事件协调）
├── boot.py                       # 智能启动器（虚拟环境管理 + 后台运行）
├── requirements.txt              # 依赖列表（PyQt5 + pynput）
├── README.md                     # 项目说明文档
├── LICENSE                       # MIT 许可证
├── .gitignore                    # Git 忽略文件
│
├── tools/                        # 核心工具模块
│   ├── Dialog.py                 # 操作记录显示窗口
│   ├── Log.py                    # 日志查看窗口（带信号通知）
│   ├── ToolTip.py                # 首次启动提示气泡
│   ├── mouse_highlight.py        # 鼠标高亮窗口
│   └── key_mouse_monitor.py      # 键鼠事件监听器（pynput 封装）
│
└── test/                         # 开发测试文件（非运行必需）
    ├── hello_qt.py               # PyQt5 基础示例
    ├── key_mouse_monitor.py      # 独立键鼠监听器测试
    ├── transparent_window.py     # 透明穿透窗口测试
    ├── transparent_window_control.py  # 透明窗口控制器测试
    └── tray_icon_app.py          # 系统托盘功能测试
```

## 模块说明

### 1. EchoKeys.py（主程序）
- **CircleWindow** 类：可拖拽的蓝色圆形悬浮窗（80x80，透明度 0.7）
- **事件协调逻辑**：
  - 连接所有子模块的信号
  - 管理操作记录的显示、合并、计数、自动销毁
  - 根据屏幕空间智能定位操作记录
- **常量配置**：
  - `CIRCLE_DIAMETER = 80`：圆形窗口直径
  - `MAX_DIALOGS = 6`：最大操作记录数
  - `DIALOG_GAP = 5`：记录间距
  - `DIALOG_HEIGHT_LARGE = 60`：最新记录高度
  - `DIALOG_HEIGHT_SMALL = 30`：旧记录高度

### 2. boot.py（智能启动器）
- **配置参数**：
  - `VENV_DIR = "venv"`：虚拟环境目录
  - `LOG_FILE = "boot.log"`：启动日志文件
  - `PIP_RETRIES = 3`：pip 安装重试次数
  - `MAX_LOG_SIZE_BYTES = 500 * 1024`：日志文件上限
- **核心功能**：
  - `is_venv_valid()`：校验虚拟环境有效性
  - `get_requirements_hash()`：计算依赖文件 MD5 哈希
  - `is_venv_up_to_date()`：检查依赖是否最新
  - `pip_install_with_retry()`：带重试的依赖安装
  - `run_target_no_console()`：无控制台后台启动

### 3. tools/Dialog.py（操作记录窗口）
- **DialogWindow** 类：
  - 无边框、置顶、鼠标穿透
  - 圆角灰色背景（透明度 0.9）
  - 最新记录：Arial 18pt Bold
  - 旧记录：Arial 14pt Bold
  - `start_destroy_timer(seconds)`：自动销毁定时器
  - `set_to_old_style()`：切换为旧记录样式

### 4. tools/Log.py（日志窗口）
- **LogWindow** 类：
  - 深色主题（VSCode 风格 `#1e1e1e` 背景）
  - Consolas 10pt 等宽字体
  - `window_opened` / `window_closed` 信号：用于暂停/恢复监控
  - `append_log_with_timestamp()`：带时间戳追加日志

### 5. tools/ToolTip.py（启动提示气泡）
- **ToolTipWindow** 类：
  - 无边框、置顶、半透明紫色背景
  - 显示 3 条使用提示
  - 最小宽度 380px
  - `close_tooltip()`：关闭提示槽函数

### 6. tools/mouse_highlight.py（鼠标高亮）
- **MouseHighlightWindow** 类：
  - 80x80 圆形窗口
  - 颜色映射：
    - 左键：黄色 `QColor(255, 200, 0, 100)`
    - 右键：粉色 `QColor(255, 105, 180, 100)`
    - 同时按下：蓝色 `QColor(100, 100, 255, 100)`
  - 信号驱动：`on_left_press/release`、`on_right_press/release`

### 7. tools/key_mouse_monitor.py（键鼠监听）
- **KeyMouseMonitor** 类（继承 `QObject`）：
  - 基于 pynput 的键盘/鼠标监听
  - **发射信号**：
    - `key_pressed(str)`：按键按下
    - `key_released(str)`：按键释放
    - `mouse_pressed(str, str, str)`：鼠标点击/释放（按钮, x, y）
    - `mouse_scrolled(str, str, str, str)`：鼠标滚轮（x, y, dx, dy）
    - `mouse_moved(str, str)`：鼠标移动
    - `left_pressed/released(str, str)`：左键按下/释放
    - `right_pressed/released(str, str)`：右键按下/释放
  - **组合键识别**：通过 `pressed_keys` 集合追踪当前按下的修饰键（ctrl/shift/alt/cmd/fn/menu）
  - **虚拟键码支持**：处理 VK 码到字符的映射（A-Z、0-9、符号键）

## 技术实现

- **GUI 框架**: PyQt5 5.15.11
- **键鼠监听**: pynput 1.8.2
- **窗口特性**:
  - 无边框（`Qt.FramelessWindowHint`）
  - 始终置顶（`Qt.WindowStaysOnTopHint`）
  - 工具窗口（`Qt.Tool`）
  - 鼠标穿透（操作记录和高亮窗口：`Qt.WindowTransparentForInput` + `Qt.WA_TransparentForMouseEvents`）
  - 半透明背景（`Qt.WA_TranslucentBackground` + `setWindowOpacity`）
- **信号通信**: PyQt5 Signal/Slot 机制实现模块间解耦
- **事件协调**: 主程序作为中枢，连接监听器信号到各显示窗口

## 应用场景

- 软件操作教学视频录制
- 远程技术支持演示
- 编程教学直播
- 快捷键操作演示
- 任何需要展示键鼠操作的场合

## License

MIT
