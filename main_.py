import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                            QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                            QLineEdit, QFrame, QScrollArea, QSpacerItem, 
                            QSizePolicy, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QMessageBox, QDialog, QListWidget,
                            QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
import difflib
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users = {
            "admin": {"password": "1234", "email": "admin@coffeef5.com"},
            "staff": {"password": "1111", "email": "staff@coffeef5.com"}
        }
    
    def authenticate(self, username, password):
        user = self.users.get(username)
        if user and user["password"] == password:
            return True
        return False
    
    def register(self, username, password, email):
        if username in self.users:
            return False, "Username already exists!"
        if not username or not password or not email:
            return False, "All fields are required!"
        self.users[username] = {"password": password, "email": email}
        return True, "Registration successful!"

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
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
        font.setPointSize(10)
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
        signup_button.clicked.connect(self.show_signup_dialog)
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
        forgot_password_button.clicked.connect(self.show_forgot_password_dialog)
        main_layout.addWidget(forgot_password_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields!")
            return
            
        if self.user_manager.authenticate(username, password):
            self.main_window = CoffeePOS()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Invalid credentials!")

    def show_signup_dialog(self):
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
        self.signup_username = QLineEdit()
        self.signup_username.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.signup_username.returnPressed.connect(lambda: self.signup_password.setFocus())
        
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: white; font-size: 14px;")
        self.signup_password = QLineEdit()
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_password.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.signup_password.returnPressed.connect(lambda: self.signup_email.setFocus())
        
        email_label = QLabel("Email:")
        email_label.setStyleSheet("color: white; font-size: 14px;")
        self.signup_email = QLineEdit()
        self.signup_email.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.signup_email.returnPressed.connect(lambda: confirm_button.click())
        
        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(self.signup_username, 0, 1)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.signup_password, 1, 1)
        form_layout.addWidget(email_label, 2, 0)
        form_layout.addWidget(self.signup_email, 2, 1)
        
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
        confirm_button.clicked.connect(lambda: self.handle_signup(dialog))
        
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
        
        self.signup_username.setFocus()
        dialog.exec()

    def handle_signup(self, dialog):
        username = self.signup_username.text().strip()
        password = self.signup_password.text().strip()
        email = self.signup_email.text().strip()
        
        success, message = self.user_manager.register(username, password, email)
        if success:
            QMessageBox.information(self, "Success", message)
            dialog.accept()
        else:
            QMessageBox.critical(self, "Error", message)

    def show_forgot_password_dialog(self):
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
        self.forgot_username = QLineEdit()
        self.forgot_username.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.forgot_username.returnPressed.connect(lambda: self.forgot_email.setFocus())
        
        email_label = QLabel("Email:")
        email_label.setStyleSheet("color: white; font-size: 14px;")
        self.forgot_email = QLineEdit()
        self.forgot_email.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.forgot_email.returnPressed.connect(lambda: submit_button.click())
        
        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(self.forgot_username, 0, 1)
        form_layout.addWidget(email_label, 1, 0)
        form_layout.addWidget(self.forgot_email, 1, 1)
        
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
        
        self.forgot_username.setFocus()
        dialog.exec()

    def verify_user_info(self, dialog):
        username = self.forgot_username.text().strip()
        email = self.forgot_email.text().strip()
        
        if not username or not email:
            QMessageBox.warning(self, "Error", "Please fill in all fields!")
            return
        
        user = self.user_manager.users.get(username)
        if user and user["email"] == email:
            dialog.accept()
            self.show_reset_password_dialog(username)
        else:
            QMessageBox.critical(self, "Error", "Username or email is incorrect!")

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
        self.new_password.returnPressed.connect(lambda: self.confirm_password.setFocus())
        
        confirm_pass_label = QLabel("Confirm Password:")
        confirm_pass_label.setStyleSheet("color: white; font-size: 14px;")
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setStyleSheet("background-color: white; border-radius: 5px; color: black; font-size: 14px; padding: 5px;")
        self.confirm_password.returnPressed.connect(lambda: reset_button.click())
        
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
        
        self.new_password.setFocus()
        dialog.exec()

    def handle_reset_password(self, username, dialog):
        new_pass = self.new_password.text().strip()
        confirm_pass = self.confirm_password.text().strip()
        
        if not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Error", "Please fill in all fields!")
            return
            
        if new_pass != confirm_pass:
            QMessageBox.critical(self, "Error", "Passwords do not match!")
            return
            
        self.user_manager.users[username]["password"] = new_pass
        QMessageBox.information(self, "Success", "Password has been reset successfully!")
        dialog.accept()

class CoffeePOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coffee F5 - POS System")
        self.resize(1200, 700)
        
        self.menu_items = {
            "Trà gừng": 14000,
            "Soda dâu": 27000,
            "Bạc xỉu": 29000,
            "Cà Phê Đá": 27000,
            "Cà Phê Sữa": 27000,
            "Sữa Tươi Cà Phê": 30000,
            "SỮA CHUA LÁC": 28000,
            "Lipton sữa": 20000,
            "Trà sữa": 25000,
            "Trà chanh dâu": 26000,
            "Thủy MỰC sữa": 26000,
            "Mì xào bò trứng": 35000,
            "SỮA CHUA LÁC PHÔ MAI BỘ TỚC": 28000
        }
        self.tables = [f"Bàn {i}" for i in range(1, 11)]  # 10 tables
        self.current_table = "Bàn 1"  # Default table
        self.current_order = {}
        self.total_amount = 0
        self.notifications = []
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        self.setup_ui(main_layout)
    
    def setup_ui(self, main_layout):
        # Menu frame (left side)
        menu_frame = QFrame()
        menu_frame.setFrameShape(QFrame.Shape.StyledPanel)
        menu_frame.setStyleSheet("background-color: rgb(0, 51, 102);")
        menu_layout = QVBoxLayout(menu_frame)
        
        menu_title = QLabel("Menu")
        menu_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        menu_title.setStyleSheet("color: white;")
        menu_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(menu_title)
        
        # Search bar with suggestions
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        search_layout.setContentsMargins(10, 5, 10, 5)

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
        
        menu_scroll = QScrollArea()
        menu_scroll.setWidgetResizable(True)
        self.menu_content = QWidget()
        self.menu_grid = QGridLayout(self.menu_content)
        self.menu_grid.setSpacing(10)
        
        self.display_menu_items(self.menu_items)
        
        menu_scroll.setWidget(self.menu_content)
        menu_layout.addWidget(menu_scroll)
        
        # Order frame (right side)
        order_frame = QFrame()
        order_frame.setFrameShape(QFrame.Shape.StyledPanel)
        order_frame.setStyleSheet("background-color: #333; color: white;")
        order_frame.setMinimumWidth(400)
        order_frame.setMaximumWidth(500)
        order_layout = QVBoxLayout(order_frame)
        
        self.order_title = QLabel(f"Hóa đơn - {self.current_table}")  # Lưu tham chiếu để cập nhật sau
        self.order_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.order_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        order_layout.addWidget(self.order_title)
        
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
        
        buttons_layout = QHBoxLayout()
        
        print_btn = QPushButton("In")
        print_btn.setStyleSheet("background-color: #ccc; color: black; padding: 8px;")
        print_btn.clicked.connect(self.show_print_receipt_dialog)
        
        payment_btn = QPushButton("Thanh toán (F9)")
        payment_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        payment_btn.clicked.connect(self.show_payment_dialog)
        
        notification_btn = QPushButton("Thông báo")
        notification_btn.setStyleSheet("background-color: #FF4081; color: white; padding: 8px;")
        notification_btn.clicked.connect(self.show_notification_dialog)
        
        table_btn = QPushButton("Chuyển ghế bàn")
        table_btn.setStyleSheet("background-color: #64B5F6; color: white; padding: 8px;")
        table_btn.clicked.connect(self.show_table_transfer_dialog)
        
        buttons_layout.addWidget(print_btn)
        buttons_layout.addWidget(payment_btn)
        buttons_layout.addWidget(notification_btn)
        buttons_layout.addWidget(table_btn)
        
        order_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(menu_frame, 2)
        main_layout.addWidget(order_frame, 1)

    def display_menu_items(self, items):
        for i in reversed(range(self.menu_grid.count())): 
            widget = self.menu_grid.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
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

    def select_suggestion(self, item):
        self.search_input.setText(item.text())
        self.filter_menu()
        self.suggestion_list.clear()
        self.suggestion_list.hide()

    def filter_menu(self):
        search_text = self.search_input.text().lower()
        if not search_text:
            self.display_menu_items(self.menu_items)
            return
        
        matched_items = {}
        for item, price in self.menu_items.items():
            if search_text in item.lower():
                matched_items[item] = price
            else:
                matches = difflib.get_close_matches(search_text, [item.lower()], n=1, cutoff=0.6)
                if matches and matches[0] == item.lower():
                    matched_items[item] = price
        
        self.display_menu_items(matched_items)

    def add_to_order(self, item_name, price):
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

    def update_total(self):
        self.total_amount = sum(item["subtotal"] for item in self.current_order.values())
        self.total_value.setText(f"{self.total_amount:,} VND")

    def show_print_receipt_dialog(self):
        if not self.current_order:
            QMessageBox.warning(self, "Warning", "Không có món nào trong đơn hàng!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("In Hóa Đơn")
        dialog.setMinimumSize(400, 550)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 51, 102))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dialog.setPalette(palette)

        layout = QVBoxLayout(dialog)
        
        # Payment method selection
        payment_widget = QWidget()
        payment_layout = QHBoxLayout(payment_widget)
        
        payment_label = QLabel("Hình thức thanh toán:")
        payment_label.setStyleSheet("color: white; font-size: 14px;")
        payment_method = QComboBox()
        payment_method.addItems(["Tiền mặt", "Thẻ ngân hàng", "QR Code"])
        payment_method.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 5px;")
        
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(payment_method)
        layout.addWidget(payment_widget)
        
        # Receipt preview
        receipt_text = QTextEdit()
        receipt_text.setReadOnly(True)
        receipt_text.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 10px;")
        
        def update_receipt():
            # Generate receipt content
            receipt_content = "Coffee F5\n"
            receipt_content += f"Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            receipt_content += f"Bàn: {self.current_table}\n"
            receipt_content += f"Hình thức thanh toán: {payment_method.currentText()}\n"
            receipt_content += "-" * 40 + "\n"
            receipt_content += f"{'Món':<20}{'SL':<5}{'Giá':>8}{'Tổng':>8}\n"
            receipt_content += "-" * 40 + "\n"
            
            for item, data in self.current_order.items():
                receipt_content += f"{item[:19]:<20}{data['quantity']:<5}{data['price']:>8,}{data['subtotal']:>8,}\n"
            
            receipt_content += "-" * 40 + "\n"
            receipt_content += f"{'Tổng cộng':<33}{self.total_amount:>8,}\n"
            receipt_content += "\nCảm ơn quý khách!\n"
            
            receipt_text.setText(receipt_content)

        payment_method.currentTextChanged.connect(update_receipt)
        update_receipt()  # Initial display
        layout.addWidget(receipt_text)
        
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
        print_button.clicked.connect(lambda: self.print_receipt(dialog, payment_method.currentText()))
        
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
        
        dialog.exec()

    def print_receipt(self, dialog, payment_method):
        # Simulate printing
        print("Đang in hóa đơn...")
        self.add_notification(f"In hóa đơn cho {self.current_table} (Thanh toán: {payment_method})")
        QMessageBox.information(self, "Success", "Hóa đơn đã được in thành công!")
        dialog.accept()

    def show_payment_dialog(self):
        if not self.current_order:
            QMessageBox.warning(self, "Warning", "Không có món nào trong đơn hàng!")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Thanh Toán")
        dialog.setMinimumSize(350, 250)
        
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
        payment_method = QComboBox()
        payment_method.addItems(["Tiền mặt", "Thẻ ngân hàng", "QR Code"])
        payment_method.setStyleSheet("background-color: white; color: black; font-size: 14px; padding: 5px;")
        
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
        
        form_layout.addWidget(amount_label, 0, 0, 1, 2)
        form_layout.addWidget(payment_method_label, 1, 0)
        form_layout.addWidget(payment_method, 1, 1)
        form_layout.addWidget(received_label, 2, 0)
        form_layout.addWidget(received_input, 2, 1)
        form_layout.addWidget(change_label, 3, 0, 1, 2)
        
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

    def process_payment(self, dialog):
        QMessageBox.information(self, "Thanh toán", f"Đã thanh toán {self.total_amount:,} VND")
        self.add_notification(f"Thanh toán thành công cho {self.current_table}: {self.total_amount:,} VND")
        self.clear_order()
        dialog.accept()

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

    def add_notification(self, message):
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.notifications.append(f"[{timestamp}] {message}")
        if len(self.notifications) > 50:  # Limit to 50 notifications
            self.notifications.pop(0)

    def clear_notifications(self):
        self.notifications.clear()

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

    def transfer_table(self, new_table, dialog):
        if new_table == self.current_table:
            QMessageBox.warning(self, "Warning", "Vui lòng chọn bàn khác!")
            return
        
        old_table = self.current_table
        self.current_table = new_table
        self.order_title.setText(f"Hóa đơn - {self.current_table}")  # Cập nhật tiêu đề hóa đơn
        self.order_table.setHorizontalHeaderLabels([f"Món ({new_table})", "Giá", "SL", "Thành tiền"])
        self.add_notification(f"Chuyển đơn hàng từ {old_table} sang {new_table}")
        QMessageBox.information(self, "Success", f"Đã chuyển sang {new_table}!")
        dialog.accept()

    def clear_order(self):
        self.order_table.setRowCount(0)
        self.current_order = {}
        self.total_amount = 0
        self.total_value.setText("0 VND")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())