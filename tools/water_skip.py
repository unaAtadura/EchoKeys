# -*- coding: utf-8 -*-
"""
「打水漂」落点效果模块（纯 Qt / QPainter / 对象池方案）
======================================================

移植自样例项目 water_skip.py / main_water_skip.py，参数与核心设计保持不变。
与 tools/mouse_trail.py（QOpenGLWidget + PyOpenGL 彗尾拖尾）互不依赖、可切换。

效果语义：
    不做连续密集的粒子拖尾，而是「稀疏、离散、按位移间隔落点」的圆点序列：
    鼠标每累计移动约 STEP_CM 厘米，才在屏幕全局位置落下一个淡蓝色半透明圆点
    （直径约 DIAMETER_CM 厘米），形态类似石子在水面上打出的一个个落点。
    鼠标静止时不会产生任何新圆点。

架构说明：
    RippleController（后台控制器，QObject）
        ├── 轮询 QTimer：按 POLL_MS 间隔读取 QCursor.pos()（全局坐标，
        │   与焦点/遮挡无关），累计路径长度达到阈值即落点；
        ├── 对象池 pool：启动时预创建 MAX_DOTS 个圆点窗口常驻，运行期
        │   零创建/销毁；
        └── active 存活列表：队首为最旧圆点；池空（满 MAX_DOTS）时新落点
            复用最旧圆点（FIFO 环形复用）。

    RippleDotWindow（单个圆点窗口）
        ├── 顶层无边框、置顶、半透明、鼠标穿透（WS_EX_TRANSPARENT 等，
        │   不接收鼠标事件、不阻挡其下任意应用的交互）；
        ├── 独立 QTimer 驱动缩小动画：半径随寿命从 0.5cm 收缩至
        │   MIN_RADIUS_PX，到达后自动发出 finished 信号（语义上的
        │   「自动销毁」，物理层面由对象池回收复用）。

cm→px 物理换算：
    px = cm × DPI ÷ 2.54（96 DPI 下 1cm ≈ 37.8px）。
    DPI 取「鼠标当前所在屏」的 QScreen.logicalDotsPerInch()——Qt 会自动
    反映系统缩放比，使圆点直径与落点间距在不同缩放/不同屏幕下物理观感一致。
    不使用 physicalDotsPerInch()（显示器 EDID 报告的物理尺寸不可靠）。

坐标设计决策：
    圆点直接以屏幕全局坐标 setGeometry 定位，与主窗口位置完全解耦，
    主窗口移动/最小化/失焦均不影响落点位置；DPI 一致性由「当前所在屏
    动态换算」保证。
"""

import ctypes
import math
import sys

from PyQt5.QtCore import QObject, QPoint, QPointF, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QCursor, QPainter
from PyQt5.QtWidgets import QApplication, QWidget

# ---------------------------------------------------------------------------
# 可调参数（与参考实现取值一致，不做改动）
# ---------------------------------------------------------------------------
STEP_CM = 2.5            # 落点间距阈值（cm），规格范围 2~3
DIAMETER_CM = 1.0        # 圆点直径（cm）
MAX_DOTS = 10            # 同屏存活圆点数量上限
POLL_MS = 16             # 全局鼠标位置轮询间隔（毫秒）
ANIM_INTERVAL_MS = 30    # 圆点缩小动画的帧间隔（毫秒）
DOT_LIFETIME_MS = 1200   # 圆点固有寿命（缩小动画总时长，毫秒）
MIN_RADIUS_PX = 2.0      # 半径收缩到该值（像素）即视为消散，触发回收
DOT_COLOR = QColor(100, 170, 255, 110)  # 淡蓝色半透明（RGBA，alpha=110）

# ---------------------------------------------------------------------------
# Win32 鼠标穿透相关常量
# ---------------------------------------------------------------------------
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020  # 鼠标事件穿透到下层窗口
WS_EX_LAYERED = 0x00080000      # 分层窗口（半透明合成，穿透的前提）
WS_EX_NOACTIVATE = 0x08000000   # 不因点击/显示而抢夺焦点

_warned_click_through = False  # 穿透样式校验失败只告警一次，避免刷屏


def cm_to_px(cm, screen):
    """把厘米换算为逻辑像素：px = cm × DPI ÷ 2.54。

    使用指定屏幕的 logicalDotsPerInch()，Qt 会自动反映系统缩放比，
    保证不同缩放（100%/125%/150%…）下物理观感一致。
    """
    return cm * screen.logicalDotsPerInch() / 2.54


