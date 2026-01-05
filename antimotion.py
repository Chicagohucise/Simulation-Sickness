import sys
import random
import math
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSlider, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QThread, QPointF, pyqtSignal, QLockFile, QDir
from PyQt6.QtGui import QPainter, QBrush, QColor
from pynput import mouse, keyboard

DISCORD_STYLE = """
QWidget {
    background-color: #36393f;
    color: #dcddde;
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
}
QFrame#Container {
    background-color: #2f3136;
    border-radius: 10px;
    padding: 10px;
}
QLabel#Title {
    font-size: 15px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 0px;
}
QLabel#SubTitle {
    font-size: 11px;
    color: #96989d;
    margin-bottom: 5px;
    font-weight: normal;
}
QLabel#ValueLabel {
    color: #b9bbbe;
    font-weight: bold;
}
QSlider::groove:horizontal {
    border: 1px solid #202225;
    height: 8px;
    background: #202225;
    margin: 2px 0;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #5865F2;
    border: 1px solid #5865F2;
    width: 16px;
    height: 16px;
    margin: -4px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #4752c4;
}
QPushButton {
    background-color: #ed4245;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #c03537;
}
"""

class InputWorker(QThread):
    exit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dx, self.dy = 0, 0
        self.key_x, self.key_y = 0, 0
        self.is_keyboard_active = False
        self.last_mouse_pos = None
        self.running = True
        self.pressed_keys = set()
        self.mouse_sens = 0.02
        self.key_sens = 5.0

    def run(self):
        with mouse.Listener(on_move=self.on_move) as m_l, \
                keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as k_l:
            while self.running:
                QThread.msleep(100)
            m_l.stop()
            k_l.stop()

    def update_direction(self):
        x, y = 0, 0
        if 'w' in self.pressed_keys: y += 1
        if 's' in self.pressed_keys: y -= 1
        if 'a' in self.pressed_keys: x += 1
        if 'd' in self.pressed_keys: x -= 1
        self.key_x = x
        self.key_y = y
        self.is_keyboard_active = (x != 0 or y != 0)

    def on_move(self, x, y):
        if self.last_mouse_pos:
            self.dx += (x - self.last_mouse_pos[0])
            self.dy += (y - self.last_mouse_pos[1])
        self.last_mouse_pos = (x, y)

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                k = key.char.lower()
                if k in ['w', 'a', 's', 'd']:
                    self.pressed_keys.add(k)
                    self.update_direction()
        except AttributeError:
            pass
        if key == keyboard.Key.end:
            self.exit_signal.emit()

    def on_release(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                k = key.char.lower()
                if k in ['w', 'a', 's', 'd']:
                    self.pressed_keys.discard(k)
                    self.update_direction()
        except:
            pass

class IOSMotionOverlay(QWidget):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen().geometry()
        self.screen_w, self.screen_h = screen.width(), screen.height()
        self.dot_radius = 3.2
        self.max_particles = 250
        self.gen_rate = 2
        self.friction = 0.92
        self.line_spacing = 45
        self.particles = []
        self.vel_x, self.vel_y = 0.0, 0.0
        self.worker = InputWorker()
        self.worker.exit_signal.connect(self.force_quit)
        self.worker.start()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loop)
        self.timer.start(16)

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint |
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setGeometry(0, 0, self.screen_w, self.screen_h)
        self.show()

    def force_quit(self):
        self.worker.running = False
        os._exit(0)

    def update_params(self, params):
        self.dot_radius = params.get('dot_radius', self.dot_radius)
        self.max_particles = params.get('max_particles', self.max_particles)
        self.gen_rate = params.get('gen_rate', self.gen_rate)
        self.friction = params.get('friction', self.friction)
        self.line_spacing = params.get('line_spacing', self.line_spacing)
        if 'mouse_sens' in params: self.worker.mouse_sens = params['mouse_sens']
        if 'key_sens' in params: self.worker.key_sens = params['key_sens']

    def create_particle(self, is_line=False):
        if len(self.particles) >= self.max_particles: return
        if is_line:
            index = random.randint(-10, 10)
            y = self.screen_h / 2 + (index * self.line_spacing)
            life = 0.7
            positions = [40, 80, self.screen_w - 80, self.screen_w - 40]
            for x in positions:
                self.particles.append({'pos': [x, y], 'life': life, 'max_life': life, 'is_line': True})
        else:
            x = random.uniform(0, self.screen_w)
            y = random.uniform(0, self.screen_h)
            life = random.uniform(0.5, 1.0)
            self.particles.append({'pos': [x, y], 'life': life, 'max_life': life, 'is_line': False})

    def loop(self):
        target_vel_x = (-self.worker.dx * self.worker.mouse_sens) + (self.worker.key_x * self.worker.key_sens)
        target_vel_y = (-self.worker.dy * self.worker.mouse_sens) + (self.worker.key_y * self.worker.key_sens)
        self.vel_x = self.vel_x * self.friction + target_vel_x
        self.vel_y = self.vel_y * self.friction + target_vel_y
        self.worker.dx *= 0.1
        self.worker.dy *= 0.1
        current_gen_rate = int(self.gen_rate)
        num_to_gen = current_gen_rate if not self.worker.is_keyboard_active else current_gen_rate * 3
        for _ in range(num_to_gen):
            self.create_particle(is_line=self.worker.is_keyboard_active)
        for p in self.particles[:]:
            p['life'] -= 0.018
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
            p['pos'][0] += self.vel_x * (p['life'] + 0.3)
            p['pos'][1] += self.vel_y * (p['life'] + 0.3)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        speed = math.hypot(self.vel_x, self.vel_y)
        for p in self.particles:
            alpha = int(210 * (p['life'] / p['max_life']))
            painter.setBrush(QBrush(QColor(255, 255, 255, alpha)))
            painter.setPen(Qt.PenStyle.NoPen)
            px, py = p['pos'][0], p['pos'][1]
            if speed > 0.5:
                painter.save()
                painter.translate(px, py)
                angle = math.atan2(self.vel_y, self.vel_x)
                painter.rotate(math.degrees(angle))
                stretch = min(speed * 2.0 * p['life'], 45)
                r = self.dot_radius
                painter.drawRoundedRect(int(-(r + stretch / 2)), int(-r), int(r * 2 + stretch), int(r * 2), r, r)
                painter.restore()
            else:
                painter.drawEllipse(QPointF(px, py), self.dot_radius, self.dot_radius)

