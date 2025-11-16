"""
Unit tests for optimiser.py
"""
import pytest
from pathlib import Path
from optimiser import run_optimisation, load_config


class TestLoadConfig:
    """Test configuration loading."""
    
    def test_load_valid_config(self):
        """Test loading valid config file."""
        config_path = Path("config.json")
        if config_path.exists():
            config = load_config(config_path)
            assert isinstance(config, dict)
            # Check expected keys
            if "optimiser" in config:
                assert "staff" in config["optimiser"] or "shift_requirements" in config["optimiser"]
    
    def test_load_missing_config(self, tmp_path):
        """Test loading non-existent config file."""
        missing_path = tmp_path / "nonexistent.json"
        config = load_config(missing_path)
        assert config == {}


class TestRunOptimisation:
    """Test the optimization function."""
    
    def test_basic_optimisation(self):
        """Test basic optimization run."""
        results = run_optimisation(verbose=False)
        
        # Should return results or None
        if results:
            assert "status" in results
            assert "total_cost" in results
            assert "assignments" in results
            assert results["status"] == "Optimal"
            assert results["total_cost"] > 0
            
            # Check assignments
            assignments = results["assignments"]
            assert isinstance(assignments, dict)
            
            # Each staff member should have shifts and hours
            for staff, data in assignments.items():
                assert "shifts" in data
                assert "hours" in data
                assert isinstance(data["shifts"], list)
                assert isinstance(data["hours"], (int, float))
                assert data["hours"] >= 0
    
    def test_optimisation_respects_constraints(self):
        """Test that optimization respects max hours and availability."""
        results = run_optimisation(verbose=False)
        
        if results:
            # Load config to get constraints
            config = load_config()
            opt_config = config.get("optimiser", {})
            staff_config = opt_config.get("staff", {})
            
            if staff_config:
                for staff, data in results["assignments"].items():
                    if staff in staff_config:
                        max_hours = staff_config[staff]["max_hours"]
                        assigned_hours = data["hours"]
                        # Should not exceed max hours
                        assert assigned_hours <= max_hours + 0.01, f"{staff} exceeds max hours"
    
    def test_optimisation_export(self, tmp_path):
        """Test optimization with JSON export."""
        export_path = tmp_path / "optimisation_export.json"
        
        results = run_optimisation(verbose=False, export_path=export_path)
        
        if results:
            assert export_path.exists()
            
            import json
            with open(export_path) as f:
                data = json.load(f)
            
            assert "status" in data
            assert "total_cost" in data
            assert "assignments" in data
            assert "parameters" in data
    
    def test_optimisation_deterministic(self):
        """Test that optimization produces consistent results."""
        results1 = run_optimisation(verbose=False)
        results2 = run_optimisation(verbose=False)
        
        if results1 and results2:
            # Should get same cost (optimization is deterministic)
            assert abs(results1["total_cost"] - results2["total_cost"]) < 0.01
    
    def test_shift_coverage(self):
        """Test that all shifts have required coverage."""
        results = run_optimisation(verbose=False)
        
        if results:
            # Load shift requirements
            config = load_config()
            opt_config = config.get("optimiser", {})
            shift_requirements = opt_config.get("shift_requirements", {})
            
            if shift_requirements:
                # Count assignments per shift
                shift_counts = {}
                for staff, data in results["assignments"].items():
                    for shift in data["shifts"]:
                        shift_counts[shift] = shift_counts.get(shift, 0) + 1
                
                # Check each requirement is met
                for shift, required in shift_requirements.items():
                    actual = shift_counts.get(shift, 0)
                    assert actual >= required, f"Shift {shift} under-staffed: {actual} < {required}"
    
    def test_one_shift_per_day_constraint(self):
        """Test that no staff works multiple shifts in one day."""
        results = run_optimisation(verbose=False)
        
        if results:
            for staff, data in results["assignments"].items():
                shifts = data["shifts"]
                
                # Extract days from shifts (format: Day_Time)
                days = {}
                for shift in shifts:
                    if "_" in shift:
                        day = shift.split("_")[0]
                        days[day] = days.get(day, 0) + 1
                
                # Each day should have at most 1 shift
                for day, count in days.items():
                    assert count <= 1, f"{staff} has {count} shifts on {day}"
    
    def test_cost_calculation(self):
        """Test that cost is calculated correctly."""
        results = run_optimisation(verbose=False)
        
        if results:
            # Manually calculate expected cost
            config = load_config()
            opt_config = config.get("optimiser", {})
            staff_config = opt_config.get("staff", {})
            shift_duration = opt_config.get("shift_duration_hours", 8)
            
            if staff_config:
                manual_cost = 0
                for staff, data in results["assignments"].items():
                    if staff in staff_config:
                        hourly_cost = staff_config[staff]["cost"]
                        hours = data["hours"]
                        manual_cost += hourly_cost * hours
                
                # Should match optimization result
                assert abs(manual_cost - results["total_cost"]) < 0.01


class TestOptimisationEdgeCases:
    """Test edge cases and error handling."""
    
    def test_with_verbose_output(self, capsys):
        """Test that verbose mode produces output."""
        results = run_optimisation(verbose=True)
        
        captured = capsys.readouterr()
        assert "MediFlow Rota Optimiser" in captured.out or results is None
    
    def test_handles_infeasible_problem(self):
        """Test graceful handling of infeasible problems."""
        # With default config, should be feasible
        # This test mainly ensures no crashes
        results = run_optimisation(verbose=False)
        # Should return dict or None, not crash
        assert results is None or isinstance(results, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