class RippleDotWindow(QWidget):
    """单个「打水漂」圆点窗口：顶层无边框 + 半透明 + 鼠标穿透。

    生命周期（对象池语义）：
        activate_at(x, y) 落点并开始缩小动画
        → 独立 QTimer 逐帧收缩半径
        → 寿命耗尽自动 hide 并发出 finished 信号
        → 由控制器从存活列表移除、归还对象池（供后续落点复用）。
    """

    finished = pyqtSignal(object)  # 参数为本窗口对象，控制器据此回收

    def __init__(self):
        # 顶层窗口：无边框 + 置顶 + Tool（不进任务栏/Alt-Tab）
        super().__init__(
            None,
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)   # 每像素 alpha 半透明
        self.setAttribute(Qt.WA_ShowWithoutActivating)   # 显示时不抢焦点
        self._elapsed = 0        # 本轮动画已流逝时间（毫秒）

        # 独立定时器：每个圆点一套动画节拍（对象池方案下总数恒为 MAX_DOTS）
        self._timer = QTimer(self)
        self._timer.setInterval(ANIM_INTERVAL_MS)
        self._timer.timeout.connect(self._on_anim_tick)

        # 预创建阶段即创建原生句柄并设置穿透样式（首次 show 后会再补一次，
        # 防止 Qt 显示窗口时重置非 Qt 管理的扩展样式位）
        self._apply_click_through()

    # ------------------------------------------------------------------
    # 鼠标穿透（Win32）
    # ------------------------------------------------------------------
    def _apply_click_through(self):
        """追加 WS_EX_TRANSPARENT 等扩展样式，实现跨进程鼠标穿透。

        仅追加样式位（幂等），不改动 Qt 的窗口 flags——复用期间不会触发
        Qt 重建原生窗口，避免穿透样式意外丢失。
        """
        global _warned_click_through
        user32 = ctypes.windll.user32
        hwnd = int(self.winId())  # 强制创建原生句柄
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(
            hwnd, GWL_EXSTYLE,
            style | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_NOACTIVATE,
        )
        # 读回校验：穿透失效时窗口会「挡住下层应用的点击」，属于隐蔽 bug，
        # 必须在此尽早暴露（只告警一次）
        new_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ok = (new_style & WS_EX_TRANSPARENT) and (new_style & WS_EX_LAYERED)
        if not ok and not _warned_click_through:
            _warned_click_through = True
            print(
                "警告：圆点窗口鼠标穿透样式设置未生效（WS_EX_TRANSPARENT），"
                "圆点可能阻挡下层应用的点击。",
                file=sys.stderr,
            )

    # ------------------------------------------------------------------
    # 落点与动画
    # ------------------------------------------------------------------
    def activate_at(self, x, y):
        """在屏幕全局坐标 (x, y) 落点：定位 + 重置动画 + 显示置顶。"""
        screen = QApplication.screenAt(QPoint(x, y))
        if screen is None:  # 坐标落在所有屏幕之外时兜底主屏
            screen = QApplication.primaryScreen()
        diameter = cm_to_px(DIAMETER_CM, screen)
        # 居中于落点：全局坐标直接定位，与主窗口位置完全解耦
        self.setGeometry(
            int(x - diameter / 2.0),
            int(y - diameter / 2.0),
            int(round(diameter)),
            int(round(diameter)),
        )
        self._elapsed = 0
        self._timer.start()
        self.show()
        self.raise_()  # 保持置顶层级（被其他置顶窗口覆盖时抬起）
        self._apply_click_through()  # show 后补一次，防 Qt 重置样式

    def recycle(self):
        """立即停止动画并隐藏（供控制器 stop 时全量回收）。"""
        self._timer.stop()
        self.hide()
        self._elapsed = 0

    def _on_anim_tick(self):
        """动画帧：推进寿命；寿命耗尽 → 自动停表、隐藏并通知控制器回收。"""
        self._elapsed += ANIM_INTERVAL_MS
        if self._elapsed >= DOT_LIFETIME_MS:
            self.recycle()
            self.finished.emit(self)  # 语义上的「自动销毁」
            return
        self.update()  # 请求重绘下一帧

    def paintEvent(self, event):
        """绘制淡蓝半透明圆：半径随寿命进度收缩（缓出：先快后慢）。"""
        progress = min(self._elapsed / float(DOT_LIFETIME_MS), 1.0)
        ease = 1.0 - (1.0 - progress) ** 2          # ease-out 缓动
        r0 = self.width() / 2.0
        radius = r0 + (MIN_RADIUS_PX - r0) * ease   # 0.5cm → MIN_RADIUS_PX
        if radius <= 0.5:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(DOT_COLOR))
        center = self.width() / 2.0
        painter.drawEllipse(QPointF(center, center), radius, radius)


