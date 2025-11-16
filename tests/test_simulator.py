"""
Unit tests for simulator.py
"""
import pytest
from pathlib import Path
from simulator import run_simulation, SimulationResults, Clinic
import simpy


class TestSimulationResults:
    """Test SimulationResults class."""
    
    def test_initialization(self):
        """Test that SimulationResults initializes correctly."""
        results = SimulationResults()
        assert results.wait_times == []
        assert results.service_times == []
        assert results.patients_served == 0
        assert results.avg_wait_time == 0.0
        assert results.avg_queue_length == 0.0
        assert results.utilization == 0.0
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        results = SimulationResults()
        results.patients_served = 10
        results.avg_wait_time = 0.5
        results.parameters = {"arrival_rate": 10}
        
        result_dict = results.to_dict()
        assert "parameters" in result_dict
        assert "metrics" in result_dict
        assert result_dict["metrics"]["patients_served"] == 10
        assert result_dict["metrics"]["avg_wait_time"] == 0.5
    
    def test_save_json(self, tmp_path):
        """Test JSON export functionality."""
        results = SimulationResults()
        results.patients_served = 5
        results.parameters = {"test": "value"}
        
        export_path = tmp_path / "test_results.json"
        results.save_json(export_path)
        
        assert export_path.exists()
        import json
        with open(export_path) as f:
            data = json.load(f)
        assert data["metrics"]["patients_served"] == 5


class TestRunSimulation:
    """Test the run_simulation function."""
    
    def test_basic_simulation(self):
        """Test a basic simulation run."""
        results = run_simulation(
            arrival_rate=5,
            service_rate=10,
            servers=2,
            hours=10,
            seed=42,
            verbose=False
        )
        
        assert "avg_wait_time" in results
        assert "avg_queue_length" in results
        assert "utilization" in results
        assert "patients_served" in results
        assert results["patients_served"] > 0
        assert results["utilization"] >= 0
        assert results["utilization"] <= 1.5  # Allow for slight overutilization
    
    def test_deterministic_with_seed(self):
        """Test that same seed produces same results."""
        results1 = run_simulation(
            arrival_rate=10,
            service_rate=4,
            servers=3,
            hours=20,
            seed=42,
            verbose=False
        )
        
        results2 = run_simulation(
            arrival_rate=10,
            service_rate=4,
            servers=3,
            hours=20,
            seed=42,
            verbose=False
        )
        
        # Results should be identical with same seed
        assert results1["patients_served"] == results2["patients_served"]
        assert abs(results1["avg_wait_time"] - results2["avg_wait_time"]) < 0.0001
    
    def test_high_utilization_warning(self):
        """Test that high utilization is detected."""
        # High arrival rate relative to service capacity
        results = run_simulation(
            arrival_rate=20,
            service_rate=5,
            servers=2,
            hours=10,
            seed=42,
            verbose=False
        )
        
        assert results["utilization"] > 0.9
        assert "High utilization" in results["system_status"] or "Unstable" in results["system_status"]
    
    def test_stable_system(self):
        """Test that stable system is detected."""
        # Low arrival rate relative to service capacity
        results = run_simulation(
            arrival_rate=5,
            service_rate=10,
            servers=3,
            hours=10,
            seed=42,
            verbose=False
        )
        
        assert results["utilization"] < 0.9
        assert "within limits" in results["system_status"]
    
    def test_export_functionality(self, tmp_path):
        """Test that export creates file with correct data."""
        export_path = tmp_path / "simulation_export.json"
        
        results = run_simulation(
            arrival_rate=10,
            service_rate=4,
            servers=3,
            hours=10,
            seed=42,
            verbose=False,
            export_path=export_path
        )
        
        assert export_path.exists()
        
        import json
        with open(export_path) as f:
            data = json.load(f)
        
        assert "parameters" in data
        assert "metrics" in data
        assert data["parameters"]["arrival_rate"] == 10
        assert data["metrics"]["patients_served"] == results["patients_served"]
    
    def test_zero_servers_error(self):
        """Test that zero servers causes an error or low utilization."""
        # This should either fail or have strange results
        with pytest.raises(Exception):
            run_simulation(
                arrival_rate=10,
                service_rate=4,
                servers=0,  # Invalid
                hours=10,
                verbose=False
            )
    
    def test_different_parameters(self):
        """Test with different parameter combinations."""
        test_cases = [
            {"arrival_rate": 5, "service_rate": 10, "servers": 1, "hours": 5},
            {"arrival_rate": 15, "service_rate": 5, "servers": 4, "hours": 20},
            {"arrival_rate": 8, "service_rate": 8, "servers": 2, "hours": 15},
        ]
        
        for params in test_cases:
            results = run_simulation(**params, seed=42, verbose=False)
            assert results["patients_served"] > 0
            assert results["utilization"] >= 0


class TestClinic:
    """Test the Clinic class."""
    
    def test_clinic_initialization(self):
        """Test Clinic object creation."""
        env = simpy.Environment()
        results = SimulationResults()
        clinic = Clinic(env, 3, 10, 4, results, verbose=False)
        
        assert clinic.staff.capacity == 3
        assert clinic.arrival_rate == 10
        assert clinic.service_rate == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
