from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.graphics import (Color, Ellipse, Rectangle, Line)
from kivy.core.image import Image
from time import sleep as time_sleep
from random import randint as random_int
from parse_args import get_arguments as get_args
from parse_args import set_arguments as set_args
from threading import Thread as NewThread
from subprocess import check_output as cmd_run_log
from subprocess import CalledProcessError as ExitCodeException
from subprocess import STDOUT as stdout
from os import getcwd as get_current_dir
from os import name as os_type
from os import chdir as change_dir
from os import listdir as scan_dir
from os.path import isdir as is_dir
'''
try:
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
except ImportError:
    print('Import error')
'''


class PixelsuftTerminalWidget(Widget):
    def __init__(self, **kwargs):
        self.fps = 60
        self.keyboard_opened = False
        self.button_pressed = []
        self.shift = False
        self.back_commands = ['']
        self.history = []
        self.jumping = 0
        self.current_command = ''
        self.cursor_count = -30
        self.encoding = 'utf-8'
        self.cursor = '_'
        self.btn = Image('btn.png').texture
        self.btn_hover = Image('btn_hover.png').texture
        self.btn_click = Image('btn_click.png').texture
        self.btn_border = Image('btn_border.png').texture
        self.btn_click_border = Image('btn_click_border.png').texture
        self.btn_hover_border = Image('btn_hover_border.png').texture
        self.keyboard_mas = []
        self.keyboard_special = [
            'Shift', 'Up', ' ', 'BackSpace', 'Enter'
        ]
        self.keyboard_nums_lower = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='
        ]
        self.keyboard_nums_upper = [
            '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+'
        ]
        self.keyboard_lower = [
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '\\'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
        ]
        self.keyboard_upper = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '\"', '|'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?']
        ]
        Window.bind(on_key_down=self.on_keyboard_down)
        Window.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.main_loop, 1 / self.fps)
        super(PixelsuftTerminalWidget, self).__init__(**kwargs)

    def get_height(self, top, height=0):
        if type(height) == int:
            return self.height - top - height
        else:
            return self.height - top - height[0]

    def draw_button(self, pos, size, text='', font_size=25):
        with self.canvas:
            Rectangle(texture=self.btn_border, pos=(pos[0], self.get_height(pos[1], size[1])), size=size)
            Rectangle(
                texture=self.btn,
                pos=(
                    pos[0] + 1,
                    self.get_height(pos[1] + 1, size[1] - 1)
                ),
                size=(
                    size[0] - 1,
                    size[1] - 1
                )
            )
            if text:
                this_text = CoreLabel(text=text, font_size=font_size, color=(0, 0, 0, 1))
                this_text.refresh()
                Rectangle(
                    texture=this_text.texture,
                    pos=(pos[0], self.get_height(pos[1], size[1])),
                    size=(font_size * len(text) / 2.5, font_size * 1.2)
                )

    def draw_pressed_button(self, pos, size, text='', font_size=25):
        with self.canvas:
            Rectangle(texture=self.btn_click_border, pos=(pos[0], self.get_height(pos[1], size[1])), size=size)
            Rectangle(
                texture=self.btn_click,
                pos=(
                    pos[0] + 1,
                    self.get_height(pos[1] + 1, size[1] - 1)
                ),
                size=(
                    size[0] - 1, size[1] - 1
                )
            )
            if text:
                this_text = CoreLabel(text=text, font_size=font_size, color=(0, 0, 0, 1))
                this_text.refresh()
                Rectangle(
                    texture=this_text.texture,
                    pos=(pos[0], self.get_height(pos[1], size[1])),
                    size=(font_size * len(text) / 2.5, font_size * 1.2)
                )

    def draw_current_path(self):
        t = 0
        if self.keyboard_opened:
            t = 150
        this_dir = get_current_dir()
        this_dir_text = CoreLabel(text=this_dir, font_size=15)
        this_dir_text.refresh()
        Color(1, 0, 0, 1)
        Rectangle(
            pos=(0, t + 30),
            size=(15 * len(this_dir) / 2.5, 15 * 1.2)
        )
        Color(0, 0, 0, 1)
        Rectangle(
            texture=this_dir_text.texture,
            pos=(0, t + 30),
            size=(15 * len(this_dir) / 2.5, 15 * 1.2)
        )

    def draw_input(self):
        t = 0
        if self.keyboard_opened:
            t = 150
        temp_text = f'>> {self.current_command}'
        if self.cursor_count < 0:
            if self.cursor_count >= -1:
                self.cursor_count = 0
            else:
                self.cursor_count += 1
                temp_text += self.cursor
        else:
            if self.cursor_count > 30:
                self.cursor_count = -31
            else:
                self.cursor_count += 1
        this_dir_text = CoreLabel(text=temp_text, font_size=15)
        this_dir_text.refresh()
        Color(0, 1, 0, 1)
        Rectangle(
            texture=this_dir_text.texture,
            pos=(0, t),
            size=(15 * len(temp_text) / 2.5, 15 * 1.2)
        )

    def draw_result(self):
        t = 50
        if self.keyboard_opened:
            t = 200
        i = len(self.history)
        while t < self.height + self.jumping and i > 0:
            i -= 1
            temp_text = self.history[i][1]
            if temp_text:
                for j in temp_text.split('\n')[::-1]:
                    this_dir_text = CoreLabel(text=j, font_size=15)
                    this_dir_text.refresh()
                    Color(0, 1, 0, 1)
                    Rectangle(
                        texture=this_dir_text.texture,
                        pos=(0, t + self.jumping),
                        size=(15 * len(j) / 2.5, 15 * 1.2)
                    )
                    t += 15
            temp_text_run = self.history[i][0]
            this_dir_text = CoreLabel(text=temp_text_run, font_size=15)
            this_dir_text.refresh()
            Color(0, 1, 0, 1)
            Rectangle(
                texture=this_dir_text.texture,
                pos=(0, t + self.jumping),
                size=(15 * len(temp_text_run) / 2.5, 15 * 1.2)
            )
            t += 15

    def command_up(self):
        if len(self.back_commands) > 0:
            self.current_command = self.back_commands[-1]
            self.back_commands.remove(self.back_commands[-1])

    def execute(self):
        self.back_commands.append(self.current_command)
        launch_string = self.current_command.strip()
        self.current_command = ''
        temp_cmd = get_args(launch_string)
        cmd = temp_cmd[0].lower()
        args = temp_cmd[1:]
        can_add_result = True
        result = ''
        if cmd == 'exit' or cmd == 'quit' or cmd == 'close' or cmd == 'q':
            exit()
        elif cmd == 'ver':
            result = f'Pixelsuft Terminal Beta\nRunning on {os_type}'
        elif cmd == 'encoding':
            if len(args) > 0:
                self.encoding = args[0]
        elif cmd == 'cat':
            for i in args:
                try:
                    temp_f = open(i, 'r')
                    if result:
                        result += '\n'
                    result += temp_f.read()
                    temp_f.close()
                except:
                    print(f'Error while opening {i} file!')
        elif cmd == 'dir' or cmd == 'ls' or cmd == 'listdir':
            path_to_scan = get_current_dir()
            if len(args) > 0:
                path_to_scan = args[0]
            try:
                for i in scan_dir(path_to_scan):
                    if result:
                        result += '\n'
                    result += i
            except:
                result = 'Access error!'
        elif cmd == 'cd' or cmd == 'chdir':
            if len(args) > 0 and is_dir(launch_string[len(cmd) + 1:]):
                change_dir(launch_string[len(cmd) + 1:])
        elif cmd == 'log':
            try:
                result = cmd_run_log(launch_string[4:], shell=True, encoding=self.encoding, stderr=stdout)
            except FileNotFoundError:
                result = 'File not found'
            except ExitCodeException as e:
                result = e.output + '\nProcess finished with error code.'
        elif cmd == 'eval':
            result = eval(launch_string[5:])
        elif cmd == 'cursor':
            if len(args) > 0:
                self.cursor = args[0]
        elif cmd == 'cls' or cmd == 'clear':
            self.history.clear()
            can_add_result = False
        if can_add_result:
            self.history.append((f'>> {launch_string}', result))

    def draw_keyboard(self):
        self.keyboard_mas = []
        if self.shift:
            a = len(self.keyboard_upper[2])
            a_t = self.width / a
            for i in range(a):
                if self.keyboard_upper[2][i] in self.button_pressed:
                    self.draw_pressed_button((i * a_t, self.height - 30), (a_t, 30), self.keyboard_upper[2][i])
                else:
                    self.draw_button((i * a_t, self.height - 30), (a_t, 30), self.keyboard_upper[2][i])
                self.keyboard_mas.append((self.keyboard_upper[2][i], (i * a_t, self.height - 30), (a_t, 30)))
            b = len(self.keyboard_upper[1])
            b_t = self.width / b
            for i in range(b):
                if self.keyboard_upper[1][i] in self.button_pressed:
                    self.draw_pressed_button((i * b_t, self.height - 60), (b_t, 30), self.keyboard_upper[1][i])
                else:
                    self.draw_button((i * b_t, self.height - 60), (b_t, 30), self.keyboard_upper[1][i])
                self.keyboard_mas.append((self.keyboard_upper[1][i], (i * b_t, self.height - 60), (b_t, 30)))
            c = len(self.keyboard_upper[0])
            c_t = self.width / c
            for i in range(c):
                if self.keyboard_upper[0][i] in self.button_pressed:
                    self.draw_pressed_button((i * c_t, self.height - 90), (c_t, 30), self.keyboard_upper[0][i])
                else:
                    self.draw_button((i * c_t, self.height - 90), (c_t, 30), self.keyboard_upper[0][i])
                self.keyboard_mas.append((self.keyboard_upper[0][i], (i * c_t, self.height - 90), (c_t, 30)))
            d = len(self.keyboard_nums_lower)
            d_t = self.width / d
            for i in range(d):
                if self.keyboard_nums_upper[i] in self.button_pressed:
                    self.draw_pressed_button((i * d_t, self.height - 120), (d_t, 30), self.keyboard_nums_upper[i])
                else:
                    self.draw_button((i * d_t, self.height - 120), (d_t, 30), self.keyboard_nums_upper[i])
                self.keyboard_mas.append((self.keyboard_nums_upper[i], (i * d_t, self.height - 120), (d_t, 30)))
        else:
            a = len(self.keyboard_lower[2])
            a_t = self.width / a
            for i in range(a):
                if self.keyboard_lower[2][i] in self.button_pressed:
                    self.draw_pressed_button((i * a_t, self.height - 30), (a_t, 30), self.keyboard_lower[2][i])
                else:
                    self.draw_button((i * a_t, self.height - 30), (a_t, 30), self.keyboard_lower[2][i])
                self.keyboard_mas.append((self.keyboard_lower[2][i], (i * a_t, self.height - 30), (a_t, 30)))
            b = len(self.keyboard_lower[1])
            b_t = self.width / b
            for i in range(b):
                if self.keyboard_lower[1][i] in self.button_pressed:
                    self.draw_pressed_button((i * b_t, self.height - 60), (b_t, 30), self.keyboard_lower[1][i])
                else:
                    self.draw_button((i * b_t, self.height - 60), (b_t, 30), self.keyboard_lower[1][i])
                self.keyboard_mas.append((self.keyboard_lower[1][i], (i * b_t, self.height - 60), (b_t, 30)))
            c = len(self.keyboard_lower[0])
            c_t = self.width / c
            for i in range(c):
                if self.keyboard_lower[0][i] in self.button_pressed:
                    self.draw_pressed_button((i * c_t, self.height - 90), (c_t, 30), self.keyboard_lower[0][i])
                else:
                    self.draw_button((i * c_t, self.height - 90), (c_t, 30), self.keyboard_lower[0][i])
                self.keyboard_mas.append((self.keyboard_lower[0][i], (i * c_t, self.height - 90), (c_t, 30)))
            d = len(self.keyboard_nums_lower)
            d_t = self.width / d
            for i in range(d):
                if self.keyboard_nums_lower[i] in self.button_pressed:
                    self.draw_pressed_button((i * d_t, self.height - 120), (d_t, 30), self.keyboard_nums_lower[i])
                else:
                    self.draw_button((i * d_t, self.height - 120), (d_t, 30), self.keyboard_nums_lower[i])
                self.keyboard_mas.append((self.keyboard_nums_lower[i], (i * d_t, self.height - 120), (d_t, 30)))
        e = len(self.keyboard_special)
        e_t = self.width / e
        for i in range(e):
            if self.keyboard_special[i] in self.button_pressed:
                self.draw_pressed_button((i * e_t, self.height - 150), (e_t, 30), self.keyboard_special[i])
            else:
                self.draw_button((i * e_t, self.height - 150), (e_t, 30), self.keyboard_special[i])
            self.keyboard_mas.append((self.keyboard_special[i], (i * e_t, self.height - 150), (e_t, 30)))

    def main_loop(self, sec):
        self.canvas.clear()
        with self.canvas:
            self.draw_result()
            self.draw_current_path()
            self.draw_input()
            Color(1, 1, 1, 1)
            if self.keyboard_opened:
                self.draw_keyboard()
                self.draw_pressed_button((0, 0), (30, 30), ' O ')
            else:
                self.draw_button((0, 0), (30, 30), ' O ')

    def on_touch_down(self, touch):
        can_pass = True
        norm_y = self.get_height(touch.y)
        if touch.x <= 30 and self.get_height(touch.y) <= 30:
            self.keyboard_opened = not self.keyboard_opened
            can_pass = False
        elif touch.y <= 150 and self.keyboard_opened:
            for i in self.keyboard_mas:
                if i[1][0] < touch.x < i[1][0] + i[2][0] and i[1][1] < norm_y < i[1][1] + i[2][1]:
                    if i[0] == 'Shift':
                        if self.shift:
                            if 'Shift' in self.button_pressed:
                                self.button_pressed.remove('Shift')
                            self.shift = False
                        else:
                            self.button_pressed.append('Shift')
                            self.shift = True
                    else:
                        if i[0] not in self.button_pressed:
                            if i[0] == 'BackSpace':
                                self.current_command = self.current_command[:-1]
                            elif i[0] == 'Enter':
                                self.execute()
                            elif i[0] == 'Up':
                                self.command_up()
                            else:
                                try:
                                    self.current_command += i[0]
                                except TypeError:
                                    pass
                            self.button_pressed.append(i[0])
                    can_pass = False
        if can_pass:
            a = self.height
            if self.keyboard_opened:
                a -= 150
            if norm_y < a / 2:
                self.jumping -= 5 * 15
            else:
                self.jumping += 5 * 15

    def on_touch_up(self, touch):
        norm_y = self.get_height(touch.y)
        if self.keyboard_opened:
            for i in self.keyboard_mas:
                if not i[0] == 'Shift' and i[0] in self.button_pressed:
                    self.button_pressed.remove(i[0])

    def on_keyboard_down(self, a, b, c, d, e):
        if 'shift' in e:
            self.shift = True
        elif c == 40:
            self.execute()
        elif c == 42:
            self.current_command = self.current_command[:-1]
        elif c == 82:
            self.command_up()
        elif d:
            try:
                if self.shift:
                    self.current_command += d.upper()
                else:
                    self.current_command += d.lower()
            except TypeError:
                pass

    def on_keyboard_up(self, a, b, c):
        if b == 304:
            self.shift = False


class PixelsuftTerminalApp(App):
    def build(self):
        return PixelsuftTerminalWidget()


if __name__ == '__main__':
    PixelsuftTerminalApp().run()
