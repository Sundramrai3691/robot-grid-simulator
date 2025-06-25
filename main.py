# A* Navigation Simulator - Ultimate Edition
# 🚀 Real-Time Features | 🗺️ Image-Based Mapping | 🚦 Smart Traffic | 🏁 Robot Trails

import pygame
import random
import threading
import time
import json
import os
import math
from queue import PriorityQueue
from PIL import Image

# -------------------- Color Constants --------------------
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)
RED = (231, 76, 60)
GREEN = (46, 204, 113)
PURPLE = (155, 89, 182)
GREY = (180, 180, 180)
BLUE = (52, 152, 219)
DARK_GREEN = (34, 139, 34)
YELLOW = (255, 255, 0)

# -------------------- Visualization Parameters --------------------
TRAIL_LENGTH = 15
TRAIL_ALPHA = 150
FADING_SPEED = 5
DEFAULT_SPEED = 1
TRAFFIC_LIGHT_CYCLE = 5  # seconds

# -------------------- Spot (Node) --------------------
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.original_color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.previous = None
        self.cost = 1
        self.is_traffic_stop = False
        self.light_state = "green"  # green, yellow, red

    def get_pos(self): return self.row, self.col
    def is_closed(self): return self.color == RED
    def is_open(self): return self.color == GREEN
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == ORANGE
    def is_end(self): return self.color == TURQUOISE
    def is_dynamic(self): return self.color == BLUE

    def reset(self):
        self.color = self.original_color
        self.cost = 1
        self.previous = None

    def make_start(self): 
        self.color = ORANGE
        self.original_color = ORANGE
    
    def make_closed(self): self.color = RED
    def make_open(self): self.color = GREEN
    def make_barrier(self): 
        self.color = BLACK
        self.original_color = BLACK
    
    def make_end(self): 
        self.color = TURQUOISE
        self.original_color = TURQUOISE
    
    def make_path(self): self.color = PURPLE
    def make_dynamic(self): self.color = BLUE
    def make_traffic_light(self):
        self.is_traffic_stop = True
        self.update_traffic_light()
    
    def update_traffic_light(self):
        current_time = time.time()
        cycle_pos = (current_time % TRAFFIC_LIGHT_CYCLE) / TRAFFIC_LIGHT_CYCLE
        
        if cycle_pos < 0.7:
            self.light_state = "green"
            self.color = GREEN
        elif cycle_pos < 0.8:
            self.light_state = "yellow"
            self.color = YELLOW
        else:
            self.light_state = "red"
            self.color = RED

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        
        # Draw traffic light indicator if applicable
        if self.is_traffic_stop:
            radius = self.width // 4
            offset = self.width // 4
            if self.light_state == "green":
                pygame.draw.circle(win, GREEN, 
                                 (self.x + offset, self.y + offset), radius)
            elif self.light_state == "yellow":
                pygame.draw.circle(win, YELLOW, 
                                 (self.x + self.width//2, self.y + offset), radius)
            else:
                pygame.draw.circle(win, RED, 
                                 (self.x + self.width - offset, self.y + offset), radius)

    def update_neighbors(self, grid):
        self.neighbors = []
        dirs = [(0,1),(1,0),(-1,0),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
        for d in dirs:
            r, c = self.row + d[0], self.col + d[1]
            if 0 <= r < self.total_rows and 0 <= c < self.total_rows:
                neighbor = grid[r][c]
                
                # Check if neighbor is a red traffic light
                if neighbor.is_traffic_stop and neighbor.light_state == "red":
                    continue  # Skip this neighbor if it's a red light
                    
                if not neighbor.is_barrier():
                    self.neighbors.append(neighbor)

# -------------------- Trail Effect --------------------
class TrailMarker:
    def __init__(self, pos, color, width):
        self.pos = pos
        self.color = color
        self.width = width
        self.alpha = TRAIL_ALPHA
        self.lifetime = TRAIL_LENGTH
        
    def update(self):
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - FADING_SPEED)
        self.color = (*self.color[:3], self.alpha)
        
    def draw(self, win):
        if self.alpha > 0:
            s = pygame.Surface((self.width, self.width), pygame.SRCALPHA)
            pygame.draw.rect(s, self.color, (0, 0, self.width, self.width))
            win.blit(s, (self.pos[0], self.pos[1]))

# -------------------- Grid Utilities --------------------
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            grid[i].append(Spot(i, j, gap, rows))
    return grid

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    return y // gap, x // gap

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width, trails=[], robot_pos=None):
    win.fill(WHITE)
    
    # Draw all cells
    for row in grid:
        for spot in row:
            spot.draw(win)
    
    # Draw trails behind everything
    for trail in trails:
        trail.draw(win)
    
    # Draw robot with direction indicator
    if robot_pos:
        pos_x, pos_y = robot_pos
        radius = grid[0][0].width // 3
        pygame.draw.circle(win, ORANGE, (pos_x, pos_y), radius)
        
        # Draw direction arrow
        if len(trails) > 1:
            prev_pos = trails[-2].pos
            angle = math.atan2(pos_y - prev_pos[1], pos_x - prev_pos[0])
            arrow_length = radius * 1.5
            end_x = pos_x + arrow_length * math.cos(angle)
            end_y = pos_y + arrow_length * math.sin(angle)
            pygame.draw.line(win, BLACK, (pos_x, pos_y), (end_x, end_y), 2)
    
    draw_grid(win, rows, width)
    draw_ui(win)
    pygame.display.update()

def draw_ui(win):
    font = pygame.font.SysFont('Arial', 20)
    instructions = [
        "Controls:",
        "Left Click: Set Start/End/Barrier/Traffic Light (hold T)",
        "Right Click: Remove Cell",
        "Space: Start Simulation",
        "C: Clear Grid", "R: Reset",
        "S: Save Map", "L: Load Map",
        "I: Import Image Map",
        "1-4: Change Speed (Current: {})".format(sim_speed),
        "T: Toggle Traffic Light Tool"
    ]
    for i, text in enumerate(instructions):
        label = font.render(text, True, BLACK)
        win.blit(label, (10, 10 + i * 25))

# -------------------- A* Algorithm --------------------
def heuristic(a, b):
    x1, y1 = a.get_pos()
    x2, y2 = b.get_pos()
    return math.hypot(x1 - x2, y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def a_star(draw_func, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    f_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score[start] = heuristic(start, end)
    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw_func)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            dx = abs(current.row - neighbor.row)
            dy = abs(current.col - neighbor.col)
            step_cost = 1.41 if dx + dy == 2 else 1
            temp_g = g_score[current] + step_cost * neighbor.cost

            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score[neighbor] = temp_g + heuristic(neighbor, end)
                neighbor.previous = current

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

        draw_func()
        if current != start:
            current.make_closed()
    
    return False

# -------------------- Dynamic Obstacles --------------------
class DynamicObstacle:
    def __init__(self, path, name="obstacle", speed=1):
        self.path = path
        self.index = 0
        self.name = name
        self.current = None
        self.speed = speed
        self.cycle_time = time.time()

    def move(self):
        current_time = time.time()
        if current_time - self.cycle_time >= 0.4 / self.speed:
            self.cycle_time = current_time
            if self.current:
                self.current.reset()
            self.current = self.path[self.index]
            self.current.make_dynamic()
            self.index = (self.index + 1) % len(self.path)

# -------------------- Robot --------------------
class Robot:
    def __init__(self, start, end, grid, draw_func):
        self.grid = grid
        self.draw = draw_func
        self.start = start
        self.end = end
        self.path = []
        self.index = 0
        self.current = start
        self.trails = []
        self.last_move_time = time.time()
        self.paused = False
        self.pause_time = 0

    def plan_path(self):
        for row in self.grid:
            for spot in row:
                if not spot.is_barrier() and not spot.is_start() and not spot.is_end():
                    spot.reset()
                spot.previous = None
        self.path.clear()
        self.index = 0
        if a_star(self.draw, self.grid, self.start, self.end):
            self.extract_path()
        else:
            self.draw_fail_overlay()

    def draw_fail_overlay(self):
        for _ in range(3):
            for row in self.grid:
                for spot in row:
                    if not spot.is_barrier():
                        pygame.draw.rect(WIN, RED, (spot.x, spot.y, spot.width, spot.width), 1)
            pygame.display.update()
            time.sleep(0.2)
            draw(WIN, self.grid, ROWS, WIDTH, self.trails, self.get_center())

    def extract_path(self):
        current = self.end
        path = []
        while hasattr(current, 'previous') and current.previous and current != self.start:
            path.append(current)
            current = current.previous
        path.append(self.start)
        path.reverse()
        self.path = path

    def step(self):
        current_time = time.time()
        
        # Handle pausing at traffic lights
        if self.paused:
            if current_time - self.pause_time >= 2:  # Pause for 2 seconds
                self.paused = False
            return False
            
        # Check if it's time to move based on simulation speed
        if current_time - self.last_move_time < 0.4 / DEFAULT_SPEED:
            return True
        
        self.last_move_time = current_time
        
        if self.index < len(self.path):
            next_spot = self.path[self.index]
            
            # Check for traffic lights
            if next_spot.is_traffic_stop and next_spot.light_state != "green":
                self.paused = True
                self.pause_time = current_time
                return False
                
            if next_spot.is_barrier() or next_spot.is_dynamic():
                self.plan_path()
                return False
                
            # Add to trail
            self.trails.append(TrailMarker(
                (self.current.x + self.current.width//2, 
                 self.current.y + self.current.width//2),
                (*PURPLE, TRAIL_ALPHA),
                self.current.width
            ))
            
            # Update trails
            for trail in self.trails[:]:
                trail.update()
                if trail.lifetime <= 0:
                    self.trails.remove(trail)
            
            self.current.reset()
            self.current = next_spot
            self.current.make_start()
            self.index += 1
            return True
        return False

    def reached_goal(self): 
        return self.current == self.end
        
    def get_center(self):
        return (self.current.x + self.current.width//2, 
                self.current.y + self.current.width//2)

# -------------------- Main Program --------------------
WIDTH = 800
ROWS = 50
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Navigation Simulator - Ultimate Edition")

sim_speed = DEFAULT_SPEED
traffic_light_tool = False

def main(win, width):
    global sim_speed, traffic_light_tool
    
    pygame.font.init()
    grid = make_grid(ROWS, width)
    start = end = robot = None
    run = True
    clock = pygame.time.Clock()
    sim_running = False

    while run:
        clock.tick(30)
        
        # Update traffic lights
        for row in grid:
            for spot in row:
                if spot.is_traffic_stop:
                    spot.update_traffic_light()
        
        draw(win, grid, ROWS, width, 
            robot.trails if robot else [], 
            robot.get_center() if robot else None)
            
        if sim_running and robot:
            if not robot.reached_goal():
                robot.step()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()
                    elif not end and spot != start:
                        end = spot
                        end.make_end()
                    elif traffic_light_tool:
                        spot.make_traffic_light()
                    elif spot != start and spot != end:
                        spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                row, col = get_clicked_pos(pygame.mouse.get_pos(), ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    spot = grid[row][col]
                    if spot == start: 
                        start = None
                    elif spot == end: 
                        end = None
                    spot.reset()
                    spot.is_traffic_stop = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    robot = Robot(start, end, grid, lambda: draw(win, grid, ROWS, width, robot.trails, robot.get_center()))
                    robot.plan_path()
                    sim_running = True
                if event.key == pygame.K_c:
                    grid = make_grid(ROWS, width)
                    start = end = robot = None
                    sim_running = False
                if event.key == pygame.K_r:  # Reset simulation
                    grid = make_grid(ROWS, width)
                    start = end = robot = None
                    sim_running = False
                if event.key == pygame.K_s:  # Save obstacles
                    with open("obstacles.json", 'w') as f:
                        json.dump([[spot.get_pos() for spot in row if spot.is_barrier()] for row in grid], f)
                if event.key == pygame.K_l:  # Load obstacles
                    if os.path.exists("obstacles.json"):
                        with open("obstacles.json", 'r') as f:
                            obstacle_positions = json.load(f)
                            for positions in obstacle_positions:
                                for row, col in positions:
                                    grid[row][col].make_barrier()
                    else:
                        print("No saved obstacles found.")
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    sim_speed = [0.1, 0.3, 0.5, 1.0][event.key - pygame.K_1]

                if event.key == pygame.K_t:  # Toggle traffic light tool
                    traffic_light_tool = not traffic_light_tool

    pygame.quit()

if __name__ == '__main__':
    main(WIN, WIDTH)

