import tkinter as tk
import random
import time

# ─── НАСТРОЙКИ ───────────────────────────────────────────────────────────────
CELL = 28          # размер клетки
COLS = 21          # столбцы лабиринта
ROWS = 21          # строки лабиринта
W    = COLS * CELL # ширина canvas
H    = ROWS * CELL # высота canvas
FPS  = 120         # миллисекунды между кадрами

# ─── ЛАБИРИНТ (1=стена, 0=точка, 2=суперточка, 3=пусто) ─────────────────────
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    [1,2,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,2,1],
    [1,0,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,3,3,3,3,3,1,1,1,0,1,1,1,1],
    [1,1,1,1,0,1,3,3,3,3,3,3,3,3,3,1,0,1,1,1,1],
    [1,1,1,1,0,3,3,1,1,3,3,3,1,1,3,3,0,1,1,1,1],
    [3,3,3,3,0,3,3,1,3,3,3,3,3,1,3,3,0,3,3,3,3],
    [1,1,1,1,0,3,3,1,1,1,1,1,1,1,3,3,0,1,1,1,1],
    [1,1,1,1,0,1,3,3,3,3,3,3,3,3,3,1,0,1,1,1,1],
    [1,1,1,1,0,1,3,1,1,1,1,1,1,1,3,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1],
    [1,2,0,1,0,0,0,0,0,0,3,0,0,0,0,0,0,1,0,2,1],
    [1,1,0,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,0,1,1],
    [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,1,1,0,1,1,1,1,1,1,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# ─── ЦВЕТА ───────────────────────────────────────────────────────────────────
BG        = "#0a0a1a"
WALL_C    = "#1a1aff"
WALL_HL   = "#4444ff"
DOT_C     = "#ffddaa"
SDOT_C    = "#ffaa00"
TEXT_C    = "#ffffff"
SCORE_C   = "#ffdd00"

GHOST_COLORS = ["#ff4444", "#ffb8ff", "#00ffff", "#ffb852"]
GHOST_SCARED = "#2233ff"
GHOST_NAMES  = ["ПОЛИТИК", "НАЧАЛЬНИК", "СОСЕД", "ПРЕПОД"]
GHOST_EMOJIS = ["🤡", "👔", "👴", "📚"]

# ─── НАПРАВЛЕНИЯ ─────────────────────────────────────────────────────────────
DIR = {
    "Left":  (0, -1),
    "Right": (0,  1),
    "Up":    (-1, 0),
    "Down":  ( 1, 0),
}

class PacmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🍕 ПИЦЦА-МЭН vs Злодеи 🍕")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # ── Верхняя панель ──
        top = tk.Frame(root, bg=BG, pady=6)
        top.pack(fill="x")

        tk.Label(top, text="🍕 ПИЦЦА-МЭН", font=("Courier", 20, "bold"),
                 fg="#ff6600", bg=BG).pack(side="left", padx=14)

        self.score_var = tk.StringVar(value="СЧЁТ: 0")
        tk.Label(top, textvariable=self.score_var,
                 font=("Courier", 16, "bold"), fg=SCORE_C, bg=BG).pack(side="left", padx=20)

        self.lives_var = tk.StringVar(value="❤️❤️❤️")
        tk.Label(top, textvariable=self.lives_var,
                 font=("Courier", 16), fg="#ff4444", bg=BG).pack(side="left", padx=10)

        self.level_var = tk.StringVar(value="УРОВЕНЬ: 1")
        tk.Label(top, textvariable=self.level_var,
                 font=("Courier", 14, "bold"), fg="#aaaaff", bg=BG).pack(side="right", padx=14)

        # ── Canvas ──
        self.cv = tk.Canvas(root, width=W, height=H, bg=BG,
                            highlightthickness=3, highlightbackground="#1a1aff")
        self.cv.pack(padx=10, pady=(0, 6))

        # ── Нижняя строка подсказок ──
        bot = tk.Frame(root, bg=BG)
        bot.pack(fill="x", pady=(0, 6))
        tk.Label(bot, text="СТРЕЛКИ — движение   |   P — пауза   |   R — рестарт",
                 font=("Courier", 10), fg="#555577", bg=BG).pack()

        # ── Привязка клавиш ──
        root.bind("<KeyPress>", self.key_press)

        self.reset_game()
        self.game_loop()

    # ──────────────────────────────────────────────────────────────────────────
    def reset_game(self):
        self.maze   = [row[:] for row in MAZE]
        self.score  = 0
        self.lives  = 3
        self.level  = 1
        self.paused = False
        self.over   = False
        self.won    = False
        self.scared_timer = 0
        self.anim_tick    = 0

        # Подсчёт точек
        self.total_dots = sum(
            1 for r in range(ROWS) for c in range(COLS)
            if self.maze[r][c] in (0, 2)
        )
        self.eaten_dots = 0

        # Игрок — стартовая позиция
        self.px, self.py = 16.0, 10.0   # строка, столбец (float для плавного движения)
        self.pdir    = "Left"
        self.next_dir = "Left"
        self.p_mouth = 0
        self.p_open  = True

        # Призраки
        self.ghosts = []
        starts = [(9, 9), (9, 11), (10, 9), (10, 11)]
        for i in range(4):
            r, c = starts[i]
            self.ghosts.append({
                "r": float(r), "c": float(c),
                "dir": random.choice(list(DIR.keys())),
                "color": GHOST_COLORS[i],
                "name": GHOST_NAMES[i],
                "emoji": GHOST_EMOJIS[i],
                "scared": False,
                "eaten": False,
                "anim": 0,
            })

        self.update_hud()
        self.draw()

    # ──────────────────────────────────────────────────────────────────────────
    def update_hud(self):
        self.score_var.set(f"СЧЁТ: {self.score}")
        self.lives_var.set("❤️" * self.lives + "🖤" * (3 - self.lives))
        self.level_var.set(f"УРОВЕНЬ: {self.level}")

    # ──────────────────────────────────────────────────────────────────────────
    def key_press(self, e):
        k = e.keysym
        if k in DIR:
            self.next_dir = k
        elif k == "p" or k == "P":
            self.paused = not self.paused
        elif k == "r" or k == "R":
            self.reset_game()

    # ──────────────────────────────────────────────────────────────────────────
    def can_move(self, r, c):
        ri, ci = int(round(r)), int(round(c))
        if ri < 0 or ri >= ROWS or ci < 0 or ci >= COLS:
            return False
        return self.maze[ri][ci] != 1

    # ──────────────────────────────────────────────────────────────────────────
    def move_player(self):
        speed = 0.18 + self.level * 0.02
        dr, dc = DIR[self.next_dir]
        nr = self.px + dr * speed
        nc = self.py + dc * speed
        if self.can_move(nr, nc):
            self.pdir = self.next_dir
            self.px, self.py = nr, nc
        else:
            dr, dc = DIR[self.pdir]
            nr = self.px + dr * speed
            nc = self.py + dc * speed
            if self.can_move(nr, nc):
                self.px, self.py = nr, nc

        # Тоннель
        if self.py < 0:   self.py = COLS - 1
        if self.py >= COLS: self.py = 0

        # Поедание точек
        ri, ci = int(round(self.px)), int(round(self.py))
        cell = self.maze[ri][ci]
        if cell == 0:
            self.maze[ri][ci] = 3
            self.score += 10
            self.eaten_dots += 1
        elif cell == 2:
            self.maze[ri][ci] = 3
            self.score += 50
            self.eaten_dots += 1
            self.scared_timer = 200
            for g in self.ghosts:
                g["scared"] = True
                g["eaten"]  = False

        self.p_mouth = (self.p_mouth + 1) % 6

    # ──────────────────────────────────────────────────────────────────────────
    def move_ghosts(self):
        speed = 0.12 + self.level * 0.015
        for g in self.ghosts:
            if g["eaten"]:
                speed = 0.22   # быстрее возвращаются

            dr, dc = DIR[g["dir"]]
            nr = g["r"] + dr * speed
            nc = g["c"] + dc * speed

            if self.can_move(nr, nc):
                g["r"], g["c"] = nr, nc
            else:
                # Выбор нового направления
                dirs = list(DIR.keys())
                random.shuffle(dirs)
                moved = False
                for d in dirs:
                    ddr, ddc = DIR[d]
                    tr = g["r"] + ddr * speed
                    tc = g["c"] + ddc * speed
                    if self.can_move(tr, tc):
                        g["dir"] = d
                        g["r"]   = tr
                        g["c"]   = tc
                        moved    = True
                        break

            # Тоннель
            if g["c"] < 0:      g["c"] = COLS - 1
            if g["c"] >= COLS:  g["c"] = 0

            g["anim"] = (g["anim"] + 1) % 8

    # ──────────────────────────────────────────────────────────────────────────
    def check_collisions(self):
        for g in self.ghosts:
            dist = abs(g["r"] - self.px) + abs(g["c"] - self.py)
            if dist < 0.9:
                if g["scared"] and not g["eaten"]:
                    g["eaten"]  = True
                    g["scared"] = False
                    self.score += 200
                elif not g["scared"] and not g["eaten"]:
                    self.lives -= 1
                    self.update_hud()
                    if self.lives <= 0:
                        self.over = True
                    else:
                        # Сброс позиции
                        self.px, self.py = 16.0, 10.0
                        self.pdir = "Left"
                        self.next_dir = "Left"
                        for i, gh in enumerate(self.ghosts):
                            r, c = [(9,9),(9,11),(10,9),(10,11)][i]
                            gh["r"], gh["c"] = float(r), float(c)
                            gh["scared"] = False
                            gh["eaten"]  = False
                    return

    # ──────────────────────────────────────────────────────────────────────────
    def update_scared(self):
        if self.scared_timer > 0:
            self.scared_timer -= 1
            if self.scared_timer == 0:
                for g in self.ghosts:
                    g["scared"] = False
                    g["eaten"]  = False

    # ──────────────────────────────────────────────────────────────────────────
    def check_win(self):
        if self.eaten_dots >= self.total_dots:
            self.level += 1
            if self.level > 3:
                self.won = True
            else:
                self.maze = [row[:] for row in MAZE]
                self.total_dots = sum(
                    1 for r in range(ROWS) for c in range(COLS)
                    if self.maze[r][c] in (0, 2)
                )
                self.eaten_dots  = 0
                self.scared_timer = 0
                self.px, self.py = 16.0, 10.0
                self.pdir = "Left"
                for i, g in enumerate(self.ghosts):
                    r, c = [(9,9),(9,11),(10,9),(10,11)][i]
                    g["r"], g["c"] = float(r), float(c)
                    g["scared"] = False
                    g["eaten"]  = False
            self.update_hud()

    # ══════════════════════════════════════════════════════════════════════════
    #  РИСОВАНИЕ
    # ══════════════════════════════════════════════════════════════════════════
    def draw(self):
        cv = self.cv
        cv.delete("all")
        self.anim_tick += 1

        # ── Лабиринт ──
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * CELL;  y1 = r * CELL
                x2 = x1 + CELL; y2 = y1 + CELL
                cell = self.maze[r][c]

                if cell == 1:
                    cv.create_rectangle(x1, y1, x2, y2, fill=WALL_C, outline=WALL_HL, width=1)
                    # Декоративные точки на стенах
                    cx, cy = x1 + CELL//2, y1 + CELL//2
                    cv.create_oval(cx-2, cy-2, cx+2, cy+2, fill=WALL_HL, outline="")
                elif cell == 0:
                    cx, cy = x1 + CELL//2, y1 + CELL//2
                    cv.create_oval(cx-3, cy-3, cx+3, cy+3, fill=DOT_C, outline="")
                elif cell == 2:
                    cx, cy = x1 + CELL//2, y1 + CELL//2
                    pulse = 5 + 3 * abs((self.anim_tick % 20) / 10 - 1)
                    cv.create_oval(cx-pulse, cy-pulse, cx+pulse, cy+pulse,
                                   fill=SDOT_C, outline="#ffffff", width=1)

        # ── Призраки ──
        for g in self.ghosts:
            self.draw_ghost(g)

        # ── Пицца-Мэн ──
        self.draw_player()

        # ── Оверлеи ──
        if self.paused:
            self.draw_overlay("⏸ ПАУЗА", "#ffdd00", "Нажми P чтобы продолжить")
        elif self.over:
            self.draw_overlay("💀 GAME OVER", "#ff3333", f"Счёт: {self.score}  |  R — рестарт")
        elif self.won:
            self.draw_overlay("🎉 ПОБЕДА!", "#00ff88", f"Финальный счёт: {self.score}  |  R — рестарт")

    # ──────────────────────────────────────────────────────────────────────────
    def draw_player(self):
        cv = self.cv
        cx = self.py * CELL + CELL // 2
        cy = self.px * CELL + CELL // 2
        R  = CELL // 2 - 2

        # Угол открытия рта
        mouth_angle = [30, 20, 10, 0, 10, 20][self.p_mouth]

        # Поворот в зависимости от направления
        rot_map = {"Right": 0, "Left": 180, "Up": 90, "Down": 270}
        rot = rot_map.get(self.pdir, 0)

        start = rot + mouth_angle
        extent = 360 - mouth_angle * 2

        # Тело — пицца жёлтый
        cv.create_arc(cx-R, cy-R, cx+R, cy+R,
                      start=start, extent=extent,
                      fill="#ffcc00", outline="#ff8800", width=2)

        # Глаз
        eye_angle = rot + 60
        import math
        ex = cx + (R * 0.55) * math.cos(math.radians(eye_angle))
        ey = cy - (R * 0.55) * math.sin(math.radians(eye_angle))
        cv.create_oval(ex-3, ey-3, ex+3, ey+3, fill="#000000", outline="")

        # Метка 🍕
        cv.create_text(cx, cy + R + 7, text="🍕", font=("Arial", 8))

    # ──────────────────────────────────────────────────────────────────────────
    def draw_ghost(self, g):
        cv  = self.cv
        cx  = g["c"] * CELL + CELL // 2
        cy  = g["r"] * CELL + CELL // 2
        R   = CELL // 2 - 2

        if g["eaten"]:
            # Только глаза
            cv.create_oval(cx-5, cy-4, cx-1, cy,   fill="white", outline="")
            cv.create_oval(cx+1, cy-4, cx+5, cy,   fill="white", outline="")
            cv.create_oval(cx-4, cy-3, cx-2, cy-1, fill="#2244ff", outline="")
            cv.create_oval(cx+2, cy-3, cx+4, cy-1, fill="#2244ff", outline="")
            return

        color = GHOST_SCARED if g["scared"] else g["color"]
        if g["scared"] and self.scared_timer < 60:
            # Мигание
            color = "#ffffff" if (self.anim_tick % 8 < 4) else GHOST_SCARED

        # Тело
        cv.create_arc(cx-R, cy-R, cx+R, cy+R,
                      start=0, extent=180, fill=color, outline="")
        # Нижняя часть с зубчиками
        wave_pts = []
        steps = 4
        for i in range(steps + 1):
            fx = cx - R + (2*R) * i / steps
            fy = cy + (R if i % 2 == 0 else R//2)
            wave_pts.extend([fx, fy])
        wave_pts = [cx-R, cy] + wave_pts + [cx+R, cy]
        cv.create_polygon(wave_pts, fill=color, outline="")

        # Глаза
        if not g["scared"]:
            cv.create_oval(cx-7, cy-8, cx-2, cy-3, fill="white", outline="")
            cv.create_oval(cx+2, cy-8, cx+7, cy-3, fill="white", outline="")
            cv.create_oval(cx-6, cy-7, cx-4, cy-5, fill="#000088", outline="")
            cv.create_oval(cx+3, cy-7, cx+5, cy-5, fill="#000088", outline="")
        else:
            # Испуганные глаза
            cv.create_line(cx-7, cy-8, cx-4, cy-5, fill="white", width=2)
            cv.create_line(cx-4, cy-5, cx-7, cy-2, fill="white", width=2)
            cv.create_line(cx+3, cy-8, cx+6, cy-5, fill="white", width=2)
            cv.create_line(cx+6, cy-5, cx+3, cy-2, fill="white", width=2)

        # Подпись
        cv.create_text(cx, cy + R + 8, text=g["emoji"],
                       font=("Arial", 7), fill="white")

    # ──────────────────────────────────────────────────────────────────────────
    def draw_overlay(self, title, color, subtitle=""):
        cv = self.cv
        cv.create_rectangle(0, H//2 - 60, W, H//2 + 60,
                            fill="#000000cc", outline="", stipple="gray50")
        cv.create_rectangle(30, H//2 - 55, W-30, H//2 + 55,
                            fill="#000022", outline=color, width=3)
        cv.create_text(W//2, H//2 - 18, text=title,
                       font=("Courier", 28, "bold"), fill=color, anchor="center")
        if subtitle:
            cv.create_text(W//2, H//2 + 20, text=subtitle,
                           font=("Courier", 13), fill="#aaaaaa", anchor="center")

    # ══════════════════════════════════════════════════════════════════════════
    #  ГЛАВНЫЙ ЦИКЛ
    # ══════════════════════════════════════════════════════════════════════════
    def game_loop(self):
        if not self.paused and not self.over and not self.won:
            self.move_player()
            self.move_ghosts()
            self.check_collisions()
            self.update_scared()
            self.check_win()
            self.update_hud()
        self.draw()
        self.root.after(FPS, self.game_loop)


# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = PacmanGame(root)
    root.mainloop()