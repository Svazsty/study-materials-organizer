from operator import index
import sys
import ctypes
from PySide6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QFileDialog, QMessageBox, QScrollArea
from PySide6.QtCore import QRectF, QPointF, Qt, QEvent
from PySide6.QtGui import QColor, QPainter, QPixmap, QRadialGradient, QCursor, QPen, QFont, QFontDatabase
from pathlib import Path
from ctypes import wintypes
from ui_theme import (BACKGROUND, SURFACE, BORDER, TEXT_PRIMARY, TEXT_MUTED, TEXT_SECONDARY)
from semesters import load_semesters, set_active_semester, add_semester, delete_semester, save_semesters, set_semester_subjects
from uuid import uuid4
from subjects import load_subjects, add_subject, delete_subject


def load_font(filename):
    font_path = (
        Path(__file__).resolve().parent
        / "assets"
        / "fonts"
        / filename
    )

    font_id = QFontDatabase.addApplicationFont(str(font_path))

    if font_id == -1:
        raise RuntimeError(f"Nie udało się wczytać: {filename}")

    return QFontDatabase.applicationFontFamilies(font_id)[0]

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

class SemesterComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = False

    def showPopup(self):
        self.expanded = True
        self.update()
        super().showPopup()

    def hidePopup(self):
        super().hidePopup()
        self.expanded = False
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        color = QColor(
            "#F5F7FA" if self.expanded else f"{TEXT_SECONDARY}"
        )

        pen = QPen(color, 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        x = self.width() - 20
        y = self.height() / 2

        direction = -1 if self.expanded else 1

        painter.drawLine(
            QPointF(x - 4, y - 2 * direction),
            QPointF(x, y + 2 * direction)
        )

        painter.drawLine(
            QPointF(x, y + 2 * direction),
            QPointF(x + 4, y - 2 * direction)
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
        shell.setStyleSheet(f"""
            QFrame#shell {{
                background: {BACKGROUND};
                border: 1px solid #343A44;
                border-radius: 12px;
            }}
            QLabel {{
                color: #F5F7FA;
                border: none;
            }}
            QPushButton {{
                border: none;
                background: transparent;
                font-size: 17px;
            }}
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
        title.setStyleSheet(f"""
            color: #F5F7FA;
            font-family: "{MANROPE_SEMIBOLD}";
            font-size: 13px;
            font-weight: 600;
        """)

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
            f"color: {TEXT_SECONDARY}; font-size: 14px;"
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

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(1, 0, 1, 0)
        content_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)

        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {SURFACE};
                border: none;
                border-right: 1px solid #343A44;
                border-bottom-left-radius: 11px;
            }}
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 24, 20, 20)
        sidebar_layout.setSpacing(12)

        heading_style = f"""
            color: {TEXT_SECONDARY};
            font-family: "{MANROPE}";
            font-size: 11px;
            font-weight: 500;
        """

        semester_label = QLabel("SEMESTR")
        semester_label.setStyleSheet(heading_style)

        
        sidebar_layout.addWidget(semester_label)

        self.semester_combo = SemesterComboBox()
        self.semester_combo.setObjectName("semesterCombo")
        self.semester_combo.setFixedHeight(38)

        self.semester_combo.setStyleSheet("""
            QComboBox#semesterCombo {
                background-color: #0B0D12;
                color: #F5F7FA;
                border: 1px solid #1F2125;
                border-radius: 8px;
                padding-left: 12px;
                font-size: 13px;
            }

            QComboBox#semesterCombo:hover {
                border-color: #343A44;
            }

            QComboBox#semesterCombo::drop-down {
                border: none;
                width: 34px;
            }

            QComboBox#semesterCombo::down-arrow {
                image: none;
            }

            QComboBox#semesterCombo:on {
                background-color: #171B22;
                border-color: #343A44;
            }

            QComboBox QAbstractItemView {
                background-color: #171B22;
                color: #F5F7FA;
                border: 1px solid #343A44;
                selection-background-color: #232831;
            }
        """)

        data = load_semesters()

        for semester_id, semester in data["semesters"].items():
            self.semester_combo.addItem(
                semester.get("name") or semester_id,
                userData=semester_id,
            )

        if self.semester_combo.count() == 0:
            self.semester_combo.addItem("Brak semestrów")
            self.semester_combo.setEnabled(False)
        else:
            active_id = data.get("active_semester")
            active_index = self.semester_combo.findData(active_id)

            if active_index >= 0:
                self.semester_combo.setCurrentIndex(active_index)

            self.semester_combo.currentIndexChanged.connect(
                self.change_semester
            )

        sidebar_layout.addWidget(self.semester_combo)
        semester_row = QHBoxLayout()
        semester_row.setSpacing(8)

        self.new_semester_name = QLineEdit()
        self.new_semester_name.setPlaceholderText("Nowy semestr")
        self.new_semester_name.setFixedHeight(36)

        self.new_semester_name.setStyleSheet("""
            QLineEdit {
                background-color: #0B0D12;
                color: #F5F7FA;
                border: 1px solid #1F2125;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
            }

            QLineEdit:focus {
                border-color: #343A44;
            }
        """)

        add_button = QPushButton("DODAJ")
        add_button.setFixedSize(70, 36)

        add_button.setStyleSheet("""
            QPushButton {
                background-color: #171B22;
                color: #F5F7FA;
                border: 1px solid #1F2125;
                border-radius: 8px;
                font-size: 11px;
            }

            QPushButton:hover {
                background-color: #232831;
            }

            QPushButton:pressed {
                background-color: #343A44;
            }
        """)

        add_button.clicked.connect(self.create_semester)
        semester_row.addWidget(self.new_semester_name, 1)
        semester_row.addWidget(add_button)
        sidebar_layout.addLayout(semester_row)
        delete_button = QPushButton("USUŃ SEMESTR")
        delete_button.setFixedHeight(36)

        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #171B22;
                color: #F5F7FA;
                border: 1px solid #1F2125;
                border-radius: 8px;
                font-size: 11px;
            }

            QPushButton:hover {
                background-color: #232831;
                border-color: #343A44;
            }

            QPushButton:pressed {
                background-color: #343A44;
            }
        """)

        delete_button.clicked.connect(
            self.remove_semester
        )

        sidebar_layout.addWidget(delete_button)

        self.subjects_heading = QLabel("PRZEDMIOTY · 0")
        self.subjects_heading.setStyleSheet(heading_style)

        sidebar_layout.addSpacing(18)
        sidebar_layout.addWidget(self.subjects_heading)
        self.subjects_scroll = QScrollArea()
        self.subjects_scroll.setWidgetResizable(True)
        self.subjects_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.subjects_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.subjects_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.subjects_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 3px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: rgba(75, 83, 96, 70);
                border-radius: 1px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: rgba(100, 110, 125, 120);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        subjects_container = QWidget()
        subjects_container.setStyleSheet(
            "background: transparent;"
        )

        self.subjects_list_layout = QVBoxLayout(
            subjects_container
        )

        self.subjects_list_layout.setSpacing(6)
        self.subjects_list_layout.setContentsMargins(
            0, 0, 4, 8
        )
        self.subjects_list_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.subjects_scroll.setWidget(
            subjects_container
        )

        sidebar_layout.addWidget(
            self.subjects_scroll,
            stretch=1
        )

        subject_header = QWidget()
        header_layout = QHBoxLayout(subject_header)

        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        new_subject_label = QLabel("NOWY PRZEDMIOT")
        new_subject_label.setStyleSheet(heading_style)

        section_line = QFrame()
        section_line.setFixedHeight(1)
        section_line.setStyleSheet("""
            background-color: #343A44;
            border: none;
        """)

        header_layout.addWidget(new_subject_label)
        header_layout.addWidget(section_line, stretch=1)

        sidebar_layout.addWidget(subject_header)

        subject_input_style = f"""
            QLineEdit {{
                background-color: {BACKGROUND};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                font-family: "{INTER}";
                font-weight: 400;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 12px;
            }}

            QLineEdit:focus {{
                border-color: #343A44;
            }}
        """

        self.subject_name_input = QLineEdit()
        self.subject_name_input.setPlaceholderText(
            "Nazwa przedmiotu"
        )
        self.subject_name_input.setFixedHeight(36)
        self.subject_name_input.setStyleSheet(subject_input_style)

        self.subject_code_input = QLineEdit()
        self.subject_code_input.setPlaceholderText(
            "Kod przedmiotu, np. algebra"
        )
        self.subject_code_input.setFixedHeight(36)
        self.subject_code_input.setStyleSheet(subject_input_style)

        add_subject_button = QPushButton("DODAJ PRZEDMIOT")
        add_subject_button.setFixedHeight(36)

        add_subject_button.setStyleSheet("""
            QPushButton {
                background-color: #171B22;
                font-weight: 500;
                color: #F5F7FA;
                border: 1px solid #1F2125;
                border-radius: 8px;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #232831;
                border-color: #343A44;
            }

            QPushButton:pressed {
                background-color: #343A44;
            }
        """)

        add_subject_button.clicked.connect(
            self.create_subject_for_semester
        )

        sidebar_layout.addWidget(self.subject_name_input)
        sidebar_layout.addWidget(self.subject_code_input)
        sidebar_layout.addWidget(add_subject_button)


        workspace = QFrame()
        workspace.setObjectName("workspace")

        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(20, 20, 20, 20)
        workspace_label = QLabel("OBSZAR ROBOCZY")
        workspace_label.setStyleSheet(heading_style)
        workspace_layout.addWidget(workspace_label)
        workspace_layout.addStretch()
        content_layout.addWidget(sidebar)
        content_layout.addWidget(workspace, stretch=1)
        layout.addWidget(content, stretch=1)
        self.titlebar.mousePressEvent = self.start_drag
        self.titlebar.mouseDoubleClickEvent = (
            lambda event: self.toggle_maximize()
        )
        self.refresh_subjects()
    
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

    
    def create_semester(self):
        name = self.new_semester_name.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Brak nazwy",
                "Wpisz nazwę nowego semestru."
            )
            return

        data = load_semesters()

        for semester in data["semesters"].values():
            if semester.get("name", "").casefold() == name.casefold():
                QMessageBox.warning(
                    self,
                    "Duplikat",
                    "Semestr o tej nazwie już istnieje."
                )
                return

        target = QFileDialog.getExistingDirectory(
            self,
            "Wybierz folder docelowy semestru",
            str(Path.home())
        )

        if not target:
            return

        semester_id = f"semester_{uuid4().hex}"

        try:
            created = add_semester(
                semester_id,
                name,
                target,
                []
            )

            if not created:
                raise ValueError("Nie udało się dodać semestru.")

            set_active_semester(semester_id)

        except (ValueError, OSError) as error:
            QMessageBox.critical(
                self,
                "Błąd zapisu",
                str(error)
            )
            return

        self.semester_combo.blockSignals(True)

        try:
            if (
                self.semester_combo.count() == 1
                and self.semester_combo.itemData(0) is None
            ):
                self.semester_combo.clear()

            self.semester_combo.addItem(
                name,
                userData=semester_id
            )

            index = self.semester_combo.findData(semester_id)
            self.semester_combo.setCurrentIndex(index)
            self.semester_combo.setEnabled(True)

        finally:
            self.semester_combo.blockSignals(False)

        self.new_semester_name.clear()
        self.refresh_subjects()

    def remove_semester(self):
        semester_id = self.semester_combo.currentData()

        if semester_id is None:
            return

        data = load_semesters()
        semesters = data["semesters"]

        if len(semesters) <= 1:
            QMessageBox.warning(
                self,
                "Nie można usunąć",
                "Nie możesz usunąć ostatniego semestru."
            )
            return

        semester = semesters.get(semester_id)

        if semester is None:
            QMessageBox.warning(
                self,
                "Błąd",
                "Wybrany semestr już nie istnieje."
            )
            return

        name = semester.get("name") or semester_id

        answer = QMessageBox.question(
            self,
            "Usuń semestr",
            f"Czy na pewno chcesz usunąć semestr:\n\n{name}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            deleted = delete_semester(semester_id)

            if not deleted:
                raise ValueError(
                    "Nie udało się usunąć semestru."
                )

            updated_data = load_semesters()

        except (ValueError, OSError) as error:
            QMessageBox.critical(
                self,
                "Błąd usuwania",
                str(error)
            )
            return
        
        self.semester_combo.blockSignals(True)
        self.refresh_subjects()

        try:
            self.semester_combo.clear()

            for sid, semester in updated_data["semesters"].items():
                self.semester_combo.addItem(
                    semester.get("name") or sid,
                    userData=sid,
                )

            active_id = updated_data["active_semester"]
            index = self.semester_combo.findData(active_id)

            if index >= 0:
                self.semester_combo.setCurrentIndex(index)

            self.semester_combo.setEnabled(
                bool(updated_data["semesters"])
            )

        finally:
            self.semester_combo.blockSignals(False)

    def change_semester(self, index):
        semester_id = self.semester_combo.itemData(index)

        if semester_id is not None:
            set_active_semester(semester_id)
            self.refresh_subjects()

    def refresh_subjects(self):
        while self.subjects_list_layout.count():
            item = self.subjects_list_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        semester_id = self.semester_combo.currentData()
        data = load_semesters()

        semester = data["semesters"].get(
            semester_id, {}
        )

        subject_codes = semester.get("subjects", [])

        try:
            subject_names = load_subjects()
        except (OSError, ValueError):
            subject_names = {}

        self.subjects_heading.setText(
            f"PRZEDMIOTY · {len(subject_codes)}"
        )

        if not subject_codes:
            empty_label = QLabel("Brak przedmiotów")
            empty_label.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 11px;"
            )

            self.subjects_list_layout.addWidget(empty_label)
            return

        for code in subject_codes:
            name = subject_names.get(
                code, f"Nieznany przedmiot ({code})"
            )

            card = QFrame()
            card.setObjectName("subjectCard")

            card.setStyleSheet("""
                QFrame#subjectCard {
                    background-color: #0B0D12;
                    border: 1px solid #1F2125;
                    border-radius: 8px;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 8, 10, 8)
            card_layout.setSpacing(3)
            header_row = QHBoxLayout()
            header_row.setContentsMargins(0, 0, 0, 0)
            header_row.setSpacing(8)
            name_label = QLabel(name)
            name_label.setWordWrap(True)
            name_label.setStyleSheet(
                f"color: {TEXT_PRIMARY}; font-size: 12px;"
            )

            remove_button = QPushButton("USUŃ")
            remove_button.setFixedSize(48, 26)
            remove_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            remove_button.setStyleSheet("""
                QPushButton {
                    color: #A8AFB8;
                    background: transparent;
                    border: none;
                    border-radius: 5px;
                    font-size: 10px;
                }

                QPushButton:hover {
                    color: #FF304B;
                    background: rgba(255, 48, 75, 15);
                }

                QPushButton:pressed {
                    background: rgba(255, 48, 75, 30);
                }
            """)

            remove_button.clicked.connect(
                lambda checked=False, subject_code=code:
                    self.remove_subject_from_semester(subject_code)
            )

            header_row.addWidget(name_label, stretch=1)
            header_row.addWidget(remove_button)
            code_label = QLabel(code)
            code_label.setStyleSheet(
                f"color: {TEXT_SECONDARY}; font-size: 11px;"
            )

            card_layout.addLayout(header_row)
            card_layout.addWidget(code_label)
            self.subjects_list_layout.addWidget(card)

    def create_subject_for_semester(self):
        semester_id = self.semester_combo.currentData()

        name = self.subject_name_input.text().strip()
        code = self.subject_code_input.text().strip()

        if not semester_id:
            QMessageBox.warning(
                self,
                "Brak semestru",
                "Najpierw wybierz semestr."
            )
            return

        if not name or not code:
            QMessageBox.warning(
                self,
                "Brak danych",
                "Podaj nazwę i kod przedmiotu."
            )
            return

        try:
            data = load_semesters()
            semester = data["semesters"].get(semester_id)

            if semester is None:
                raise ValueError(
                    "Wybrany semestr nie istnieje."
                )

            assigned_codes = list(
                semester.get("subjects", [])
            )

            if code in assigned_codes:
                QMessageBox.warning(
                    self,
                    "Duplikat",
                    "Ten przedmiot jest już przypisany "
                    "do wybranego semestru."
                )
                return

            known_subjects = load_subjects()
            existing_name = known_subjects.get(code)

            if existing_name is not None:
                if existing_name.casefold() != name.casefold():
                    raise ValueError(
                        f"Kod '{code}' należy już do "
                        f"przedmiotu '{existing_name}'."
                    )
            else:
                created = add_subject(code, name)

                if not created:
                    raise ValueError(
                        "Nie udało się utworzyć przedmiotu."
                    )

            assigned_codes.append(code)

            set_semester_subjects(
                semester_id,
                assigned_codes
            )

        except (ValueError, OSError) as error:
            QMessageBox.critical(
                self,
                "Błąd dodawania przedmiotu",
                str(error)
            )
            return

        self.subject_name_input.clear()
        self.subject_code_input.clear()

        self.refresh_subjects()

    def remove_subject_from_semester(self, subject_code):
        semester_id = self.semester_combo.currentData()

        if not semester_id:
            return

        data = load_semesters()
        semester = data["semesters"].get(semester_id)

        if semester is None:
            QMessageBox.warning(
                self,
                "Błąd",
                "Wybrany semestr nie istnieje."
            )
            return

        assigned_codes = list(
            semester.get("subjects", [])
        )

        if subject_code not in assigned_codes:
            self.refresh_subjects()
            return

        answer = QMessageBox.question(
            self,
            "Usuń przedmiot",
            f"Usunąć przedmiot '{subject_code}' "
            "z tego semestru?\n\n"
            "Nie spowoduje to usunięcia plików "
            "ani przedmiotu z globalnej bazy.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        updated_codes = [
            code for code in assigned_codes
            if code != subject_code
        ]

        try:
            set_semester_subjects(
                semester_id,
                updated_codes
            )

        except (ValueError, OSError) as error:
            QMessageBox.critical(
                self,
                "Błąd usuwania",
                str(error)
            )
            return

        self.refresh_subjects()

    def start_drag(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.windowHandle().startSystemMove()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


app = QApplication(sys.argv)

INTER = load_font("Inter_18pt-Regular.ttf")
load_font("Inter_18pt-Medium.ttf")

MANROPE = load_font("Manrope-Medium.ttf")
MANROPE_SEMIBOLD = load_font("Manrope-SemiBold.ttf")

font = QFont(INTER)
font.setPixelSize(13)

app.setFont(font)

window = TestWindow()
window.show()

sys.exit(app.exec())
