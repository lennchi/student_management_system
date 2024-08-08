from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QLineEdit, QGridLayout, QPushButton, \
    QComboBox, QMainWindow, QTableWidget, QTableWidgetItem, QDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.resize(500, 400)

        # Top menu
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Menu items inside top menu
        # Add student
        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Find student
        search_action = QAction("Search Student", self)
        file_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        #About
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        # Student table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))
        self.table.verticalHeader().setVisible(False)

        # Set column widths
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)

        self.setCentralWidget(self.table)
        self.load_data()

    def load_data(self):
        connection = sqlite3.connect("database.db")
        self.table.setRowCount(0)  # So the data doesn't get added on top of the existing data
        data = connection.execute("SELECT * FROM students")
        for row_nr, row_data in enumerate(data):
            self.table.insertRow(row_nr)
            for column_nr, data in enumerate(row_data):
                self.table.setItem(row_nr, column_nr, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Dialog fields
        # Student name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Student name")
        layout.addWidget(self.student_name)

        # Course name
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Phone number
        self.phone_nr = QLineEdit()
        self.phone_nr.setPlaceholderText("Student phone number")
        layout.addWidget(self.phone_nr)

        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        phone = self.phone_nr.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)", (name, course, phone))
        connection.commit()
        cursor.close()
        connection.close()

        # Display the newly added data
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        # Dialog fields
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter student name")
        layout.addWidget(self.search_box)

        # Search button
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_student)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search_student(self):
        searched_name = self.search_box.text()
        # Connect to the DB
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (searched_name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(searched_name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


# Initialize the app and display the main window
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
