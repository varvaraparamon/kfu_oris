import sys

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QPushButton, QHBoxLayout, QListWidget, \
    QRadioButton, QListWidgetItem, QCheckBox, QLabel, QMessageBox

from client import TaskClient

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

        self.client = TaskClient()
        self.client.tasks_updated.connect(self.update_gui)
        self.client.connect()

    def get_priority(self):
        if self.high_priority.isChecked():
            return "high"
        elif self.low_priority.isChecked():
            return "low"
        return "medium"

    def add_task(self):
        text = self.task_input.text().strip()
        if text:
            priority = self.get_priority()
            self.client.send_command({"action": "add", "text": text, "priority": priority})
            self.task_input.clear()

    def delete_task(self):
        selected_item = self.tasks_list.currentItem()
        if selected_item:
            index = self.tasks_list.row(selected_item)
            self.client.send_command({"action": "delete", "index": index})

    def delete_completed_task(self):
        for i, task in enumerate(self.client.tasks):
            if task.get("completed"):
                self.client.send_command({"action": "delete", "index": i})

    def update_gui(self, tasks):
        self.tasks_list.clear()
        for idx, task_data in enumerate(tasks):
            text = task_data["text"]
            priority = task_data["priority"]
            completed = task_data["completed"]

            widget = TaskWidget(text, priority)
            widget.completed = completed
            widget.checkbox.setChecked(completed)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())

            widget.checkbox.stateChanged.connect(
                lambda state, i=idx: self.client.send_command({
                    "action": "update",
                    "index": i,
                    "completed": state == 2
                })
            )

            self.tasks_list.addItem(item)
            self.tasks_list.setItemWidget(item, widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    app.exec()