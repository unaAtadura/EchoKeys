import math
import random
import sys

from OpenGL.GL import *  # noqa: F401,F403  PyOpenGL 固定管线接口
from PyQt5.QtCore import QElapsedTimer, Qt, QTimer
from PyQt5.QtGui import QCursor, QSurfaceFormat
from PyQt5.QtWidgets import QApplication, QOpenGLWidget

# ---------------------------------------------------------------------------
# OpenGL 渲染配置（必须在 QApplication 创建之前执行）。
# EchoKeys.py 在模块顶部 import 本模块，此时 app 尚未创建，时机即满足要求：
# 1) 强制桌面 OpenGL：固定管线 glBegin/glOrtho 可用，避免误用 ANGLE/GLES；
# 2) 请求 2.1 兼容性 profile：固定管线需要 compatibility profile。
# 普通窗口仍走 raster 绘制，不受影响。
# ---------------------------------------------------------------------------
QApplication.setAttribute(Qt.AA_UseDesktopOpenGL, True)
_surface_format = QSurfaceFormat()
_surface_format.setVersion(2, 1)
_surface_format.setProfile(QSurfaceFormat.CompatibilityProfile)
QSurfaceFormat.setDefaultFormat(_surface_format)

# 粒子数量上限：超过时丢弃最老粒子，防止长时间高速移动导致列表无界增长
MAX_PARTICLES = 900
# 帧间隔（毫秒），约 60 FPS，与项目动画重绘节奏保持一致
FRAME_INTERVAL_MS = 16


class Particle:
    """单个拖尾粒子：位置、速度、寿命、大小（坐标均为 Qt 逻辑像素）。"""

    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size")

    def __init__(self, x, y, vx, vy, life, size):
        self.x = x                # 当前位置（逻辑像素）
        self.y = y
        self.vx = vx              # 速度（像素/帧）
        self.vy = vy
        self.life = life          # 剩余寿命（秒）
        self.max_life = life      # 初始寿命，用于计算衰减比例
        self.size = size          # 初始半径（像素）


