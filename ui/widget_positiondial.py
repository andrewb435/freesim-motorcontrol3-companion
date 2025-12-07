import math
from PyQt6.QtWidgets import QWidget as qtw
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import QPoint

class PositionDial(qtw):
    def __init__(self, parent=None):
        super(PositionDial, self).__init__(parent)
        self.angle = 0  # Initial angle

    def set_angle(self, angle):
        self.angle = angle
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        size = min(rect.width(), rect.height())
        center = QPoint(rect.center().x(), rect.center().y())
        radius = size // 2 * 0.8  # Dial radius

        # Draw the dial background
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(center, int(radius), int(radius))

        # Draw the compass markings
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        for i in range(0, 360, 30):  # Mark every 30 degrees
            angle_rad = math.radians(i)
            x_start = center.x() + (radius - 10) * math.cos(angle_rad)
            y_start = center.y() + (radius - 10) * math.sin(angle_rad)
            x_end = center.x() + radius * math.cos(angle_rad)
            y_end = center.y() + radius * math.sin(angle_rad)
            painter.drawLine(int(x_start), int(y_start), int(x_end), int(y_end))

        # Draw the needle
        painter.setPen(QPen(QColor(150, 150, 150), 3))
        needle_length = radius * 0.8
        needle_x = center.x() + needle_length * math.cos(math.radians(self.angle))
        needle_y = center.y() + needle_length * math.sin(math.radians(self.angle))
        painter.drawLine(center, QPoint(int(needle_x), int(needle_y)))

        # Draw the center circle
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(center, 2, 2)
        painter.end()