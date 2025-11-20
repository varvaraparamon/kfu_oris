import sys

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QPushButton, QHBoxLayout, QListWidget, \
    QRadioButton, QListWidgetItem, QCheckBox, QLabel, QMessageBox

class TaskWidget(QWidget):
    def __init__(self, text, priority):
        super().__init__()
        self.text = text
        self.priority = priority
        self.completed = False

        layout = QHBoxLayout(self)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.update_style)

        self.label = QLabel(text)
        self.apply_priority_style()

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)

    def apply_priority_style(self):
        colors = {
            "high" : "red",
            "medium" : "orange",
            "low" : "green"
        }
        color = colors.get(self.priority)
        self.label.setStyleSheet(f"color: {color}; font-weight: bold")

    def update_style(self, state):
        self.completed = state == 2
        if self.completed:
            self.label.setStyleSheet("color: gray; text-decoration: line-through;")
        else:
            self.apply_priority_style()

class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")

        layout = QVBoxLayout(self)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите задачу...")

        buttons_layout = QHBoxLayout()

        add_button = QPushButton("Добавить задачу")
        delete_button = QPushButton("Удалить выбранную задачу")
        clear_completed_task = QPushButton("Удалить все выполненные")

        self.tasks_list = QListWidget()

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(clear_completed_task)

        priority_layout = QHBoxLayout()

        self.low_priority = QRadioButton("Низкий")
        self.medium_priority = QRadioButton("Средний")
        self.high_priority = QRadioButton("Высокий")

        self.medium_priority.setChecked(True)

        priority_layout.addWidget(self.low_priority)
        priority_layout.addWidget(self.medium_priority)
        priority_layout.addWidget(self.high_priority)
        priority_layout.addStretch()

        layout.addWidget(self.task_input)
        layout.addLayout(priority_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.tasks_list)

        add_button.clicked.connect(self.add_task)
        self.task_input.returnPressed.connect(self.add_task)
        delete_button.clicked.connect(self.delete_task)
        clear_completed_task.clicked.connect(self.delete_completed_task)

    def get_priority(self):
        if self.high_priority.isChecked():
            return "high"
        elif self.low_priority.isChecked():
            return "low"
        return "medium"

    def add_task(self):
        text = self.task_input.text().strip()
        if text:
            task = TaskWidget(text, self.get_priority())
            item = QListWidgetItem()
            item.setSizeHint(task.sizeHint())
            self.tasks_list.addItem(item)
            self.tasks_list.setItemWidget(item, task)
            self.task_input.clear()

    def delete_task(self):
        selected_item = self.tasks_list.currentItem()
        if selected_item:
            row = self.tasks_list.row(selected_item)
            self.tasks_list.takeItem(row)

    def delete_completed_task(self):
        count = 0
        for i in range(self.tasks_list.count() - 1, -1, -1):
            item = self.tasks_list.item(i)
            widget = self.tasks_list.itemWidget(item)
            if widget.completed:
                self.tasks_list.takeItem(i)
                count += 1
        msg = "Нет выполненных задач" if count == 0 else f"Удалено {count} задач"
        QMessageBox.information(self, "Информация", msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    app.exec()