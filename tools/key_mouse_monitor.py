from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard, mouse


class KeyMouseMonitor(QObject):
    key_pressed = pyqtSignal(str)
    key_released = pyqtSignal(str)
    mouse_pressed = pyqtSignal(str, str, str)
    mouse_scrolled = pyqtSignal(str, str, str, str)
    mouse_moved = pyqtSignal(str, str)
    left_pressed = pyqtSignal(str, str)
    left_released = pyqtSignal(str, str)
    right_pressed = pyqtSignal(str, str)
    right_released = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.keyboard_listener = None
        self.mouse_listener = None
        self.is_monitoring = False
        self.pressed_keys = set()
        self.modifier_keys = {
            'Key.ctrl', 'Key.ctrl_l', 'Key.ctrl_r',
            'Key.shift', 'Key.shift_l', 'Key.shift_r',
            'Key.alt', 'Key.alt_l', 'Key.alt_r',
            'Key.cmd', 'Key.cmd_l', 'Key.cmd_r',
            'Key.fn',
            'Key.menu',
            'Key.alt_gr'
        }
        self.last_scroll_time = None

    def start(self):
        if self.is_monitoring:
            return
        self.is_monitoring = True

        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_keyboard_press,
            on_release=self.on_keyboard_release
        )
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll_callback,
            on_move=self.on_mouse_move_callback
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self):
        if not self.is_monitoring:
            return
        self.is_monitoring = False

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

    def is_modifier(self, key_str):
        return key_str in self.modifier_keys

    def format_key_with_modifier(self, key):
        try:
            if hasattr(key, 'name'):
                return key.name
            elif hasattr(key, 'vk'):
                vk = key.vk
                if 96 <= vk <= 105:
                    return f"NumPad {vk - 96}"
                elif vk == 110:
                    return "NumPad ."
                elif vk == 106:
                    return "NumPad *"
                elif vk == 107:
                    return "NumPad +"
                elif vk == 109:
                    return "NumPad -"
                elif vk == 111:
                    return "NumPad /"
                elif vk >= 65 and vk <= 90:
                    return chr(vk).lower()
                elif vk >= 48 and vk <= 57:
                    return chr(vk)
                elif vk == 187:
                    return '='
                elif vk == 186:
                    return ';'
                elif vk == 188:
                    return ','
                elif vk == 189:
                    return '-'
                elif vk == 190:
                    return '.'
                elif vk == 191:
                    return '/'
                elif vk == 192:
                    return '`'
                elif vk == 219:
                    return '['
                elif vk == 220:
                    return '\\'
                elif vk == 221:
                    return ']'
                elif vk == 222:
                    return "'"
                elif vk == 226:
                    return '\\'
                elif hasattr(key, 'char') and key.char:
                    return key.char
                else:
                    return f"VK:{vk}"
            elif hasattr(key, 'char') and key.char:
                return key.char
            else:
                return str(key)
        except:
            return str(key)

    def on_keyboard_press(self, key):
        try:
            key_str = self.format_key(key)
            if key_str in self.pressed_keys:
                return
            self.pressed_keys.add(key_str)
            if not self.is_modifier(key_str) and len(self.pressed_keys) > 1:
                modifiers = [k for k in self.pressed_keys if self.is_modifier(k)]
                if modifiers:
                    display_key = self.format_key_with_modifier(key)
                    all_keys = modifiers + [display_key]
                    combo_str = ' + '.join([k.replace('Key.', '') for k in all_keys])
                    self.key_pressed.emit(combo_str)
                    return
            self.key_pressed.emit(key_str)
        except Exception as e:
            print(f"Key error: {e}")

    def on_keyboard_release(self, key):
        try:
            key_str = self.format_key(key)
            if key_str in self.pressed_keys:
                self.pressed_keys.remove(key_str)
            if self.is_modifier(key_str):
                self.key_released.emit(key_str)
        except Exception as e:
            print(f"Key release error: {e}")

    def on_mouse_click(self, x, y, button, pressed):
        try:
            button_name = str(button)
            if button_name == 'Button.left':
                if pressed:
                    self.left_pressed.emit(str(x), str(y))
                    self.mouse_pressed.emit(button_name, str(x), str(y))
                else:
                    self.left_released.emit(str(x), str(y))
                    self.mouse_pressed.emit(f"release:{button_name}", str(x), str(y))
            elif button_name == 'Button.right':
                if pressed:
                    self.right_pressed.emit(str(x), str(y))
                    self.mouse_pressed.emit(button_name, str(x), str(y))
                else:
                    self.right_released.emit(str(x), str(y))
                    self.mouse_pressed.emit(f"release:{button_name}", str(x), str(y))
            elif pressed:
                self.mouse_pressed.emit(button_name, str(x), str(y))
        except Exception as e:
            print(f"Mouse error: {e}")

    def on_mouse_move_callback(self, x, y):
        try:
            self.mouse_moved.emit(str(x), str(y))
        except Exception as e:
            print(f"Mouse move error: {e}")

    def on_mouse_scroll_callback(self, x, y, dx, dy):
        try:
            current_time = datetime.now()
            if self.last_scroll_time is not None:
                time_diff = (current_time - self.last_scroll_time).total_seconds()
                if time_diff < 1.0:
                    return
            self.last_scroll_time = current_time
            self.mouse_scrolled.emit(str(x), str(y), str(dx), str(dy))
        except Exception as e:
            print(f"Scroll error: {e}")

    def format_key(self, key):
        if hasattr(key, 'name'):
            return f"Key.{key.name}"
        elif hasattr(key, 'vk'):
            vk = key.vk
            if 96 <= vk <= 105:
                return f"NumPad {vk - 96}"
            elif vk == 110:
                return "NumPad ."
            elif vk == 106:
                return "NumPad *"
            elif vk == 107:
                return "NumPad +"
            elif vk == 109:
                return "NumPad -"
            elif vk == 111:
                return "NumPad /"
            elif hasattr(key, 'char') and key.char:
                return key.char
            else:
                return f"VK:{vk}"
        elif hasattr(key, 'char') and key.char:
            return key.char
        else:
            return str(key)
