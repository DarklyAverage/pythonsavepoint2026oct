#continuing the one from jame gam in savepoint becaue i didnt get all the mechanics i wanted
#what to add:
#interactable objects and such and items
#^ still didn't get to do this but whatevs


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
        Enemy(x=28, y=5, role="spawner", spawn_cooldown=5)
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
    if enemy.role != "spawner" or not enemy.alive or enemy.stunned:
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
        elif enemy.role == "spawner":
            spawnenemy(enemy, game_map, enemies, player)
        elif enemy.role == "spawned":
            move_slow_enemy(enemy, player, game_map, enemies)

def draw_enemies(screen, enemies):
    for enemy in enemies:
        if not enemy.alive:
            continue


        if enemy.role == "teleporter":
            screen[enemy.y][enemy.x] = "T"
        elif enemy.role == "spawner":
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
confetti_cannon_AREA_COLOR = color(HEX_COLORS["red"])
STUNNED_COLOR = color(HEX_COLORS["white"])

CHARACTER_LOADOUTS = {
    "zoomie": {
        "display_name": "Zoomie",
        "weapon": "Twin sticks",
        "max_hp": 2,
        "damage": 4,
        "ability": "zoomies",
        "description": "Fast and fragile. Zoomies lets you dash two squares.",
    },
    #naming stuff to fit iwth this theme is annoyign
    "bonker": {
        "display_name": "Bonker",
        "weapon": "Heavy gloves",
        "max_hp": 8,
        "damage": 2,
        "ability": "confetti cannon",
        "description": "Tough and powerful. The confetti cannon stuns nearby enemies.",
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

DIRECTIONS = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
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
    ability: str = "zoomies"

    playerequippedclass: Optional[str]= None

    last_move: tuple = (0,0)

    move_history: list[tuple[int,int]] = field(default_factory=list)
    extra_moves: int=0
    last_message: str = ""

    zoomies_available: bool = False
    zoomies_cooldown: int = 0
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

    def use_zoomies(self,game_map, enemies=None):
        if not self.zoomies_available:
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
            self.zoomies_available = False
            self.zoomies_cooldown = 4
            self.dash_color_turns = 2
            self.last_message = f"VROOM! Two squares in one turn! ({moves}/2)"
        return moves > 0

    confetti_cannon_available: bool = True
    confetti_cannon_cooldown: int = 0
    confetti_cannon_range_visible: bool = False
    second_wind_available: bool = False

    def use_confetti(self, game_map, enemies=None):
        if not self.confetti_cannon_available:
            self.last_message = "The confetti cannon is recharging."
            return False
        if not enemies:
            self.last_message = "Confetti cannon failed: no enemy nearby."
            return False

        stunned_count = 0  
        for enemy in enemies:
            if not enemy.alive:
                continue

            affected_cells = (
                worm_cells(enemy)
                if enemy.role == "worm"
                else {(enemy.x, enemy.y)}
            )
            if any(
                abs(x - self.x) <= 1 and abs(y - self.y) <= 1
                for x, y in affected_cells
            ):
                enemy.stunned = True
                enemy.stun_timer = 3
                stunned_count += 1

        if stunned_count == 0:
            self.last_message = "Confetti cannon failed: no enemy nearby."
            return False

        self.confetti_cannon_available = False
        self.confetti_cannon_cooldown = 8
        self.confetti_cannon_range_visible = True
        enemy_word = "enemy" if stunned_count == 1 else "enemies"
        self.last_message = f"Confetti cannon worked! Stunned {stunned_count} {enemy_word}."
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
    hp: int = 0
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
                "behemoth": float("inf"),
                "worm": 3,
            }.get(self.role, 1)

    def take_push_damage(self, damage=1):
        if self.role == "behemoth":
            return False
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
    if enemy.role != "spawner" or not enemy.alive or enemy.stunned:
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
    if enemy.role != "spawned" or not enemy.alive or enemy.stunned:
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
    def __init__(self, width=WIDTH, height=HEIGHT, theme_index=0):
        self.width = width
        self.height = height
        self.theme_index = theme_index % 4
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
        if self.theme_index == 0:
            for x in range(self.width // 5, self.width * 2 // 5):
                self.add_wall(x, self.height // 3)
            for x in range(self.width * 3 // 5, self.width * 4 // 5):
                self.add_wall(x, self.height * 2 // 3)
        elif self.theme_index == 1:
            for x in range(self.width // 4, self.width * 3 // 4, 4):
                for y in range(2, self.height - 2):
                    if y != self.height // 2:
                        self.add_wall(x, y)
        elif self.theme_index == 2:
            left = self.width // 3
            right = self.width * 2 // 3
            top = max(2, self.height // 3 - 1)
            bottom = min(self.height - 2, self.height * 2 // 3 + 1)
            for x in range(left, right + 1):
                self.add_wall(x, top)
                self.add_wall(x, bottom)
            for y in range(top, bottom + 1):
                self.add_wall(left, y)
                self.add_wall(right, y)
            self.walls.discard((left, top + 1))
            self.walls.discard((right, bottom - 1))
        else:
            for x, y in (
                (self.width // 4, self.height // 3),
                (self.width // 2, self.height // 2),
                (self.width * 3 // 4, self.height // 3),
            ):
                self.add_wall(x, y)
                self.add_wall(x + 1, y)
                self.add_wall(x, y + 1)
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
                elif enemy.role == "behemoth":
                    player.last_message = (
                        "Wall slam! The behemoth is immune to damage, but it is stunned."
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
            elif enemy.role == "behemoth":
                player.last_message = (
                    "Bonk! You pushed the behemoth, but it didn't take any damage."
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
    if start == target:
        return None
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

    if ability_name in ("zoomies", "dash") and player.ability == "zoomies":
        return player.use_zoomies(game_map, enemies)
    if ability_name in ("confetti", "confetti cannon") and player.ability == "confetti cannon":
        return player.use_confetti(game_map, enemies)
    if ability_name in ("second wind", "secondwind") and player.ability == "second wind":
        return player.use_second_wind()

    player.last_message = "That ability does not belong to this class."

    return False


def is_adjacent(first, second):
    return abs(first.x - second.x) + abs(first.y - second.y) == 1


def check_player_enemy_collision(player,enemies):
    for enemy in enemies:
        if not enemy.alive or enemy.stunned or enemy.burrowed:
            continue

        if enemy.role == "teleporter":
            touching = max(
                abs(enemy.x - player.x),
                abs(enemy.y - player.y),
            ) == 1
        elif enemy.role == "worm":
            touching = any(
                abs(x - player.x) + abs(y - player.y) == 1
                for x, y in worm_cells(enemy)
            )
        else:
            touching = is_adjacent(enemy, player)

        if touching:
            enemy.attack(player)
   
def check_goal_reached(player,game_map):
    if game_map.goal is None:
        return False
    return (player.x,player.y) == game_map.goal


class Game:
    def __init__(self):
        self.game_map = GameMap()

        self.player = Player(x=1, y=1, playerequippedclass=None)
        self.character_key = "zoomie"
        self.upgrade_level = 0

        self.enemies = []
        self.round_number = 1
        self.round_won = False
        self.running = True
        self.upgrade_message = ""

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
            choice = input("Class (zoomie/bonker/medic): ").strip().lower()
            if choice in CHARACTER_LOADOUTS:
                self.character_key = choice
                return
            print("Please choose zoomie, bonker, or medic.")

    def setup_round(self, round_number):
        self.round_number = round_number
        width = WIDTH + (round_number - 1) * 4
        height = HEIGHT + (round_number - 1) * 2
        self.game_map = GameMap(width, height, round_number - 1)
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
        self.player.zoomies_available = loadout["ability"] == "zoomies"
        self.player.confetti_cannon_available = loadout["ability"] == "confetti cannon"
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
        max_hp = self.player.max_hp
        damage = self.player.damage
        self.setup_round(self.round_number + 1)
        self.player.max_hp = max_hp
        self.player.damage = damage
        self.apply_round_upgrade()
        self.player.hp = self.player.max_hp
        print(
            f"\nRound {self.round_number}! "
            "The maze is shifting and more little guys are waiting."
        )
        print(self.upgrade_message)
        print(self.filler_text())
        input("Press Enter to continue...")

    def apply_round_upgrade(self):
        print("\nChoose your upgrade:")
        print("1. Extra health (+2 maximum HP)")
        print("2. Bigger bonk (+1 damage)")
        print("3. Gamble with both (+2 maximum HP, +1 damage, and one extra enemy)")
        while True:
            choice = input("Upgrade (1/2/3): ").strip()
            if choice in ("1", "2", "3"):
                break
            print("Please choose 1, 2, or 3.")

        self.upgrade_level += 1
        if choice in ("1", "3"):
            self.player.max_hp += 2
        if choice in ("2", "3"):
            self.player.damage += 1
        if choice == "3":
            self.add_extra_enemy()
        self.player.hp = self.player.max_hp
        self.upgrade_message = (
            "Upgrade applied! Your little guy is stronger and ready for more nonsense."
        )
    def add_extra_enemy(self):
        candidates = [
            (self.game_map.width // 2, self.game_map.height // 2),
            (self.game_map.width - 4, 2),
            (4, self.game_map.height // 2),
            (self.game_map.width // 2, self.game_map.height - 3),
        ]
        occupied = {
            (enemy.x, enemy.y)
            for enemy in self.enemies
            if enemy.alive
        }
        position = next(
            (
                candidate
                for candidate in candidates
                if self.game_map.iswalkable(*candidate)
                and candidate != (self.player.x, self.player.y)
                and candidate != self.game_map.goal
                and candidate not in occupied
            ),
            None,
        )
        if position is not None:
            self.enemies.append(Enemy(x=position[0], y=position[1], role="basic"))
    def filler_text(self):
        messages = (
            "Fun Tzu says: the supreme art of war is winning with excellent snacks.",
            "Keep your friends close and your goobers slightly farther away.",
            "A journey of a thousand tiles begins with one very small step.",
            "Do not worry about the maze; worry about becoming maze-proof.",
            "Lebron James is the goat.",
            "Hi! I'm Finley, the creator of the game and these filler texts.",
        )
        return messages[(self.round_number - 2) % len(messages)]
    def handle_player_input(self, key):
        if key in DIRECTIONS:
            if not move_player(self.player, key, self.game_map, self.enemies):
                print(self.player.last_message)
                input("Press Enter to continue...")
                return False
            else:
                print(self.player.last_message)
                input("Press Enter to continue...")
            return True
        if key in ("skip", "wait", "."):
            self.player.last_message = "You wait a turn. The other goobers take theirs."
            print(self.player.last_message)
            return True
        if key in ("e", "zoomies"):
            if self.player.ability != "zoomies":
                print("That ability does not belong to this class.")
                input("Press Enter to continue...")
                return False
            if not use_player_ability(self.player,"zoomies",self.game_map,self.enemies):
                print(self.player.last_message or "Zoomies is unavailable. Move first, then try again.")
                return False
            else:
                print(self.player.last_message)
            input("Press Enter to continue...")
            return True
        if key in ("c", "confetti", "confetti cannon"):
            if self.player.ability != "confetti cannon":
                print("That ability does not belong to this class.")
                input("Press Enter to continue...")
                return False
            self.player.confetti_cannon_range_visible = True
            self.render()
            confirmation = input(
                "Press Enter to throw confetti, or type q to cancel..."
            ).strip().lower()
            if confirmation in ("q", "cancel"):
                self.player.confetti_cannon_range_visible = False
                print("Confetti cannon cancelled.")
                return False
            if not use_player_ability(self.player, "confetti", self.game_map, self.enemies):
                print(self.player.last_message or "Confetti cannon is unavailable. Wait for it to recharge.")
                return False
            else:
                print(self.player.last_message)
                input("Press Enter to continue...")
                return True

        if key in ("h", "heal", "second wind"):
            if self.player.ability != "second wind":
                print("That ability does not belong to this class.")
                input("Press Enter to continue...")
                return False
            if not use_player_ability(self.player, "second wind", self.game_map, self.enemies):
                print(self.player.last_message)
                input("Press Enter to continue...")
                return False
            print(self.player.last_message)
            return True

        print("That is not a valid action. Use w/a/s/d, e (zoomies), c (confetti cannon), h (second wind), skip, or quit.")
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
            if is_adjacent(enemy, self.player) or worm_attacking:
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
        if self.turn_number >= BEHEMOTH_SPAWN_TURN and not self.behemoth_spawned:
            self.spawn_behemoth()
        if self.player.zoomies_cooldown > 0:
            self.player.zoomies_cooldown -= 1
            if self.player.zoomies_cooldown == 0:
                self.player.zoomies_available = True
                self.player.last_message = "Zoomies is recharged! The little legs are ready to get zoomy again."

        if self.player.confetti_cannon_cooldown > 0:
            self.player.confetti_cannon_cooldown -= 1
        if self.player.confetti_cannon_cooldown == 0:
            self.player.confetti_cannon_available = True
            self.player.last_message = "Confetti cannon is ready."

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
            print(f"You reached the goal in round {self.round_number}!")
            input("Press Enter to continue...")
            self.round_won = True
            self.running = False

    def render(self):
        print("\n" * 2)
        print(f"Round {self.round_number}/{TOTAL_ROUNDS}")
        controls = "wait | quit"
        if self.player.ability == "zoomies":
            controls = "w/a/s/d | e (zoomies) | " + controls
        elif self.player.ability == "confetti cannon":
            controls = "w/a/s/d | c (confetti cannon) | " + controls
        elif self.player.ability == "second wind":
            controls = "w/a/s/d | h (second wind) | " + controls
        print(f"Character: {self.player.character_name} | Weapon: {self.player.weapon}")
        print(f"Controls: {controls}")
        print(f"HP: {self.player.hp}/{self.player.max_hp} | Damage: {self.player.damage}")
        if self.player.ability == "zoomies":
            zoomies_status = (
                "ready"
                if self.player.zoomies_available
                else f"recharging ({self.player.zoomies_cooldown} turns)"
            )
            print(f"Zoomies: {zoomies_status}")
        elif self.player.ability == "confetti cannon":
            confetti_cannon_status = (
                "ready"
                if self.player.confetti_cannon_available
                else f"recharging ({self.player.confetti_cannon_cooldown} turns)"
            )
            print(f"Confetti cannon: {confetti_cannon_status}")
        if self.behemoth_spawned:
            behemoth_status = "ACTIVE"
        else:
            turns_left = max(0, BEHEMOTH_SPAWN_TURN - self.turn_number)
            behemoth_status = f"in {turns_left} turns"
        print(f"Behemoth: {behemoth_status}")
        enemies_by_position = {
            (x, y): enemy
            for enemy in self.enemies
            if enemy.alive and not enemy.burrowed
            for x, y in (
                worm_cells(enemy) if enemy.role == "worm" else {(enemy.x, enemy.y)}
            )        }
        confetti_cannon_area = {
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
                elif self.player.confetti_cannon_range_visible and position in confetti_cannon_area:
                    row.append(f"{confetti_cannon_AREA_COLOR}.{RESET}")
                elif position in self.game_map.walls:
                    row.append(f"{WALL_COLOR}#{RESET}")
                elif position == self.game_map.goal:
                    row.append(f"{GOAL_COLOR}O{RESET}")
                else:
                    row.append(".")

            print("".join(row))

        self.player.confetti_cannon_range_visible = False

    def show_intro(self):
        while True:
            print("\n" * 2)
            print("===================================")
            print("              GOOBERS")
            print("===================================")
            print("Type \"start\" to play, or type \"lore\" to learn about cool story features.")
            print("Alternatively, enter an enemy type to learn about it.")
            print("Enemy types: basic, teleporter, spawned, spawner, behemoth, worm")
            choice = input("> ").strip().lower()

            if choice == "start":
                return
            if choice == "lore":
                print("\nYou are just a little guy in a \"maze\" full of other little guys.")
                print("Armed with nothing but party decorations and your own abilities you have to get to the exit.")
                print("Reach the O, avoid the other little guys, or evilly push them out of your way.")
                print("Input an enemy type name for more information on a specific one.")
                print("Enemy types: basic, teleporter, spawned, spawner, behemoth, worm")
                print("Symbols: P = you, e = enemy, ? = teleport target, # = wall, O = goal.")
                print("Colors: blue = you, pink = zoomies, red = basic, purple = teleporter,")
                print("green = spawned, orange = spawner, dark red = behemoth, magenta = worm,")
                print("grey = wall, yellow = goal.")
                print("Abilities: zoomies gives your little legs two moves after pressing e, while confetti cannon")
                print("stuns nearby enemies for 2 turns, and takes 8 turns to recharge.")
                print("The red dots show where confetti cannon will hit. Stunned enemies turn white")
                print("and show the number of stun turns they have left.")
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
            elif choice == "worm":
                print("\nWorm: a long, burrowing goober that can appear beside you.")
                input("\nPress Enter to return to the menu...")
            else:
                print("Please type \"start\", \"lore\", or an enemy type name.")
                print("Enemy types: basic, teleporter, spawned, spawner, behemoth, worm")
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

