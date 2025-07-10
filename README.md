# Robot Grid Simulator

A simple grid-based simulator for robot pathfinding in a dynamic, urban-style environment.

## Features

- Realistic map with buildings, traffic lights, and dynamic obstacles
- Smart robot that navigates using path planning and obstacle avoidance
- Traffic light logic with red/yellow/green states
- Visual trail effect for robot movement
- Keyboard controls to set start/end, barriers, and run simulation
- Support for saving/loading maps

## Controls

- **Left Click**: Place Start / End / Barrier / Traffic Light (when holding `T`)
- **Right Click**: Remove cell
- **Space**: Start simulation
- **C**: Clear grid
- **R**: Reset simulation
- **S**: Save map
- **L**: Load map
- **I**: Import image map (future)
- **1–4**: Change robot speed
- **T**: Toggle traffic light tool

## Requirements

- Python 3.x
- pygame
- pillow

Install with:
pip install -r requirements.txt

## How to Run

Run the simulator using: python main.py

