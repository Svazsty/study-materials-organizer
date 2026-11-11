import sys
import ctypes
from PySide6.QtWidgets import (QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import QRectF, QPointF, Qt, QEvent
from PySide6.QtGui import QColor, QPainter, QPixmap, QRadialGradient, QCursor
from pathlib import Path
from ctypes import wintypes



class DotButton(QPushButton):
    def __init__(self, color, name, action):
        super().__init__()

        self.dot_color = QColor(color)
        self.hovered = False

        self.setFixedSize(23, 30)
        self.setAccessibleName(name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(action)

    def enterEvent(self, event):
        self.hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )
        painter.setPen(Qt.PenStyle.NoPen)
        center_x = self.width() / 2
        center_y = self.height() / 2

        if self.hovered:
            gradient = QRadialGradient(
                QPointF(center_x, center_y),
                11.5
            )

            for position, alpha in [
                (0.0, 165),
                (0.4, 115),
                (0.75, 45),
                (1.0, 0),
            ]:
                glow_color = QColor(self.dot_color)
                glow_color.setAlpha(alpha)

                gradient.setColorAt(
                    position,
                    glow_color
                )

            painter.setBrush(gradient)
            painter.drawEllipse(
                QRectF(
                    center_x - 11.5,
                    center_y - 11.5,
                    23,
                    23
                )
            )


        painter.setBrush(self.dot_color)
        diameter = 12

        painter.drawEllipse(
            QRectF(
                center_x - diameter / 2,
                center_y - diameter / 2,
                diameter,
                diameter
            )
        )

        painter.end()


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Materials Organizer")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.resize(1050, 650)
        self.setMinimumSize(700, 450)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        shell = QFrame()
        shell.setObjectName("shell")
        shell.setStyleSheet("""
            QFrame#shell {
                background: #0B0D12;
                border: 1px solid #343A44;
                border-radius: 12px;
            }
            QLabel {
                color: #F5F7FA;
                border: none;
            }
            QPushButton {
                border: none;
                background: transparent;
                font-size: 17px;
            }
        """)
        outer.addWidget(shell)

        layout = QVBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.titlebar = QWidget()
        bar = QHBoxLayout(self.titlebar)
        bar.setContentsMargins(16, 0, 16, 0)

        bar.setSpacing(8)
        
        title = QLabel("Materials Organizer")
        title.setStyleSheet(
            "color: #F5F7FA; font-size: 13px; font-weight: 600;"
        )

        dot_holder = QWidget()
        dot_holder.setFixedSize(
            10,
            title.sizeHint().height()
        )

        brand_dot = QFrame(dot_holder)
        brand_dot.setFixedSize(10, 10)
        brand_dot.setStyleSheet("""
            background-color: #FF183A;
            border-radius: 5px;
            border: none;
        """)

        dot_y = round(
            (dot_holder.height() - brand_dot.height()) / 2
        ) + 2
        brand_dot.move(0, dot_y)
        bar.addWidget(dot_holder)
        bar.addWidget(title)


        separator = QLabel("│")
        separator.setStyleSheet(
            "color: #343A44; font-size: 14px;"
        )
        bar.addWidget(separator)

        wordmark_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "PUNQTA-wordmark-master.png"
        )

        wordmark = QLabel()
        pixmap = QPixmap(str(wordmark_path))

        if pixmap.isNull():
            raise FileNotFoundError(
                f"Nie znaleziono wordmarku: {wordmark_path}"
            )

        wordmark.setPixmap(
            pixmap.scaled(
                82,
                18,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        bar.addWidget(wordmark)

        slash = QLabel("/")
        slash.setStyleSheet(
            "color: #7B828C; font-size: 12px;"
        )
        bar.addWidget(slash)

        ferrum = QLabel("FERRUM")
        ferrum.setStyleSheet(
            "color: #FF183A; font-size: 12px; font-weight: 400;"
        )
      
        bar.addWidget(ferrum)
        bar.addStretch()       
        controls = QWidget()
        dots_layout = QHBoxLayout(controls)
        dots_layout.setContentsMargins(0, 0, 0, 0)
        dots_layout.setSpacing(0)

        for color, name, action in [
            ("#8F8F9B", "Minimalizuj", self.showMinimized),
            ("#F5F7FA", "Maksymalizuj", self.toggle_maximize),
            ("#FF304B", "Zamknij", self.close),
        ]:
            button = DotButton(color, name, action)
            dots_layout.addWidget(button)

        bar.addWidget(controls)
        self.titlebar.setFixedHeight(44)
        layout.addWidget(self.titlebar)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(
            "background-color: #343A44; border: none;"
        )
        layout.addWidget(divider)
        layout.addStretch()
        self.titlebar.mousePressEvent = self.start_drag
        self.titlebar.mouseDoubleClickEvent = (
            lambda event: self.toggle_maximize()
        )
    
    def nativeEvent(self, eventType, message):
        if (
            sys.platform != "win32"
            or eventType != b"windows_generic_MSG"
        ):
            return super().nativeEvent(eventType, message)

        msg = wintypes.MSG.from_address(int(message))

        WM_NCHITTEST = 0x0084

        if msg.message != WM_NCHITTEST:
            return super().nativeEvent(eventType, message)

        if self.isMaximized() or self.isMinimized():
            return super().nativeEvent(eventType, message)

        pos = self.mapFromGlobal(QCursor.pos())

        x = pos.x()
        y = pos.y()

        width = self.width()
        height = self.height()

        margin = 10

        left = 0 <= x < margin
        right = width - margin <= x < width
        top = 0 <= y < margin
        bottom = height - margin <= y < height

        if top and left:
            return True, 13      

        if top and right:
            return True, 14     

        if bottom and left:
            return True, 16      

        if bottom and right:
            return True, 17      

        if left:
            return True, 10      

        if right:
            return True, 11      

        if top:
            return True, 12      

        if bottom:
            return True, 15      

        return super().nativeEvent(eventType, message)


    def start_drag(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.windowHandle().startSystemMove()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


app = QApplication(sys.argv)
window = TestWindow()
window.show()
sys.exit(app.exec())
