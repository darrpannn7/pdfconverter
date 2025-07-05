from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox, QHBoxLayout, QDialog, QProgressBar, QComboBox, QSlider, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
import sys
from watermark import add_watermark
import os

COLOR_MAP = {
    'Black': (0, 0, 0),
    'White': (255, 255, 255),
    'Gray': (128, 128, 128),
    'Light Gray': (200, 200, 200),
    'Red': (220, 38, 38),
    'Blue': (37, 99, 235),
    'Green': (16, 185, 129),
}

POSITION_MAP = [
    'Center Diagonal',
    'Center',
    'Top-left',
    'Top-right',
    'Bottom-left',
    'Bottom-right',
]

class WatermarkWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int, int)  # current, total

    def __init__(self, input_path, watermark_text, save_path, color, opacity, position, font_size, password=None):
        super().__init__()
        self.input_path = input_path
        self.watermark_text = watermark_text
        self.save_path = save_path
        self.color = color
        self.opacity = opacity
        self.position = position
        self.font_size = font_size
        self.password = password

    def run(self):
        try:
            def progress_callback(current, total):
                self.progress.emit(current, total)
            add_watermark(self.input_path, self.watermark_text, self.save_path, color=self.color, opacity=self.opacity, position=self.position, font_size=self.font_size, password=self.password, progress_callback=progress_callback)
            self.finished.emit(True, self.save_path)
        except Exception as e:
            self.finished.emit(False, str(e))

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Processing...')
        self.setModal(True)
        self.setFixedSize(350, 120)
        layout = QVBoxLayout()
        self.label = QLabel('Adding watermark, please wait...')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet('color: #1976d2; font-weight: bold; font-size: 15px;')
        layout.addWidget(self.label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.page_label = QLabel('')
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet('color: #1976d2; font-weight: bold; font-size: 14px;')
        layout.addWidget(self.page_label)
        self.setLayout(layout)
        self.setStyleSheet('QDialog { color: #1976d2; font-size: 15px; }')

    def set_progress(self, current, total):
        if total > 0:
            percent = int((current / total) * 100)
            self.progress.setValue(percent)
            self.page_label.setText(f'Page {current} of {total}')
        else:
            self.progress.setValue(0)
            self.page_label.setText('')

class WatermarkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Document Watermarker')
        self.setGeometry(100, 100, 540, 600)
        self.file_path = None
        self.worker = None
        self.progress_dialog = None
        self.init_ui()
        self.setStyleSheet(self.stylesheet())

    def init_ui(self):
        # Card-like container
        card = QFrame()
        card.setObjectName('card')
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)

        # Gradient header
        header = QLabel('Document Watermarker')
        header.setFont(QFont('Segoe UI', 26, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setObjectName('headerLabel')
        card_layout.addWidget(header)

        desc = QLabel('Upload a PDF or Word file and add your custom watermark!')
        desc.setFont(QFont('Segoe UI', 13))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setObjectName('descLabel')
        card_layout.addWidget(desc)

        # File upload row
        file_row = QHBoxLayout()
        self.upload_btn = QPushButton('Upload File')
        self.upload_btn.clicked.connect(self.upload_file)
        file_row.addWidget(self.upload_btn)
        self.file_label = QLabel('No file selected')
        self.file_label.setFont(QFont('Segoe UI', 10))
        self.file_label.setObjectName('file_label')
        file_row.addWidget(self.file_label)
        card_layout.addLayout(file_row)

        # Watermark input
        self.watermark_input = QLineEdit()
        self.watermark_input.setPlaceholderText('Enter watermark text')
        self.watermark_input.setFont(QFont('Segoe UI', 13))
        self.watermark_input.setObjectName('watermarkInput')
        card_layout.addWidget(self.watermark_input)

        # Color, opacity, position, and font size settings
        settings_row = QHBoxLayout()
        color_label = QLabel('Color:')
        color_label.setFont(QFont('Segoe UI', 11))
        color_label.setObjectName('settingLabel')
        settings_row.addWidget(color_label)
        self.color_combo = QComboBox()
        for color in COLOR_MAP:
            self.color_combo.addItem(color)
        self.color_combo.setCurrentText('Light Gray')
        settings_row.addWidget(self.color_combo)
        opacity_label = QLabel('Opacity:')
        opacity_label.setFont(QFont('Segoe UI', 11))
        opacity_label.setObjectName('settingLabel')
        settings_row.addWidget(opacity_label)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(10)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        settings_row.addWidget(self.opacity_slider)
        self.opacity_value_label = QLabel('80%')
        self.opacity_value_label.setObjectName('settingLabel')
        settings_row.addWidget(self.opacity_value_label)
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        position_label = QLabel('Position:')
        position_label.setFont(QFont('Segoe UI', 11))
        position_label.setObjectName('settingLabel')
        settings_row.addWidget(position_label)
        self.position_combo = QComboBox()
        for pos in POSITION_MAP:
            self.position_combo.addItem(pos)
        self.position_combo.setCurrentText('Center Diagonal')
        settings_row.addWidget(self.position_combo)
        card_layout.addLayout(settings_row)

        # Font size slider
        font_row = QHBoxLayout()
        font_label = QLabel('Font Size:')
        font_label.setFont(QFont('Segoe UI', 11))
        font_label.setObjectName('settingLabel')
        font_row.addWidget(font_label)
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setMinimum(10)
        self.font_slider.setMaximum(150)
        self.font_slider.setValue(48)
        self.font_slider.setTickInterval(10)
        self.font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        font_row.addWidget(self.font_slider)
        self.font_value_label = QLabel('48')
        self.font_value_label.setObjectName('settingLabel')
        font_row.addWidget(self.font_value_label)
        self.font_slider.valueChanged.connect(self.update_font_label)
        card_layout.addLayout(font_row)

        # Password protection
        self.pw_checkbox = QCheckBox('Password protect PDF')
        self.pw_checkbox.setObjectName('settingLabel')
        self.pw_checkbox.stateChanged.connect(self.toggle_password_input)
        card_layout.addWidget(self.pw_checkbox)
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText('Enter password')
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setFont(QFont('Segoe UI', 12))
        self.pw_input.setObjectName('watermarkInput')
        self.pw_input.setVisible(False)
        card_layout.addWidget(self.pw_input)

        # Add Watermark button
        self.add_btn = QPushButton('Add Watermark')
        self.add_btn.setObjectName('addBtn')
        self.add_btn.clicked.connect(self.add_watermark)
        card_layout.addWidget(self.add_btn)

        card.setLayout(card_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addStretch(1)
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def update_opacity_label(self):
        self.opacity_value_label.setText(f'{self.opacity_slider.value()}%')

    def update_font_label(self):
        self.font_value_label.setText(f'{self.font_slider.value()}')

    def toggle_password_input(self):
        self.pw_input.setVisible(self.pw_checkbox.isChecked())

    def stylesheet(self):
        return """
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e3f0ff, stop:1 #f9fafc);
        }
        #card {
            background: #fff;
            border-radius: 18px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.12);
        }
        #headerLabel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1976d2, stop:1 #90caf9);
            color: #fff;
            border-radius: 12px;
            padding: 18px 0 18px 0;
            margin-bottom: 0px;
        }
        #descLabel {
            color: #1976d2;
            margin-bottom: 8px;
        }
        QLabel#settingLabel, QLabel#file_label {
            color: #1976d2;
        }
        QPushButton {
            background-color: #1976d2;
            color: white;
            border-radius: 12px;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0px 2px 8px rgba(25, 118, 210, 0.15);
            border: none;
            transition: background 0.2s, transform 0.2s;
        }
        QPushButton#addBtn {
            margin-top: 12px;
            margin-bottom: 8px;
        }
        QPushButton:hover {
            background-color: #1565c0;
            transform: scale(1.04);
            box-shadow: 0px 4px 16px rgba(25, 118, 210, 0.25);
        }
        QLineEdit#watermarkInput {
            border: 2px solid #1976d2;
            border-radius: 8px;
            padding: 12px;
            font-size: 15px;
            background: #f0f7ff;
            color: #1976d2;
        }
        QLineEdit#watermarkInput::placeholder {
            color: #1976d2;
            font-weight: bold;
        }
        QComboBox {
            color: #222;
            background: #fff;
            border: 2px solid #1976d2;
            border-radius: 6px;
            padding: 6px 24px 6px 8px;
            font-size: 14px;
        }
        QComboBox QAbstractItemView {
            color: #222;
            background: #fff;
            selection-background-color: #e3f2fd;
        }
        QSlider::groove:horizontal {
            border: 1px solid #bbb;
            height: 8px;
            background: #e3f2fd;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #1976d2;
            border: 2px solid #90caf9;
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }
        QSlider::sub-page:horizontal {
            background: #90caf9;
            border-radius: 4px;
        }
        #file_label {
            color: #1976d2;
        }
        """

    def upload_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open file', '',
            'Documents (*.pdf *.docx)')
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f'Selected: {os.path.basename(file_path)}')
        else:
            self.file_label.setText('No file selected')

    def add_watermark(self):
        if not self.file_path:
            QMessageBox.warning(self, 'No File', 'Please upload a file first.')
            return
        watermark_text = self.watermark_input.text().strip()
        if not watermark_text:
            QMessageBox.warning(self, 'No Watermark', 'Please enter watermark text.')
            return
        ext = os.path.splitext(self.file_path)[1].lower()
        # Force PDF output for Word
        if ext == '.docx':
            default_save = os.path.splitext(self.file_path)[0] + '_watermarked.pdf'
            save_filter = 'PDF Files (*.pdf)'
        else:
            default_save = os.path.splitext(self.file_path)[0] + '_watermarked' + ext
            save_filter = f'Documents (*{ext})'
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save watermarked file',
            default_save, save_filter)
        if not save_path:
            return
        # Ensure .pdf extension for converted files
        if ext == '.docx' and not save_path.lower().endswith('.pdf'):
            save_path += '.pdf'
        color_name = self.color_combo.currentText()
        color = COLOR_MAP[color_name]
        opacity = self.opacity_slider.value()
        position = self.position_combo.currentText()
        font_size = self.font_slider.value()
        password = None
        if self.pw_checkbox.isChecked():
            password = self.pw_input.text()
            if not password:
                QMessageBox.warning(self, 'No Password', 'Please enter a password for PDF protection.')
                return
        self.progress_dialog = ProgressDialog(self)
        self.worker = WatermarkWorker(self.file_path, watermark_text, save_path, color, opacity, position, font_size, password)
        self.worker.progress.connect(self.progress_dialog.set_progress)
        self.worker.finished.connect(self.on_watermark_finished)
        self.worker.start()
        self.progress_dialog.exec()

    def on_watermark_finished(self, success, message):
        self.progress_dialog.close()
        # Custom QMessageBox with dark blue text
        msg = QMessageBox(self)
        if success:
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('Success')
            msg.setText(f'Watermarked file saved to:\n{message}')
        else:
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle('Error')
            msg.setText(f'Failed to add watermark:\n{message}')
        msg.setStyleSheet('QLabel { color: #1976d2; font-size: 15px; font-weight: bold; } QPushButton { min-width: 80px; }')
        msg.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec()) 