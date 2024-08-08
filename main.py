from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QLineEdit, QGridLayout, QPushButton, \
    QComboBox, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import sqlite3


class DBConnection:
    def __init__(self, db_file="database.db"):
        self.db_file = db_file

    def connect(self):
        connection = sqlite3.connect(self.db_file)
        return connection


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
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Find student
        search_action = QAction(QIcon("icons/search.png"), "Search Student", self)
        file_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # About
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # Main window – Student table
        self.table = QTableWidget()

        # Set columns
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Phone"))

        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)

        self.table.verticalHeader().setVisible(False)

        self.setCentralWidget(self.table)
        self.load_data()

        # Toolbar & elements
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.table.cellClicked.connect(self.cell_selected)  # Detect cell click

    def cell_selected(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        """Load student data from the database into the student table """
        connection = DBConnection().connect()
        self.table.setRowCount(0)  # So the data doesn't get added on top of the existing data
        data = connection.execute("SELECT * FROM students")
        for row_nr, row_data in enumerate(data):
            self.table.insertRow(row_nr)
            for column_nr, data in enumerate(row_data):
                self.table.setItem(row_nr, column_nr, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        """Display a dialog to insert a new student record into the table and database"""
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        """Display a dialog to search for a student by name"""
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        """Display a dialog to edit a selected student record"""
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        """Display a dialot to delete a selected student record"""
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        """Display the About dialog"""
        dialog = AboutDialog()
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
        connection = DBConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)", (name, course, phone))
        connection.commit()
        cursor.close()
        connection.close()

        # Display the newly added data
        main_window.load_data()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Record")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()

        # Get data to edit from the selected row
        row_index = main_window.table.currentRow()
        self.student_id = main_window.table.item(row_index, 0).text()
        student_name = main_window.table.item(row_index, 1).text()
        course_name = main_window.table.item(row_index, 2).text()
        phone_nr = main_window.table.item(row_index, 3).text()

        # Dialog fields
        # Student name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Course name
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Phone number
        self.phone_nr = QLineEdit(phone_nr)
        self.phone_nr.setPlaceholderText("")
        layout.addWidget(self.phone_nr)

        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.update)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def update(self):
        connection = DBConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(), self.course_name.itemText(self.course_name.currentIndex()),
                        self.phone_nr.text(), self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        main_window.load_data()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Record")
        self.setFixedSize(300, 100)

        layout = QGridLayout()

        # Confirmation msg
        confirmation = QLabel("Are you sure you want to delete this record?")
        yes = QPushButton("YES")
        no = QPushButton("NO")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        # Delete on YES
        yes.clicked.connect(self.delete_record)

    def delete_record(self):
        # Get index and id from the table
        row_index = main_window.table.currentRow()
        student_id = main_window.table.item(row_index, 0).text()

        connection = DBConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Yay!")
        confirmation_widget.setText("The record has been deleted.")
        confirmation_widget.exec()


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
        connection = DBConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (searched_name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(searched_name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About This App")
        content = "This is a super simple student management system app developed to practice OOP and PyQt6 and " \
                  "working with databases :) "
        self.setText(content)

# Initialize the app and display the main window
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
