"""
Interactive PS4 Controller Widget
Displays a PS4 controller and visualizes real-time input
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QLinearGradient, QRadialGradient, QPolygonF, QFont
from PyQt5.QtCore import Qt, QPoint, QRectF, QPointF


class InteractiveControllerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 300)
        self.controller_state = {}
        self._init_controller_layout()
        self.setStyleSheet("background-color: #1a1a1a;")
        
    def _init_controller_layout(self):
        self.setMinimumSize(500, 250)
        
        self.elements = {
            # Shoulder/Trigger buttons on top edge
            'l1': {'type': 'shoulder', 'rect': QRectF(50, 20, 50, 20), 'label': 'L1'},
            'r1': {'type': 'shoulder', 'rect': QRectF(400, 20, 50, 20), 'label': 'R1'},
            'l2': {'type': 'trigger', 'rect': QRectF(50, 45, 50, 20), 'label': 'L2'},
            'r2': {'type': 'trigger', 'rect': QRectF(400, 45, 50, 20), 'label': 'R2'},

            # D-Pad on left side
            'dpad_up': {'type': 'dpad', 'center': (100, 100), 'direction': 'up'},
            'dpad_down': {'type': 'dpad', 'center': (100, 140), 'direction': 'down'},
            'dpad_left': {'type': 'dpad', 'center': (80, 120), 'direction': 'left'},
            'dpad_right': {'type': 'dpad', 'center': (120, 120), 'direction': 'right'},

            # Face buttons on right side - PlayStation layout
            'cross': {'type': 'face_button', 'pos': (400, 140), 'radius': 20, 'symbol': '✕', 'color': QColor("#1E88E5")},
            'circle': {'type': 'face_button', 'pos': (440, 120), 'radius': 20, 'symbol': '●', 'color': QColor("#E53935")},
            'square': {'type': 'face_button', 'pos': (360, 120), 'radius': 20, 'symbol': '■', 'color': QColor("#8E24AA")},
            'triangle': {'type': 'face_button', 'pos': (400, 100), 'radius': 20, 'symbol': '▲', 'color': QColor("#43A047")},

            # Analog sticks
            'left_stick': {'type': 'joystick', 'pos': (150, 170), 'radius': 30},
            'right_stick': {'type': 'joystick', 'pos': (350, 170), 'radius': 30},

            # Center buttons
            'share': {'type': 'small_button', 'pos': (180, 90), 'size': (40, 15), 'label': 'SHARE'},
            'options': {'type': 'small_button', 'pos': (280, 90), 'size': (40, 15), 'label': 'OPTIONS'},
            'ps': {'type': 'ps_button', 'pos': (250, 120), 'radius': 15},

            # Touchpad
            'touchpad': {'type': 'touchpad', 'rect': QRectF(200, 140, 100, 50)},
        }

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.scale(self.width() / 500, self.height() / 250)
        self._draw_controller_body(painter)
        for name, element in self.elements.items():
            self._draw_element(painter, name, element)

    def _draw_controller_body(self, painter):
        # Clean SNES-style controller body
        gradient = QLinearGradient(QPointF(250, 0), QPointF(250, 220))
        gradient.setColorAt(0, QColor("#4a4a4a"))
        gradient.setColorAt(1, QColor("#3a3a3a"))
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#2a2a2a"), 2))
        
        # Main rectangular body with rounded corners (SNES style)
        painter.drawRoundedRect(QRectF(30, 70, 440, 130), 20, 20)

    def _draw_element(self, painter, name, element):
        is_active = self.controller_state.get(name, False)
        
        # Dispatch to the correct drawing method based on type
        method_name = f"_draw_{element['type']}"
        method = getattr(self, method_name, self._draw_unknown)
        method(painter, name, element, is_active)
        
    def _draw_dpad(self, painter, name, element, is_active):
        size = 15
        center = QPointF(*element['center'])
        direction = element['direction']
        
        poly = QPolygonF()
        if direction == 'up':
            poly.append(center + QPointF(0, -size))
            poly.append(center + QPointF(size / 2, 0))
            poly.append(center + QPointF(-size / 2, 0))
        elif direction == 'down':
            poly.append(center + QPointF(0, size))
            poly.append(center + QPointF(size / 2, 0))
            poly.append(center + QPointF(-size / 2, 0))
        elif direction == 'left':
            poly.append(center + QPointF(-size, 0))
            poly.append(center + QPointF(0, -size / 2))
            poly.append(center + QPointF(0, size / 2))
        elif direction == 'right':
            poly.append(center + QPointF(size, 0))
            poly.append(center + QPointF(0, -size / 2))
            poly.append(center + QPointF(0, size / 2))
            
        color = QColor("#6a6a6a") if is_active else QColor("#3a3a3a")
        painter.setBrush(color)
        painter.setPen(QPen(QColor("#2a2a2a"), 1))
        painter.drawPolygon(poly)

    def _draw_face_button(self, painter, name, element, is_active):
        pos = QPointF(*element['pos'])
        radius = element['radius']
        color = element['color']
        symbol = element['symbol']

        # Glow effect
        if is_active:
            glow_grad = QRadialGradient(pos, radius * 1.5)
            glow_grad.setColorAt(0, color.lighter(120))
            glow_grad.setColorAt(1, Qt.transparent)
            painter.setBrush(glow_grad)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos, radius * 1.5, radius * 1.5)
        
        # Main button
        btn_grad = QRadialGradient(pos, radius)
        if is_active:
            btn_grad.setColorAt(0, color.lighter(110))
            btn_grad.setColorAt(1, color)
        else:
            btn_grad.setColorAt(0, QColor("#4a4a4a"))
            btn_grad.setColorAt(1, QColor("#3a3a3a"))
        painter.setBrush(btn_grad)
        painter.setPen(QPen(QColor("#2a2a2a"), 1))
        painter.drawEllipse(pos, radius, radius)
        
        # Symbol
        font = QFont("Segoe UI Symbol", 12, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(pos.x() - radius, pos.y() - radius, radius * 2, radius * 2), Qt.AlignCenter, symbol)

    def _draw_joystick(self, painter, name, element, is_active):
        pos = QPointF(*element['pos'])
        radius = element['radius']

        # Base
        base_grad = QRadialGradient(pos, radius)
        base_grad.setColorAt(0, QColor("#2a2a2a"))
        base_grad.setColorAt(1, QColor("#1a1a1a"))
        painter.setBrush(base_grad)
        painter.setPen(QPen(QColor("#111"), 2))
        painter.drawEllipse(pos, radius, radius)
        
        # Nub
        x, y = self.controller_state.get(f"{name}_x", 0), self.controller_state.get(f"{name}_y", 0)
        nub_pos = pos + QPointF(x, y) * (radius / 32767)
        
        nub_grad = QRadialGradient(nub_pos, radius * 0.7)
        nub_grad.setColorAt(0, QColor("#5a5a5a"))
        nub_grad.setColorAt(1, QColor("#3a3a3a"))
        painter.setBrush(nub_grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(nub_pos, radius * 0.7, radius * 0.7)

    def _draw_shoulder(self, painter, name, element, is_active):
        rect = element['rect']
        color = QColor("#7a7a7a") if is_active else QColor("#5a5a5a")
        
        painter.setBrush(color)
        painter.setPen(QPen(QColor("#2a2a2a"), 1))
        painter.drawRoundedRect(rect, 5, 5)
        
        # Add label
        font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#fff"))
        painter.drawText(rect, Qt.AlignCenter, element['label'])

    def _draw_trigger(self, painter, name, element, is_active):
        rect = element['rect']
        color = QColor("#8a8a8a") if is_active else QColor("#4a4a4a")

        painter.setBrush(color)
        painter.setPen(QPen(QColor("#2a2a2a"), 1))
        painter.drawRoundedRect(rect, 8, 8)
        
        # Add label
        font = QFont("Arial", 8, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#fff"))
        painter.drawText(rect, Qt.AlignCenter, element['label'])

    def _draw_small_button(self, painter, name, element, is_active):
        pos = QPointF(*element['pos'])
        size = element['size']
        rect = QRectF(pos.x(), pos.y(), size[0], size[1])
        
        color = QColor("#5a5a5a") if is_active else QColor("#3a3a3a")
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 3, 3)
        
        font = QFont("Arial", 7, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#ccc"))
        painter.drawText(rect, Qt.AlignCenter, element['label'])

    def _draw_ps_button(self, painter, name, element, is_active):
        pos = QPointF(*element['pos'])
        radius = element['radius']
        
        if is_active:
            glow_grad = QRadialGradient(pos, radius * 1.5)
            glow_grad.setColorAt(0, QColor("#0078D7").lighter(120))
            glow_grad.setColorAt(1, Qt.transparent)
            painter.setBrush(glow_grad)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos, radius * 1.5, radius * 1.5)
            
        ps_grad = QRadialGradient(pos, radius)
        ps_grad.setColorAt(0, QColor("#4a4a4a"))
        ps_grad.setColorAt(1, QColor("#2a2a2a"))
        painter.setBrush(ps_grad)
        painter.setPen(QPen(QColor("#1a1a1a"), 1))
        painter.drawEllipse(pos, radius, radius)
        
        # PS Logo
        painter.setPen(QColor("#0078D7") if is_active else QColor("#005a9e"))
        font = QFont("Arial", 12, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(pos.x() - radius, pos.y() - radius, radius * 2, radius * 2), Qt.AlignCenter, "PS")

    def _draw_touchpad(self, painter, name, element, is_active):
        rect = element['rect']
        color = QColor("#2a2a2a") if is_active else QColor("#1a1a1a")
        
        painter.setBrush(color)
        painter.setPen(QPen(QColor("#4a4a4a"), 1))
        painter.drawRoundedRect(rect, 5, 5)
        
    def _draw_light_bar(self, painter, name, element, is_active):
        rect = element['rect']
        
        if is_active: # Using 'is_active' to show a connected color
            color = QColor("#0078D7") # Blue light for connected
        else:
            color = QColor("#3a3a3a") # Off state
            
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 3, 3)
        
    def _draw_unknown(self, painter, name, element, is_active):
        pass # Silently ignore unknown element types
        painter.drawRoundedRect(element['rect'], 5, 5)

    def update_inputs(self, xinput_report):
        """Update the controller state from an XInput report"""
        state = {}
        
        # Face buttons
        state['cross'] = bool(xinput_report.wButtons & 0x1000)  # A
        state['circle'] = bool(xinput_report.wButtons & 0x2000)  # B
        state['square'] = bool(xinput_report.wButtons & 0x4000)  # X
        state['triangle'] = bool(xinput_report.wButtons & 0x8000)  # Y
        
        # D-pad
        state['dpad_up'] = bool(xinput_report.wButtons & 0x0001)
        state['dpad_down'] = bool(xinput_report.wButtons & 0x0002)
        state['dpad_left'] = bool(xinput_report.wButtons & 0x0004)
        state['dpad_right'] = bool(xinput_report.wButtons & 0x0008)
        
        # Shoulder buttons
        state['l1'] = bool(xinput_report.wButtons & 0x0100)  # LB
        state['r1'] = bool(xinput_report.wButtons & 0x0200)  # RB
        
        # Triggers (analog values converted to boolean for now)
        state['l2'] = xinput_report.bLeftTrigger > 30  # LT
        state['r2'] = xinput_report.bRightTrigger > 30  # RT
        
        # Center buttons
        state['share'] = bool(xinput_report.wButtons & 0x0020)  # Back
        state['options'] = bool(xinput_report.wButtons & 0x0010)  # Start
        
        # Thumbstick clicks
        state['left_stick_click'] = bool(xinput_report.wButtons & 0x0040)  # Left thumb
        state['right_stick_click'] = bool(xinput_report.wButtons & 0x0080)  # Right thumb
        
        # Joysticks
        state['left_stick_x'] = xinput_report.sThumbLX
        state['left_stick_y'] = -xinput_report.sThumbLY  # Invert Y for correct display
        state['right_stick_x'] = xinput_report.sThumbRX
        state['right_stick_y'] = -xinput_report.sThumbRY  # Invert Y for correct display
        
        self.controller_state = state
        self.update()  # Trigger repaint

    def update_connection_status(self, connected):
        self.setVisible(connected)
        if not connected:
            self.controller_state = {}
            self.update()