class MouseTrailWindow(QOpenGLWidget):
    """鼠标彗星状粒子拖尾窗口：全屏透明置顶 overlay，OpenGL 渲染。

    由主程序 monitor.mouse_moved 信号驱动 on_mouse_move；
    粒子随鼠标移动生成，静止后寿命耗尽自然收尾。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._particles = []           # 存活粒子列表
        self._last_pos = None          # 上一次鼠标位置 (x, y)，用于计算运动方向与速度
        self._clock = QElapsedTimer()  # 测量每帧真实时间间隔 dt，保证衰减与帧率无关
        self._timer = QTimer(self)     # 帧循环计时器
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.setInterval(FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._on_tick)
        self.init_ui()

    def init_ui(self):
        # WindowDoesNotAcceptFocus + WA_ShowWithoutActivating：show() 不请求前台激活。
        # 否则后台进程反复 show 会被 Windows 拒绝前台切换并闪烁任务栏，
        # 进而触发 Win11「请勿打扰」提示
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 透明 QOpenGLWidget 的标准组合：内容叠加合成 + 全透明清屏，粒子方可透出窗口
        self.setAttribute(Qt.WA_AlwaysStackOnTop, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen_geometry.width(), screen_geometry.height())
        self.move(0, 0)
        self.hide()

    # ------------------------------------------------------------------
    # 主程序信号槽入口
    # ------------------------------------------------------------------
    def on_mouse_move(self, x, y):
        # 与项目现有窗口一致：忽略监听线程的物理坐标，
        # 统一用 QCursor 的 Qt 逻辑坐标，规避高 DPI 换算差异
        pos = QCursor.pos()
        x, y = pos.x(), pos.y()
        if self._last_pos is not None:
            dx = x - self._last_pos[0]
            dy = y - self._last_pos[1]
            speed = math.hypot(dx, dy)
            # 生成数量与移动速度成正比：移动越快，拖尾越"密"
            count = 2 + min(int(speed / 3.0), 8)
            for _ in range(count):
                self._spawn_particle(x, y, dx, dy)
        else:
            # 首次进入：只在当前位置生成一个粒子，避免方向未知
            self._spawn_particle(x, y, 0.0, 0.0)
        self._last_pos = (x, y)
        if not self.isVisible():
            self.show()
        if not self._timer.isActive():
            self._timer.start()
            self._clock.restart()
        # 重绘统一由帧循环驱动，保持固定重绘节奏

    def _spawn_particle(self, x, y, dx, dy):
        """在鼠标附近生成一个彗尾粒子（粒子生成的核心逻辑）。"""
        if len(self._particles) >= MAX_PARTICLES:
            self._particles.pop(0)  # 丢弃最老粒子，保证内存占用有界
        back = 0.12                 # 拖尾向后漂移系数：初速度 = 鼠标运动反方向 × 系数
        jitter = 0.35               # 随机扰动幅度，让拖尾形态自然、有厚度
        vx = -dx * back + random.uniform(-jitter, jitter)
        vy = -dy * back + random.uniform(-jitter, jitter)
        life = random.uniform(0.45, 0.95)  # 寿命 0.45 ~ 0.95 秒（随机化更自然）
        size = random.uniform(7.0, 15.0)   # 初始半径
        self._particles.append(Particle(
            x + random.uniform(-2.0, 2.0),  # 位置加微小抖动
            y + random.uniform(-2.0, 2.0),
            vx, vy, life, size,
        ))

    # ------------------------------------------------------------------
    # 帧循环：物理更新 + 请求重绘
    # ------------------------------------------------------------------
    def _on_tick(self):
        """帧循环回调：更新粒子物理（位移、阻尼、上浮、寿命衰减）并触发重绘。"""
        dt = self._clock.restart() / 1000.0  # 本帧真实间隔（秒）
        dt = min(dt, 0.05)                   # 防止窗口卡顿/切后台后 dt 过大
        alive = []
        for p in self._particles:
            # 位置积分；阻尼让粒子逐渐减速，轻微上浮（y 轴向下为正，故减）
            p.x += p.vx
            p.y += p.vy
            p.vx *= 0.94
            p.vy *= 0.94
            p.vy -= 0.006
            p.life -= dt            # 寿命随真实时间衰减（与帧率无关）
            if p.life > 0.0:
                alive.append(p)     # 寿命耗尽的粒子被自然剔除 → 拖尾逐渐消散
        self._particles = alive
        if self._particles:
            self.update()           # 请求重绘 → 触发 paintGL
        else:
            # 粒子全部消散：停帧循环、隐藏窗口并复位参考点
            self._timer.stop()
            self._last_pos = None
            self.hide()

    # ------------------------------------------------------------------
    # OpenGL 渲染
    # ------------------------------------------------------------------
    def initializeGL(self):
        """GL 上下文就绪后调用一次：配置渲染所需的 OpenGL 状态。"""
        glClearColor(0.0, 0.0, 0.0, 0.0)     # 全透明背景，窗口仅显示粒子
        glEnable(GL_BLEND)
        # 标准 over 混合：本模块由 pynput 全局钩子驱动，鼠标移动事件频率远高于参考实现，
        # 轨迹上粒子重叠密度极高；若用加法叠加（GL_SRC_ALPHA, GL_ONE），重叠处 RGB
        # 会累加饱和成纯白，glColor 设置的淡蓝色端点被完全掩盖。over 混合下重叠
        # 只做 alpha 合成、颜色不饱和，淡蓝色可真实呈现，且写入的 rgb 天然满足
        # Qt 的 premultiplied alpha 合成，透到桌面不偏色
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)             # 2D 粒子无需深度测试

    def resizeGL(self, w, h):
        """窗口尺寸变化：建立与 Qt 逻辑像素一致的 2D 正交投影。"""
        dpr = self.devicePixelRatioF()
        # framebuffer 为逻辑尺寸 × dpr，viewport 须用设备像素
        glViewport(0, 0, int(w * dpr), int(h * dpr))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # 投影坐标系直接采用逻辑像素（y 轴翻转，屏幕习惯向下为正），
        # QCursor 逻辑坐标无需任何换算即可用于绘制
        glOrtho(0.0, float(w), float(h), 0.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        """每帧渲染：透明清屏后逐个绘制存活粒子。"""
        glClear(GL_COLOR_BUFFER_BIT)
        for p in self._particles:
            self._draw_particle(p)

    def _draw_particle(self, p):
        """绘制单个粒子：淡蓝色软圆光斑 + 彗核亮点（拖尾衰减的可视化核心）。"""
        t = p.life / p.max_life   # 剩余寿命比例：1（新生）→ 0（消亡）
        age = 1.0 - t             # 年龄比例：0 → 1
        if t <= 0.0:
            return

        # --- 颜色随年龄两段插值（淡蓝色系）：淡冰蓝(彗头) → lightblue(中段) → 深淡蓝(彗尾) ---
        # r/g 分量保持低位、b 恒为 1.0，避免加法叠加后拖尾发白，全程蓝色主导
        if age < 0.5:
            k = age / 0.5
            r = 0.60 + (0.53 - 0.60) * k
            g = 0.80 + (0.81 - 0.80) * k
            b = 1.00
        else:
            k = (age - 0.5) / 0.5
            r = 0.53 + (0.25 - 0.53) * k
            g = 0.81 + (0.55 - 0.81) * k
            b = 1.00

        # --- 拖尾衰减：半径随寿命线性缩小，透明度随寿命平方衰减 ---
        radius = p.size * t
        alpha = t * t
        if radius <= 0.1 or alpha <= 0.004:
            return

        segments = 14
        # --- 软圆光斑：GL_TRIANGLE_FAN，中心不透明、边缘全透明，GPU 插值出径向渐变 ---
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(r, g, b, min(alpha, 1.0) * 0.9)
        glVertex2f(p.x, p.y)
        for i in range(segments + 1):
            ang = 2.0 * math.pi * i / segments
            glColor4f(r, g, b, 0.0)
            glVertex2f(p.x + math.cos(ang) * radius,
                       p.y + math.sin(ang) * radius)
        glEnd()

        # --- 彗核亮点：叠加一个更小更亮的核心，加法混合下"彗头"过曝发白 ---
        core = radius * 0.35
        if core > 0.5:
            glBegin(GL_TRIANGLE_FAN)
            glColor4f(0.95, 0.98, 1.00, alpha * 0.9)
            glVertex2f(p.x, p.y)
            for i in range(segments + 1):
                ang = 2.0 * math.pi * i / segments
                glColor4f(0.95, 0.98, 1.00, 0.0)
                glVertex2f(p.x + math.cos(ang) * core,
                           p.y + math.sin(ang) * core)
            glEnd()


def main():
    app = QApplication(sys.argv)
    window = MouseTrailWindow()
    # 独立运行预览：overlay 对鼠标输入透明收不到鼠标事件，改用 QCursor 轮询驱动
    probe_timer = QTimer()
    probe_timer.setInterval(FRAME_INTERVAL_MS)
    last_pos = None
    def probe_cursor():
        nonlocal last_pos
        pos = QCursor.pos()
        if last_pos is None or pos != last_pos:
            last_pos = pos
            window.on_mouse_move(pos.x(), pos.y())
    probe_timer.timeout.connect(probe_cursor)
    probe_timer.start()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