class RippleController(QObject):
    """后台控制器：全局鼠标轮询、位移阈值落点判定、对象池与 FIFO 管理。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pool = []        # 空闲圆点窗口池（预创建，恒为 MAX_DOTS 总量）
        self._active = []      # 存活圆点列表，队首 active[0] 为最旧（FIFO）
        self._enabled = False  # 「开启/关闭」状态
        self._accumulated = 0.0  # 自上一落点以来累计的路径长度（逻辑像素）
        self._last_pos = None    # 上一次轮询到的全局鼠标位置
        self._poll_timer = None  # 轮询定时器（懒创建，保证全局唯一）

        # 预创建对象池：窗口总数恒定，运行期零创建/零销毁
        for _ in range(MAX_DOTS):
            dot = RippleDotWindow()
            dot.finished.connect(self._on_dot_finished)
            self._pool.append(dot)

    # ------------------------------------------------------------------
    # 对外接口：开启 / 关闭（幂等，供托盘「切换轨迹」调用）
    # ------------------------------------------------------------------
    def start(self):
        """「开启」：启用落点效果。重复调用不会重复创建/启动轮询定时器。"""
        if self._enabled:
            return
        self._enabled = True
        self._accumulated = 0.0
        self._last_pos = None  # 首次采样只记录位置，不参与距离累计
        if self._poll_timer is None:
            self._poll_timer = QTimer(self)
            self._poll_timer.setInterval(POLL_MS)
            self._poll_timer.timeout.connect(self._on_poll)
        if not self._poll_timer.isActive():
            self._poll_timer.start()

    def stop(self):
        """「关闭」：立即停止落点，回收全部存活圆点（清屏无残留）。"""
        self._enabled = False
        if self._poll_timer is not None and self._poll_timer.isActive():
            self._poll_timer.stop()
        for dot in self._active:
            dot.recycle()
            self._pool.append(dot)  # 归还对象池，保证池总量恒为 MAX_DOTS
        self._active.clear()
        self._last_pos = None
        self._accumulated = 0.0

    @property
    def enabled(self):
        return self._enabled

    # ------------------------------------------------------------------
    # 全局鼠标轮询与落点判定
    # ------------------------------------------------------------------
    def _on_poll(self):
        """轮询回调：累计鼠标路径长度，达到阈值则在当前位置落点。

        QCursor.pos() 返回屏幕全局坐标，与键盘焦点、窗口遮挡无关，
        鼠标位于其他应用上方时同样有效；位移阈值驱动保证鼠标静止时
        不产生任何新圆点。
        """
        if not self._enabled:
            return
        pos = QCursor.pos()
        x, y = pos.x(), pos.y()
        if self._last_pos is not None:
            # 路径长度口径：每段位移绝对值累加（圆弧/折线运动也会落点）
            self._accumulated += math.hypot(
                x - self._last_pos.x(), y - self._last_pos.y()
            )
            step_px = self._current_step_px(x, y)
            if self._accumulated >= step_px:
                self._accumulated = 0.0
                self._spawn(x, y)
        self._last_pos = QPoint(x, y)

    def _current_step_px(self, x, y):
        """落点间距阈值（像素）：按鼠标当前所在屏的 DPI 动态换算。"""
        screen = QApplication.screenAt(QPoint(x, y))
        if screen is None:
            screen = QApplication.primaryScreen()
        return cm_to_px(STEP_CM, screen)

    # ------------------------------------------------------------------
    # 落点与对象池管理（FIFO 环形复用）
    # ------------------------------------------------------------------
    def _spawn(self, x, y):
        """落下一个圆点：优先取空闲池；池空（满 MAX_DOTS）时复用最旧的。"""
        if self._pool:
            dot = self._pool.pop()
        else:
            # FIFO：active[0] 为最旧圆点 → 移除并复用，随后排到队尾
            dot = self._active.pop(0)
        dot.activate_at(x, y)
        self._active.append(dot)

    def _on_dot_finished(self, dot):
        """圆点动画到寿消散：从存活列表移除并归还对象池。"""
        try:
            self._active.remove(dot)
        except ValueError:
            pass  # 防御：stop() 全量回收等边界下信号晚到的重复通知
        if dot not in self._pool:
            self._pool.append(dot)


def main():
    app = QApplication(sys.argv)
    controller = RippleController()
    controller.start()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
