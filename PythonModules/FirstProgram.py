import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(200, 200, 300, 200)

        # Create a grid layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Create username label and textbox for the first column
        username_label1 = QLabel("Username:")
        username_textbox1 = QLineEdit()
        username_textbox1.setObjectName("username1")

        # Create password label and textbox for the first column
        password_label1 = QLabel("Password:")
        password_textbox1 = QLineEdit()
        password_textbox1.setEchoMode(QLineEdit.Password)  # Mask password with *
        password_textbox1.setObjectName("password1")

        # Create PTZ camera IP address label and textbox for the first column
        ip_label1 = QLabel("PTZ Camera IP:")
        ip_textbox1 = QLineEdit()
        ip_textbox1.setObjectName("ip_address1")

        # Create the login button for the first column
        login_button1 = QPushButton("Log In")
        login_button1.clicked.connect(self.login_clicked)

        # Create username label and textbox for the second column
        username_label2 = QLabel("Username:")
        username_textbox2 = QLineEdit()
        username_textbox2.setObjectName("username2")

        # Create password label and textbox for the second column
        password_label2 = QLabel("Password:")
        password_textbox2 = QLineEdit()
        password_textbox2.setEchoMode(QLineEdit.Password)  # Mask password with *
        password_textbox2.setObjectName("password2")

        # Create PTZ camera IP address label and textbox for the second column
        ip_label2 = QLabel("PTZ Camera IP:")
        ip_textbox2 = QLineEdit()
        ip_textbox2.setObjectName("ip_address2")

        # Create the login button for the second column
        login_button2 = QPushButton("Log In")
        login_button2.clicked.connect(self.login_clicked)

        # Add widgets to the grid layout for the first column
        grid.addWidget(username_label1, 0, 0)
        grid.addWidget(username_textbox1, 0, 1)
        grid.addWidget(password_label1, 1, 0)
        grid.addWidget(password_textbox1, 1, 1)
        grid.addWidget(ip_label1, 2, 0)
        grid.addWidget(ip_textbox1, 2, 1)
        grid.addWidget(login_button1, 3, 0, 1, 2)

        # Add widgets to the grid layout for the second column
        grid.addWidget(username_label2, 0, 2)
        grid.addWidget(username_textbox2, 0, 3)
        grid.addWidget(password_label2, 1, 2)
        grid.addWidget(password_textbox2, 1, 3)
        grid.addWidget(ip_label2, 2, 2)
        grid.addWidget(ip_textbox2, 2, 3)
        grid.addWidget(login_button2, 3, 2, 1, 2)


    def login_clicked(self):
        # Perform login logic here
        username1 = self.findChild(QLineEdit, "username1").text()
        password1 = self.findChild(QLineEdit, "password1").text()
        ip_address1 = self.findChild(QLineEdit, "ip_address1").text()

        username2 = self.findChild(QLineEdit, "username2").text()
        password2 = self.findChild(QLineEdit, "password2").text()
        ip_address2 = self.findChild(QLineEdit, "ip_address2").text()

        # Example login validation
        if username1 and password1 and ip_address1 and username2 and password2 and ip_address2:
            QMessageBox.information(self, "Login", "Both Logins Successful!")
            self.close()
        elif username1 and password1 and ip_address1:
            QMessageBox.information(self, "Login", "Login Successful (1)!")
        elif username2 and password2 and ip_address2:
            QMessageBox.information(self, "Login", "Login Successful (2)!")
        else:
            QMessageBox.warning(self, "Login", "Invalid login credentials!")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(200, 200, 1200, 600)

        # Create left window
        left_window = QWidget()
        left_window.setStyleSheet("background-color: green;")

        # Create right window
        right_window = QWidget()
        right_window.setStyleSheet("background-color: blue;")

        # Create the grid layout for the main window
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        self.setLayout(grid)

        # Add left and right windows to the grid layout
        grid.addWidget(left_window, 0, 0)
        grid.addWidget(right_window, 0, 1)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    login_window = LoginWindow()
    login_window.raise_()
    login_window.activateWindow()
    login_window.show()

    sys.exit(app.exec_())
