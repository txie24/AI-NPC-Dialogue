import pygame
import sys
import threading
import UI  # 确保 UI.py 中有 trigger_conversation_from_game 函数

conversation_log = []  # 用于存储最近几条对话文本

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI NPC Dialogue Side Scroller Demo")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
player_image = pygame.image.load("Assets/Player.png").convert_alpha()
ramen_stall_image = pygame.image.load("Assets/Ramen Stall.png").convert_alpha()
weapon_stall_image = pygame.image.load("Assets/Weapon Stall.png").convert_alpha()
newspaper_stall_image = pygame.image.load("Assets/Newspaper Stall.png").convert_alpha()  # Newspaper stall remains
background_image = pygame.image.load("Assets/background.jpg").convert()  # Background image
ramen_chef_image = pygame.image.load("Assets/Ramen chef.png").convert_alpha()   # Ramen stall owner
weapon_seller_image = pygame.image.load("Assets/Weapon Seller.png").convert_alpha()  # Weapon seller
newspaper_seller_image = pygame.image.load("Assets/Newpaper Seller.png").convert_alpha()  # Newspaper seller

# Scale images
player_image = pygame.transform.scale(player_image, (70, 130))
ramen_stall_image = pygame.transform.scale(ramen_stall_image, (380, 390))
weapon_stall_image = pygame.transform.scale(weapon_stall_image, (280, 300))
newspaper_stall_image = pygame.transform.scale(newspaper_stall_image, (270, 290))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
ramen_chef_image = pygame.transform.scale(ramen_chef_image, (130, 150))
weapon_seller_image = pygame.transform.scale(weapon_seller_image, (80, 140))
newspaper_seller_image = pygame.transform.scale(newspaper_seller_image, (110, 125))

# Player settings
player_speed = 10
player_rect = player_image.get_rect()
player_rect.x = 0  # Starting at the left edge
player_rect.y = HEIGHT - player_rect.height - 20

# Define margin from bottom
margin = 10

# Compute center positions for equally spaced stalls
center_ramen = WIDTH / 4
center_weapon = WIDTH / 2
center_newspaper = 3 * WIDTH / 4

# 映射游戏中的 stall key 到 UI/ai_logic 中对应的 NPC key
npc_mappings = {
    "ramen_owner": "ramen_owner",       # 对应 ai_logic.py 里的 ramen_owner
    "weapon_stall": "Weapons_merchant",
    "newspaper_stall": "Newspaper_merchant"
}

def add_chat_message(msg):
    """
    往 conversation_log 里插入一条新文本。
    为防止列表无限增长，可以限制最大行数
    """
    max_lines = 8  # 你可以按需求改
    conversation_log.append(msg)
    if len(conversation_log) > max_lines:
        conversation_log.pop(0)

def start_conversation(npc_key):
    """
    当玩家按下空格时，被调用。
    """
    if npc_key == "ramen_owner":
        print("Starting conversation with Sato!")
    elif npc_key == "weapon_stall":
        print("Starting conversation with Grim!")
    elif npc_key == "newspaper_stall":
        print("Starting conversation with Bob!")

    # 调用 UI 中的函数来触发对话逻辑（语音输入 + GPT + TTS）
    # 这里利用 npc_mappings，把游戏用的key转换成ai_logic中的key
    if npc_key in npc_mappings:
        UI.trigger_conversation_from_game(npc_mappings[npc_key])
    else:
        print("Warning: No mapping found for NPC key:", npc_key)

# Calculate stall positions: x = center - (stall_width/2), y = HEIGHT - stall_height - margin
npc_stalls = {
    "ramen_owner": pygame.Rect(int(center_ramen - ramen_stall_image.get_width() / 2),
                               int(HEIGHT - ramen_stall_image.get_height() - -40),
                               ramen_stall_image.get_width(),
                               ramen_stall_image.get_height()),
    "weapon_stall": pygame.Rect(int(center_weapon - weapon_stall_image.get_width() / 2),
                                int(HEIGHT - weapon_stall_image.get_height() - margin),
                                weapon_stall_image.get_width(),
                                weapon_stall_image.get_height()),
    "newspaper_stall": pygame.Rect(int(center_newspaper - newspaper_stall_image.get_width() / 2),
                                   int(HEIGHT - newspaper_stall_image.get_height() - 25),
                                   newspaper_stall_image.get_width(),
                                   newspaper_stall_image.get_height())
}

# For the ramen stall, position the chef image in front.
ramen_chef_rect = pygame.Rect(
    npc_stalls["ramen_owner"].x + (ramen_stall_image.get_width() - ramen_chef_image.get_width()) // 2,
    npc_stalls["ramen_owner"].y + int((ramen_stall_image.get_height() - ramen_chef_image.get_height()) / 1.3),
    ramen_chef_image.get_width(),
    ramen_chef_image.get_height()
)

# For the weapon stall, position the weapon seller in front.
weapon_seller_rect = pygame.Rect(
    npc_stalls["weapon_stall"].x + (weapon_stall_image.get_width() - weapon_seller_image.get_width()) // 2,
    npc_stalls["weapon_stall"].y + int((weapon_stall_image.get_height() - weapon_seller_image.get_height()) / 1.1),
    weapon_seller_image.get_width(),
    weapon_seller_image.get_height()
)

