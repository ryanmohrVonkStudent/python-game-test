from ursina import *
import random
import math

app = Ursina()

# --- Hier kun je je eigen afbeeldingen instellen ---
floor_texture = 'mijnvloer.png'  # Vervang door jouw afbeelding
platform_textures = [
    'platform1.png',  # Platform 1
    'platform2.png',  # Platform 2
    'platform3.png',  # Platform 3
    'platform4.png',  # Platform 4
    'platform5.png',  # Platform 5 (doel)
]
# ---------------------------------------------------

# Maak een vloer met eigen afbeelding
floor = Entity(model='plane', scale=(20,1,20), color=color.gray, collider='box', texture=floor_texture)

# Voeg meerdere platforms toe met eigen afbeeldingen
platforms = []
platform_positions = [
    (3, 4, 3),
    (-4, 7, 2),
    (5, 10, -3),
    (0, 13, 5),
    (6, 16, 6), # doel-platform
]
for i, pos in enumerate(platform_positions):
    color_choice = color.azure if i < len(platform_positions)-1 else color.lime
    texture_choice = platform_textures[i % len(platform_textures)]
    platforms.append(Entity(model='cube', color=color_choice, scale=(4,1.5,4), position=pos, collider='box', texture=texture_choice))

target_platform = platforms[-1]

# Maak een speler (cube)
player = Entity(model='cube', color=color.orange, scale_y=2, position=(0,1,0), collider='box')

# Voeg verticale snelheid toe voor springen
player.y_velocity = 0
jump_force = 0.08
gravity = 0.2

# First person camera setup
camera.parent = player
camera.position = (0, 1.5, 0)
camera.rotation = (0,0,0)
mouse_sensitivity = Vec2(40, 40)
camera_vertical_angle = 0

# Zet het gezichtsveld (FOV) van de camera groter
camera.fov = 120

speed = 5
score = 0
won = False

# UI
score_text = Text(text='Spring naar het groene platform!', origin=(0,8), scale=2, background=True)
reset_button = Button(text='Opnieuw spelen', color=color.azure, scale=(0.2,0.1), position=(0,0), visible=False)

# Reset-functie
def reset_game():
    global won, score
    player.position = (0,1,0)
    player.y_velocity = 0
    camera_vertical_angle = 0
    player.rotation_y = 0
    camera.rotation_x = 0
    score_text.text = 'Spring naar het groene platform!'
    score_text.background = True
    score_text.color = color.white
    won = False
    reset_button.visible = False
    score = 0

reset_button.on_click = reset_game

# Lock de muis op het spel voor 360 graden kijken
def input(key):
    if key == 'escape':
        mouse.locked = False
    if key == 'left mouse down':
        mouse.locked = True

mouse.locked = True  # Lock direct bij start

# Highscore en score
highscore = 0

# Power-up timers
# speed_boost_timer = 0
# invincible_timer = 0

# Dubbel springen
can_double_jump = False
has_double_jumped = False


# Simpel verhaal/missie
story_text = Text(text='Missie: Bereik het groene platform!', origin=(0,6), scale=1.2, background=True, position=(-0.15,0.4))
# ---------------------------------------------------

def update():
    global camera_vertical_angle, won, score, speed, speed_boost_timer, invincible_timer, can_double_jump, has_double_jumped, current_time, highscore

    if won:
        return

    # Beweging
    move_x = int(held_keys['d']) - int(held_keys['a'])
    move_z = int(held_keys['w']) - int(held_keys['s'])
    if move_x != 0 or move_z != 0:
        angle = math.radians(player.rotation_y)
        dx = (move_z * math.sin(angle)) + (move_x * math.cos(angle))
        dz = (move_z * math.cos(angle)) - (move_x * math.sin(angle))
        lengte = math.sqrt(dx*dx + dz*dz)
        if lengte > 0:
            dx /= lengte
            dz /= lengte
        player.x += dx * time.dt * speed
        player.z += dz * time.dt * speed

    # Zwaartekracht en springen
    player.y_velocity -= gravity * time.dt
    player.y += player.y_velocity

    # Check of speler op de vloer of platform staat
    hit_info = player.intersects()
    on_ground = False
    # Alleen als speler naar beneden beweegt en van bovenaf landt
    if hit_info.hit and player.y_velocity <= 0 and player.y > hit_info.entity.world_y:
        player.y = hit_info.entity.world_y + player.scale_y / 2 + 0.01
        player.y_velocity = 0
        on_ground = True

    # Springen alleen als je op iets staat
    if on_ground and held_keys['space']:
        player.y_velocity = jump_force
        has_double_jumped = False  # Reset dubbel springen als je op de grond bent

    # Dubbel springen
    if not on_ground and not has_double_jumped and held_keys['space']:
        player.y_velocity = jump_force
        has_double_jumped = True

    # Muis besturing voor camera
    player.rotation_y += mouse.velocity[0] * mouse_sensitivity[0]
    camera_vertical_angle -= mouse.velocity[1] * mouse_sensitivity[1]
    camera_vertical_angle = clamp(camera_vertical_angle, -90, 90)
    camera.rotation_x = camera_vertical_angle

    # Check of speler het doel-platform raakt
    if player.intersects(target_platform).hit:
        won = True
        score_text.text = 'Gefeliciteerd! Je hebt het gehaald!'
        score_text.background = True
        score_text.color = color.lime
        reset_button.visible = True

    # Dubbel springen
    if on_ground:
        can_double_jump = True
        has_double_jumped = False
    if not on_ground and can_double_jump and held_keys['space'] and not has_double_jumped:
        player.y_velocity = jump_force
        has_double_jumped = True
        can_double_jump = False

    # Highscore
    global highscore
    if score > highscore:
        highscore = score

    # Winconditie: alleen doelplatform
    if player.intersects(target_platform).hit:
        won = True
        score_text.text = f'Gefeliciteerd! Je hebt het gehaald! Score: {score} (Highscore: {highscore})'
        score_text.background = True
        score_text.color = color.lime
        reset_button.visible = True

app.run()
