#continuing the one from jame gam in savepoint becaue i didnt get all the mechanics i wanted
#what to add:
#rounds system that changes enemies
#multiple upgrades and classes and tools and stuff
# teleporter rework since this one is lame
#better maps and such
# enemy health bar and fighting mechanics
#interactable objects and such
#better text in between levels and so on
#how do i make player heal between rounds
#bro what is this S enemy i forgot all about them
#change names of classes and abilities to match theme
# also the behemoth ocunts down twice a turn instead of once
#i should fix the behemoth thing after if i have time
#multiplayer? very ambitious but well....


#pyinstaller and venv stuff fixing NOWWWWW
#ASAP

#whatever im shipping this ill fix after
#rytuiytygjhkitu67iy8o

def __init__(self, x=0, y=0, role="teleporter", hp=5,
        alive=True, stunned=False, stun_timer=0,
        last_move=(0, 0), attack_cooldown=0,
        teleport_cooldown=0, spawn_cooldown=0):
        self.x = x
        self.y = y
        self.role = role
        self.hp = hp
        self.alive = alive
        self.stunned = stunned
        self.stun_timer = stun_timer
        self.last_move = last_move
        self.attack_cooldown = attack_cooldown
        self.teleport_cooldown = teleport_cooldown
        self.spawn_cooldown = spawn_cooldown

def move(self, dx, dy, game_map):
        if self.stunned or not self.alive:
            return False
        new_x = self.x + dx
        new_y = self.y + dy
        if not game_map.iswalkable(new_x, new_y):
            return False
        self.x = new_x
        self.y = new_y
        self.last_move = (dx, dy)
        return True

def attack(self, player):
        if self.stunned or not self.alive:
            return

        player.hp -= 1

        if player.hp <= 0:
            player.alive = False

def update(self):
        if self.stun_timer > 0:
            self.stun_timer -= 1
        if self.stun_timer <= 0:
            self.stunned = False

def create_enemies():
    return [
        Enemy(x=5, y=5, role="teleporter"),
        Enemy(x=28, y=5, role="S", spawn_cooldown=5)
    ]

def teleport_enemy(enemy, player, game_map, enemies):
    if enemy.role != "teleporter" or not enemy.alive or enemy.stunned:
        return False

    if enemy.teleport_cooldown > 0:
        enemy.teleport_cooldown -= 1
        return False

    candidates = [
        (player.x + 1, player.y),
        (player.x - 1, player.y),
        (player.x, player.y + 1),
        (player.x, player.y - 1)
    ]
    shuffle(candidates)
    occupied = {
        (other.x, other.y)
        for other in enemies
        if other is not enemy and other.alive
    }

    for tx, ty in candidates:
        if not game_map.iswalkable(tx, ty):
            continue
        if (tx, ty) == (player.x, player.y):
            continue
        if (tx, ty) in occupied:
            continue
        enemy.last_move = (tx - enemy.x, ty - enemy.y)
        enemy.x = tx
        enemy.y = ty
        enemy.teleport_cooldown = 4
        return True
    return False

def spawnenemy(enemy, game_map, enemies, player=None):
    if enemy.role != "S" or not enemy.alive or enemy.stunned:
        return False

    if player is None:
        return False

    if enemy.spawn_cooldown > 1:
        enemy.spawn_cooldown -= 1
        return False

    enemy.spawn_cooldown = 6

    spawned_any = False
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        tx = enemy.x + dx
        ty = enemy.y + dy
        if not game_map.iswalkable(tx, ty):
            continue
        if tx == player.x and ty == player.y:
            continue
        if (tx, ty) == game_map.goal:
            continue
        taken = False
        for other_enemy in enemies:
            if other_enemy.alive and other_enemy.x == tx and other_enemy.y == ty:
                taken = True
        if taken:
            continue
       
        enemies.append(Enemy(x=tx, y=ty, role="spawned"))
        spawned_any = True
    return spawned_any

def move_slow_enemy(enemy, player, game_map, enemies):
    if enemy.role != "spawned" or enemy.stunned:
        return False

    moves = []
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        tx = enemy.x + dx
        ty = enemy.y + dy
        distance = abs(player.x - tx) + abs(player.y - ty)
        moves.append((distance, dx, dy))
    moves.sort()

    for distance, dx, dy in moves:
        tx = enemy.x + dx
        ty = enemy.y + dy
        if not game_map.iswalkable(tx, ty):
            continue
        if (tx, ty) == (player.x, player.y):
            continue
        if (tx, ty) == game_map.goal:
            continue
        taken = False
        for other_enemy in enemies:
            if other_enemy is not enemy and other_enemy.alive and (other_enemy.x, other_enemy.y) == (tx, ty):
                taken = True
        if taken:
            continue
        return enemy.move(dx, dy, game_map)

    return False

def move_behemoth(enemy, player, game_map, enemies):
    if enemy.role != "behemoth" or enemy.stunned or not enemy.alive:
        return False

    speed = max(1, enemy.behemoth_speed)
    moved = False
    for i in range(speed):
        target = next_path_step(enemy, (player.x, player.y), game_map)
        if target is None or target == (player.x, player.y):
            break
        if any(
            other is not enemy
            and other.alive
            and (other.x, other.y) == target
            for other in enemies
        ):
            break
        dx = target[0] - enemy.x
        dy = target[1] - enemy.y
        if not enemy.move(dx, dy, game_map):
            break
        moved = True

    enemy.behemoth_speed += 1
    return moved

