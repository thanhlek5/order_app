import sys
import PyQt6.QtCore
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QLineEdit, QFrame, QScrollArea, QSpacerItem, 
                            QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QDialog, QListWidget, QComboBox, QTextEdit,QInputDialog,QFormLayout,QListWidgetItem
                            )
from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QImage
import pyodbc
import difflib
from datetime import datetime
from PIL import Image
import io
import qrcode
from io import BytesIO
from NguyenLieuTonKho import InNguyenLieu, add_NguyenLieu, xoa_nguyenlieu, cap_nhat_ton_kho,tim_kiem_nguyen_lieu
from Mon import create_mon, read_all_mon, delete_mon
from doanh_thu import get_doanhthu, tong_all_doanhthu,tong_nam_doanhthu,tong_thang_doanhthu,avg_doanhthu,avg_nam,avg_thang
import matplotlib.pyplot as plt  
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


# Kết nối đến cơ sở dữ liệu
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=legion5-thanhle;'
                      'Database=ban_nuoc;'
                      'UID=thanh;'
                      'PWD=1;')

# Phần quản lý người dùng
class UserManager:
    def __init__(self, connection):
        self.conn = connection
        self.cursor = connection.cursor()
        self.use_hash = self._check_password_hash_column()
        self.users = self.get_user()

    # Kiểm tra danh sách người dùng
    def check_user(self):
        self.cursor.execute("SELECT Username, Password, Email FROM dbo.ACCOUNT")
        return self.cursor.fetchall()

    # Lấy danh sách người dùng từ cơ sở dữ liệu
    def get_user(self):
        list_users = {}
        users = self.check_user()
        for user in users:
            list_users[user[0]] = {
                'password': user[1],
                'email': user[2]
            }
        return list_users

    # Đóng kết nối
    def close_connect(self):
        self.cursor.close()
        self.conn.close()

    # Kiểm tra cột PasswordHash có tồn tại không
    def _check_password_hash_column(self):
        try:
            self.cursor.execute("SELECT TOP 1 PasswordHash FROM dbo.ACCOUNT")
            return True
        except pyodbc.Error:
            return False

    # Xác thực người dùng
    def authenticate(self, username, password):
        try:
            self.cursor.execute('SELECT Username, Password FROM dbo.ACCOUNT WHERE Username = ?', (username,))
            result = self.cursor.fetchone()
            if result is not None:
                stored_username, stored_password = result
                if stored_password == password:
                    return True
            return False
        except Exception as e:
            print(f"Lỗi xác thực: {str(e)}")
            return False

    # Đăng ký người dùng mới
    def register(self, username, password, email):
        if not username or not password or not email:
            return False, "Hãy điền đủ thông tin"
        if len(password) < 8:
            return False, "Mật khẩu phải có ít nhất 8 ký tự"
        if '@' not in email or '.' not in email:
            return False, "Email không hợp lệ"
        try:
            self.cursor.execute("SELECT Username FROM dbo.ACCOUNT WHERE Username = ?", (username,))
            if self.cursor.fetchone():
                return False, "Tên đăng nhập đã tồn tại"
            self.cursor.execute("SELECT Email FROM dbo.ACCOUNT WHERE Email = ?", (email,))
            if self.cursor.fetchone():
                return False, "Email đã được sử dụng"
            self.cursor.execute(
                "INSERT INTO dbo.ACCOUNT (Username, Password, Email) VALUES (?, ?, ?)",
                (username, password, email)
            )
            self.conn.commit()
            return True, "Đã tạo tài khoản thành công"
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi khi tạo tài khoản: {str(e)}"

    # Đặt lại mật khẩu
    def reset_password(self, username, email):
        self.cursor.execute(
            "SELECT * FROM dbo.ACCOUNT WHERE username = ? AND email = ?",
            (username, email)
        )
        if self.cursor.fetchone():
            return True, "Người dùng xác minh."
        return False, "Tên đăng nhập hoặc email không đúng!"

    # Cập nhật mật khẩu
    def update_password(self, username, new_password):
        self.cursor.execute("UPDATE dbo.ACCOUNT SET Password = ? WHERE Username = ?", (new_password, username))
        self.conn.commit()

