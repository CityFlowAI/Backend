import time
import random
import threading

class Lane:
    def __init__(self, name):
        self.name = name
        self.vehicle_count = 0
        self.waiting_time = 0
        self.total_passed = 0
        self.is_emergency = False

    def update(self, is_green):
        # Presentation Speed: 1 car every 2-3 seconds
        if random.random() < 0.4:
            self.vehicle_count += 1

        if is_green:
            # Presentation Speed: 1 car departs every second
            passed = min(self.vehicle_count, 1)
            self.vehicle_count -= passed
            self.total_passed += passed
            if self.vehicle_count == 0:
                self.waiting_time = 0
            else:
                self.waiting_time += 1
        else:
            # Waiting time increases if red and there are vehicles
            if self.vehicle_count > 0:
                self.waiting_time += 1

class SimulationEngine:
    def __init__(self):
        self.lanes = {
            "North": Lane("North"),
            "South": Lane("South"),
            "East": Lane("East"),
            "West": Lane("West")
        }
        self.phases = [
            ("North", "South"), # Phase 0: North and South are green
            ("East", "West")    # Phase 1: East and West are green
        ]
        self.current_phase_idx = 0
        self.phase_timer = 0
        self.phase_duration = 100 # Default ticks
        
        self.is_running = False
        self.thread = None
        self.ai_enabled = True
        self.emergency_mode = False
        self.emergency_lane = None
        
        self.optimization_score = 85
        self.history = []

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False

    def trigger_emergency(self, lane_name):
        self.emergency_mode = True
        self.emergency_lane = lane_name
        self.lanes[lane_name].is_emergency = True
        # Immediately switch phase to favor the emergency lane
        if lane_name in ["North", "South"]:
            self.current_phase_idx = 0
        else:
            self.current_phase_idx = 1
        self.phase_timer = 0 # reset timer

    def clear_emergency(self):
        self.emergency_mode = False
        self.emergency_lane = None
        for lane in self.lanes.values():
            lane.is_emergency = False

    def _run_loop(self):
        tick = 0
        while self.is_running:
            self.step(tick)
            time.sleep(1.0) # 1 tick = 1 real second
            tick += 1

    def step(self, tick):
        from ai_engine import optimize_signals, predict_congestion
        
        # Advance phase timer
        if not self.emergency_mode:
            self.phase_timer += 1
            
            if self.ai_enabled:
                # Ask AI for the best phase continuously
                skip_phase, best_phase_idx, new_duration, new_score = optimize_signals(self.lanes, self.phases, self.current_phase_idx, self.phase_duration)
                
                # Update duration/score only periodically so the UI doesn't flicker
                if tick % 5 == 0:
                    self.phase_duration = new_duration
                    self.optimization_score = new_score
                
                if self.phase_timer >= self.phase_duration or skip_phase:
                    self.phase_timer = 0
                    self.current_phase_idx = best_phase_idx
                    self.phase_duration = new_duration
            else:
                # Basic fixed timer mode
                if self.phase_timer >= self.phase_duration:
                    self.phase_timer = 0
                    self.current_phase_idx = (self.current_phase_idx + 1) % len(self.phases)

        active_lanes = self.phases[self.current_phase_idx]
        
        for name, lane in self.lanes.items():
            is_green = (name in active_lanes)
            lane.update(is_green)
            
        # Analytics capture (every 5 seconds)
        if tick % 5 == 0:
            total_vehicles = sum(l.vehicle_count for l in self.lanes.values())
            congestion_risk = predict_congestion(total_vehicles)
            self.history.append({
                "time": tick,
                "total_vehicles": total_vehicles,
                "congestion_risk": congestion_risk,
                "optimization_score": self.optimization_score
            })
            # Keep history bounded
            if len(self.history) > 50:
                self.history.pop(0)

    def get_state(self):
        active_lanes = self.phases[self.current_phase_idx]
        return {
            "ai_enabled": self.ai_enabled,
            "emergency_mode": self.emergency_mode,
            "emergency_lane": self.emergency_lane,
            "active_phase": active_lanes,
            "phase_timer": self.phase_timer,
            "phase_duration": self.phase_duration,
            "optimization_score": self.optimization_score,
            "lanes": {
                name: {
                    "vehicle_count": lane.vehicle_count,
                    "waiting_time": lane.waiting_time,
                    "total_passed": lane.total_passed,
                    "is_green": name in active_lanes,
                    "is_emergency": lane.is_emergency
                } for name, lane in self.lanes.items()
            }
        }