# For the newspaper stall, position the newspaper seller in front.
newspaper_seller_rect = pygame.Rect(
    npc_stalls["newspaper_stall"].x + (newspaper_stall_image.get_width() - newspaper_seller_image.get_width()) // 2,
    npc_stalls["newspaper_stall"].y + int((newspaper_stall_image.get_height() - newspaper_seller_image.get_height()) / 1),
    newspaper_seller_image.get_width(),
    newspaper_seller_image.get_height()
)

# Font for on-screen text (all text in white)
font = pygame.font.SysFont(None, 24)

def draw_text_with_border(text, pos, font, text_color, border_color, border_width=2):
    """Draw text with a border to improve legibility."""
    x, y = pos
    for dx in range(-border_width, border_width+1):
        for dy in range(-border_width, border_width+1):
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, border_color)
                screen.blit(outline_surface, (x+dx, y+dy))
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, pos)

def draw_conversation_log():
    """
    把 conversation_log 中的行，逐行渲染到屏幕上，示例放在左上角。
    """
    x = 10
    y = 10
    line_height = 24
    for msg in conversation_log:
        draw_text_with_border(msg, (x, y), font, WHITE, BLACK)
        y += line_height

def draw_scene(collision_message=None):
    # Draw background
    screen.blit(background_image, (0, 0))
    
    # Draw the ramen stall and its label with border
    screen.blit(ramen_stall_image, (npc_stalls["ramen_owner"].x, npc_stalls["ramen_owner"].y))
    draw_text_with_border("Ramen Stall", (npc_stalls["ramen_owner"].x, npc_stalls["ramen_owner"].y - -20),
                          font, WHITE, BLACK)
    
    # Draw the ramen chef (the stall owner) on top of the ramen stall
    screen.blit(ramen_chef_image, (ramen_chef_rect.x, ramen_chef_rect.y))
    
    # Draw the weapon stall and its label with border
    weapon_rect = npc_stalls["weapon_stall"]
    screen.blit(weapon_stall_image, (weapon_rect.x, weapon_rect.y))
    draw_text_with_border("Weapon Stall", (weapon_rect.x, weapon_rect.y - 20),
                          font, WHITE, BLACK)
    
    # Draw the weapon seller on top of the weapon stall
    screen.blit(weapon_seller_image, (weapon_seller_rect.x, weapon_seller_rect.y))
    
    # Draw the newspaper stall and its label with border
    newspaper_rect = npc_stalls["newspaper_stall"]
    screen.blit(newspaper_stall_image, (newspaper_rect.x, newspaper_rect.y))
    draw_text_with_border("Newspaper Stall", (newspaper_rect.x, newspaper_rect.y - 20),
                          font, WHITE, BLACK)
    
    # Draw the newspaper seller on top of the newspaper stall
    screen.blit(newspaper_seller_image, (newspaper_seller_rect.x, newspaper_seller_rect.y))
    
    # Draw the player
    screen.blit(player_image, (player_rect.x, player_rect.y))
    
    # 绘制左上角的对话日志
    draw_conversation_log()

    # If there is a collision message, draw it with border
    if collision_message:
        draw_text_with_border(collision_message["text"], collision_message["pos"],
                              font, WHITE, BLACK)

def main_loop():
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        keys = pygame.key.get_pressed()
        # Move player
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
            if player_rect.x < 0:
                player_rect.x = 0
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed
            if player_rect.x > WIDTH - player_rect.width:
                player_rect.x = WIDTH - player_rect.width
                
        # Check for collision and prepare message
        collision_message = None
        conversation_npc = None

        # For "ramen_owner", check collision with ramen_chef_rect
        if player_rect.colliderect(ramen_chef_rect):
            collision_message = {
                "text": "Press SPACE to talk to Sato",
                "pos": (ramen_chef_rect.x, ramen_chef_rect.y - 40)
            }
            conversation_npc = "ramen_owner"
        # For "weapon_stall", check collision with weapon_seller_rect
        elif player_rect.colliderect(weapon_seller_rect):
            collision_message = {
                "text": "Press SPACE to talk to Grim",
                "pos": (weapon_seller_rect.x, weapon_seller_rect.y - 40)
            }
            conversation_npc = "weapon_stall"
        else:
            # Check collision for newspaper stall using newspaper_seller_rect
            if player_rect.colliderect(newspaper_seller_rect):
                collision_message = {
                    "text": "Press SPACE to talk to Bob",
                    "pos": (newspaper_seller_rect.x, newspaper_seller_rect.y - 40)
                }
                conversation_npc = "newspaper_stall"
        
        # Draw scene with optional collision message
        draw_scene(collision_message)
        
        # Check if space is pressed while in collision
        if conversation_npc and keys[pygame.K_SPACE]:
            start_conversation(conversation_npc)
        
        pygame.display.flip()
        clock.tick(30)
