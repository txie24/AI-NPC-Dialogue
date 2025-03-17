import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side Scroller Shop Demo")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images
player_image = pygame.image.load("Assets/Player.png").convert_alpha()
ramen_stall_image = pygame.image.load("Assets/Ramen Stall.png").convert_alpha()
weapon_stall_image = pygame.image.load("Assets/Weapon Stall.png").convert_alpha()
newspaper_stall_image = pygame.image.load("Assets/Newspaper Stall.png").convert_alpha()  # New image for newspaper stall
background_image = pygame.image.load("Assets/background.jpg").convert()  # Background image

# Scale images
player_image = pygame.transform.scale(player_image, (70, 130))
ramen_stall_image = pygame.transform.scale(ramen_stall_image, (340, 350))
weapon_stall_image = pygame.transform.scale(weapon_stall_image, (280, 300))
newspaper_stall_image = pygame.transform.scale(newspaper_stall_image, (270, 290))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Player settings
player_speed = 10
player_rect = player_image.get_rect()
player_rect.x = 0  # Starting at the left edge
player_rect.y = HEIGHT - player_rect.height - 20

# Define a baseline for all stalls (10 pixels from bottom)
baseline = HEIGHT - 10

# Compute center positions for equally spaced stalls
center_ramen = WIDTH / 4
center_weapon = WIDTH / 2
center_newspaper = 3 * WIDTH / 4

# Calculate stall positions: x = center - (stall_width/2), y = baseline - stall_height
npc_stalls = {
    "ramen_owner": pygame.Rect(95, HEIGHT - ramen_stall_image.get_height() + 15, ramen_stall_image.get_width(), ramen_stall_image.get_height()),
    "weapon_stall": pygame.Rect(350, HEIGHT - weapon_stall_image.get_height() - 10, weapon_stall_image.get_width(), weapon_stall_image.get_height()),
    "newspaper_stall": pygame.Rect(600, HEIGHT - newspaper_stall_image.get_height() - 10, newspaper_stall_image.get_width(), newspaper_stall_image.get_height())
}

# Font for on-screen text (all text in white)
font = pygame.font.SysFont(None, 24)

def draw_scene(collision_message=None):
    # Draw background
    screen.blit(background_image, (0, 0))
    
    # Draw the ramen stall
    screen.blit(ramen_stall_image, (npc_stalls["ramen_owner"].x, npc_stalls["ramen_owner"].y))
    label = font.render("ramen_owner", True, WHITE)
    screen.blit(label, (npc_stalls["ramen_owner"].x, npc_stalls["ramen_owner"].y - 20))
    
    # Draw the weapon stall
    weapon_rect = npc_stalls["weapon_stall"]
    screen.blit(weapon_stall_image, (weapon_rect.x, weapon_rect.y))
    label = font.render("weapon_stall", True, WHITE)
    screen.blit(label, (weapon_rect.x, weapon_rect.y - 20))
    
    # Draw the newspaper stall
    newspaper_rect = npc_stalls["newspaper_stall"]
    screen.blit(newspaper_stall_image, (newspaper_rect.x, newspaper_rect.y))
    label = font.render("newspaper_stall", True, WHITE)
    screen.blit(label, (newspaper_rect.x, newspaper_rect.y - 20))
    
    # Draw the player
    screen.blit(player_image, (player_rect.x, player_rect.y))
    
    # If there is a collision message, draw it in white
    if collision_message:
        screen.blit(collision_message["surface"], collision_message["pos"])

def start_conversation(npc_key):
    # For now, simply print a message.
    print(f"Starting conversation with {npc_key}!")

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
            
    # Check for collision and prepare message (only one collision message at a time)
    collision_message = None
    conversation_npc = None
    for npc_key, stall_rect in npc_stalls.items():
        if player_rect.colliderect(stall_rect):
            msg_text = f"Press SPACE to talk to {npc_key}"
            msg_surface = font.render(msg_text, True, WHITE)
            # Position the message 40 pixels above the stall
            msg_pos = (stall_rect.x, stall_rect.y - 40)
            collision_message = {"surface": msg_surface, "pos": msg_pos}
            conversation_npc = npc_key
            break  # Only handle the first collision
    
    # Draw scene with (optional) collision message
    draw_scene(collision_message)
    
    # Check if space is pressed while in collision
    if conversation_npc and keys[pygame.K_SPACE]:
        start_conversation(conversation_npc)
    
    pygame.display.flip()
    clock.tick(30)
