import tkinter as tk
from tkinter import font as tkfont
import random
import time

class GameApp:
    def __init__(self, master):
        self.master = master
        self.bg_color = '#333333'
        self.button_color = '#555555'
        self.text_color = 'white'
        self.screen_width = 1200
        self.screen_height = 800
        self.high_score = 0

        self.master.title("SURFER RUN")
        self.master.configure(bg=self.bg_color)
        self.master.geometry(f"{self.screen_width}x{self.screen_height}")
        self.master.resizable(False, False)

        self.score = 0
        self.game_paused = False
        self.game_active = False
        self.sound_on = True

        self.player_x = 150
        self.player_y = 650
        self.player_velocity_y = 0
        self.gravity = 0.5
        self.jump_power = -12
        self.ground_level = 650

        self.player_speed = 7
        self.move_speed = 10
        self.player_move_x = 0

        self.obstacles = []
        self.pause_menu_shown = False

        self.master.bind('<KeyPress>', self.handle_keypress)
        self.master.bind('<KeyRelease>', self.handle_keyrelease)
        self.keys_pressed = {
            'up': False,
            'left': False,
            'right': False,
            'Escape': False
        }

        self.show_main_menu()

    def create_player_sprite(self, canvas, x, y):
        head = canvas.create_oval(x - 20, y - 90, x + 20, y - 50, fill='#FFD700', outline='black')
        body = canvas.create_rectangle(x - 15, y - 50, x + 15, y - 25, fill='#4682B4', outline='black')
        left_arm = canvas.create_line(x - 15, y - 45, x - 35, y - 30, width=4, fill='#FFD700')
        right_arm = canvas.create_line(x + 15, y - 45, x + 35, y - 30, width=4, fill='#FFD700')
        left_leg = canvas.create_line(x - 8, y - 25, x - 20, y, width=4, fill='#FFD700')
        right_leg = canvas.create_line(x + 8, y - 25, x + 20, y, width=4, fill='#FFD700')
        board = canvas.create_oval(x - 40, y - 15, x + 40, y + 15, fill='#8B4513', outline='black')
        return [head, body, left_arm, right_arm, left_leg, right_leg, board]

    def create_obstacle_sprite(self, canvas, x, y):
        wave = canvas.create_arc(x, y - 40, x + 70, y + 30,
                                 start=0, extent=180,
                                 fill='#1E90FF', outline='black')
        foam = canvas.create_line(x, y, x + 70, y, width=4, fill='white')
        return [wave, foam]

    def move_sprite(self, canvas, sprite, x, y):
        if len(sprite) == 7:
            head, body, left_arm, right_arm, left_leg, right_leg, board = sprite
            canvas.coords(head, x - 20, y - 90, x + 20, y - 50)
            canvas.coords(body, x - 15, y - 50, x + 15, y - 25)
            canvas.coords(left_arm, x - 15, y - 45, x - 35, y - 30)
            canvas.coords(right_arm, x + 15, y - 45, x + 35, y - 30)
            canvas.coords(left_leg, x - 8, y - 25, x - 20, y)
            canvas.coords(right_leg, x + 8, y - 25, x + 20, y)
            canvas.coords(board, x - 40, y - 15, x + 40, y + 15)
        elif len(sprite) == 2:
            wave, foam = sprite
            canvas.coords(wave, x, y - 40, x + 70, y + 30)
            canvas.coords(foam, x, y, x + 70, y)

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()
        self.game_active = False

        container = tk.Frame(self.master, bg=self.bg_color)
        container.pack(expand=True, fill='both')

        title_font = tkfont.Font(family="Impact", size=72, weight="bold")
        tk.Label(container, text="SURFER RUN", font=title_font,
                 fg=self.text_color, bg=self.bg_color).pack(pady=(120, 80))

        buttons = [
            ("ИГРАТЬ", self.start_game),
            ("НАСТРОЙКИ", self.show_settings_menu),
            ("ВЫЙТИ ИЗ ИГРЫ", self.master.quit)
        ]

        for text, cmd in buttons:
            btn = self.create_button(container, text, cmd, width=400, height=70)
            btn.pack(pady=25)

    def show_settings_menu(self):
        self.clear_window()

        container = tk.Frame(self.master, bg=self.bg_color)
        container.pack(expand=True, fill='both')

        title_font = tkfont.Font(family="Impact", size=54, weight="bold")
        tk.Label(container, text="НАСТРОЙКИ", font=title_font,
                 fg=self.text_color, bg=self.bg_color).pack(pady=(100, 80))

        buttons = [
            (f"ЗВУК: {'ВКЛ' if self.sound_on else 'ВЫКЛ'}", self.toggle_sound),
            ("НАЗАД", self.show_main_menu)
        ]

        for text, cmd in buttons:
            btn = self.create_button(container, text, cmd, width=400, height=70)
            btn.pack(pady=30)

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.show_settings_menu()

    def start_game(self):
        self.clear_window()
        self.game_active = True
        self.game_paused = False
        self.score = 0
        self.player_y = self.ground_level
        self.player_velocity_y = 0
        self.player_move_x = 0
        self.obstacles = []
        self.pause_menu_shown = False

        self.game_canvas = tk.Canvas(self.master, bg='#222222', highlightthickness=0)
        self.game_canvas.pack(fill='both', expand=True)

        # Фон
        self.game_canvas.create_rectangle(0, 0, self.screen_width, 550, fill='#87CEEB', outline='')
        self.game_canvas.create_rectangle(0, 550, self.screen_width, self.screen_height, fill='#1E90FF', outline='')

        self.score_bg = self.game_canvas.create_rectangle(
            20, 20, 380, 100,
            fill='#444444', outline='#666666', width=2
        )

        self.current_score_label = self.game_canvas.create_text(
            200, 40, text=f"Счет: {self.score}",
            font=('Arial', 24, 'bold'), fill='white', anchor='center'
        )
        self.high_score_label = self.game_canvas.create_text(
            200, 70, text=f"Рекорд: {self.high_score}",
            font=('Arial', 24, 'bold'), fill='white', anchor='center'
        )

        self.pause_button = self.create_game_button("ПАУЗА", self.show_pause_menu, width=150, height=50)
        self.pause_button.place(relx=0.95, y=30, anchor='ne')

        self.player_sprite = self.create_player_sprite(self.game_canvas, self.player_x, self.player_y)
        self.update_game()

    def handle_keypress(self, event):
        if not self.game_active:
            return

        key = event.keysym
        if key.lower() in ('w', 'ц', 'up'):
            self.keys_pressed['up'] = True
            if self.player_y >= self.ground_level:
                self.player_velocity_y = self.jump_power
        elif key.lower() in ('a', 'ф', 'left'):
            self.keys_pressed['left'] = True
        elif key.lower() in ('d', 'в', 'right'):
            self.keys_pressed['right'] = True
        elif key == 'Escape':
            if self.game_paused:
                self.resume_game()
            else:
                self.show_pause_menu()

    def handle_keyrelease(self, event):
        key = event.keysym
        if key.lower() in ('a', 'ф', 'left'):
            self.keys_pressed['left'] = False
        elif key.lower() in ('d', 'в', 'right'):
            self.keys_pressed['right'] = False
        elif key.lower() in ('w', 'ц', 'up'):
            self.keys_pressed['up'] = False

    def move_player(self):
        if self.keys_pressed['left']:
            self.player_move_x = -self.move_speed
        elif self.keys_pressed['right']:
            self.player_move_x = self.move_speed
        else:
            self.player_move_x = 0

        new_x = self.player_x + self.player_move_x
        if 40 <= new_x <= self.screen_width - 40:
            self.player_x = new_x

        self.player_velocity_y += self.gravity
        self.player_y += self.player_velocity_y

        if self.player_y > self.ground_level:
            self.player_y = self.ground_level
            self.player_velocity_y = 0

        self.move_sprite(self.game_canvas, self.player_sprite, self.player_x, self.player_y)

    def generate_obstacles(self):
        if self.obstacles:
            last_obstacle = self.obstacles[-1]
            last_coords = self.game_canvas.coords(last_obstacle[0])
            if last_coords and last_coords[0] > self.screen_width - 300:
                return
        if random.random() < 0.03:
            x = self.screen_width
            y = self.ground_level
            obstacle_sprite = self.create_obstacle_sprite(self.game_canvas, x, y)
            self.obstacles.append(obstacle_sprite)

    def move_obstacles(self):
        for obs in self.obstacles[:]:
            for item in obs:
                self.game_canvas.move(item, -self.player_speed, 0)

            first_item_coords = self.game_canvas.coords(obs[0])
            if first_item_coords and first_item_coords[0] < -70:
                for item in obs:
                    self.game_canvas.delete(item)
                self.obstacles.remove(obs)

    def check_collisions(self):
        player_coords = self.game_canvas.coords(self.player_sprite[1])

        for obs in self.obstacles:
            obs_coords = self.game_canvas.coords(obs[0])

            if (player_coords[2] > obs_coords[0] and
                    player_coords[0] < obs_coords[2] and
                    player_coords[3] > obs_coords[1] and
                    player_coords[1] < obs_coords[3]):
                self.show_game_over_menu()
                return True
        return False

    def show_pause_menu(self):
        if not self.game_active or self.pause_menu_shown:
            return

        self.game_paused = True
        self.pause_menu_shown = True

        self.pause_frame = tk.Frame(self.master, bg=self.bg_color, bd=5, relief='ridge')
        self.pause_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=400)

        self.darken_background()

        title_font = tkfont.Font(family="Impact", size=48, weight="bold")
        tk.Label(self.pause_frame, text="ПАУЗА", font=title_font,
                 fg=self.text_color, bg=self.bg_color).pack(pady=(40, 50))

        buttons = [
            ("ПРОДОЛЖИТЬ", self.resume_game),
            ("ВЫЙТИ В МЕНЮ", self.return_to_main_menu)
        ]

        for text, cmd in buttons:
            btn = self.create_button(self.pause_frame, text, cmd, width=350, height=60)
            btn.pack(pady=15)

    def show_game_over_menu(self):
        self.game_active = False
        self.game_paused = True

        self.pause_frame = tk.Frame(self.master, bg=self.bg_color, bd=5, relief='ridge')
        self.pause_frame.place(relx=0.5, rely=0.4, anchor='center', width=500, height=450)

        self.darken_background()

        title_font = tkfont.Font(family="Impact", size=48, weight="bold")
        tk.Label(self.pause_frame, text="ИГРА ОКОНЧЕНА", font=title_font,
                 fg='red', bg=self.bg_color).pack(pady=(30, 20))

        score_frame = tk.Frame(self.pause_frame, bg=self.bg_color, height=100)
        score_frame.pack(pady=(0, 10), fill='x')

        score_font = tkfont.Font(family="Arial", size=24, weight="bold")
        tk.Label(score_frame, text=f"Текущий счет: {self.score}", font=score_font,
                 fg=self.text_color, bg=self.bg_color).pack(pady=5)
        tk.Label(score_frame, text=f"Рекорд: {self.high_score}", font=score_font,
                 fg=self.text_color, bg=self.bg_color).pack(pady=5)

        buttons_frame = tk.Frame(self.pause_frame, bg=self.bg_color)
        buttons_frame.pack(pady=(20, 30), fill='both', expand=True)

        buttons = [
            ("НАЧАТЬ ЗАНОВО", self.restart_game),
            ("ВЕРНУТЬСЯ В МЕНЮ", self.return_to_main_menu)
        ]

        for text, cmd in buttons:
            btn = self.create_button(buttons_frame, text, cmd, width=350, height=60)
            btn.pack(pady=10, fill='x')

    def restart_game(self):
        if hasattr(self, 'pause_frame'):
            self.pause_frame.destroy()
        if hasattr(self, 'dark_rect'):
            self.game_canvas.delete(self.dark_rect)
        self.start_game()

    def return_to_main_menu(self):
        self.resume_game()
        self.show_main_menu()

    def darken_background(self):
        self.dark_rect = self.game_canvas.create_rectangle(
            0, 0, self.screen_width, self.screen_height,
            fill='black', stipple='gray50', width=0
        )
        self.game_canvas.tag_lower(self.dark_rect)

    def resume_game(self):
        if not self.pause_menu_shown:
            return
        self.game_paused = False
        self.pause_menu_shown = False
        if hasattr(self, 'pause_frame'):
            self.pause_frame.destroy()
        if hasattr(self, 'dark_rect'):
            self.game_canvas.delete(self.dark_rect)

    def update_game(self):
        if not self.game_active or self.game_paused:
            self.master.after(30, self.update_game)
            return

        self.move_player()
        self.generate_obstacles()
        self.move_obstacles()

        if self.check_collisions():
            return

        self.score += 1
        self.game_canvas.itemconfig(self.current_score_label, text=f"Счет: {self.score}")

        if self.score > self.high_score:
            self.high_score = self.score
            self.game_canvas.itemconfig(self.high_score_label, text=f"Рекорд: {self.high_score}")

        if self.score % 1000 == 0 and self.score != 0:
            self.player_speed *= 1.1

        self.master.after(30, self.update_game)

    def create_button(self, parent, text, command, width=300, height=50):
        btn_frame = tk.Frame(parent, bg=self.bg_color)
        canvas = tk.Canvas(btn_frame, width=width, height=height,
                           bg=self.bg_color, highlightthickness=0)
        canvas.create_rounded_rect(0, 0, width, height, radius=25,
                                   fill=self.button_color, outline='#777777', width=2)
        canvas.create_text(width / 2, height / 2, text=text,
                           font=tkfont.Font(family="Arial", size=24, weight="bold"),
                           fill=self.text_color)

        if command:
            canvas.bind("<Button-1>", lambda e: command())
            canvas.bind("<Enter>", lambda e: canvas.itemconfig(1, fill='#666666'))
            canvas.bind("<Leave>", lambda e: canvas.itemconfig(1, fill=self.button_color))

        canvas.pack()
        return btn_frame

    def create_game_button(self, text, command, width=300, height=50):
        return self.create_button(self.master, text, command, width, height)


def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2,
        x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1
    ]
    return self.create_polygon(points, **kwargs, smooth=True)


tk.Canvas.create_rounded_rect = create_rounded_rect

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()