def worm_cells(enemy, head=None, shape=None):
    head_x, head_y = head or (enemy.x, enemy.y)
    return {
        (head_x + dx, head_y + dy)
        for dx, dy in (shape or enemy.shape)
    }

def choose_worm_shape(enemy, head, game_map, player, enemies):
    shapes = [
        enemy.shape,
        ((0, 0), (-1, 0), (-2, 0)),
        ((0, 0), (1, 0), (2, 0)),
        ((0, 0), (0, -1), (0, -2)),
        ((0, 0), (0, 1), (0, 2)),
        ((0, 0), (-1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1)),
        ((0, 0), (-1, 0), (0, -1)),
        ((0, 0), (1, 0), (0, -1)),
    ]
    occupied = {
        cell
        for other in enemies
        if other is not enemy and other.alive and not other.burrowed
        for cell in worm_cells(other)
        if other.role == "worm"
    }
    occupied.update(
        (other.x, other.y)
        for other in enemies
        if other is not enemy and other.alive and other.role != "worm"
    )
    for candidate in shapes:
        cells = worm_cells(enemy, head, candidate)
        if all(game_map.iswalkable(*cell) for cell in cells):
            if (player.x, player.y) not in cells and not cells & occupied:
                return candidate
    return None

def burrow_worm(enemy):
    enemy.burrowed = True
    enemy.burrow_timer = 2
    enemy.burrow_cooldown = 5

def move_worm(enemy, player, game_map, enemies):
    if enemy.role != "worm" or not enemy.alive or enemy.stunned:
        return False
    if enemy.burrowed:
        enemy.burrow_timer -= 1
        if enemy.burrow_timer > 0:
            return False
        candidates = [
            (player.x + dx, player.y + dy)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
        ]
def move_worm(enemy, player, game_map, enemies):
    if enemy.role != "worm" or not enemy.alive or enemy.stunned:
        return False
    if enemy.burrowed:
        enemy.burrow_timer -= 1
        if enemy.burrow_timer > 0:
            return False
        candidates = [
            (player.x + dx, player.y + dy)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
        ]
        shuffle(candidates)
        for head in candidates:
            shape = choose_worm_shape(enemy, head, game_map, player, enemies)
            if shape is not None:
                enemy.x, enemy.y = head
                enemy.shape = shape
                enemy.burrowed = False
                player.last_message = "The worm burrows back up with a rumble!"
                return True
        enemy.burrow_timer = 1
        return False

    if enemy.burrow_cooldown > 0:
        enemy.burrow_cooldown -= 1
    if enemy.burrow_cooldown == 0:
        burrow_worm(enemy)
        player.last_message = "The worm dives underground!"
        return False

    target = next_path_step(enemy, (player.x, player.y), game_map)
    if target is None or target == (player.x, player.y):
        return False
    shape = choose_worm_shape(enemy, target, game_map, player, enemies)
    if shape is None:
        burrow_worm(enemy)
        player.last_message = "The worm squeezes underground to get around the walls!"
        return False
    enemy.last_move = (target[0] - enemy.x, target[1] - enemy.y)
    enemy.x, enemy.y = target
    enemy.shape = shape
    return True

def update_enemies(enemies, player, game_map):
    for enemy in enemies[:]:
        if not enemy.alive:
            continue
        enemy.update()
        if enemy.stunned:
            continue
        if enemy.role == "teleporter":
            teleport_enemy(enemy, player, game_map, enemies)
        elif enemy.role == "S":
            spawnenemy(enemy, game_map, enemies, player)
        elif enemy.role == "spawned":
            move_slow_enemy(enemy, player, game_map, enemies)

def draw_enemies(screen, enemies):
    for enemy in enemies:
        if not enemy.alive:
            continue


        if enemy.role == "teleporter":
            screen[enemy.y][enemy.x] = "T"
        elif enemy.role == "S":
            screen[enemy.y][enemy.x] = "S"
        elif enemy.role == "spawned":
            screen[enemy.y][enemy.x] = "e"

from dataclasses import dataclass, field
import heapq
from random import shuffle
from typing import Optional
WIDTH = 35
HEIGHT= 8
TOTAL_ROUNDS = 5
BEHEMOTH_SPAWN_TURN = 50
TELEPORT_WINDUP_TURNS = 2
TELEPORT_COOLDOWN_TURNS = 2
#behemoth is temp name its just an enemy to stop player from camping forever

RESET = "\033[0m"
HEX_COLORS = {
    "white": "#fcfbfc",
    "grey": "#dbd3d8",
    "red": "#db9692",
    "orange": "#dcaf91",
    "yellow": "#dbd991",
    "green": "#96db91",
    "blue": "#92b5db",
    "indigo": "#9196db",
    "purple": "#b991da",
    "pink": "#db91d3",
    "dark_grey": "#514d4a",
    "black": "#2d2730",
    "behemoth": "#8b0000",
    "worm": "#a30092"
}

def color(hex_code):
    red = int(hex_code[1:3], 16)
    green = int(hex_code[3:5], 16)
    blue = int(hex_code[5:7], 16)
    return f"\033[38;2;{red};{green};{blue}m"

