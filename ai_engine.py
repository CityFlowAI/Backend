import random
import math

def optimize_signals(lanes, phases, current_phase_idx, current_phase_duration):
    """
    PPO-inspired Adaptive Timing:
    Calculates a congestion score for all available phases:
    score = vehicle_count + (waiting_time * 0.5)
    
    The AI will demand the phase with the highest congestion score.
    """
    phase_scores = []
    
    for idx, phase_lanes in enumerate(phases):
        score = sum(lanes[name].vehicle_count + (lanes[name].waiting_time * 0.5) for name in phase_lanes)
        phase_scores.append(score)
        
    best_phase_idx = phase_scores.index(max(phase_scores))
    active_score = phase_scores[current_phase_idx]
    best_score = max(phase_scores)
    
    skip_phase = False
    
    # If the active phase has 0 score, but another phase needs attention, instantly skip
    if active_score == 0 and best_score > 0:
        skip_phase = True
    
    # If a waiting phase has significantly more congestion (+50 points) than the active phase, override
    elif best_score > active_score + 50 and current_phase_idx != best_phase_idx:
        skip_phase = True
        
    # Calculate duration based on severity of congestion
    # Calculate duration based on severity of congestion
    if best_score > 100:
        new_duration = 45 # 45 seconds for heavy traffic
    elif best_score > 50:
        new_duration = 30 # 30 seconds for medium
    else:
        new_duration = 15 # 15 seconds for light traffic
        
    # Introduce slight PPO exploration noise for realism
    new_duration += random.randint(-5, 5)
    
    # Global optimization metric (0-100)
    total_waiting = sum(l.waiting_time for l in lanes.values())
    max_queue = max(l.vehicle_count for l in lanes.values())
    opt_score = 100 - min(100, (total_waiting * 0.1) + (max_queue * 2))
    
    return skip_phase, best_phase_idx, int(new_duration), round(max(0, opt_score), 1)

def predict_congestion(total_vehicles):
    """
    ANN-inspired Congestion Prediction:
    Uses a simple sigmoid activation function over total vehicle count
    to predict the probability/risk of severe congestion.
    """
    # Parameters tuned for our mock simulation (expecting 0-100 vehicles total)
    threshold = 40
    steepness = 0.1
    
    # Sigmoid function
    z = steepness * (total_vehicles - threshold)
    risk_prob = 1 / (1 + math.exp(-z))
    
    # Return as percentage
    return round(risk_prob * 100, 1)
