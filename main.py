import pygame
import datetime
import sys
import os

# 初始化 Pygame
pygame.init()

# 取得 Android 手機螢幕的最佳解析度並開全螢幕
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Car Clock")
pygame.mouse.set_visible(False)

# 載入圖片輔助函式（適應 Android 打包後的資源路徑）
def load_img(path, alpha=True):
    try:
        # 優先嘗試相對路徑
        if os.path.exists(path):
            full_path = path
        else:
            # 備用：尋找腳本同級目錄
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_path, path)

        img = pygame.image.load(full_path)
        return img.convert_alpha() if alpha else img.convert()
    except Exception as e:
        print(f"無法載入圖片 {path}: {e}")
        # 如果在 Android 上找不到圖檔，自動建立替代區塊，避免 App 直接崩潰
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        surf.fill((255, 0, 0, 128))
        return surf

# --- 1. 載入原始資源 ---
orig_hour_img = load_img('1.png')
orig_min_img  = load_img('2.png')
orig_face_img = load_img('4.png')

# =========================================================================
# 🛠️ 【參數調校區】
# =========================================================================
POINTER_CENTER_OFFSET_Y = int(HEIGHT * 0.1)  # 依螢幕高度動態調整微調偏移量
POINTER_SCALE_MULTIPLIER = 1.2  
# =========================================================================

# --- 2. 自動等比例放大邏輯 ---
face_w, face_h = orig_face_img.get_size()
scale_ratio = min(WIDTH / face_w, HEIGHT / face_h)

new_face_size = (int(face_w * scale_ratio), int(face_h * scale_ratio))
pointer_scale_ratio = scale_ratio * POINTER_SCALE_MULTIPLIER

new_hour_size = (int(orig_hour_img.get_width() * pointer_scale_ratio), int(orig_hour_img.get_height() * pointer_scale_ratio))
new_min_size  = (int(orig_min_img.get_width() * pointer_scale_ratio), int(orig_min_img.get_height() * pointer_scale_ratio))

# 開機時進行一次性平滑縮放
face_img = pygame.transform.smoothscale(orig_face_img, new_face_size)
hour_img = pygame.transform.smoothscale(orig_hour_img, new_hour_size)
min_img  = pygame.transform.smoothscale(orig_min_img, new_min_size)

# --- 3. 指針旋轉繪製函數 ---
def draw_pointer(surf, image, center_pos, angle, pivot_y_percent=0.80):
    w, h = image.get_size()
    pivot_x = w // 2
    pivot_y = int(h * pivot_y_percent)
    
    rotated_image = pygame.transform.rotozoom(image, -angle, 1)
    
    center_to_pivot = pygame.math.Vector2(pivot_x - w/2, pivot_y - h/2)
    rotated_offset = center_to_pivot.rotate(angle)
    rect = rotated_image.get_rect(center=center_pos - rotated_offset)
    surf.blit(rotated_image, rect)

clock = pygame.time.Clock()
SCREEN_CENTER = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 鍵盤與 Android 物理/虛擬返回鍵支援
        elif event.type == pygame.KEYDOWN:
            # 27 = ESC 鍵, 1073742094/pygame.K_AC_BACK = Android 返回鍵
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, getattr(pygame, 'K_AC_BACK', 27)):
                running = False
                
        # 手機觸控支援：點擊螢幕任意處退出 App
        elif event.type == pygame.MOUSEBUTTONDOWN:
            running = False

    now = datetime.datetime.now()
    min_angle = (now.minute + now.second/60.0) * 6
    hour_angle = (now.hour % 12 + now.minute/60.0) * 30

    # --- 4. 繪製順序 ---
    screen.fill((0, 0, 0))
    
    face_rect = face_img.get_rect(center=SCREEN_CENTER)
    screen.blit(face_img, face_rect)

    pointer_center = pygame.math.Vector2(SCREEN_CENTER.x, SCREEN_CENTER.y + POINTER_CENTER_OFFSET_Y)

    draw_pointer(screen, hour_img, pointer_center, hour_angle, 0.80)
    draw_pointer(screen, min_img, pointer_center, min_angle, 0.80)

    pygame.display.flip()
    
    # 限制 5 FPS，極度省電且低發熱
    clock.tick(5)

pygame.quit()
sys.exit()