class ControlPanel(QWidget):
    def __init__(self, overlay_ref):
        super().__init__()
        self.overlay = overlay_ref
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Simulation Sickness")
        self.resize(360, 650)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        title_label = QLabel("SETTINGS / 设置")
        title_label.setObjectName("Title")
        title_label.setStyleSheet("font-size: 20px; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        container = QFrame()
        container.setObjectName("Container")
        form_layout = QVBoxLayout(container)
        form_layout.setSpacing(12)
        self.add_slider(form_layout, "Mouse Sensitivity", "鼠标灵敏度",
                        1, 100, 15, lambda v: v / 1000.0, 'mouse_sens', "x0.001")
        self.add_slider(form_layout, "Keyboard Sensitivity", "键盘灵敏度 (WASD力度)",
                        1, 100, 27, lambda v: v / 10.0, 'key_sens', "x0.1")
        self.add_slider(form_layout, "Max Particles", "最大粒子数 (数量上限)",
                        10, 1000, 100, lambda v: v, 'max_particles')
        self.add_slider(form_layout, "Dot Radius", "粒子半径 (圆点大小)",
                        10, 100, 32, lambda v: v / 10.0, 'dot_radius', "px")
        self.add_slider(form_layout, "Friction", "物理摩擦力 (越小越不滑)",
                        50, 99, 92, lambda v: v / 100.0, 'friction')
        self.add_slider(form_layout, "Generation Rate", "生成速率 (产生密度)",
                        1, 20, 2, lambda v: v, 'gen_rate')
        self.add_slider(form_layout, "Line Spacing", "行间距 (WASD移动时的间距)",
                        10, 100, 45, lambda v: v, 'line_spacing')
        main_layout.addWidget(container)
        info_label = QLabel("按 'End' 键彻底退出程序\nPress 'End' to exit completely")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #72767d; font-size: 12px; margin-top: 5px;")
        main_layout.addWidget(info_label)
        exit_btn = QPushButton("退出程序 / EXIT")
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self.overlay.force_quit)
        main_layout.addWidget(exit_btn)
        self.setLayout(main_layout)

    def add_slider(self, layout, en_text, cn_text, min_val, max_val, init_val, convert_func, param_name, suffix=""):
        top_row = QHBoxLayout()
        lbl_en = QLabel(en_text)
        lbl_en.setObjectName("Title")
        top_row.addWidget(lbl_en)
        val_lbl = QLabel(f"{convert_func(init_val)}{suffix}")
        val_lbl.setObjectName("ValueLabel")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        top_row.addWidget(val_lbl)
        layout.addLayout(top_row)
        lbl_cn = QLabel(cn_text)
        lbl_cn.setObjectName("SubTitle")
        layout.addWidget(lbl_cn)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(init_val)
        layout.addWidget(slider)
        def on_change(val):
            real_val = convert_func(val)
            display_text = f"{real_val:.2f}" if isinstance(real_val, float) else f"{real_val}"
            val_lbl.setText(f"{display_text}{suffix}")
            self.overlay.update_params({param_name: real_val})
        slider.valueChanged.connect(on_change)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DISCORD_STYLE)
    lock_file_path = os.path.join(QDir.tempPath(), "ios_motion_overlay_v4.lock")
    lock_file = QLockFile(lock_file_path)
    if not lock_file.tryLock(100):
        sys.exit(0)
    overlay = IOSMotionOverlay()
    ctrl_panel = ControlPanel(overlay)
    ctrl_panel.show()
    sys.exit(app.exec())