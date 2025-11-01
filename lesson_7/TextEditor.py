import threading
import time


class TextEditor:
    def __init__(self, auto_save_interval=3):
        self.auto_save_timer = None
        self.unsaved_changes = False
        self.content = ""
        self.save_count = 0
        self.auto_save_interval = auto_save_interval

    def on_text_change(self, new_char):
        self.content += new_char
        self.unsaved_changes = True

        self.auto_save_timer = threading.Timer(self.auto_save_interval, self.auto_save)
        self.auto_save_timer.start()

    def auto_save(self):
        if self.unsaved_changes:
            self.save_count += 1
            self.unsaved_changes = False

    def manual_save(self):
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None
        self.save_count += 1

        self.unsaved_changes = False

    def close(self):
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None

        if self.unsaved_changes:
            self.auto_save()


# ТЕСТЫ

# тест с автосохранением
def test_fast_typing():
    editor = TextEditor()

    # пользователь типа быстро печатает "Hello" (мы тут имитируем это)
    for char in "Hello":
        editor.on_text_change(char)
        time.sleep(0.5)  # быстрый ввод

    # пауза - должно сработать автосохранение (по идее)
    time.sleep(4)
    print(editor.content)

# тест с ручным сохранением
def test_manual_save():
    editor = TextEditor()

    editor.on_text_change("T")
    editor.on_text_change("e")
    editor.on_text_change("s")
    editor.on_text_change("t")

    # пользователь сохраняет вручную
    editor.manual_save()

    # ждем - автосохранение не должно сработать (по идее)
    time.sleep(4)
    print(editor.content)

# тест с закрытием с несохраненными изменениями
def test_close_with_unsaved():
    editor = TextEditor()

    editor.on_text_change("U")
    editor.on_text_change("n")
    editor.on_text_change("s")
    editor.on_text_change("a")
    editor.on_text_change("v")
    editor.on_text_change("e")
    editor.on_text_change("d")

    # закрываем сразу - должно выполнить автосохранение
    editor.close()
    print(editor.content)

test_fast_typing()
test_manual_save()
test_close_with_unsaved()
