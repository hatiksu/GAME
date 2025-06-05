import tkinter as tk
from tkinter import font as tkfont
import random
import time
import os
import winsound
from threading import Thread


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

        self.music_playing = False
        self.music_thread = None
        self.load_images()
        self.sound_on = True
        self.background_music = "background.wav"

        # Новая система управления скоростью
        self.game_speed = 1.0  # Базовый множитель скорости (1.0 = нормальная скорость)
        self.max_game_speed = 3.0  # Максимальный множитель скорости
        self.speed_increment = 0.1  # Шаг увеличения скорости
        self.speed_increase_interval = 500  # Очки между увеличениями скорости
        
        self.score = 0
        self.last_speed_up_score = 0
        
        # Физические параметры (остаются постоянными)
        self.player_base_speed = 5
        self.move_speed = 10
        self.jump_power = -12
        self.gravity = 0.5

        self.game_paused = False
        self.game_active = False
        self.reset_game_state()

        self.master.bind('<KeyPress>', self.handle_keypress)
        self.master.bind('<KeyRelease>', self.handle_keyrelease)
        self.keys_pressed = {
            'up': False,
            'left': False,
            'right': False,
            'Escape': False
        }

        self.show_main_menu()

    def reset_game_state(self):
        """Полный сброс состояния игры"""
        self.player_x = 150
        self.player_y = 650
        self.player_velocity_y = 0
        self.ground_level = 650
        self.player_move_x = 0
        self.obstacles = []
        self.pause_menu_shown = False
        self.game_speed = 1.0  # Сбрасываем множитель скорости

    def load_images(self):
        if not os.path.exists("personazh.png"):
            raise FileNotFoundError("Файл personazh.png не найден!")
        if not os.path.exists("prepyatsvie.png"):
            raise FileNotFoundError("Файл prepyatsvie.png не найден!")

        try:
            self.player_img = tk.PhotoImage(file="personazh.png")
            width_ratio = max(1, int(self.player_img.width() / 150))
            height_ratio = max(1, int(self.player_img.height() / 140))
            self.player_img = self.player_img.subsample(width_ratio, height_ratio)

            self.obstacle_img = tk.PhotoImage(file="prepyatsvie.png")
            width_ratio = max(1, int(self.obstacle_img.width() / 100))
            height_ratio = max(1, int(self.obstacle_img.height() / 70))
            self.obstacle_img = self.obstacle_img.subsample(width_ratio, height_ratio)
        except Exception as e:
            raise Exception(f"Ошибка загрузки изображений: {str(e)}")

    def play_background_music(self):
        if not self.sound_on:
            return

        self.stop_music()
        self.music_playing = True

        def music_loop():
            try:
                while self.music_playing:
                    winsound.PlaySound(self.background_music,
                                     winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                    time.sleep(120)
            except Exception as e:
                print(f"Ошибка воспроизведения музыки: {e}")

        self.music_thread = Thread(target=music_loop, daemon=True)
        self.music_thread.start()

    def stop_music(self):
        self.music_playing = False
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass

    def create_player_sprite(self, canvas, x, y):
        return canvas.create_image(x, y, image=self.player_img)

    def create_obstacle_sprite(self, canvas, x, y):
        return canvas.create_image(x, y, image=self.obstacle_img)

    def move_sprite(self, canvas, sprite, x, y):
        canvas.coords(sprite, x, y)

    def clear_window(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()
        self.game_active = False
        if not self.music_playing:
            self.play_background_music()

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
        if self.sound_on:
            self.play_background_music()
        else:
            self.stop_music()
        self.show_settings_menu()

    def start_game(self):
        self.clear_window()
        self.reset_game_state()  # Полный сброс состояния
        self.game_active = True
        self.game_paused = False
        self.score = 0
        self.last_speed_up_score = 0

        if not self.music_playing:
            self.play_background_music()

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

        self.pause_button = self.create_button(self.master, "ПАУЗА", self.show_pause_menu, width=180, height=60)
        self.pause_button.place(relx=0.95, y=30, anchor='ne')

        self.player_sprite = self.create_player_sprite(self.game_canvas, self.player_x, self.player_y)
        self.last_update_time = time.time()
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
        player_width = self.player_img.width() / 2
        new_x = max(player_width, min(new_x, self.screen_width - player_width))

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
            last_coords = self.game_canvas.coords(last_obstacle)
            if last_coords and last_coords[0] > self.screen_width - 400:
                return
        
        # Частота генерации зависит от текущей скорости игры
        spawn_chance = 0.02 * (1.0 / self.game_speed)  # Чем выше скорость, тем реже появляются препятствия
        if random.random() < spawn_chance:
            x = self.screen_width
            y = self.ground_level + 50
            obstacle_sprite = self.create_obstacle_sprite(self.game_canvas, x, y)
            self.obstacles.append(obstacle_sprite)

    def move_obstacles(self):
        current_speed = self.player_base_speed * self.game_speed  # Реальная скорость с учетом множителя
        
        for obs in self.obstacles[:]:
            self.game_canvas.move(obs, -current_speed, 0)

            first_item_coords = self.game_canvas.coords(obs)
            if first_item_coords and first_item_coords[0] < -70:
                self.game_canvas.delete(obs)
                self.obstacles.remove(obs)

    def check_collisions(self):
        player_coords = self.game_canvas.coords(self.player_sprite)
        if not player_coords:
            return False
            
        player_width = self.player_img.width() / 2
        player_height = self.player_img.height() / 2

        hitbox_scale = 0.2

        for obs in self.obstacles:
            obs_coords = self.game_canvas.coords(obs)
            if not obs_coords:
                continue
                
            obs_width = self.obstacle_img.width() / 2 * hitbox_scale
            obs_height = self.obstacle_img.height() / 2 * hitbox_scale

            if (player_coords[0] + player_width > obs_coords[0] - obs_width and
                    player_coords[0] - player_width < obs_coords[0] + obs_width and
                    player_coords[1] + player_height > obs_coords[1] - obs_height and
                    player_coords[1] - player_height < obs_coords[1] + obs_height):
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
        self.pause_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=500)

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
        self.game_active = False
        if hasattr(self, 'pause_frame'):
            self.pause_frame.destroy()
        if hasattr(self, 'dark_rect'):
            self.game_canvas.delete(self.dark_rect)
        self.start_game()

    def return_to_main_menu(self):
        self.game_active = False
        self.game_paused = False
        if hasattr(self, 'pause_frame'):
            self.pause_frame.destroy()
        if hasattr(self, 'dark_rect'):
            self.game_canvas.delete(self.dark_rect)
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
        self.last_update_time = time.time()  # Сброс времени после паузы

    def update_game(self):
        if not self.game_active:
            return

        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        if self.game_paused:
            self.master.after(16, self.update_game)
            return

        # Обновление скорости игры на основе набранных очков
        if (self.score - self.last_speed_up_score) >= self.speed_increase_interval:
            self.game_speed = min(self.game_speed + self.speed_increment, self.max_game_speed)
            self.last_speed_up_score = self.score

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

        # Рассчитываем задержку с учетом текущей скорости игры
        delay = max(5, int(30 / self.game_speed))
        self.master.after(delay, self.update_game)

    def create_button(self, parent, text, command, width=300, height=50):
        btn_frame = tk.Frame(parent, bg=self.bg_color)
        canvas = tk.Canvas(btn_frame, width=width, height=height,
                          bg=self.bg_color, highlightthickness=0)

        canvas.create_rectangle(0, 0, width, height, fill=self.bg_color, outline='')

        canvas.create_rounded_rect(0, 0, width, height, radius=25,
                                  fill=self.button_color, outline='#777777', width=2)
        canvas.create_text(width/2, height/2, text=text,
                         font=tkfont.Font(family="Arial", size=24, weight="bold"),
                         fill=self.text_color)

        if command:
            canvas.bind("<Button-1>", lambda e: command())
            canvas.bind("<Enter>", lambda e: canvas.itemconfig(2, fill='#666666'))
            canvas.bind("<Leave>", lambda e: canvas.itemconfig(2, fill=self.button_color))

        canvas.pack()
        return btn_frame

    def create_game_button(self, text, command, width=300, height=50):
        return self.create_button(self.master, text, command, width, height)


def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = []
    points.extend([x1 + radius, y1, x2 - radius, y1])
    points.extend([x2 - radius, y1, x2, y1, x2, y1 + radius])
    points.extend([x2, y1 + radius, x2, y2 - radius])
    points.extend([x2, y2 - radius, x2, y2, x2 - radius, y2])
    points.extend([x2 - radius, y2, x1 + radius, y2])
    points.extend([x1 + radius, y2, x1, y2, x1, y2 - radius])
    points.extend([x1, y2 - radius, x1, y1 + radius])
    points.extend([x1, y1 + radius, x1, y1, x1 + radius, y1])

    return self.create_polygon(points, **kwargs, smooth=True)


tk.Canvas.create_rounded_rect = create_rounded_rect

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()