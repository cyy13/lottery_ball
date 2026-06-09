import pygame
import random
import math
import sys
import os


# --- 【关键修正】---
# 强制将当前工作目录切换到程序所在的真实路径
def fix_work_dir():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的程序，使用可执行文件所在目录
        application_path = os.path.dirname(os.path.abspath(sys.executable))
        # 如果是 .app 包，则需要向上跳转到 Contents 之外的目录
        if "Contents/MacOS" in application_path:
            application_path = os.path.abspath(os.path.join(application_path, "../.."))
        os.chdir(application_path)
    else:
        # 本地开发模式
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 立即执行修复
fix_work_dir()
# ------------------

# # --- 核心：路径兼容函数 ---
# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     return os.path.join(base_path, relative_path)

def resource_path(relative_path):
    """获取资源文件的绝对路径，适配打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的运行路径
        return os.path.join(sys._MEIPASS, relative_path)
    # 本地运行的路径
    return os.path.join(os.path.abspath("."), relative_path)

# 初始化 Pygame
pygame.init()
pygame.font.init()
# 初始化音频混合器
pygame.mixer.init()

# --- 屏幕分辨率 ---
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🧧 开灵启智 - 崇道堂幸运大抽奖")

# --- 盛典色彩配置 ---
COLOR_BG = (160, 15, 20)  # 经典盛典红
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_BTN = (230, 126, 34)  # 按钮橙
COLOR_GOLD = (241, 196, 15)  # 璀璨金
COLOR_LIGHT_GOLD = (255, 220, 80)  # 高光金
COLOR_SHADOW_RED = (40, 2, 5)  # 深渊投影红
COLOR_LIGHT_GRAY = (238, 238, 242)  # 结算板浅灰
COLOR_WINNER_RED = (215, 25, 25)  # 中奖人名字红

# 五行幸运色
WUXING_COLORS = [
    (52, 152, 219), (46, 204, 113), (231, 76, 60), (241, 196, 15), (255, 255, 255)
]


# --- 字体加载 ---
def get_font(size, bold=False):
    try:
        font_path = resource_path("myfont.ttf")
        return pygame.font.Font(font_path, size)
    except:
        system_fonts = ["pingfangsc", "heitisc", "microsoftyahei", "simhei"]
        for name in system_fonts:
            try:
                f = pygame.font.SysFont(name, size)
                f.set_bold(bold)
                return f
            except:
                continue
    return pygame.font.Font(None, size)


# 字体矩阵
FONT_XXXL = get_font(90, bold=True)
FONT_XXL = get_font(52, bold=True)
FONT_XL = get_font(38, bold=True)
FONT_TITLE = get_font(18, bold=True)
FONT_NUM = get_font(16, bold=True)
FONT_S = get_font(16, bold=True)
FONT_CLOSE = get_font(18, bold=True)


# ==================== 【音频加载与安全控制】 ====================
def load_and_play_bgm():
    """
    智能加载并播放背景音乐，自带防崩溃保护
    支持 mp3 或 wav 格式
    """
    # 优先寻找软件同级目录下的 bgm.mp3
    # bgm_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "bgm.mp3")
    bgm_path = resource_path("bgm.mp3")
    # 如果找不到 mp3，尝试寻找 wav
    if not os.path.exists(bgm_path):
        # bgm_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "bgm.wav")
        bgm_path = resource_path("bgm.wav")
    if os.path.exists(bgm_path):
        try:
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(0.6)  # 设置音量 (0.0 到 1.0)，0.6 既热闹又不会太吵
            pygame.mixer.music.play(-1)  # 参数 -1 代表无限循环播放
            print(f"成功加载并开始循环播放背景音乐: {bgm_path}")
        except Exception as e:
            print(f"音乐文件格式可能不兼容或加载失败: {e}")
    else:
        print("未检测到 bgm.mp3 或 bgm.wav，系统将开启静音安全模式运行。")


# ==================== 【美学画布：五方神兽与吉祥暗纹生成器】 ====================
bg_pattern_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)


def draw_mythical_creature_patterns(surf):
    p_color = (241, 196, 15, 13)  # 超低调丝绸暗金

    def draw_cloud(sx, sy):
        pygame.draw.circle(surf, p_color, (sx, sy), 20)
        pygame.draw.circle(surf, p_color, (sx + 15, sy - 6), 16)
        pygame.draw.circle(surf, p_color, (sx - 15, sy + 5), 14)
        pygame.draw.ellipse(surf, p_color, (sx - 30, sy + 10, 70, 8))

    def draw_wealth_money(bx, by):
        pts = [(bx - 12, by - 20), (bx + 12, by - 20), (bx + 12, by - 4), (bx + 18, by + 12), (bx + 8, by + 20),
               (bx, by + 10), (bx - 8, by + 20), (bx - 18, by + 12), (bx - 12, by - 4)]
        pygame.draw.polygon(surf, p_color, pts, 1)
        pygame.draw.rect(surf, p_color, (bx - 3, by - 15, 6, 6), 1)
        pygame.draw.circle(surf, p_color, (bx + 40, by + 5), 12, 1)
        pygame.draw.rect(surf, p_color, (bx + 36, by + 1, 8, 8), 1)

    def draw_deer_xiezhi(x, y):
        for a in range(0, 360, 72):
            rad = math.radians(a)
            pygame.draw.circle(surf, p_color, (int(x + 8 * math.cos(rad)), int(y + 8 * math.sin(rad))), 5)
        pygame.draw.arc(surf, p_color, (x - 20, y + 20, 30, 40), 0, math.pi / 2, 1)
        pygame.draw.line(surf, p_color, (x - 5, y + 20), (x + 15, y - 5), 1)

    def draw_qinglong(x, y):
        for i in range(3):
            pygame.draw.arc(surf, p_color, (x + i * 15, y, 30, 20), 0, math.pi, 1)
            pygame.draw.arc(surf, p_color, (x + i * 15 - 7, y + 10, 30, 20), 0, math.pi, 1)
        pygame.draw.line(surf, p_color, (x + 15, y - 5), (x - 5, y - 25), 1)
        pygame.draw.line(surf, p_color, (x - 5, y - 25), (x - 15, y - 20), 1)

    def draw_baihu(x, y):
        pygame.draw.line(surf, p_color, (x - 15, y - 15), (x + 15, y - 15), 2)
        pygame.draw.line(surf, p_color, (x - 10, y - 8), (x + 10, y - 8), 2)
        pygame.draw.line(surf, p_color, (x - 18, y), (x + 18, y), 2)
        pygame.draw.line(surf, p_color, (x, y - 18), (x, y), 2)
        pygame.draw.line(surf, p_color, (x - 25, y + 10), (x + 15, y + 20), 1)
        pygame.draw.line(surf, p_color, (x - 15, y + 18), (x + 25, y + 28), 1)

    def draw_zhuque(x, y):
        pygame.draw.bezier_curve = pygame.draw.arc(surf, p_color, (x - 30, y - 10, 60, 40), math.pi, math.pi * 2, 1)
        for i in range(3):
            pygame.draw.arc(surf, p_color, (x - 40 + i * 10, y + i * 8, 40, 25), 0, math.pi / 2, 1)
        pygame.draw.arc(surf, p_color, (x + 5, y - 20, 20, 30), math.pi / 2, math.pi, 1)

    def draw_xuanwu(x, y):
        r = 14
        for r_idx in range(2):
            dy = r_idx * 18
            dx_shift = 12 if r_idx % 2 == 1 else 0
            for c_idx in range(2):
                dx = c_idx * 24 + dx_shift
                pts = []
                for angle in range(0, 360, 60):
                    rad = math.radians(angle)
                    pts.append((x + dx + r * math.cos(rad), y + dy + r * math.sin(rad)))
                pygame.draw.polygon(surf, p_color, pts, 1)
        pygame.draw.arc(surf, p_color, (x - 15, y - 10, 35, 50), 0, math.pi, 1)
        pygame.draw.arc(surf, p_color, (x - 10, y + 15, 35, 40), math.pi, math.pi * 2, 1)

    def draw_gouchen(x, y):
        pygame.draw.line(surf, p_color, (x - 25, y), (x + 25, y), 1)
        pygame.draw.line(surf, p_color, (x, y - 25), (x, y + 25), 1)
        pygame.draw.line(surf, p_color, (x - 15, y - 15), (x + 15, y + 15), 1)
        pygame.draw.line(surf, p_color, (x - 15, y + 15), (x + 15, y - 15), 1)
        pygame.draw.circle(surf, p_color, (x, y), 6, 1)

    # 五方对称排布
    draw_qinglong(120, 150);
    draw_qinglong(80, 420)
    draw_baihu(780, 150);
    draw_baihu(820, 420)
    draw_zhuque(250, 540);
    draw_zhuque(650, 540)
    draw_xuanwu(280, 80);
    draw_xuanwu(620, 80)
    draw_gouchen(180, 300);
    draw_gouchen(720, 300)

    draw_cloud(450, 45);
    draw_cloud(50, 260);
    draw_cloud(850, 260)
    draw_wealth_money(110, 50);
    draw_wealth_money(720, 45)
    draw_deer_xiezhi(200, 210);
    draw_deer_xiezhi(700, 210)


draw_mythical_creature_patterns(bg_pattern_surface)


# =================================================================================

# --- 3D 节点类 ---
class Node3D:
    def __init__(self, text, x, y, z):
        self.text = text
        self.x, self.y, self.z = x, y, z
        self.screen_x = 0
        self.screen_y = 0
        self.scale = 1.0
        self.base_color = random.choice(WUXING_COLORS)

    def rotate_y(self, angle):
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        self.x, self.z = self.x * cos_a - self.z * sin_a, self.x * sin_a + self.z * cos_a

    def rotate_x(self, angle):
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        self.y, self.z = self.y * cos_a - self.z * sin_a, self.y * sin_a + self.z * cos_a

    def project(self, radius_len):
        distance = 350
        factor = distance / (distance + self.z)
        self.screen_x = int(WIDTH / 2 + self.x * factor)
        self.screen_y = int(HEIGHT / 2 - 20 + self.y * factor)
        self.scale = factor


# --- 粒子烟花类 ---
class FireworkParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.color = random.choice(WUXING_COLORS)
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.06
        self.alpha -= 5


# --- 绘图增强函数 ---
def draw_stage_curtains():
    for i in range(7):
        cur_x = i * 20
        color = (130 - i * 10, 10, 15)
        pygame.draw.polygon(screen, color, [(0, 0), (140 - cur_x, 0), (0, HEIGHT)])
        pygame.draw.polygon(screen, color, [(WIDTH, 0), (WIDTH - 140 + cur_x, 0), (WIDTH, HEIGHT)])
    pygame.draw.line(screen, COLOR_GOLD, (140, 0), (0, HEIGHT // 1.5), 3)
    pygame.draw.line(screen, COLOR_GOLD, (WIDTH - 140, 0), (WIDTH, HEIGHT // 1.5), 3)


def draw_fancy_lantern(x, y, pulse):
    l_w, l_h = 70, 90
    y += pulse
    pygame.draw.ellipse(screen, (220, 30, 30), (x, y, l_w, l_h))
    pygame.draw.ellipse(screen, (200, 20, 20), (x + 15, y, l_w - 30, l_h), 2)
    pygame.draw.line(screen, (200, 20, 20), (x + l_w // 2, y), (x + l_w // 2, y + l_h), 1)
    pygame.draw.rect(screen, COLOR_GOLD, (x + 20, y - 6, 30, 8), border_radius=2)
    pygame.draw.rect(screen, COLOR_GOLD, (x + 20, y + l_h - 2, 30, 8), border_radius=2)
    for i in range(-2, 3):
        lx = x + l_w // 2 + i * 6
        pygame.draw.line(screen, (255, 50, 50), (lx, y + l_h + 5), (lx, y + l_h + 35), 2)


# --- 全局状态 ---
candidates = ["暂无数据"]
nodes = []
winners = []
draw_count = 1
is_rolling = False
radius = 175
pulse_angle = 0
fireworks = []

close_btn_rect = pygame.Rect(0, 0, 0, 0)

# ==================== 金匾容器参数 ====================
PANEL_W, PANEL_H = 170, 115
PANEL_X, PANEL_Y = 25, 15
PANEL_CX = PANEL_X + PANEL_W // 2

BTN_W, BTN_H = 42, 28

r1_y = PANEL_Y + 45
rect_btn1 = pygame.Rect(PANEL_CX - 6 - BTN_W, r1_y, BTN_W, BTN_H)
rect_btn2 = pygame.Rect(PANEL_CX + 6, r1_y, BTN_W, BTN_H)

r2_y = PANEL_Y + 78
rect_btn3 = pygame.Rect(PANEL_CX - BTN_W // 2 - 8 - BTN_W, r2_y, BTN_W, BTN_H)
rect_btn4 = pygame.Rect(PANEL_CX - BTN_W // 2, r2_y, BTN_W, BTN_H)
rect_btn5 = pygame.Rect(PANEL_CX + BTN_W // 2 + 8, r2_y, BTN_W, BTN_H)

btn_rects = [rect_btn1, rect_btn2, rect_btn3, rect_btn4, rect_btn5]


# ===================================================================

def auto_import():
    global candidates
    # 1. 优先获取 exe 所在目录（外部目录）
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    external_path = os.path.join(exe_dir, "名单.txt")

    # 2. 其次获取打包内置的路径（备用）
    internal_path = resource_path("名单.txt")

    # 优先级：外部文件 > 内置文件
    target_path = external_path if os.path.exists(external_path) else internal_path

    if os.path.exists(target_path):
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f.readlines() if line.strip()]
            if names:
                candidates = names
                print(f"成功加载名单文件: {target_path}")  # 调试用，可选
        except Exception as e:
            print(f"读取名单文件失败: {e}")
    else:
        print("未找到名单.txt（外部和内置均未检测到），使用默认值")

def init_nodes():
    global nodes
    nodes = []
    num_nodes = len(candidates)
    if num_nodes == 0 or "暂无" in candidates[0]: return
    phi = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(num_nodes):
        y = 1 - (i / float(num_nodes - 1)) * 2 if num_nodes > 1 else 0
        radius_at_y = math.sqrt(1 - y * y)
        theta = phi * i
        x = math.cos(theta) * radius_at_y
        z = math.sin(theta) * radius_at_y
        nodes.append(Node3D(candidates[i], x * radius, y * radius, z * radius))


# 启动自动加载
auto_import()
init_nodes()
# 启动背景音乐循环
load_and_play_bgm()

clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()

# --- 主循环 ---
while True:
    screen.fill(COLOR_BG)
    screen.blit(bg_pattern_surface, (0, 0))

    mx, my = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()
    elapsed = current_time - start_ticks

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and elapsed > 2000:
            if event.button == 1:
                if not is_rolling and winners and close_btn_rect.collidepoint(mx, my):
                    winners = []
                    continue

                for idx, rrect in enumerate(btn_rects):
                    if rrect.collidepoint(mx, my):
                        draw_count = idx + 1

                if WIDTH / 2 - 90 <= mx <= WIDTH / 2 + 90 and HEIGHT - 60 <= my <= HEIGHT - 20:
                    if len(candidates) > 0 and "暂无" not in candidates[0]:
                        if not is_rolling:
                            is_rolling, winners = True, []
                        else:
                            is_rolling = False
                            winners = random.sample(candidates, min(len(candidates), draw_count))
                            for w in winners: candidates.remove(w)
                            init_nodes()

    # ==================== 状态一：前 2 秒主界面盛典开场 ====================
    if elapsed <= 2000:
        if random.random() < 0.18:
            fx, fy = random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 300)
            for _ in range(35): fireworks.append(FireworkParticle(fx, fy))
        for p in fireworks[:]:
            p.update()
            if p.alpha <= 0:
                fireworks.remove(p)
            else:
                s = pygame.Surface((4, 4));
                s.fill(p.color);
                s.set_alpha(p.alpha);
                screen.blit(s, (p.x, p.y))

        draw_stage_curtains()
        draw_fancy_lantern(80, 50, 5 * math.sin(current_time * 0.005))
        draw_fancy_lantern(WIDTH - 150, 50, 5 * math.sin(current_time * 0.005))

        pygame.draw.circle(screen, COLOR_GOLD, (WIDTH // 2, HEIGHT // 2), 190, 8)
        pygame.draw.circle(screen, (255, 235, 120), (WIDTH // 2, HEIGHT // 2), 178, 2)

        t1 = FONT_XXXL.render("幸 运", True, COLOR_GOLD)
        t2 = FONT_XXXL.render("大抽奖", True, COLOR_GOLD)
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 5))

    # ==================== 状态二：正式抽奖与球体滚动界面 ====================
    else:
        # 3D 计算
        pulse_angle += 0.05
        p_rad = radius * (1 + 0.04 * math.sin(pulse_angle)) if is_rolling else radius
        for n in nodes:
            n.rotate_x(3.0 if is_rolling else 0.25)
            n.rotate_y(4.0 if is_rolling else 0.35)
            n.project(p_rad)

        nodes.sort(key=lambda n: n.z, reverse=True)
        for n in nodes:
            a = max(40, min(255, int(255 * (340 - n.z) / 450)))
            clr = random.choice(WUXING_COLORS) if is_rolling else [int(c * (a / 255)) for c in n.base_color]
            df = get_font(int(max(10, 18 * n.scale)), True)
            txt = df.render(n.text, True, clr)
            tw, th = txt.get_size()
            bs = pygame.Surface((tw + 20, th + 10), pygame.SRCALPHA)
            pygame.draw.rect(bs, (241, 196, 15, int(a * 0.3)), (0, 0, tw + 20, th + 10), 1, 6)
            screen.blit(bs, (n.screen_x - 10, n.screen_y - 5))
            screen.blit(txt, (n.screen_x, n.screen_y))

        # 金匾控制区
        pygame.draw.rect(screen, (100, 10, 15), (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), border_radius=12)
        pygame.draw.rect(screen, COLOR_GOLD, (PANEL_X, PANEL_Y, PANEL_W, PANEL_H), width=3, border_radius=12)
        pygame.draw.rect(screen, (255, 235, 120), (PANEL_X + 4, PANEL_Y + 4, PANEL_W - 8, PANEL_H - 8), width=1,
                         border_radius=10)

        for cx, cy in [(PANEL_X + 8, PANEL_Y + 8), (PANEL_X + PANEL_W - 8, PANEL_Y + 8),
                       (PANEL_X + 8, PANEL_Y + PANEL_H - 8), (PANEL_X + PANEL_W - 8, PANEL_Y + PANEL_H - 8)]:
            pygame.draw.circle(screen, COLOR_LIGHT_GOLD, (cx, cy), 3)

        txt_raw = "单次抽取人数"
        surf_shadow = FONT_TITLE.render(txt_raw, True, COLOR_SHADOW_RED)
        surf_main = FONT_TITLE.render(txt_raw, True, COLOR_LIGHT_GOLD)
        tx = PANEL_CX - surf_main.get_width() // 2
        ty = PANEL_Y + 14
        screen.blit(surf_shadow, (tx + 2, ty + 2))
        screen.blit(surf_main, (tx, ty))

        for i in range(1, 6):
            rect = btn_rects[i - 1]
            b_color = COLOR_GOLD if draw_count == i else (145, 18, 22)
            text_color = (30, 30, 30) if draw_count == i else COLOR_TEXT_WHITE

            pygame.draw.rect(screen, b_color, rect, border_radius=6)
            pygame.draw.rect(screen, COLOR_GOLD if draw_count == i else (190, 150, 50), rect, width=1, border_radius=6)

            num_surf = FONT_NUM.render(str(i), True, text_color)
            screen.blit(num_surf, (rect.x + rect.width // 2 - num_surf.get_width() // 2,
                                   rect.y + rect.height // 2 - num_surf.get_height() // 2))

        # UI：大按钮
        pygame.draw.rect(screen, (231, 76, 60) if is_rolling else COLOR_BTN, (WIDTH // 2 - 90, HEIGHT - 60, 180, 40),
                         border_radius=10)
        pygame.draw.rect(screen, COLOR_GOLD, (WIDTH // 2 - 90, HEIGHT - 60, 180, 40), 2, 10)
        btn_t = FONT_NUM.render("停  止" if is_rolling else "开始抽奖", True, COLOR_TEXT_WHITE)
        screen.blit(btn_t, (WIDTH // 2 - btn_t.get_width() // 2, HEIGHT - 51))

        # 结算弹窗
        if not is_rolling and winners:
            lns = [winners[i:i + 2] for i in range(0, len(winners), 2)]
            bh = 100 + len(lns) * 70
            by = HEIGHT // 2 - bh // 2

            pygame.draw.rect(screen, COLOR_LIGHT_GRAY, (WIDTH // 2 - 280, by, 560, bh), border_radius=18)
            pygame.draw.rect(screen, COLOR_GOLD, (WIDTH // 2 - 280, by, 560, bh), 5, 18)

            close_cx, close_cy = WIDTH // 2 + 250, by + 30
            close_radius = 16
            close_btn_rect = pygame.Rect(close_cx - close_radius, close_cy - close_radius, close_radius * 2,
                                         close_radius * 2)
            circle_color = (190, 20, 25) if close_btn_rect.collidepoint(mx, my) else (231, 76, 60)
            pygame.draw.circle(screen, circle_color, (close_cx, close_cy), close_radius)
            pygame.draw.circle(screen, COLOR_GOLD, (close_cx, close_cy), close_radius, width=1)
            close_txt = FONT_CLOSE.render("X", True, COLOR_TEXT_WHITE)
            screen.blit(close_txt, (close_cx - close_txt.get_width() // 2, close_cy - close_txt.get_height() // 2 - 1))

            title = FONT_XXL.render("幸运中奖榜", True, (60, 60, 70))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, by + 25))

            for idx, line in enumerate(lns):
                curr_y = by + 105 + idx * 70
                if len(line) == 2:
                    for i, name in enumerate(line):
                        s = FONT_XL.render(name, True, COLOR_WINNER_RED)
                        nx = WIDTH // 2 - s.get_width() - 40 if i == 0 else WIDTH // 2 + 40
                        pygame.draw.rect(screen, COLOR_GOLD,
                                         (nx - 15, curr_y - 6, s.get_width() + 30, s.get_height() + 12), 2, 8)
                        screen.blit(s, (nx, curr_y))
                else:
                    s = FONT_XL.render(line[0], True, COLOR_WINNER_RED)
                    pygame.draw.rect(screen, COLOR_GOLD,
                                     (WIDTH // 2 - s.get_width() // 2 - 20, curr_y - 6, s.get_width() + 40,
                                      s.get_height() + 12), 2, 8)
                    screen.blit(s, (WIDTH // 2 - s.get_width() // 2, curr_y))

    pygame.display.flip()
    clock.tick(60)