# Phần đăng nhập
class LoginWindow(QMainWindow):
    def __init__(self, conn):
        super().__init__()
        self.user_manager = UserManager(conn)
        self.setWindowTitle("Coffee F5")
        self.setGeometry(100, 100, 300, 200)
        self.setMinimumSize(250, 250)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(0, 77, 153))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        font = QFont()
        font.setPointSizeF(10)
        QApplication.instance().setFont(font)

        title = QLabel("Coffee F5")
        title.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        main_layout.addStretch()
        main_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_widget.setMaximumWidth(400)

        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: white; font-size: 14px;")
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.username_input.setMinimumWidth(150)
        self.username_input.setMaximumWidth(200)
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())

        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: white; font-size: 14px;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.password_input.setMinimumWidth(150)
        self.password_input.setMaximumWidth(200)
        self.password_input.returnPressed.connect(self.login)

        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)

        main_layout.addWidget(form_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        login_button.clicked.connect(self.login)

        signup_button = QPushButton("Sign Up")
        signup_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        signup_button.clicked.connect(self.signup)
        button_layout.addWidget(login_button)
        button_layout.addWidget(signup_button)
        main_layout.addWidget(button_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        forgot_password_button = QPushButton("Forgot Password?")
        forgot_password_button.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: white; 
                font-size: 12px; 
                border: none; 
                padding: 5px; 
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #cccccc;
            }
        """)
        forgot_password_button.clicked.connect(self.forgot_password)
        main_layout.addWidget(forgot_password_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

        self.adjustFontSize()

    # Điều chỉnh kích thước font khi thay đổi cửa sổ
    def resizeEvent(self, event):
        self.adjustFontSize()
        super().resizeEvent(event)

    # Điều chỉnh kích thước font tự động
    def adjustFontSize(self):
        base_size = min(self.width(), self.height()) / 50
        font_size = max(8, int(base_size))

        title = self.findChild(QLabel, "Coffee F5")
        if title:
            title.setStyleSheet(f"font-size: {font_size * 2}px; color: white; font-weight: bold;")

        for label in [self.findChild(QLabel, "Username:"), self.findChild(QLabel, "Password:")]:
            if label:
                label.setStyleSheet(f"color: white; font-size: {font_size}px;")

        self.username_input.setStyleSheet(f"background-color: white; border-radius: 5px; color: black; font-size: {font_size}px; padding: 5px;")
        self.password_input.setStyleSheet(f"background-color: white; border-radius: 5px; color: black; font-size: {font_size}px; padding: 5px;")

        login_button = self.findChild(QPushButton, "Login")
        if login_button:
            login_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #005599; 
                    color: white; 
                    border-radius: 5px; 
                    padding: 5px; 
                    font-size: {font_size}px;
                }}
                QPushButton:hover {{
                    background-color: #0077cc;
                }}
            """)

        signup_button = self.findChild(QPushButton, "Sign Up")
        if signup_button:
            signup_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #005599; 
                    color: white; 
                    border-radius: 5px; 
                    padding: 5px; 
                    font-size: {font_size}px;
                }}
                QPushButton:hover {{
                    background-color: #0077cc;
                }}
            """)

        forgot_password_button = self.findChild(QPushButton, "Forgot Password?")
        if forgot_password_button:
            forgot_password_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent; 
                    color: white; 
                    font-size: {font_size - 2}px; 
                    border: none; 
                    padding: 5px; 
                    text-decoration: underline;
                }}
                QPushButton:hover {{
                    color: #cccccc;
                }}
            """)

    # Xử lý đăng nhập
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields!")
            return
            
        if self.user_manager.authenticate(username, password):
            self.statusBar().showMessage("Login successful!")
            self.main_window = CoffeePOS(conn)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Invalid credentials!")
            self.statusBar().showMessage("Invalid credentials!")

    # Hiển thị cửa sổ đăng ký
    def signup(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Sign Up")
        dialog.setMinimumSize(300, 200)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: white; font-size: 14px;")
        username_input = QLineEdit()
        username_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: white; font-size: 14px;")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        email_label = QLabel("Email:")
        email_label.setStyleSheet("color: white; font-size: 14px;")
        email_input = QLineEdit()
        email_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(username_input, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(password_input, 1, 1)
        form_layout.addWidget(email_label, 2, 0)
        form_layout.addWidget(email_input, 2, 1)
        
        layout.addWidget(form_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        confirm_button = QPushButton("Confirm")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        confirm_button.clicked.connect(lambda: self.handle_signup(dialog, username_input.text(), password_input.text(), email_input.text()))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_widget)
        
        dialog.setModal(True)
        dialog.exec()

    # Xử lý đăng ký
    def handle_signup(self, dialog, username, password, email):
        success, message = self.user_manager.register(username.strip(), password.strip(), email.strip())
        if success:
            QMessageBox.information(self, "Success", message)
            dialog.accept()
        else:
            QMessageBox.critical(self, "Error", message)

    # Hiển thị cửa sổ quên mật khẩu
    def forgot_password(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Forgot Password")
        dialog.setMinimumSize(350, 200)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: white; font-size: 14px;")
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        email_label = QLabel("Email:")
        email_label.setStyleSheet("color: white; font-size: 14px;")
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)
        form_layout.addWidget(email_label, 1, 0)
        form_layout.addWidget(self.email_input, 1, 1)
        
        layout.addWidget(form_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        submit_button.clicked.connect(lambda: self.verify_user_info(dialog))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(submit_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Xác minh thông tin người dùng
    def verify_user_info(self, dialog):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        
        if not username or not email:
            QMessageBox.warning(self, "Lỗi", "Hãy điền đủ thông tin!")
            return
        
        success, message = self.user_manager.reset_password(username, email)
        if success:
            dialog.accept()
            self.show_reset_password_dialog(username)
        else:
            QMessageBox.critical(self, "Lỗi", message)

    # Hiển thị cửa sổ đặt lại mật khẩu
    def show_reset_password_dialog(self, username):
        dialog = QDialog(self)
        dialog.setWindowTitle("Reset Password")
        dialog.setMinimumSize(350, 200)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        
        new_pass_label = QLabel("New Password:")
        new_pass_label.setStyleSheet("color: white; font-size: 14px;")
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        confirm_pass_label = QLabel("Confirm Password:")
        confirm_pass_label.setStyleSheet("color: white; font-size: 14px;")
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        form_layout.addWidget(new_pass_label, 0, 0)
        form_layout.addWidget(self.new_password, 0, 1)
        form_layout.addWidget(confirm_pass_label, 1, 0)
        form_layout.addWidget(self.confirm_password, 1, 1)
        
        layout.addWidget(form_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        reset_button = QPushButton("Reset Password")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        reset_button.clicked.connect(lambda: self.handle_reset_password(username, dialog))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(reset_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Xử lý đặt lại mật khẩu
    def handle_reset_password(self, username, dialog):
        new_pass = self.new_password.text().strip()
        confirm_pass = self.confirm_password.text().strip()
        
        if not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Lỗi", "Hãy điền đủ thông tin!")
            return
            
        if new_pass != confirm_pass:
            QMessageBox.critical(self, "Lỗi", "Mật khẩu không khớp!")
            return
            
        self.user_manager.update_password(username, new_pass)
        QMessageBox.information(self, "Thành công", "Mật khẩu đã được cài đặt lại!")
        dialog.accept()

# Phần main, màn hình chính
class CoffeePOS(QMainWindow):
    def __init__(self,connection):
        super().__init__()
        self.conn = connection
        self.cursor = connection.cursor()
        self.setWindowTitle("Coffee F5 - POS System")
        self.resize(1200, 700)
        self.tables = [f"Bàn {i}" for i in range(1, 11)]
        self.current_table = "Bàn 1"
        self.current_order = {}
        self.total_amount = 0
        self.notifications = []
        # Khai báo các thuộc tính cho show_print_receipt_dialog
        self.payment_method = None
        self.receipt_text = None
        self.qr_label = None
        self.receipt_layout = None
        # ... (các dòng khác)
        self.staff_list = QListWidget()

        # Lấy món từ database
        def menu():
            conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                'Server=legion5-thanhle;'
                                'Database=ban_nuoc;'
                                'UID=thanh;'
                                'PWD=1;')
            cursor = conn.cursor()
            cursor.execute("SELECT TEN_MON, DON_GIA FROM dbo.MON")
            mon = cursor.fetchall()
            conn.close()
            return mon

        def get_menu():
            menu_list = {}
            meu = menu()
            for item in meu:
                menu_list[item[0]] = item[1]
            return menu_list

        self.menu_items = get_menu()
        
        # Đơn hàng hiện tại
        self.current_order = {}
        self.total_amount = 0
        
        # Tạo widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout chính
        main_layout = QHBoxLayout(central_widget)
        
        # Tạo giao diện
        self.setup_ui(main_layout)


    def mo_quan_ly_mon(self):
        self.mon_window = MonManager()
        self.mon_window.show()

        #Hàm Quản Lý Nguyên Liệu
    def mo_quan_ly_nguyen_lieu(self):
        self.nl_window = NguyenLieuTonKhoUI()
        self.nl_window.show()

    def mo_ql_doanh_thu(self):
        self.nl_window = Doanh_thu(conn)
        self.nl_window.show()

    # Giao diện màn hình chính
    def setup_ui(self, main_layout):
        # Phần menu (bên trái)
        menu_frame = QFrame()
        menu_frame.setFrameShape(QFrame.Shape.StyledPanel)
        menu_frame.setStyleSheet("background-color: rgb(0, 51, 102);")
        menu_layout = QVBoxLayout(menu_frame)


        top_buttons_layout = QHBoxLayout()

        logout_btn = QPushButton("Đăng Xuất")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color:red; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        top_buttons_layout.addWidget(logout_btn)

        doanhthu_btn = QPushButton("Doanh thu")
        doanhthu_btn.setStyleSheet("""
            QPushButton {
                background-color:#f0ad4e; 
                color: black; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: plum;
            }
        """)
        doanhthu_btn.clicked.connect(self.mo_ql_doanh_thu)
        top_buttons_layout.addWidget(doanhthu_btn)

        menu_layout.addLayout(top_buttons_layout)  # chỉ thêm 1 lần

        # Layout chứa: Quản lý món | Nguyên liệu | Thêm món
        buttons_layout = QHBoxLayout()

        quanly_btn = QPushButton("Quản lý món")
        quanly_btn.setStyleSheet("background-color: #f0ad4e; color: black; padding: 8px;")
        quanly_btn.clicked.connect(self.mo_quan_ly_mon)
        buttons_layout.addWidget(quanly_btn)

        nguyenlieu_btn = QPushButton("Nguyên liệu")
        nguyenlieu_btn.setStyleSheet("background-color: #f0ad4e; color: black; padding: 10px;")
        nguyenlieu_btn.clicked.connect(self.mo_quan_ly_nguyen_lieu)
        buttons_layout.addWidget(nguyenlieu_btn)

        menu_layout.addLayout(buttons_layout)     
        
        menu_title = QLabel("Menu")
        menu_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        menu_title.setStyleSheet("color: white;")
        menu_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(menu_title)
        
        # Thanh tìm kiếm với gợi ý
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(10, 5, 10, 5)

        # Layout cho ô tìm kiếm và nút kính lúp
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm món...")
        self.search_input.setStyleSheet("""
            background-color: white; 
            border-radius: 5px; 
            color: black; 
            font-size: 14px; 
            padding: 5px;
            border: 1px solid #ccc;
        """)
        self.search_input.textChanged.connect(self.update_suggestions)
        self.search_input.returnPressed.connect(self.filter_menu)
        
        search_btn = QPushButton()
        search_btn.setIcon(QIcon.fromTheme("system-search"))
        search_btn.setStyleSheet("""
            padding: 8px; 
            border-radius: 5px;
            background-color: #005599;
            color: white;
        """)
        search_btn.clicked.connect(self.filter_menu)
        
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(search_btn)
        
        # Danh sách gợi ý
        self.suggestion_list = QListWidget()
        self.suggestion_list.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 5px;
                color: black;
                font-size: 14px;
                padding: 5px;
                margin-top: 2px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #0077cc;
                color: white;
            }
        """)
        self.suggestion_list.setMaximumHeight(100)
        self.suggestion_list.itemDoubleClicked.connect(self.select_suggestion)
        self.suggestion_list.hide()
        
        search_layout.addLayout(search_input_layout)
        search_layout.addWidget(self.suggestion_list)
        menu_layout.addWidget(search_widget)
        
        # Scroll area cho menu
        menu_scroll = QScrollArea()
        menu_scroll.setWidgetResizable(True)
        self.menu_content = QWidget()
        self.menu_grid = QGridLayout(self.menu_content)
        self.menu_grid.setSpacing(10)
        
        # Hiển thị menu ban đầu
        self.display_menu_items(self.menu_items)
        
        menu_scroll.setWidget(self.menu_content)
        menu_layout.addWidget(menu_scroll)

        # Tạo phần hóa đơn (bên phải)
        order_frame = QFrame()
        order_frame.setFrameShape(QFrame.Shape.StyledPanel)
        order_frame.setStyleSheet("background-color: #333; color: white;")
        order_frame.setMinimumWidth(400)
        order_frame.setMaximumWidth(500)
        order_layout = QVBoxLayout(order_frame)
        
        # Tiêu đề hóa đơn
        self.order_title = QLabel(f"Hóa đơn - {self.current_table}")
        self.order_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.order_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        order_layout.addWidget(self.order_title)
        
        # Tạo bảng hiển thị các món đã gọi
        self.order_table = QTableWidget(0, 4)
        self.order_table.setHorizontalHeaderLabels(["Món", "Giá", "SL", "Thành tiền"])
        self.order_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.order_table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #444; color: white; }")
        self.order_table.setStyleSheet("""
            QTableWidget {
                background-color: #444;
                color: white;
                gridline-color: #555;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        order_layout.addWidget(self.order_table)
        
        # Tạo layout hiển thị tổng tiền
        total_layout = QHBoxLayout()
        total_label = QLabel("Tổng tiền:")
        total_label.setFont(QFont("Arial", 14))
        self.total_value = QLabel("0 VND")
        self.total_value.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_value)
        order_layout.addLayout(total_layout)
        
        # Tạo layout các nút chức năng
        buttons_layout = QHBoxLayout()
        
        
        order_layout.addLayout(buttons_layout)

        print_btn = QPushButton("In")
        print_btn.setMinimumWidth(60)
        print_btn.setStyleSheet("background-color: #ccc; color: black; padding: 8px;")
        print_btn.clicked.connect(self.show_print_receipt_dialog)

        payment_btn = QPushButton("Thanh toán")
        payment_btn.setMinimumWidth(130)
        payment_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        payment_btn.clicked.connect(self.show_payment_dialog)

        notification_btn = QPushButton("Thông báo")
        notification_btn.setMinimumWidth(100)
        notification_btn.setStyleSheet("background-color: #FF4081; color: white; padding: 8px;")
        notification_btn.clicked.connect(self.show_notification_dialog)

        table_btn = QPushButton("Chuyển bàn")
        table_btn.setMinimumWidth(140)
        table_btn.setStyleSheet("background-color: #64B5F6; color: white; padding: 8px;")
        table_btn.clicked.connect(self.show_table_transfer_dialog)

        staff_btn = QPushButton("Quản Lý Nhân Viên")
        staff_btn.setMinimumWidth(160)
        staff_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 8px;")
        staff_btn.clicked.connect(self.show_staff_management)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(payment_btn)
        buttons_layout.addWidget(notification_btn)
        buttons_layout.addWidget(table_btn)
        buttons_layout.addWidget(staff_btn)
        buttons_layout.addStretch()

        line1 = QHBoxLayout()
        line1.addWidget(print_btn)
        line1.addWidget(table_btn)
        line1.addWidget(notification_btn)

        line2 = QHBoxLayout()
        line2.addWidget(payment_btn)
        line2.addWidget(staff_btn)

        buttons_layout = QVBoxLayout()
        buttons_layout.addLayout(line1)
        buttons_layout.addLayout(line2)
        order_layout.addLayout(buttons_layout)
        
        # self.image_label = QLabel()
        # self.image_label.setFixedSize(200, 200)
        # self.image_label.setStyleSheet("background-color: white; border: 1px solid gray;")
        # self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # menu_layout.addWidget(self.image_label)
        
        order_layout.addLayout(buttons_layout)
        
        # Thêm frames vào layout chính
        main_layout.addWidget(menu_frame, 2)
        main_layout.addWidget(order_frame, 1)

    # Màn hình menu món
    def display_menu_items(self, items):
        # Xóa các widget cũ
        for i in reversed(range(self.menu_grid.count())): 
            widget = self.menu_grid.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
        # Thêm các nút menu mới
        row, col = 0, 0
        for item, price in items.items():
            btn = QPushButton(f"{item}\n{price:,} VND")
            btn.setMinimumSize(120, 80)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #ddd;
                    color: black;
                    border-radius: 5px;
                    padding: 10px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: rgb(0, 77, 153);
                }
                QPushButton:pressed {
                    background-color: black;
                }
            """)
            btn.clicked.connect(lambda checked, name=item, p=price: self.add_to_order(name, p))
            self.menu_grid.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    # Cập nhật gợi ý món
    def update_suggestions(self):
        search_text = self.search_input.text().lower()
        if not search_text:
            self.suggestion_list.clear()
            self.suggestion_list.hide()
            return
        
        suggestions = difflib.get_close_matches(search_text, [item.lower() for item in self.menu_items.keys()], n=5, cutoff=0.1)
        self.suggestion_list.clear()
        for suggestion in suggestions:
            self.suggestion_list.addItem(suggestion)
        if suggestions:
            self.suggestion_list.show()
        else:
            self.suggestion_list.hide()

    # Truy xuất các món gợi ý
    def select_suggestion(self, item):
        self.search_input.setText(item.text())
        self.filter_menu()
        self.suggestion_list.clear()
        self.suggestion_list.hide()

    # Lọc menu
    def filter_menu(self):
        search_text = self.search_input.text().lower()
        if not search_text:
            self.display_menu_items(self.menu_items)
            return
        
        matched_items = {item: self.menu_items[item] for item in self.menu_items if search_text in item.lower()}
        self.display_menu_items(matched_items)

    # # Tải ảnh món ăn
    # def load_image_for_mon(self, ten_mon):
    #     conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
    #                         'Server=legion5-thanhle;'
    #                         'Database=ban_nuoc;'
    #                         'UID=thanh;'
    #                         'PWD=1;')
        
    #     cursor = conn.cursor()
    #     cursor.execute("""
    #         SELECT I.IMAGE FROM MON M
    #         JOIN IMAGES I ON M.ID_MON = I.ID_MON
    #         WHERE M.TEN_MON = ?
    #     """, ten_mon)
    #     row = cursor.fetchone()
    #     conn.close()

    #     if row and row[0]:
    #         image_data = row[0]
    #         image = Image.open(io.BytesIO(image_data))
    #         buffer = io.BytesIO()
    #         image.save(buffer, format='PNG')
    #         qimg = QPixmap()
    #         qimg.loadFromData(QByteArray(buffer.getvalue()))
    #         self.image_label.setPixmap(qimg.scaled(200, 200))
    #     else:
    #         self.image_label.clear()

    # Thêm món vào order
    def add_to_order(self, item_name, price):
        # self.load_image_for_mon(item_name)
        
        row = -1
        for i in range(self.order_table.rowCount()):
            if self.order_table.item(i, 0).text() == item_name:
                row = i
                break

        if row != -1:
            self.current_order[item_name]["quantity"] += 1
            quantity = self.current_order[item_name]["quantity"]
            subtotal = quantity * price

            quantity_widget = self.order_table.cellWidget(row, 2)
            if quantity_widget:
                quantity_label = quantity_widget.findChild(QLabel)
                if quantity_label:
                    quantity_label.setText(str(quantity))

            subtotal_item = self.order_table.item(row, 3)
            if subtotal_item is None:
                subtotal_item = QTableWidgetItem(f"{subtotal:,} VND")
                self.order_table.setItem(row, 3, subtotal_item)
            else:
                subtotal_item.setText(f"{subtotal:,} VND")

            self.current_order[item_name]["subtotal"] = subtotal

        else:
            row = self.order_table.rowCount()
            self.order_table.insertRow(row)

            self.order_table.setItem(row, 0, QTableWidgetItem(item_name))
            self.order_table.setItem(row, 1, QTableWidgetItem(f"{price:,} VND"))
            self.order_table.setItem(row, 3, QTableWidgetItem(f"{price:,} VND"))

            quantity_widget = QWidget()
            quantity_layout = QHBoxLayout(quantity_widget)
            quantity_layout.setContentsMargins(0, 0, 0, 0)

            decrease_btn = QPushButton("-")
            decrease_btn.setFixedSize(25, 25)

            quantity_label = QLabel("1")
            quantity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            quantity_label.setFixedSize(15, 15)

            increase_btn = QPushButton("+")
            increase_btn.setFixedSize(25, 25)

            decrease_btn.clicked.connect(
                lambda checked, name=item_name, label=quantity_label: self.decrease_quantity(name, label))
            increase_btn.clicked.connect(
                lambda checked, name=item_name, label=quantity_label: self.increase_quantity(name, label))

            quantity_layout.addWidget(decrease_btn)
            quantity_layout.addWidget(quantity_label)
            quantity_layout.addWidget(increase_btn)

            self.current_order[item_name] = {
                "price": price,
                "quantity": 1,
                "subtotal": price,
                "row": row
            }

            self.order_table.setCellWidget(row, 2, quantity_widget)

        self.update_total()

    # Giảm số lượng
    def decrease_quantity(self, item_name, quantity_label):
        if item_name not in self.current_order:
            return

        if self.current_order[item_name]["quantity"] > 1:
            self.current_order[item_name]["quantity"] -= 1
            quantity = self.current_order[item_name]["quantity"]
            price = self.current_order[item_name]["price"]
            subtotal = quantity * price

            quantity_label.setText(str(quantity))

            row = self.current_order[item_name]["row"]
            subtotal_item = self.order_table.item(row, 3)
            if subtotal_item:
                subtotal_item.setText(f"{subtotal:,} VND")

            self.current_order[item_name]["subtotal"] = subtotal

        else:
            row = self.current_order[item_name]["row"]
            self.order_table.removeRow(row)

            del self.current_order[item_name]

            for item, data in self.current_order.items():
                if data["row"] > row:
                    data["row"] -= 1
        
        self.update_total()

    # Tăng số lượng
    def increase_quantity(self, item_name, quantity_label):
        if item_name not in self.current_order:
            return

        self.current_order[item_name]["quantity"] += 1
        quantity = self.current_order[item_name]["quantity"]
        price = self.current_order[item_name]["price"]
        subtotal = quantity * price

        quantity_label.setText(str(quantity))

        row = self.current_order[item_name]["row"]
        subtotal_item = self.order_table.item(row, 3)
        if subtotal_item:
            subtotal_item.setText(f"{subtotal:,} VND")

        self.current_order[item_name]["subtotal"] = subtotal

        self.update_total()

    # Xóa món
    def remove_item(self, item_name):
        if item_name in self.current_order:
            row = self.current_order[item_name]["row"]
            self.order_table.removeRow(row)
            
            for name, item in self.current_order.items():
                if item["row"] > row:
                    self.current_order[name]["row"] -= 1
            
            del self.current_order[item_name]
            
            self.update_total()

    # Cập nhật tổng tiền
    def update_total(self):
        self.total_amount = sum(item["subtotal"] for item in self.current_order.values())
        self.total_value.setText(f"{self.total_amount:,} VND")

    # Hiện in hóa đơn
    def show_print_receipt_dialog(self):
        if not self.current_order:
            QMessageBox.warning(self, "Warning", "Không có món nào trong đơn hàng!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("In Hóa Đơn")
        dialog.setMinimumSize(400, 600)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        payment_widget = QWidget()
        payment_layout = QHBoxLayout(payment_widget)
        
        payment_label = QLabel("Hình thức thanh toán:")
        payment_label.setStyleSheet("color: white; font-size: 14px;")
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Tiền mặt", "Thẻ ngân hàng", "QR Code"])
        self.payment_method.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 5px;")
        
        
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_method)
        layout.addWidget(payment_widget)
        
        receipt_widget = QWidget()
        self.receipt_layout = QVBoxLayout(receipt_widget)
        
        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        self.receipt_text.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 10px;")
        
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        def update_receipt():
            receipt_content = "Coffee F5\n"
            receipt_content += f"Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            receipt_content += f"Bàn: {self.current_table}\n"
            receipt_content += f"Hình thức thanh toán: {self.payment_method.currentText()}\n"
            receipt_content += "-" * 60 + "\n"
            receipt_content += f"{'Món':<30}{'SL':^6}{'Giá':>20}\n"  # Bỏ cột "Tổng"
            receipt_content += "-" * 60 + "\n"

            for item, data in self.current_order.items():
                name = item[:29].ljust(30)  # Độ rộng tên món
                qty = str(data['quantity']).center(6)  # Độ rộng số lượng
                price = f"{data['price']:>20,.2f} VND"  # Độ rộng giá
                receipt_content += f"{name}{qty}{price}\n"

            receipt_content += "-" * 60 + "\n"
            receipt_content += f"{'Tổng cộng':<50}{self.total_amount:>20,.2f} VND\n"
            receipt_content += "\nCảm ơn quý khách!\n"

            self.receipt_text.setText(receipt_content)
            
            if self.payment_method.currentText() == "QR Code":
                qr_data = f"Coffee F5 Payment\nTable: {self.current_table}\nAmount: {self.total_amount} VND\nDate: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                try:
                    qr = qrcode.QRCode(version=1, box_size=20, border=1)
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    qimg = QImage.fromData(buffer.getvalue())
                    pixmap = QPixmap.fromImage(qimg).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.qr_label.setPixmap(pixmap)
                    # Xóa widget cũ trước khi thêm mới
                    for i in reversed(range(self.receipt_layout.count())):
                        if self.receipt_layout.itemAt(i).widget() == self.qr_label:
                            self.receipt_layout.removeWidget(self.qr_label)
                    self.receipt_layout.addWidget(self.qr_label)
                except Exception as e:
                    print(f"Lỗi tạo QR Code: {str(e)}")
                    self.qr_label.clear()
            else:
                if self.qr_label in self.receipt_layout.children():
                    self.receipt_layout.removeWidget(self.qr_label)
                    self.qr_label.clear()

        self.payment_method.currentTextChanged.connect(update_receipt)
        update_receipt()
        self.receipt_layout.addWidget(self.receipt_text)
        layout.addWidget(receipt_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        print_button = QPushButton("In")
        print_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        print_button.clicked.connect(lambda: self.print_receipt(dialog, self.payment_method.currentText()))
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(print_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_widget)
        
        dialog.setModal(True)
        dialog.exec()

    # In hóa đơn
    def print_receipt(self, dialog, payment_method):
        try:
            if not self.current_order:
                QMessageBox.warning(self, "Warning", "Không có món nào trong đơn hàng!")
                return

            print(f"Đang in hóa đơn cho {self.current_table} (Thanh toán: {payment_method})")
            self.add_notification(f"In hóa đơn cho {self.current_table} (Thanh toán: {payment_method})")
            QMessageBox.information(self, "Success", "Hóa đơn đã được in thành công!")
            dialog.accept()
        except Exception as e:
            print(f"Lỗi khi in hóa đơn: {str(e)}")  # In lỗi ra console để debug
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi in hóa đơn: {str(e)}")
    # Hiển thị cửa sổ thanh toán
    def show_payment_dialog(self):
        if not self.current_order:
            QMessageBox.warning(self, "Warning", "Không có món nào trong đơn hàng!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Thanh Toán")
        dialog.setMinimumSize(500, 400)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        
        amount_label = QLabel(f"Tổng tiền: {self.total_amount:,} VND")
        amount_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        payment_method_label = QLabel("Phương thức thanh toán:")
        payment_method_label.setStyleSheet("color: white; font-size: 14px;")
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Tiền mặt", "Thẻ ngân hàng", "QR Code"])
        self.payment_method.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 5px;")
        
        payment_details_widget = QWidget()
        payment_details_layout = QVBoxLayout(payment_details_widget)
        
        cash_bank_widget = QWidget()
        cash_bank_layout = QGridLayout(cash_bank_widget)
        
        received_label = QLabel("Số tiền nhận:")
        received_label.setStyleSheet("color: white; font-size: 14px;")
        received_input = QLineEdit()
        received_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        change_label = QLabel("Tiền thừa: 0 VND")
        change_label.setStyleSheet("color: white; font-size: 14px;")
        
        def update_change():
            try:
                received = int(received_input.text().replace(',', '')) if received_input.text() else 0
                change = received - self.total_amount
                change_label.setText(f"Tiền thừa: {change:,} VND")
            except ValueError:
                change_label.setText("Tiền thừa: 0 VND")
        
        received_input.textChanged.connect(update_change)
        
        cash_bank_layout.addWidget(received_label, 0, 0)
        cash_bank_layout.addWidget(received_input, 0, 1)
        cash_bank_layout.addWidget(change_label, 1, 0, 1, 2)
        
        qr_widget = QWidget()
        qr_layout = QVBoxLayout(qr_widget)
        
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        def generate_qr_code():
            qr_data = f"Coffee F5 Payment\nTable: {self.current_table}\nAmount: {self.total_amount} VND\nDate: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            qr = qrcode.QRCode(version=1, box_size=5, border=1)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qimg = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            qr_label.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        
        qr_layout.addWidget(qr_label)
        
        def update_payment_details():
            for i in reversed(range(payment_details_layout.count())):
                widget = payment_details_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            if self.payment_method.currentText() == "QR Code":
                generate_qr_code()
                payment_details_layout.addWidget(qr_widget)
            else:
                payment_details_layout.addWidget(cash_bank_widget)
        
        self.payment_method.currentTextChanged.connect(update_payment_details)
        
        form_layout.addWidget(amount_label, 0, 0, 1, 2)
        form_layout.addWidget(payment_method_label, 1, 0)
        form_layout.addWidget(self.payment_method, 1, 1)
        
        layout.addWidget(form_widget)
        layout.addWidget(payment_details_widget)
        update_payment_details()
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        confirm_button = QPushButton("Xác nhận")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        confirm_button.clicked.connect(lambda: self.process_payment(dialog))
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Xử lý thanh toán
    def process_payment(self, dialog):
        QMessageBox.information(self, "Thanh toán", f"Đã thanh toán {self.total_amount:,} VND")
        self.add_notification(f"Thanh toán thành công cho {self.current_table}: {self.total_amount:,} VND")
        self.clear_order()
        dialog.accept()

    # Hiển thị cửa sổ thông báo
    def show_notification_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Thông Báo")
        dialog.setMinimumSize(400, 300)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        notification_list = QListWidget()
        notification_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                color: black;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        for notification in reversed(self.notifications):
            notification_list.addItem(notification)
        
        layout.addWidget(notification_list)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        clear_button = QPushButton("Xóa tất cả")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        clear_button.clicked.connect(self.clear_notifications)
        
        close_button = QPushButton("Đóng")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(clear_button)
        button_layout.addWidget(close_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Thêm thông báo
    def add_notification(self, message):
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.notifications.append(f"[{timestamp}] {message}")
        if len(self.notifications) > 50:
            self.notifications.pop(0)

    # Xóa tất cả thông báo
    def clear_notifications(self):
        self.notifications.clear()

    # Hiển thị cửa sổ chuyển ghế bàn
    def show_table_transfer_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Chuyển Ghế Bàn")
        dialog.setMinimumSize(300, 200)
        
        palette = QPalette()
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        
        amount_label = QLabel(f"Tổng tiền: {self.total_amount:,} VND")
        amount_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        
        payment_method_label = QLabel("Phương thức thanh toán:")
        payment_method_label.setStyleSheet("color: white; font-size: 14px;")
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Tiền mặt", "Thẻ ngân hàng", "QR Code"])
        self.payment_method.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 5px;")
        
        payment_details_widget = QWidget()
        payment_details_layout = QVBoxLayout(payment_details_widget)
        
        cash_bank_widget = QWidget()
        cash_bank_layout = QGridLayout(cash_bank_widget)
        
        received_label = QLabel("Số tiền nhận:")
        received_label.setStyleSheet("color: white; font-size: 14px;")
        received_input = QLineEdit()
        received_input.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        
        change_label = QLabel("Tiền thừa: 0 VND")
        change_label.setStyleSheet("color: white; font-size: 14px;")
        
        def update_change():
            try:
                received = int(received_input.text().replace(',', '')) if received_input.text() else 0
                change = received - self.total_amount
                change_label.setText(f"Tiền thừa: {max(0, change):,} VND")
            except ValueError:
                change_label.setText("Tiền thừa: 0 VND")
        
        received_input.textChanged.connect(update_change)
        
        cash_bank_layout.addWidget(received_label, 0, 0)
        cash_bank_layout.addWidget(received_input, 0, 1)
        cash_bank_layout.addWidget(change_label, 1, 0, 1, 2)
        
        qr_widget = QWidget()
        qr_layout = QVBoxLayout(qr_widget)
        
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        def generate_qr_code():
            qr_data = f"Coffee F5 Payment\nTable: {self.current_table}\nAmount: {self.total_amount} VND\nDate: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            qr = qrcode.QRCode(version=1, box_size=10, border=1)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qimg = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimg).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            qr_label.setPixmap(pixmap)
        
        qr_layout.addWidget(qr_label)
        
        def update_payment_details():
            for i in reversed(range(payment_details_layout.count())):
                widget = payment_details_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            if self.payment_method.currentText() == "QR Code":
                generate_qr_code()
                payment_details_layout.addWidget(qr_widget)
            else:
                payment_details_layout.addWidget(cash_bank_widget)
        
        self.payment_method.currentTextChanged.connect(update_payment_details)
        
        form_layout.addWidget(amount_label, 0, 0, 1, 2)
        form_layout.addWidget(payment_method_label, 1, 0)
        form_layout.addWidget(self.payment_method, 1, 1)
        form_layout.addWidget(payment_details_widget, 2, 0, 1, 2)
        
        layout.addWidget(form_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        confirm_button = QPushButton("Xác nhận")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        confirm_button.clicked.connect(lambda: self.process_payment(dialog))
        
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Xử lý thanh toán
    def process_payment(self, dialog):
        QMessageBox.information(self, "Thanh toán", f"Đã thanh toán {self.total_amount:,} VND")
        self.add_notification(f"Thanh toán thành công cho {self.current_table}: {self.total_amount:,} VND")
        self.save_hoadon_thanhtoan(datetime.now(),self.total_amount,self.payment_method.currentText())
        self.clear_order()
        dialog.accept()

    # Hiển thị cửa sổ thông báo
    def show_notification_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Thông Báo")
        dialog.setMinimumSize(400, 300)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        notification_list = QListWidget()
        notification_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                color: black;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        for notification in reversed(self.notifications):
            notification_list.addItem(notification)
        
        layout.addWidget(notification_list)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        clear_button = QPushButton("Xóa tất cả")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        clear_button.clicked.connect(self.clear_notifications)
        
        close_button = QPushButton("Đóng")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(clear_button)
        button_layout.addWidget(close_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Thêm thông báo
    def add_notification(self, message):
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.notifications.append(f"[{timestamp}] {message}")
        if len(self.notifications) > 50:
            self.notifications.pop(0)

    # Xóa tất cả thông báo
    def clear_notifications(self):
        self.notifications.clear()

    # Hiển thị cửa sổ chuyển ghế bàn
    def show_table_transfer_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Chuyển Ghế Bàn")
        dialog.setMinimumSize(300, 200)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        
        table_label = QLabel("Chọn bàn:")
        table_label.setStyleSheet("color: white; font-size: 14px;")
        table_combo = QComboBox()
        table_combo.addItems(self.tables)
        table_combo.setCurrentText(self.current_table)
        table_combo.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 5px;")
        
        form_layout.addWidget(table_label, 0, 0)
        form_layout.addWidget(table_combo, 0, 1)
        
        layout.addWidget(form_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        transfer_button = QPushButton("Chuyển")
        transfer_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        transfer_button.clicked.connect(lambda: self.transfer_table(table_combo.currentText(), dialog))
        
        cancel_button = QPushButton("Hủy")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(transfer_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Chuyển bàn
    def transfer_table(self, new_table, dialog):
        if new_table == self.current_table:
            QMessageBox.warning(self, "Warning", "Vui lòng chọn bàn khác!")
            return
        
        old_table = self.current_table
        self.current_table = new_table
        self.order_title.setText(f"Hóa đơn - {self.current_table}")
        self.order_table.setHorizontalHeaderLabels([f"Món ({new_table})", "Giá", "SL", "Thành tiền"])
        self.add_notification(f"Chuyển đơn hàng từ {old_table} sang {new_table}")
        QMessageBox.information(self, "Success", f"Đã chuyển sang {new_table}!")
        dialog.accept()

    # Xóa đơn hàng
    def clear_order(self):
        self.order_table.setRowCount(0)
        self.current_order = {}
        self.total_amount = 0
        self.total_value.setText("0 VND")

    # Hiển thị cửa sổ quản lý nhân viên
    def show_staff_management(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Quản Lý Nhân Viên")
        dialog.setMinimumSize(400, 300)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        staff_list = QListWidget()
        staff_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                color: black;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
        """)
        
        # Giả lập danh sách nhân viên (có thể lấy từ database sau)
        
        # Truy vấn danh sách nhân viên
        self.cursor.execute("SELECT ID_NHANSU,TEN_NHANSU, VAI_TRO FROM dbo.NHAN_SU")
        rows = self.cursor.fetchall()

        # Format dữ liệu thành chuỗi để hiển thị
        staff_data = [f"{id_nv} - {ten} - {chucvu}" for id_nv,ten, chucvu in rows]
            
        
        

        staff_list.addItems(staff_data)
        
        layout.addWidget(staff_list)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        add_button = QPushButton("Thêm")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        add_button.clicked.connect(lambda: self.add_staff(dialog, staff_list))
        
        remove_button = QPushButton("Xóa")
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        remove_button.clicked.connect(lambda: self.remove_staff(dialog,staff_list))
        
        close_button = QPushButton("Đóng")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #005599; 
                color: white; 
                border-radius: 5px; 
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0077cc;
            }
        """)
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(close_button)
        layout.addWidget(button_widget)
        
        dialog.exec()

    # Thêm nhân viên
    def add_staff(self, dialog, staff_list):
        ten_nv, ok1 = QInputDialog.getText(dialog, "Thêm Nhân Viên", "Nhập tên nhân viên:")
        if not ok1 or not ten_nv:
            return

        vai_tro, ok2 = QInputDialog.getText(dialog, "Vai Trò", "Nhập vai trò của nhân viên:")
        if not ok2 or not vai_tro:
            QMessageBox.warning(self, "Thiếu thông tin", "Bạn phải nhập vai trò!")
            return

        try:
            cursor = self.conn.cursor()

            # Tạo ID tự động (giống như NV001, NV002,...)
            cursor.execute("SELECT MAX(ID_NHANSU) FROM NHAN_SU")
            max_id = cursor.fetchone()[0]
            so_moi = int(max_id.strip()[2:]) + 1 if max_id else 1
            new_id = f"NV{so_moi:03d}"

            # Chèn vào DB đầy đủ các cột
            cursor.execute(
                "INSERT INTO NHAN_SU (ID_NHANSU, TEN_NHANSU, VAI_TRO) VALUES (?, ?, ?)",
                (new_id, ten_nv, vai_tro)
            )
            self.conn.commit()

            staff_list.addItem(f"{new_id} - {ten_nv} ({vai_tro})")
            QMessageBox.information(self, "Thành công", f"Đã thêm nhân viên {new_id}!")
            self.add_notification(f"Đã thêm nhân viên {ten_nv} với vai trò {vai_tro} thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi thêm vào database: {str(e)}")
    


            
    def remove_staff(self, dialog, staff_list):
        selected_item = staff_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Chưa chọn", "Hãy chọn một nhân viên để xóa!")
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa nhân viên này?\n{selected_item.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Lấy ID từ chuỗi (VD: "NV003 - Long_bisexual")
                parts = selected_item.text().split(" - ")
                if len(parts) < 1:
                    QMessageBox.warning(self, "Sai định dạng", "Không thể trích xuất mã nhân viên.")
                    return

                ma_nv = parts[0].strip()

                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM NHAN_SU WHERE ID_NHANSU = ?", (ma_nv,))
                self.conn.commit()
                cursor.close()

                staff_list.takeItem(staff_list.row(selected_item))

                QMessageBox.information(self, "Thành công", f"Đã xóa nhân viên {ma_nv}!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa nhân viên: {str(e)}")

    # Đăng xuất
    def logout(self):
        reply = QMessageBox.question(self, "Đăng Xuất", "Bạn có chắc muốn đăng xuất?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            login_window = LoginWindow(conn)
            login_window.show()
            
    def save_hoadon_thanhtoan(self, ngay_lap, thanh_tien, hinh_thuc_tt):
        try:
            # Không chèn ID vì nó là cột IDENTITY
            self.cursor.execute('''
                INSERT INTO HOA_DON (NGAY_HOADON, TONGTIEN, HINH_THUC_TT) 
                VALUES (?, ?, ?)''', 
                (ngay_lap, thanh_tien, hinh_thuc_tt)
            )
            
            # Lấy ID vừa tạo
            self.cursor.execute('SELECT SCOPE_IDENTITY()')
            id_result = self.cursor.fetchone()
            
            if id_result is None or id_result[0] is None:
                print("Không thể lấy ID hóa đơn sau khi tạo")
                # Thử cách khác
                self.cursor.execute('SELECT @@IDENTITY')
                id_result = self.cursor.fetchone()
                
            id_hoadon = id_result[0] if id_result and id_result[0] else None
            
            if id_hoadon is None:
                print("Không thể lấy ID hóa đơn, hủy giao dịch")
                self.conn.rollback()
                return None
                
            print(f"Đã tạo hóa đơn mới với ID: {id_hoadon}")
            
            # Debug: Kiểm tra hóa đơn vừa tạo
            self.cursor.execute('SELECT * FROM HOA_DON WHERE ID_HOADON = ?', (id_hoadon,))
            hoadon_check = self.cursor.fetchone()
            print(f"Kiểm tra hóa đơn: {hoadon_check}")
            
            # Insert chi tiết hóa đơn
            for item_name, item_data in self.current_order.items():
                print(f"Thêm món: {item_name}, SL: {item_data['quantity']}, Đơn giá: {item_data['price']}")
                self.cursor.execute('''
                    INSERT INTO CT_HOADON (ID_HOADON, TEN_MON, SO_LUONG, THANH_TIEN, DON_GIA) 
                    VALUES (?, ?, ?, ?, ?)''',
                    (id_hoadon, item_name, item_data['quantity'], item_data['subtotal'], item_data['price'])
                )
            
            self.conn.commit()
            print(f"Đã lưu hóa đơn thành công với ID: {id_hoadon}")
            return id_hoadon
        
        except Exception as e:
            self.conn.rollback()
            print(f"Lỗi khi lưu hóa đơn: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        
class NguyenLieuTonKhoUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý Nguyên Liệu Tồn Kho")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(self)

        # --- Tìm kiếm nguyên liệu
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập tên nguyên liệu cần tìm...")
        search_btn = QPushButton("Tìm")
        search_btn.clicked.connect(self.tim_nguyen_lieu)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # --- Form thêm nguyên liệu
        form_layout = QFormLayout()
        self.ten_input = QLineEdit()
        self.don_vi_input = QLineEdit()
        self.ghi_chu_input = QLineEdit()
        form_layout.addRow("Tên Nguyên Liệu:", self.ten_input)
        form_layout.addRow("Đơn Vị Tính:", self.don_vi_input)
        form_layout.addRow("Ghi Chú:", self.ghi_chu_input)
        layout.addLayout(form_layout)

        them_btn = QPushButton("Thêm Nguyên Liệu")
        them_btn.clicked.connect(self.them_nguyen_lieu)
        layout.addWidget(them_btn)

        # --- Bảng dữ liệu (QTableWidget)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Tên", "Đơn Vị", "Số Lượng", "Ngày Cập Nhật", "Ghi Chú"])
        # Thêm dòng này:
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)    

        # --- Nút chức năng
        btn_layout = QHBoxLayout()
        self.so_luong_input = QLineEdit()
        self.so_luong_input.setPlaceholderText("Nhập số lượng (+/-)")
        capnhat_btn = QPushButton("Cập nhật SL")
        capnhat_btn.clicked.connect(self.cap_nhat_so_luong)
        xoa_btn = QPushButton("Xoá nguyên liệu")
        xoa_btn.clicked.connect(self.xoa_nguyen_lieu)
        btn_layout.addWidget(self.so_luong_input)
        btn_layout.addWidget(capnhat_btn)
        btn_layout.addWidget(xoa_btn)
        layout.addLayout(btn_layout)

        self.tai_lai_bang()
        self.setLayout(layout) # Thiết lập layout cho widget

        self.table.setStyleSheet("""
            QTableWidget {
                
                gridline-color: #d0d0d0;
                font-size: 14px;
            }
            QHeaderView::section {
                "background-color: rgb(0, 51, 102);"
                color: black;
                padding: 5px;
                font-weight: bold;
                border-bottom: 2px solid #c0c0c0;
            }
            QTableWidget::item {
                color: black;                
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #a0c4ff;
                color: black;
            }
        """)

    def tai_lai_bang(self):
        data = InNguyenLieu()
        self.hien_thi_bang(data)
    
    
    def hien_thi_bang(self, data):
        self.table.setRowCount(0)
        for row_idx, row in enumerate(data):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
    
    
    def tim_nguyen_lieu(self):
        ten = self.search_input.text()
        if not ten:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Nhập tên nguyên liệu cần tìm.")
            return
        try:
            results = tim_kiem_nguyen_lieu(ten)
            self.hien_thi_bang(results)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tìm nguyên liệu: {e}")
    
    def them_nguyen_lieu(self):
        ten = self.ten_input.text()
        dv = self.don_vi_input.text()
        ghi_chu = self.ghi_chu_input.text()
        if not ten or not dv:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Tên và đơn vị không được để trống.")
            return
        add_NguyenLieu(ten, dv, datetime.today(), ghi_chu)
        QMessageBox.information(self, "Thành công", "Đã thêm nguyên liệu!")
        self.ten_input.clear()
        self.don_vi_input.clear()
        self.ghi_chu_input.clear()
        self.tai_lai_bang()

    def cap_nhat_so_luong(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Chưa chọn", "Chọn dòng cần cập nhật.")
            return
        try:
            delta = int(self.so_luong_input.text())
        except ValueError:
            QMessageBox.warning(self, "Sai định dạng", "Nhập số lượng là số.")
            return
        id_nl = int(self.table.item(selected, 0).text())
        cap_nhat_ton_kho(id_nl, delta)
        self.so_luong_input.clear()
        self.tai_lai_bang()

    def xoa_nguyen_lieu(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Chưa chọn", "Chọn dòng cần xoá.")
            return
        id_nl = int(self.table.item(selected, 0).text())
        xoa_nguyenlieu(id_nl)
        QMessageBox.information(self, "Đã xoá", f"Đã xoá nguyên liệu ID {id_nl}")
        self.tai_lai_bang()

 
    
        
class MonManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trang Quản Lý Món")
        self.resize(700, 500)

        layout = QVBoxLayout(self)


        # --- Form nhập
        form_layout = QFormLayout()
        self.ten_input = QLineEdit()
        self.gia_input = QLineEdit()
        self.loai_input = QLineEdit()
        self.mo_ta_input = QLineEdit()
        form_layout.addRow("Tên Món:", self.ten_input)
        form_layout.addRow("Đơn Giá:", self.gia_input)
        form_layout.addRow("Loại:", self.loai_input)  # Đổi vị trí Mô Tả và Loại ở form
        form_layout.addRow("Mô Tả:", self.mo_ta_input)
        layout.addLayout(form_layout)

        # --- Nút thêm
        them_btn = QPushButton("Thêm Món")
        them_btn.clicked.connect(self.them_mon)
        layout.addWidget(them_btn)

        # --- Bảng món
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Tên", "Đơn Giá", "Loại", "Mô Tả"])  # Đổi thứ tự header
        layout.addWidget(self.table)

        # --- Nút xóa
        xoa_btn = QPushButton("Xoá món được chọn")
        xoa_btn.clicked.connect(self.xoa_mon)
        layout.addWidget(xoa_btn)

        self.tai_lai_bang()

    def tai_lai_bang(self):
        self.table.setRowCount(0)
        data = read_all_mon()
        for row_idx, row in enumerate(data):
            self.table.insertRow(row_idx)
            # Giả sử dữ liệu trả về từ read_all_mon() có thứ tự là [ID, Tên, Đơn Giá, Mô Tả, Loại]
            # Chúng ta cần sắp xếp lại khi thêm vào bảng
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))  # ID
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(row[1])))  # Tên
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row[2])))  # Đơn Giá
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(row[4])))  # Loại (lấy từ index 4)
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row[3])))  # Mô Tả (lấy từ index 3)
            # Căn giữa dữ liệu (tùy chọn)
            for col_idx in range(self.table.columnCount()):
                if col_idx != 4: # Không căn giữa cột Mô Tả (giờ là cột cuối)
                    self.table.item(row_idx, col_idx).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.horizontalHeader().setStretchLastSection(True) # "Mô Tả" giờ là cột cuối


    def them_mon(self):
        ten = self.ten_input.text()
        try:
            gia = float(self.gia_input.text())
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Đơn giá phải là số!")
            return
        mo_ta = self.mo_ta_input.text()
        loai = self.loai_input.text()

        if not ten or not loai: # Thứ tự kiểm tra có thể cần điều chỉnh tùy logic
            QMessageBox.warning(self, "Thiếu thông tin", "Tên và loại không được để trống.")
            return

        create_mon(ten, gia, mo_ta, loai) # Giữ nguyên thứ tự khi gọi hàm tạo
        QMessageBox.information(self, "Thành công", "Đã thêm món thành công!")
        self.ten_input.clear()
        self.gia_input.clear()
        self.loai_input.clear()
        self.mo_ta_input.clear()
        self.tai_lai_bang()

    def xoa_mon(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Chưa chọn", "Hãy chọn một món để xoá.")
            return

        id_mon = int(self.table.item(selected_row, 0).text())
        delete_mon(id_mon)
        QMessageBox.information(self, "Đã xoá", f"Đã xoá món có ID {id_mon}")
        self.tai_lai_bang()


class Doanh_thu(QWidget):
    def __init__(self,connection):
        super().__init__()
        self.conn = connection
        self.cursor = connection.cursor()
        self.setWindowTitle("Thống kê Doanh Thu")
        self.resize(800, 600)

        self.layout = QVBoxLayout(self)

        # Tổng doanh thu toàn bộ
        self.total_label = QLabel("Tổng doanh thu (toàn bộ):")
        self.total_result = QLabel("0 VND")

        # Tổng doanh thu theo tháng
        self.month_layout = QHBoxLayout()
        self.month_input = QLineEdit()
        self.month_input.setPlaceholderText("Nhập tháng (1-12)")
        self.month_btn = QPushButton("Tính tổng theo tháng")
        self.month_btn.clicked.connect(self.tinh_tong_theo_thang)
        self.month_result = QLabel("0 VND")
        self.month_layout.addWidget(self.month_input)
        self.month_layout.addWidget(self.month_btn)
        self.month_layout.addWidget(self.month_result)

        # Tổng doanh thu theo năm
        self.year_layout = QHBoxLayout()
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Nhập năm")
        self.year_btn = QPushButton("Tính tổng theo năm")
        self.year_btn.clicked.connect(self.tinh_tong_theo_nam)
        self.year_result = QLabel("0 VND")
        self.year_layout.addWidget(self.year_input)
        self.year_layout.addWidget(self.year_btn)
        self.year_layout.addWidget(self.year_result)

        # Trung bình doanh thu toàn bộ
        self.avg_label = QLabel("Trung bình doanh thu (toàn bộ):")
        self.avg_result = QLabel("0 VND")

        # Trung bình doanh thu theo tháng
        self.avg_month_layout = QHBoxLayout()
        self.avg_month_input = QLineEdit()
        self.avg_month_input.setPlaceholderText("Nhập tháng")
        self.avg_month_btn = QPushButton("Tính TB theo tháng")
        self.avg_month_btn.clicked.connect(self.tinh_avg_thang)
        self.avg_month_result = QLabel("0 VND")
        self.avg_month_layout.addWidget(self.avg_month_input)
        self.avg_month_layout.addWidget(self.avg_month_btn)
        self.avg_month_layout.addWidget(self.avg_month_result)

        # Trung bình doanh thu theo năm
        self.avg_year_layout = QHBoxLayout()
        self.avg_year_input = QLineEdit()
        self.avg_year_input.setPlaceholderText("Nhập năm")
        self.avg_year_btn = QPushButton("Tính TB theo năm")
        self.avg_year_btn.clicked.connect(self.tinh_avg_nam)
        self.avg_year_result = QLabel("0 VND")
        self.avg_year_layout.addWidget(self.avg_year_input)
        self.avg_year_layout.addWidget(self.avg_year_btn)
        self.avg_year_layout.addWidget(self.avg_year_result)

        # Tìm kiếm hóa đơn theo ID (code của bạn)
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập ID hóa đơn")
        self.search_btn = QPushButton("Tìm hóa đơn")
        self.search_btn.clicked.connect(self.hien_thi_hoa_don)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_btn)
        self.layout.addLayout(self.search_layout)

        # Tạo canvas cho biểu đồ
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Nút vẽ biểu đồ
        self.year_chart_layout = QHBoxLayout()
        self.year_label = QLabel("Chọn năm để vẽ biểu đồ:")
        self.year_combo = QComboBox()
        self.year_chart_layout.addWidget(self.year_label)
        self.year_chart_layout.addWidget(self.year_combo)
        self.layout.addLayout(self.year_chart_layout)
        
        
        self.table = QTableWidget()  # Đảm bảo khai báo self.table
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tên món", "Số lượng", "Đơn giá", "Phương thức thanh toán"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 80)
        header.setSectionResizeMode(2, header.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 100)
        header.setSectionResizeMode(3, header.ResizeMode.Stretch)
        self.layout.addWidget(self.table)
        
        
        self.hoa_don_result = QTextEdit()
        self.hoa_don_result.setReadOnly(True)

        # Thêm tất cả vào layout chính
        self.layout.addWidget(self.total_label)
        self.layout.addWidget(self.total_result)
        self.layout.addLayout(self.month_layout)
        self.layout.addLayout(self.year_layout)
        self.layout.addWidget(self.avg_label)
        self.layout.addWidget(self.avg_result)
        self.layout.addLayout(self.avg_month_layout)
        self.layout.addLayout(self.avg_year_layout)
        self.layout.addLayout(self.search_layout)
        self.layout.addWidget(self.hoa_don_result)

        self.cap_nhat_so_lieu()

        # Lấy danh sách các năm từ NGAY_HOADON
        self.load_years()

        # Vẽ biểu đồ ban đầu (nếu có năm được chọn)
        self.year_combo.currentTextChanged.connect(self.ve_bieu_do_doanh_thu)
    def load_years(self):
        """
        Lấy danh sách các năm từ cột NGAY_HOADON trong bảng HOA_DON và thêm vào QComboBox.
        """
        try:
            self.cursor.execute("SELECT DISTINCT YEAR(NGAY_HOADON) FROM HOA_DON ORDER BY YEAR(NGAY_HOADON)")
            years = [str(row[0]) for row in self.cursor.fetchall()]
            self.year_combo.addItems(years)
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            error_msg = ex.args[1]
            print(f"Lỗi truy vấn SQL: {sqlstate} - {error_msg}")

    def ve_bieu_do_doanh_thu(self):
        """
        Vẽ biểu đồ doanh thu theo tháng trong năm được chọn.
        """
        selected_year = self.year_combo.currentText()
        if not selected_year:
            return

        try:
            # Truy vấn tổng doanh thu theo tháng trong năm được chọn
            self.cursor.execute("""
                SELECT MONTH(NGAY_HOADON) as thang, SUM(TONGTIEN) as doanh_thu
                FROM HOA_DON
                WHERE YEAR(NGAY_HOADON) = ?
                GROUP BY MONTH(NGAY_HOADON)
                ORDER BY thang
            """, (selected_year,))
            data = self.cursor.fetchall()

            # Xóa biểu đồ cũ
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            if not data:
                ax.text(0.5, 0.5, f"Không có dữ liệu cho năm {selected_year}", 
                        horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
                self.canvas.draw()
                return

            months = [row[0] for row in data]  # Tháng
            revenues = [row[1] for row in data]  # Doanh thu

            # Vẽ biểu đồ cột
            ax.bar(months, revenues, color='skyblue')
            ax.set_xlabel("Tháng")
            ax.set_ylabel("Doanh thu (VND)")
            ax.set_title(f"Doanh thu theo tháng (Năm {selected_year})")
            ax.set_xticks(range(1, 13))  # Hiển thị tất cả 12 tháng
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
            self.canvas.draw()

        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            error_msg = ex.args[1]
            print(f"Lỗi truy vấn SQL: {sqlstate} - {error_msg}")
    
    
    def hien_thi_hoa_don(self):
        """
        Hiển thị danh sách các món, số lượng, đơn giá và phương thức thanh toán của một ID_HOADON vào bảng.
        """
        id_hoadon = self.search_input.text().strip()
        if not id_hoadon:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Vui lòng nhập ID hóa đơn"))
            return

        try:
            # Truy vấn SQL
            self.cursor.execute("""
                SELECT cthd.TEN_MON, cthd.SO_LUONG, cthd.DON_GIA, hd.HINH_THUC_TT
                FROM CT_HOADON cthd
                LEFT JOIN HOA_DON hd ON cthd.ID_HOADON = hd.ID_HOADON
                WHERE cthd.ID_HOADON = ?
            """, (id_hoadon,))
            chi_tiet = self.cursor.fetchall()

            # Xóa dữ liệu cũ trong bảng
            self.table.setRowCount(0)

            if not chi_tiet:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem(f"Không tìm thấy chi tiết hóa đơn cho ID_HOADON = {id_hoadon}"))
                return

            # Điền dữ liệu vào bảng
            self.table.setRowCount(len(chi_tiet))
            for row_idx, row in enumerate(chi_tiet):
                ten_mon, so_luong, don_gia, phuong_thuc = row
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(ten_mon)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(so_luong)))
                self.table.setItem(row_idx, 2, QTableWidgetItem(f"{don_gia:,.2f}"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(phuong_thuc) if phuong_thuc else "N/A"))

        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            error_msg = ex.args[1]
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Lỗi truy vấn SQL: {sqlstate} - {error_msg}"))

    def closeEvent(self, event):
        self.cursor.close()
        self.conn.close()
        event.accept()

    def cap_nhat_so_lieu(self):

        self.total_result.setText(f"{tong_all_doanhthu():,} VND")
        self.avg_result.setText(f"{avg_doanhthu():,.0f} VND")

    def tinh_tong_theo_thang(self):

        try:
            month = int(self.month_input.text())
            self.month_result.setText(f"{tong_thang_doanhthu(month):,} VND")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def tinh_tong_theo_nam(self):

        try:
            year = int(self.year_input.text())
            self.year_result.setText(f"{tong_nam_doanhthu(year):,} VND")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def tinh_avg_thang(self):

        try:
            thang = int(self.avg_month_input.text())
            self.avg_month_result.setText(f"{avg_thang(thang):,.0f} VND")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def tinh_avg_nam(self):

        try:
            nam = int(self.avg_year_input.text())
            self.avg_year_result.setText(f"{avg_nam(nam):,.0f} VND")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

            
if __name__ == "__main__":
    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.RoundPreferFloor
    )
    
    app = QApplication(sys.argv)
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    window = LoginWindow(conn)
    window.show()
    sys.exit(app.exec())