ENEMY_COLORS = {
    "basic": color(HEX_COLORS["red"]),
    "teleporter": color(HEX_COLORS["purple"]),
    "spawned": color(HEX_COLORS["green"]),
    "spawner": color(HEX_COLORS["orange"]),
    "behemoth": color(HEX_COLORS["behemoth"]),
    "worm": color(HEX_COLORS["worm"])
}
PLAYER_COLOR = color(HEX_COLORS["blue"])
PLAYER_DASH_COLOR = color(HEX_COLORS["white"])
WALL_COLOR = color(HEX_COLORS["dark_grey"])
GOAL_COLOR = color(HEX_COLORS["yellow"])
PREVIEW_COLOR = color(HEX_COLORS["purple"])
CONFETTI_AREA_COLOR = color(HEX_COLORS["red"])
STUNNED_COLOR = color(HEX_COLORS["white"])

CHARACTER_LOADOUTS = {
    "scout": {
        "display_name": "Scout",
        "weapon": "Twin daggers",
        "max_hp": 4,
        "damage": 1,
        "ability": "vroomvroom",
        "description": "Fast and fragile. Vroomvroom lets you dash two squares.",
    },
    "guardian": {
        "display_name": "Guardian",
        "weapon": "Heavy hammer",
        "max_hp": 8,
        "damage": 2,
        "ability": "confetti",
        "description": "Tough and powerful. Confetti stuns nearby enemies.",
    },
    "medic": {
        "display_name": "Medic",
        "weapon": "Healing staff",
        "max_hp": 5,
        "damage": 1,
        "ability": "second wind",
        "description": "Balanced. Second wind restores 3 HP once per round.",
    },
}

DIRECTIONS ={
    "w" or "W": (0,-1),
    "a" or "A": (-1,0),
    "s" or "S": (0,1),
    "d" or "D": (1,0)
}


@dataclass
class Player:
    x: int = 1
    y: int=1
    hp: int = 3
    max_hp: int = 3
    alive: bool = True

    tool: str = "Sillyness"
    weapon: str = "Sillyness"
    damage: int = 1
    character_name: str = "Scout"
    #temporary character names for now
    ability: str = "vroomvroom"

    playerequippedclass: Optional[str]= None

    last_move: tuple = (0,0)

    move_history: list[tuple[int,int]] = field(default_factory=list)
    extra_moves: int=0
    last_message: str = ""

    vroomvroom_available: bool = False
    vroomvroom_cooldown: int = 0
    dash_color_turns: int = 0

    stun_timer: int=0

    def move(self, dx: int, dy: int, game_map: "GameMap"):
        new_x = self.x + dx
        new_y = self.y + dy

        if not game_map.iswalkable(new_x,new_y):
            return False

        self.x =new_x
        self.y = new_y

        self.last_move=(dx,dy)
        self.move_history.append((dx,dy))
        return True

    def use_vroomvroom(self,game_map, enemies=None):
        if not self.vroomvroom_available:
            return False

        dx,dy = get_movementdirection(input("Dash direction (w/a/s/d): "))
        if dx == 0 and dy == 0:
            self.last_message = "That is not a direction, little guy."
            return False
        moves = 0
        for _ in range(2):
            if move_player_by_delta(self, dx, dy, game_map, enemies):
                moves += 1
            else:
                break
        if moves:
            self.vroomvroom_available = False
            self.vroomvroom_cooldown = 4
            self.dash_color_turns = 2
            self.last_message = f"VROOM! Two squares in one turn! ({moves}/2)"
        return moves > 0

    confetti_available: bool = True
    confetti_cooldown: int = 0
    confetti_range_visible: bool = False
    second_wind_available: bool = False

    def use_confetti(self, game_map, enemies=None):
        if not self.confetti_available:
            self.last_message = "Confetti is recharging."
            return False
        if not enemies:
            self.last_message = "Confetti failed, no enemy near by"
            return False

        stunned_count = 0  
        for enemy in enemies:
            if not enemy.alive:
                continue

            if abs(enemy.x - self.x) <= 1 and abs(enemy.y - self.y) <= 1:
                enemy.stunned = True
                enemy.stun_timer = 3
                stunned_count += 1

        if stunned_count == 0:
            self.last_message = "Confetti failed, no enemy in range"
            return False

        self.confetti_available = False
        self.confetti_cooldown = 8
        self.confetti_range_visible = True
        enemy_word = "enemy" if stunned_count == 1 else "enemies"
        self.last_message = f"Confetti worked! Stunned {stunned_count} {enemy_word}."
        return True
    def use_second_wind(self):
        if self.ability != "second wind" or not self.second_wind_available:
            self.last_message = "Second wind is unavailable."
            return False
        if self.hp >= self.max_hp:
            self.last_message = "You are already at full health."
            return False
        healed = min(3, self.max_hp - self.hp)
        self.hp += healed
        self.second_wind_available = False
        self.last_message = f"Second wind restored {healed} HP."
        return True

