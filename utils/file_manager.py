"""
File management utilities for saving/loading maps and obstacles
"""

import json
import os
from core.spot import Spot
from config.constants import *

def save_map(grid, start, targets, map_name):
    """Save complete map layout including start, targets, and obstacles"""
    map_data = {
        'obstacles': [],
        'traffic_lights': [],
        'start': None,
        'targets': []
    }
    
    # Save obstacles and traffic lights
    for row in grid:
        for spot in row:
            if spot.is_barrier():
                map_data['obstacles'].append([spot.row, spot.col])
            elif spot.is_traffic_stop:
                map_data['traffic_lights'].append([spot.row, spot.col])
    
    # Save start position
    if start:
        map_data['start'] = [start.row, start.col]
    
    # Save targets with priorities
    for target in targets:
        map_data['targets'].append({
            'row': target.row,
            'col': target.col,
            'priority': target.target_priority
        })
    
    # Save to file
    filename = f"maps/{map_name}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(map_data, f, indent=2)
        print(f"Map saved as {filename}")
    except Exception as e:
        print(f"Error saving map: {e}")

def load_map(grid, map_name):
    """Load complete map layout"""
    filename = f"maps/{map_name}.json"
    
    if not os.path.exists(filename):
        print(f"Map file {filename} not found")
        return None
    
    try:
        with open(filename, 'r') as f:
            map_data = json.load(f)
        
        # Clear existing grid
        for row in grid:
            for spot in row:
                spot.reset()
                spot.is_traffic_stop = False
                spot.is_target = False
        
        # Load obstacles
        for pos in map_data.get('obstacles', []):
            row, col = pos
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                grid[row][col].make_barrier()
        
        # Load traffic lights
        for pos in map_data.get('traffic_lights', []):
            row, col = pos
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                grid[row][col].make_traffic_light()
        
        # Load start
        start = None
        if map_data.get('start'):
            row, col = map_data['start']
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                start = grid[row][col]
                start.make_start()
        
        # Load targets
        targets = []
        for target_data in map_data.get('targets', []):
            row, col = target_data['row'], target_data['col']
            priority = target_data.get('priority', 1)
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                target = grid[row][col]
                target.make_target(priority)
                targets.append(target)
        
        print(f"Map {map_name} loaded successfully")
        return grid, start, targets
        
    except Exception as e:
        print(f"Error loading map: {e}")
        return None

def save_obstacles(grid):
    """Save only obstacles to default file"""
    obstacles = []
    for row in grid:
        for spot in row:
            if spot.is_barrier():
                obstacles.append([spot.row, spot.col])
    
    filename = "maps/obstacles.json"
    try:
        with open(filename, 'w') as f:
            json.dump(obstacles, f, indent=2)
        print(f"Obstacles saved to {filename}")
    except Exception as e:
        print(f"Error saving obstacles: {e}")

def load_obstacles(grid):
    """Load obstacles from default file"""
    filename = "maps/obstacles.json"
    
    if not os.path.exists(filename):
        print(f"Obstacles file {filename} not found")
        return
    
    try:
        with open(filename, 'r') as f:
            obstacles = json.load(f)
        
        # Clear existing barriers
        for row in grid:
            for spot in row:
                if spot.is_barrier():
                    spot.reset()
        
        # Load obstacles
        for pos in obstacles:
            row, col = pos
            if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                grid[row][col].make_barrier()
        
        print(f"Obstacles loaded from {filename}")
        
    except Exception as e:
        print(f"Error loading obstacles: {e}")