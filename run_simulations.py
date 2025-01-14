from analysis.battle_simulator import BattleSimulator

# Run simulations
simulator = BattleSimulator(num_iterations=100)
simulator.run_simulation()

# Print analysis
analysis = simulator.analyze_results()
print(json.dumps(analysis, indent=2))