@dataclass
class Enemy:
    x: int = 0
    y: int = 0
    role: str = "teleporter"
    hp: int = 5
    alive:bool =True
    stunned: bool =False
    stun_timer: int = 0
    last_move: tuple[int, int] = (0, 0)
    attack_cooldown: int = 0
    teleport_cooldown: int = 0
    spawn_cooldown: int = 0
    pushed_this_turn: bool = False
    teleport_target: Optional[tuple[int, int]] = None
    teleport_windup: int = 0
    behemoth_speed: int = 1
    shape: tuple[tuple[int, int], ...] = ((0, 0), (-1, 0), (-2, 0))
    burrowed: bool = False
    burrow_timer: int = 0
    burrow_cooldown: int = 4

    def __post_init__(self):
        if self.hp <= 0:
            self.hp = {
                "basic": 2,
                "spawned": 1,
                "teleporter": 3,
                "spawner": 4,
                "S": 3,
                "behemoth": float("inf"),
                "worm":3

            }.get(self.role, 1)

    def take_push_damage(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            self.teleport_target = None
            return True
        return False

    def move(self, dx, dy, game_map):
        if self.stunned:
            return False

        new_x = self.x + dx
        new_y = self.y + dy
        if not game_map.iswalkable(new_x, new_y):
            return False

        self.x = new_x
        self.y = new_y
        self.last_move = (dx, dy)
        return True

    def attack(self, player):
        if self.stunned or not self.alive:
            return

        player.hp -= 1
        player.last_message = "Oof! A little enemy bonked you."
        if player.hp <= 0:
            player.alive = False

    def update(self):
        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer == 0:
                self.stunned = False
        else:
            self.stunned = False

def teleport_enemy(enemy, player, game_map, enemies):
    if enemy.role != "teleporter" or not enemy.alive or enemy.stunned:
        return False
    occupied = {(other.x, other.y) for other in enemies if other is not enemy and other.alive}
    if enemy.teleport_target is not None:
        if enemy.teleport_windup > 1:
            enemy.teleport_windup -= 1
            return False
        target_x, target_y = enemy.teleport_target
        if (
            game_map.iswalkable(target_x, target_y)
            and (target_x, target_y) not in occupied
            and (target_x, target_y) != (player.x, player.y)
        ):
            enemy.last_move = (target_x - enemy.x, target_y - enemy.y)
            enemy.x = target_x
            enemy.y = target_y
            enemy.teleport_target = None
            enemy.teleport_windup = 0
            enemy.teleport_cooldown = TELEPORT_COOLDOWN_TURNS
            player.last_message = "ZAP! The teleporter little guy has arrived!"
            return True
        enemy.teleport_target = None
        enemy.teleport_windup = 0
        player.last_message = "The teleport spot got bonked, so the teleport fizzled!"
        return False
    if enemy.teleport_cooldown > 0:
        enemy.teleport_cooldown -= 1
        return False
    candidates = [
        (player.x + 1, player.y),
        (player.x - 1, player.y),
        (player.x, player.y + 1),
        (player.x, player.y - 1),
    ]
    shuffle(candidates)
    for target_x, target_y in candidates:
        if not game_map.iswalkable(target_x, target_y):
            continue
        if (target_x, target_y) in occupied or (target_x, target_y) == (player.x, player.y):
            continue
        enemy.teleport_target = (target_x, target_y)
        enemy.teleport_windup = TELEPORT_WINDUP_TURNS
        player.last_message = (f"Uh-oh! The teleporter will appear at ({target_x}, {target_y}) in {TELEPORT_WINDUP_TURNS} turns!")
        return False
    return False

def spawnenemy(enemy,game_map,enemies, player = None):
    if not enemy.alive or enemy.stunned:
        return False
    if player is None:
        return False
    if enemy.spawn_cooldown > 1:
        enemy.spawn_cooldown -= 1
        return False
    enemy.spawn_cooldown = 5
    spawned_any = False
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        tx = enemy.x +dx
        ty = enemy.y +dy
        if not game_map.iswalkable(tx, ty):
            continue
        if tx == player.x and ty == player.y:
            continue
        if (tx, ty) == game_map.goal:
            continue
        taken = False
        for other_enemy in enemies:
            if other_enemy.alive and other_enemy.x == tx and other_enemy.y == ty:
                taken = True
        if taken:
            continue
        enemies.append(Enemy(x=tx, y=ty, role="spawned"))
        spawned_any = True
        return spawned_any
    
def move_slow_enemy(enemy, player, game_map, enemies):
    if enemy.role != "spawned" or enemy.stunned:
        return False
    moves = []
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        tx = enemy.x + dx
        ty = enemy.y + dy
        distance = abs(player.x - tx) + abs(player.y - ty)
        moves.append((distance, dx, dy))
    moves.sort()
    for distance, dx, dy in moves:
        tx = enemy.x + dx
        ty = enemy.y + dy
        if not game_map.iswalkable(tx, ty):
            continue
        if (tx, ty) == (player.x, player.y):
            continue
        if (tx, ty) == game_map.goal:
            continue
        taken = False
        for other_enemy in enemies:
            if other_enemy is not enemy and other_enemy.alive and (other_enemy.x, other_enemy.y) == (tx, ty):
                taken = True
        if taken:
            continue
        return enemy.move(dx, dy, game_map)
    return False

class GameMap:
    def __init__(self,width=WIDTH,height = HEIGHT):
        self.width = width
        self.height = height
        self.walls: set[tuple[int,int]]=set()
        self.goal: Optional[tuple[int,int]]
        self.create_map()

    def create_map(self):
        for x in range(self.width):
            self.add_wall(x, 0)
            self.add_wall(x, self.height - 1)
        for y in range(self.height):
            self.add_wall(0, y)
            self.add_wall(self.width - 1, y)
        for x in range(8, 13):
            self.add_wall(x, 3)
        for x in range(22, 27):
            self.add_wall(x, 5)
        self.goal = (self.width - 2, self.height - 2)

    def is_in_boundscheck(self, x,y):
        return 0 <= x < self.width and 0 <= y < self.height

    def iswalkable(self,x,y):
        return self.is_in_boundscheck(x,y) and (x,y) not in self.walls

    def add_wall(self,x,y):
        if self.is_in_boundscheck(x,y):
            self.walls.add((x,y))

def get_movementdirection(key):
    return DIRECTIONS.get(key.lower(),(0,0))

def move_player_by_delta(player, dx, dy, game_map, enemies=None):
    player.last_message = ""
    target = (player.x + dx, player.y + dy)
    if not game_map.iswalkable(*target):
        player.last_message = "Bonk! A wall says, 'not today, little guy.'"
        return False
    if enemies is not None:
        enemy = next(
            (
                enemy for enemy in enemies
                if enemy.alive
                and not enemy.burrowed
                and (
                    target in worm_cells(enemy)
                    if enemy.role == "worm"
                    else (enemy.x, enemy.y) == target
                )
            ),
            None,
        )
        if enemy is not None:
            if enemy.role == "worm" and target != (enemy.x, enemy.y):
                player.last_message = "The worm's body blocks that square."
                return False
            push_target = (enemy.x + dx, enemy.y + dy)
            if not game_map.iswalkable(*push_target):
                enemy.pushed_this_turn = True
                defeated = enemy.take_push_damage(player.damage)
                if not defeated:
                    enemy.stunned = True
                    enemy.stun_timer = 2
                if defeated:
                    player.last_message = (
                        f"Wall slam! The {enemy.role} took {player.damage*2} damage and is stunned "
                    )
                else:
                    player.last_message = (
                        f"Wall slam! The {enemy.role} took 2 damage and is stunned "
                        f"({enemy.hp} HP left)."
                    )
                return True
            if (
                push_target == game_map.goal
                or any(
                    other.alive and other is not enemy
                    and (other.x, other.y) == push_target
                    for other in enemies
                )
            ):
                player.last_message = "The little enemy is stuck. It goes, 'squish... nope.'"
                return False
            enemy.x, enemy.y = push_target
            enemy.last_move = (dx, dy)
            enemy.pushed_this_turn = True
            player.x, player.y = player.x-dx, player.y-dy
            defeated = enemy.take_push_damage(player.damage)
            if defeated:
                player.last_message = (
                    f"Bonk! You pushed the {enemy.role} and defeated it."
                )
            else:
                player.last_message = (
                    f"Boop! You pushed the {enemy.role}. "
                    f"It has {enemy.hp} HP left."
                )
    if player.move(dx, dy, game_map):
        if not player.last_message:
            player.last_message = "Scoot scoot! The little guy moves."
        return True
    player.last_message = "Your little legs wobble, but you stay put."
    return False

def move_player(player,key,game_map,enemies=None):
    dx,dy=get_movementdirection(key)

    if dx==0 and dy==0:
        player.last_message = "That is not a direction, sadly. :("
        return False

    return move_player_by_delta(player, dx, dy, game_map, enemies)

def move_enemy(enemy,dx,dy,game_map):
    return enemy.move(dx,dy,game_map)

def next_path_step(enemy, target, game_map):
    start = (enemy.x, enemy.y)
    frontier = [(0, start)]
    came_from = {start: None}
    cost = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == target:
            break

        for dx, dy in DIRECTIONS.values():
            next_tile = (current[0] + dx, current[1] + dy)
            if not game_map.iswalkable(*next_tile):
                continue
            new_cost = cost[current] + 1
            if new_cost < cost.get(next_tile, float("inf")):
                cost[next_tile] = new_cost
                priority = new_cost + abs(next_tile[0] - target[0]) + abs(next_tile[1] - target[1])
                heapq.heappush(frontier, (priority, next_tile))
                came_from[next_tile] = current

    if target not in came_from:
        return None

    step = target
    while came_from[step] != start:
        step = came_from[step]
    return step

def move_basic_enemy(enemy,player,game_map,enemies):
    if enemy.role != "basic" or enemy.stunned:
        return False

    target = next_path_step(enemy, (player.x, player.y), game_map)
    if target is None:
        return False

    dx = target[0] - enemy.x
    dy = target[1] - enemy.y

    if target == (player.x, player.y):
        return False

    for other_enemy in enemies:
        if other_enemy is not enemy and (other_enemy.x, other_enemy.y) == target:
            return False

    return enemy.move(dx, dy, game_map)


def use_player_ability(player,abilityname,game_map,enemies):
    ability_name = abilityname.lower()

    if ability_name == "vroomvroom":
        return player.use_vroomvroom(game_map, enemies)
    if ability_name == "confetti":
        return player.use_confetti(game_map, enemies)
    if ability_name in ("second wind", "secondwind"):
        return player.use_second_wind()

    return False


def is_adjacent(first, second):
    return abs(first.x - second.x) + abs(first.y - second.y) == 1


def check_player_enemy_collision(player,enemies):
    pass
   
def check_goal_reached(player,game_map):
    if game_map.goal is None:
        return False
    return (player.x,player.y) == game_map.goal


class Game:
    def __init__(self):
        self.game_map = GameMap()

        self.player = Player(x=1, y=1, playerequippedclass=None)
        self.character_key = "scout"

        self.enemies = []
        self.round_number = 1
        self.round_won = False
        self.running = True
        self.end_reason = ""

    def setup(self):
        self.choose_character()
        self.setup_round(1)

    def choose_character(self):
        print("\nChoose your little guy:")
        for key, loadout in CHARACTER_LOADOUTS.items():
            print(
                f"{key.title()}: {loadout['weapon']}, "
                f"{loadout['max_hp']} HP, {loadout['damage']} damage - "
                f"{loadout['description']}"
            )
        while True:
            choice = input("Character (scout/guardian/medic): ").strip().lower()
            if choice in CHARACTER_LOADOUTS:
                self.character_key = choice
                return
            print("Please choose scout, guardian, or medic.")

    def setup_round(self, round_number):
        self.round_number = round_number
        width = WIDTH + (round_number - 1) * 4
        height = HEIGHT + (round_number - 1) * 2
        self.game_map = GameMap(width, height)
        loadout = CHARACTER_LOADOUTS[self.character_key]
        self.player = Player(
            x=1,
            y=1,
            hp=loadout["max_hp"],
            max_hp=loadout["max_hp"],
            weapon=loadout["weapon"],
            damage=loadout["damage"],
            character_name=loadout["display_name"],
            ability=loadout["ability"],
            playerequippedclass=loadout["display_name"],
        )
        self.player.vroomvroom_available = loadout["ability"] == "vroomvroom"
        self.player.confetti_available = loadout["ability"] == "confetti"
        self.player.second_wind_available = loadout["ability"] == "second wind"
        self.enemies = []
        self.turn_number = 0
        self.behemoth_spawned = False
        spawn_positions = [
            (self.game_map.width // 2, self.game_map.height // 2, "teleporter"),
            (self.game_map.width - 7, self.game_map.height - 3, "spawner"),
            (self.game_map.width // 2 - 4, self.game_map.height - 2, "basic"),
            (self.game_map.width // 2 + 2, self.game_map.height // 2, "worm"),

            (self.game_map.width - 4, 2, "basic"),
            (self.game_map.width // 2, 2, "teleporter"),
            (4, self.game_map.height // 2, "basic"),
        ]
        for x, y, role in spawn_positions[:round_number]:
            position = (x, y)
            if (
                not self.game_map.iswalkable(*position)
                or position == self.game_map.goal
                or any((enemy.x, enemy.y) == position for enemy in self.enemies)
            ):
                continue
            cooldown = 5 if role == "spawner" else 0
            self.enemies.append(
                Enemy(x=x, y=y, role=role, spawn_cooldown=cooldown)

            )


    def spawn_behemoth(self):
        occupied = {
            (enemy.x, enemy.y) for enemy in self.enemies if enemy.alive
        }
        candidates = [
            (self.game_map.width - 2, 1),
            (self.game_map.width - 2, self.game_map.height - 2),
            (self.game_map.width // 2, 1),
        ]
        spawn_position = next(
            (
                position
                for position in candidates
                if self.game_map.iswalkable(*position)
                and position != self.game_map.goal
                and position != (self.player.x, self.player.y)
                and position not in occupied
            ),
            None,
        )
        if spawn_position is None:
            return
        self.enemies.append(
            Enemy(x=spawn_position[0], y=spawn_position[1], role="behemoth")
        )
        self.behemoth_spawned = True
        self.player.last_message = (
            "A CRIMSON BEHEMOTH has entered the maze! It grows faster every turn!"
        )

    def start_next_round(self):
        if self.round_number >= TOTAL_ROUNDS:
            self.round_won = False
            self.end_reason = "victory"
            self.running = False
            return
        self.round_won = False
        print("\nYou heal completely between rounds.")
        self.choose_character()
        self.setup_round(self.round_number + 1)
        print(
            f"\nRound {self.round_number} begins! "
            "The maze is shifting and more little guys are waiting."
        )
        input("Press Enter to continue...")
        

    def handle_player_input(self, key):
        if key in DIRECTIONS:
            if not move_player(self.player, key, self.game_map, self.enemies):
                print(self.player.last_message)
                return False
            else:
                print(self.player.last_message)
            return True
        if key in ("skip", "wait", "."):
            self.player.last_message = "You wait a turn. The other goobers take theirs."
            print(self.player.last_message)
            return True
        if key in ("e", "vroomvroom"):
            if not use_player_ability(self.player,"vroomvroom",self.game_map,self.enemies):
                print(self.player.last_message or "vroomvroom is unavailable. Move first, then try again.")
                return False
            else:
                print(self.player.last_message)
            input("Press Enter to continue...")
            return True
        if key in ("c", "confetti"):
            self.player.confetti_range_visible = True
            self.render()
            confirmation = input(
                "Press Enter to throw confetti, or type q to cancel..."
            ).strip().lower()
            if confirmation in ("q", "cancel"):
                self.player.confetti_range_visible = False
                print("Confetti cancelled.")
                return False
            if not use_player_ability(self.player, "confetti", self.game_map, self.enemies):
                print(self.player.last_message or "Confetti is unavailable. Wait for it to recharge.")
                return False
            else:
                print(self.player.last_message)
                input("Press Enter to continue...")
                return True

        if key in ("h", "heal", "second wind"):
            if not use_player_ability(self.player, "second wind", self.game_map, self.enemies):
                print(self.player.last_message)
                return False
            print(self.player.last_message)
            return True

        print("That is not a valid action. Use w/a/s/d, e (vroomvroom), c (confetti), h (second wind), skip, or quit.")
        return False

    def update_enemies(self):
        for enemy in self.enemies:
            if enemy.pushed_this_turn:
                enemy.pushed_this_turn = False
                enemy.update()
                continue
            if enemy.role == "worm" and enemy.burrowed:
                move_worm(enemy, self.player, self.game_map, self.enemies)
                continue
            if enemy.stunned:
                enemy.update()
                continue
            worm_attacking = (
                enemy.role == "worm"
                and any(
                    abs(x - self.player.x) + abs(y - self.player.y) == 1
                    for x, y in worm_cells(enemy)
                )
            )
            teleporter_attacking = (
                enemy.role == "teleporter"
                and max(
                    abs(enemy.x - self.player.x),
                    abs(enemy.y - self.player.y),
                ) == 1
            )
            if is_adjacent(enemy, self.player) or worm_attacking:
                continue
            if teleporter_attacking:
                continue
            if enemy.role == "basic":
                move_basic_enemy(enemy, self.player, self.game_map, self.enemies)
            elif enemy.role == "teleporter":
                teleport_enemy(enemy, self.player, self.game_map, self.enemies)
            elif enemy.role == "spawner":
                spawnenemy(enemy, self.game_map, self.enemies, self.player)
            elif enemy.role == "spawned":
                move_slow_enemy(enemy, self.player, self.game_map, self.enemies)
            elif enemy.role == "behemoth":
                move_behemoth(enemy, self.player, self.game_map, self.enemies)
            elif enemy.role == "worm":
                move_worm(enemy, self.player, self.game_map, self.enemies)
            enemy.update()

    def update(self):
        self.turn_number += 1
        check_player_enemy_collision(self.player, self.enemies)
        self.update_enemies()
        self.turn_number += 1

        if self.player.vroomvroom_cooldown > 0:
            self.player.vroomvroom_cooldown -= 1
            if self.player.vroomvroom_cooldown == 0:
                self.player.vroomvroom_available = True
                self.player.last_message = "Vroomvroom is recharged! The little legs are ready to get zoomy again."

        if self.player.confetti_cooldown > 0:
            self.player.confetti_cooldown -= 1
        if self.player.confetti_cooldown == 0:
            self.player.confetti_available = True
            self.player.last_message = "Confetti is ready."

        if self.player.dash_color_turns > 0:
            self.player.dash_color_turns -= 1

        if self.player.last_message.startswith("Oof!"):
            print(self.player.last_message)
            input("Press Enter to continue...")
        elif self.player.last_message.startswith(("Uh-oh!", "ZAP!", "The teleport", "A CRIMSON")):            
            print(self.player.last_message)
            input("Press Enter to continue...")

        if not self.player.alive:
            print("You were defeated!")
            input("Press Enter to continue...")
            self.end_reason = "defeat"
            self.running = False
            return

        if check_goal_reached(self.player,self.game_map):
            print("You reached the goal in round {self.round_number}!")
            input("Press Enter to continue...")
            self.round_won = True
            self.running = False

    def render(self):
        print("\n" * 2)
        print(f"Round {self.round_number}/{TOTAL_ROUNDS}")
        controls = "w/a/s/d | skip/wait | quit"
        if self.player.ability == "vroomvroom":
            controls = "w/a/s/d | e (vroomvroom) | " + controls
        elif self.player.ability == "confetti":
            controls = "w/a/s/d | c (confetti) | " + controls
        elif self.player.ability == "second wind":
            controls = "w/a/s/d | h (second wind) | " + controls
        print(f"Character: {self.player.character_name} | Weapon: {self.player.weapon}")
        print(f"Controls: {controls}")
        print(f"HP: {self.player.hp}/{self.player.max_hp} | Damage: {self.player.damage}")
        if self.player.ability == "second wind":
            print(f"second wind: {'ready' if self.player.second_wind_available else 'used this round'}")
        print("Controls: w/a/s/d | e (vroomvroom) | c (confetti) | skip/wait | quit")
        print(f"HP: {self.player.hp}")
        if self.player.vroomvroom_available:
            vroomvroom_status = "ready"
        else:
            vroomvroom_status = f"recharging ({self.player.vroomvroom_cooldown} turns)"
        print(f"vroomvroom: {vroomvroom_status}")
        if self.player.confetti_available:
            confetti_status = "ready"
        else:
            confetti_status = f"recharging ({self.player.confetti_cooldown} turns)"
        print(f"confetti: {confetti_status}")
        if self.behemoth_spawned:
            behemoth_status = "ACTIVE"
        else:
            turns_left = max(0, int(BEHEMOTH_SPAWN_TURN - self.turn_number*0.5))
            #bro something is wrong with the turns left thing it counts down twice
            #for now ill make the thing count down by 0.5
            # but i should prolly fix it later
            behemoth_status = f"in {turns_left} turns"
        print(f"Behemoth: {behemoth_status}")
        enemies_by_position = {
            (x, y): enemy
            for enemy in self.enemies
            if enemy.alive and not enemy.burrowed
            for x, y in (
                worm_cells(enemy) if enemy.role == "worm" else {(enemy.x, enemy.y)}
            )        }
        confetti_area = {
            (x, y)
            for x in range(self.player.x - 1, self.player.x + 2)
            for y in range(self.player.y - 1, self.player.y + 2)
            if self.game_map.iswalkable(x, y)
        }
        teleport_warning_area = {
            (target_x + dx, target_y + dy)
            for enemy in self.enemies
            if enemy.alive and enemy.role == "teleporter"
            and enemy.teleport_target is not None
            for target_x, target_y in (enemy.teleport_target,)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if (dx, dy) != (0, 0)
            and self.game_map.iswalkable(target_x + dx, target_y + dy)
        }
        for y in range(self.game_map.height):
            row = []
            for x in range(self.game_map.width):
                position = (x, y)

                if position == (self.player.x, self.player.y):
                    player_color = (
                        PLAYER_DASH_COLOR
                        if self.player.dash_color_turns
                        else PLAYER_COLOR
                    )
                    row.append(f"{player_color}P{RESET}")
                elif position in enemies_by_position:
                    enemy = enemies_by_position[position]
                    enemy_color = STUNNED_COLOR if enemy.stunned else ENEMY_COLORS.get(enemy.role, "")
                    enemy_symbol = (
                        str(enemy.stun_timer)
                        if enemy.stunned
                        else (
                            "B" if enemy.role == "behemoth"
                            else "W" if enemy.role == "worm" and position == (enemy.x, enemy.y)
                            else "w" if enemy.role == "worm"
                            else "e"
                        )                    )
                    row.append(
                        f"{enemy_color}{enemy_symbol}{RESET}"
                        if enemy_color
                        else enemy_symbol
                    )
                elif any(
                    enemy.alive and enemy.teleport_target == position
                    for enemy in self.enemies
                ):
                    row.append(f"{PREVIEW_COLOR}?{RESET}")
                elif position in teleport_warning_area:
                    row.append(f"{ENEMY_COLORS['teleporter']}!{RESET}")
                elif self.player.confetti_range_visible and position in confetti_area:
                    row.append(f"{CONFETTI_AREA_COLOR}.{RESET}")
                elif position in self.game_map.walls:
                    row.append(f"{WALL_COLOR}#{RESET}")
                elif position == self.game_map.goal:
                    row.append(f"{GOAL_COLOR}O{RESET}")
                else:
                    row.append(".")

            print("".join(row))

        self.player.confetti_range_visible = False

    def show_intro(self):
        while True:
            print("\n" * 2)
            print("===================================")
            print("              GOOBERS")
            print("===================================")
            print("Type \"start\" to play, or type \"lore\" to learn about cool story features.")
            print("alternatively, input an enemy type.")
            print("Enemy types: basic, teleporter, spawned, spawner, behemoth")
            choice = input("> ").strip().lower()

            if choice == "start":
                return
            if choice == "lore":
                print("\nYou are just a little guy in a \"maze\" full of other little guys.")
                print("Armed with nothing but party decorations and your own abilities you have to get to the exit.")
                print("Reach the O, avoid the other little guys, or evilly push them out of your way.")
                print("Input an enemy type name for more information on a specific one.")
                print("Enemy types: basic, teleporter, spawned, spawner, behemoth")
                print("Symbols: P = you, e = enemy, ? = teleport target, # = wall, O = goal.")
                print("Colors: blue = you, pink = vroomvroom, red = basic, purple = teleporter,")
                print("green = spawned, orange = spawner, grey = wall, yellow = goal.")
                print("Abilities: vroomvroom gives your little legs two moves to use after pressing e, while confetti")
                print("gives a hug to nearby enemies and stuns them for 2 turns and takes 8 turns to recharge.")
                print("The red dots show where confetti will bonk. Stunned enemies turn white")
                print("and show the number of tiny stun turns they have left.")
                input("\nPress Enter to return to the menu...")
            elif choice == "basic":
                print("\nBasic: just a basic goober who moves toward you.")
                input("\nPress Enter to return to the menu...")
            elif choice == "teleporter":
                print("\nTeleporter: the fastest silly, and can appear beside you at any moment.")
                input("\nPress Enter to return to the menu...")
            elif choice == "spawned":
                print("\nSpawned: an even littler and even more innocent guy created by another silly guy.")
                input("\nPress Enter to return to the menu...")
            elif choice == "spawner":
                    print("\nSpawner: a slightly bigger guy who makes more little guys.")
                    input("\nPress Enter to return to the menu...")
            elif choice == "behemoth":
                print(
                    "\nBehemoth: the biggest goober of all, that arrives after "
                    f"{BEHEMOTH_SPAWN_TURN} turns and accelerates every turn."
                )
                input("\nPress Enter to return to the menu...")
            else:
                print("Please type \"start\", \"lore\", or an enemy type name.")
                print("Enemy types: basic, teleporter, spawned, spawner, behemoth")
                input("> ")

    def show_end(self):
        print("\n" * 2)
        print("===================================")
        if self.end_reason == "victory":
            print("       THE LITTLE GUY DID IT!")
            print("You reached the O. Yippee!")
        elif self.end_reason == "defeat":
            print("       THE LITTLE GUY GOT BONKED!")
            print("The maze wins this time. Tiny tragedy.")
        else:
            print("THE LITTLE GUY WANDERS OFF")
            print("A mysterious exit!")
        print("===================================")
        input("Press Enter to close...")

    def run(self):
        self.show_intro()
        self.setup()

        while self.running or self.round_won:
            if self.round_won:
                self.running = True
                self.start_next_round()
                continue
            self.render()

            player_input = input("> ").strip().lower()

            if player_input == "quit":
                self.end_reason = "quit"
                self.running = False
                continue

            if self.handle_player_input(player_input) is False:
                continue
            self.update()
            if self.running:
                print("Turn complete. The other goobers have taken their turn.")
                input("Press Enter to continue...")
        self.show_end()

if __name__ == "__main__":
    game = Game()
    game.run()

