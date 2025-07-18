"""
Robot class for pathfinding and movement
"""

import pygame
import time
import math
from config.constants import *
from config.settings import *
from entities.trail import TrailMarker
from .astar import a_star

class Robot:
    def __init__(self, start, targets, grid, draw_func, **params):
        self.grid = grid
        self.draw = draw_func
        self.start = start
        self.targets = sorted(targets, key=lambda t: t.target_priority, reverse=True) if targets else []
        self.current_target = None
        self.completed_targets = []
        self.path = []
        self.index = 0
        self.current = start
        self.trails = []
        self.last_move_time = time.time()
        self.paused = False
        self.pause_time = 0
        
        # Robot parameters
        self.battery = params.get('battery', DEFAULT_BATTERY)
        self.max_battery = self.battery
        self.sensor_range = params.get('sensor_range', DEFAULT_SENSOR_RANGE)
        self.speed_multiplier = params.get('speed', DEFAULT_ROBOT_SPEED)
        self.battery_drain_rate = params.get('drain_rate', BATTERY_DRAIN_RATE)
        
        # Performance tracking
        self.distance_traveled = 0
        self.steps_taken = 0
        self.replan_count = 0
        
        # Limited perception
        self.known_map = {}
        self.perception_area = []

    def select_next_target(self):
        """Select highest priority reachable target"""
        for target in self.targets:
            if target not in self.completed_targets:
                # Test if target is reachable
                if self.test_reachability(target):
                    self.current_target = target
                    return target
        return None

    def test_reachability(self, target):
        """Test if target is reachable (simplified check)"""
        # Simple test - could be enhanced with actual pathfinding
        return True

    def update_perception(self):
        """Update robot's knowledge of nearby cells"""
        current_pos = self.current.get_pos()
        self.perception_area = []
        
        for row in range(max(0, current_pos[0] - self.sensor_range),
                        min(len(self.grid), current_pos[0] + self.sensor_range + 1)):
            for col in range(max(0, current_pos[1] - self.sensor_range),
                           min(len(self.grid[0]), current_pos[1] + self.sensor_range + 1)):
                # Check if within sensor range (circular)
                distance = math.sqrt((row - current_pos[0])**2 + (col - current_pos[1])**2)
                if distance <= self.sensor_range:
                    spot = self.grid[row][col]
                    self.known_map[(row, col)] = {
                        'is_barrier': spot.is_barrier(),
                        'is_dynamic': spot.is_dynamic(),
                        'cost': spot.cost
                    }
                    self.perception_area.append(spot)

    def get_visible_cells(self):
        """Get cells within sensor range"""
        visible = []
        current_pos = self.current.get_pos()
        
        for row in self.grid:
            for spot in row:
                spot_pos = spot.get_pos()
                distance = math.sqrt((current_pos[0] - spot_pos[0])**2 + 
                                   (current_pos[1] - spot_pos[1])**2)
                if distance <= self.sensor_range:
                    visible.append(spot)
        return visible

    def recharge_battery(self, amount=None):
        """Recharge battery (for charging stations)"""
        if amount is None:
            self.battery = self.max_battery
        else:
            self.battery = min(self.max_battery, self.battery + amount)

    def plan_path(self):
        """Plan path to current target"""
        if not self.current_target:
            self.current_target = self.select_next_target()
        
        if not self.current_target:
            return False
            
        # Clear previous path markings
        for row in self.grid:
            for spot in row:
                if not spot.is_barrier() and not spot.is_start() and not spot.is_target_spot():
                    spot.reset()
                spot.previous = None
        
        self.path.clear()
        self.index = 0
        
        if a_star(self.draw, self.grid, self.start, self.current_target):
            self.extract_path()
            return True
        else:
            # Mark target as unreachable and try next
            self.completed_targets.append(self.current_target)
            self.current_target = None
            self.replan_count += 1
            return self.plan_path()

    def draw_fail_overlay(self):
        """Draw overlay when pathfinding fails"""
        from config.settings import WIDTH, ROWS
        for _ in range(3):
            for row in self.grid:
                for spot in row:
                    if not spot.is_barrier():
                        pass  # This will need to be handled in the calling code
            time.sleep(0.2)

    def extract_path(self):
        """Extract the path from the A* result"""
        current = self.current_target
        path = []
        while hasattr(current, 'previous') and current.previous and current != self.start:
            path.append(current)
            current = current.previous
        path.append(self.start)
        path.reverse()
        self.path = path

    def step(self):
        """Enhanced step with battery management and perception"""
        # Check battery
        if self.battery <= 0:
            return False  # Robot stopped
        
        # Update perception
        self.update_perception()
        
        current_time = time.time()

        # Handle pausing at traffic lights
        if self.paused:
            if current_time - self.pause_time >= 2:  # Pause for 2 seconds
                self.paused = False
            return False

        # Check if it's time to move based on simulation speed
        if current_time - self.last_move_time < (0.4 / DEFAULT_SPEED) / self.speed_multiplier:
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
                self.replan_count += 1
                self.plan_path()
                return False

            # Add to trail
            self.trails.append(TrailMarker(
                (self.current.x + self.current.width // 2,
                 self.current.y + self.current.width // 2),
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
            
            # Update performance metrics
            self.battery -= self.battery_drain_rate
            self.steps_taken += 1
            if self.index > 0:
                self.distance_traveled += 1
                
            return True
        return False

    def reached_goal(self):
        """Check if robot reached current target"""
        if self.current == self.current_target:
            self.completed_targets.append(self.current_target)
            self.current_target = None
            # Check if all targets completed
            return len(self.completed_targets) == len(self.targets)
        return False

    def get_center(self):
        """Get the center position of the robot"""
        return (self.current.x + self.current.width // 2,
                self.current.y + self.current.width // 2)