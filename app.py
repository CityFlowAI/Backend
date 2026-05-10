from flask import Flask, jsonify, request
from flask_cors import CORS
from simulation import SimulationEngine

app = Flask(__name__)
CORS(app)

# Initialize and start the background simulation engine
engine = SimulationEngine()
engine.start()

@app.route('/api/state', methods=['GET'])
def get_state():
    """Returns the current state of the traffic junction."""
    return jsonify(engine.get_state())

@app.route('/api/emergency', methods=['POST'])
def trigger_emergency():
    """Triggers or clears emergency mode."""
    data = request.json
    lane = data.get('lane')
    action = data.get('action') # 'trigger' or 'clear'
    
    if action == 'trigger' and lane:
        engine.trigger_emergency(lane)
        return jsonify({"status": "success", "message": f"Emergency mode activated for {lane} lane."})
    elif action == 'clear':
        engine.clear_emergency()
        return jsonify({"status": "success", "message": "Emergency mode cleared."})
        
    return jsonify({"status": "error", "message": "Invalid request."}), 400

@app.route('/api/toggle_ai', methods=['POST'])
def toggle_ai():
    """Toggles AI optimization on or off."""
    data = request.json
    enabled = data.get('enabled', True)
    engine.ai_enabled = enabled
    return jsonify({"status": "success", "ai_enabled": engine.ai_enabled})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Returns historical data for charts."""
    return jsonify(engine.history)

if __name__ == '__main__':
    # Run server
    app.run(debug=True, port=5000, use_reloader=False)
