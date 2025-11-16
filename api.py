"""
Flask REST API for MediFlow Suite
Provides endpoints for simulation and optimization via web interface
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from pathlib import Path
from datetime import datetime
import logging
import json

from simulator import run_simulation
from optimiser import run_optimisation, load_config

# Initialize Flask app
app = Flask(__name__, static_folder='web/static', static_url_path='/static')
CORS(app)  # Enable CORS for frontend access

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
Path("results").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)


@app.route('/')
def index():
    """Serve the main web interface."""
    return send_file('web/index.html')


@app.route('/api')
def api_info():
    """API root endpoint."""
    return jsonify({
        "name": "MediFlow API",
        "version": "1.0.0",
        "endpoints": {
            "simulate": "/api/simulate",
            "optimize": "/api/optimize",
            "results": "/api/results/<export_id>",
            "results_list": "/api/results",
            "config": "/api/config",
            "config_test": "/api/config/test",
            "health": "/api/health"
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    Run patient flow simulation.
    
    Request body:
    {
        "arrival_rate": float,
        "service_rate": float,
        "servers": int,
        "hours": float,
        "seed": int (optional),
        "export": bool (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['arrival_rate', 'service_rate', 'servers', 'hours']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract parameters
        arrival_rate = float(data['arrival_rate'])
        service_rate = float(data['service_rate'])
        servers = int(data['servers'])
        hours = float(data['hours'])
        seed = data.get('seed', 42)
        should_export = data.get('export', True)
        
        # Validate values
        if arrival_rate <= 0 or service_rate <= 0 or servers <= 0 or hours <= 0:
            return jsonify({"error": "All parameters must be positive"}), 400
        
        # Generate export path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_id = f"simulation_{timestamp}"
        export_path = Path(f"results/{export_id}.json") if should_export else None
        
        logger.info(f"Running simulation: λ={arrival_rate}, μ={service_rate}, c={servers}, T={hours}")
        
        # Run simulation
        results = run_simulation(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            servers=servers,
            hours=hours,
            seed=seed,
            verbose=False,
            export_path=export_path
        )
        
        return jsonify({
            "status": "success",
            "results": results,
            "export_id": export_id if should_export else None,
            "timestamp": datetime.now().isoformat()
        })
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Simulation error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/optimize', methods=['POST'])
def optimize():
    """
    Run staff scheduling optimization.
    
    Request body:
    {
        "export": bool (optional)
    }
    """
    try:
        data = request.get_json() or {}
        should_export = data.get('export', True)
        
        # Generate export path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_id = f"optimisation_{timestamp}"
        export_path = Path(f"results/{export_id}.json") if should_export else None
        
        logger.info("Running optimization")
        
        # Run optimization
        results = run_optimisation(
            verbose=False,
            export_path=export_path
        )
        
        # Check if infeasible
        if results and not results.get("feasible", True):
            return jsonify({
                "status": "infeasible",
                "message": results.get("message", "No feasible solution found"),
                "analysis": results.get("analysis", {}),
                "timestamp": datetime.now().isoformat()
            }), 200
        
        if results is None:
            return jsonify({
                "status": "error",
                "message": "Optimization failed"
            }), 500
        
        return jsonify({
            "status": "success",
            "results": results,
            "export_id": export_id if should_export else None,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Optimization error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/results/<export_id>', methods=['GET'])
def get_results(export_id):
    """
    Retrieve saved results by export ID.
    """
    try:
        file_path = Path(f"results/{export_id}.json")
        
        if not file_path.exists():
            return jsonify({"error": "Results not found"}), 404
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error retrieving results: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/results', methods=['GET'])
def list_results():
    """
    List all saved results.
    """
    try:
        results_dir = Path("results")
        files = []
        
        for file_path in results_dir.glob("*.json"):
            stat = file_path.stat()
            files.append({
                "id": file_path.stem,
                "name": file_path.name,
                "type": "simulation" if "simulation" in file_path.name else "optimisation",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Sort by modification time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            "count": len(files),
            "files": files
        })
        
    except Exception as e:
        logger.error(f"Error listing results: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """
    Get current configuration with detailed structure.
    """
    try:
        config = load_config()
        
        # Get current configuration (reloaded from file)
        from optimiser import get_current_config
        current_cfg = get_current_config()
        
        response = {
            "config_file": config,
            "current_loaded": {
                "staff": [
                    {
                        "name": staff,
                        "cost": current_cfg["staff_cost"].get(staff, 0),
                        "max_hours": current_cfg["staff_max_hours"].get(staff, 0),
                        "availability": current_cfg["staff_availability"].get(staff, [])
                    }
                    for staff in current_cfg["staff"]
                ],
                "shift_requirements": current_cfg["shift_requirements"]
            }
        }
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config', methods=['PUT'])
def update_config():
    """
    Update configuration and save to file.
    """
    try:
        new_config = request.get_json()
        
        # Validate config structure (basic validation)
        if not isinstance(new_config, dict):
            return jsonify({"error": "Config must be a JSON object"}), 400
        
        # Validate optimizer config if present
        if "optimiser" in new_config:
            opt_config = new_config["optimiser"]
            if "staff" in opt_config:
                for staff_name, staff_data in opt_config["staff"].items():
                    required_fields = ["cost", "max_hours", "availability"]
                    for field in required_fields:
                        if field not in staff_data:
                            return jsonify({"error": f"Staff '{staff_name}' missing field: {field}"}), 400
        
        # Save to config file
        with open('config.json', 'w') as f:
            json.dump(new_config, f, indent=2)
        
        logger.info("Configuration updated via API")
        
        return jsonify({
            "status": "success",
            "message": "Configuration updated successfully",
            "note": "Changes will take effect on next optimization run"
        })
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config/test', methods=['POST'])
def test_config():
    """
    Test a configuration without saving it.
    Runs optimization with provided config to check feasibility.
    """
    try:
        test_config = request.get_json()
        
        if not test_config or "optimiser" not in test_config:
            return jsonify({"error": "Must provide 'optimiser' configuration"}), 400
        
        # Temporarily save current config
        import tempfile
        import shutil
        
        # Backup current config
        shutil.copy('config.json', 'config.json.backup')
        
        try:
            # Write test config
            with open('config.json', 'w') as f:
                json.dump(test_config, f, indent=2)
            
            # Run optimization (it will automatically reload config from file)
            from optimiser import run_optimisation
            results = run_optimisation(verbose=False, export_path=None)
            
            # Check if infeasible
            if results and not results.get("feasible", True):
                return jsonify({
                    "status": "infeasible",
                    "feasible": False,
                    "message": results.get("message", "No feasible solution with this configuration"),
                    "analysis": results.get("analysis", {})
                })
            
            return jsonify({
                "status": "success" if results else "error",
                "feasible": results is not None,
                "results": results if results else None,
                "message": "Configuration is valid" if results else "Configuration test failed"
            })
            
        finally:
            # Restore original config
            shutil.move('config.json.backup', 'config.json')
        
    except Exception as e:
        logger.error(f"Error testing config: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import socket
    
    # Find available port
    def find_free_port(start_port=5000, max_port=5010):
        """Find an available port starting from start_port."""
        for port in range(start_port, max_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return None
    
    port = find_free_port()
    
    if port is None:
        print("\n❌ Error: Could not find an available port between 5000-5009")
        print("Please free up a port or disable AirPlay Receiver:")
        print("  System Settings → General → AirDrop & Handoff → AirPlay Receiver → Off")
        exit(1)
    
    print(f"""
╔═══════════════════════════════════════════╗
║       MediFlow API Server Started         ║
╠═══════════════════════════════════════════╣
║  Access at: http://localhost:{port:<4}          ║
║                                           ║
║  Endpoints:                               ║
║  • POST /api/simulate                     ║
║  • POST /api/optimize                     ║
║  • GET  /api/results                      ║
║  • GET  /api/config                       ║
╚═══════════════════════════════════════════╝
    """)
    
    if port != 5000:
        print(f"⚠️  Note: Using port {port} (5000 was in use)")
        print(f"    Update API_BASE in web/static/js/app.js if needed\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)
