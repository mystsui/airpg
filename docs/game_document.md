# Combat System Design Document

## 1. System Overview
The combat system implements a time-based, turn-based combat simulation with emphasis on tactical positioning, resource management, and action timing. It supports 1v1 battles with complex interaction patterns between combatants.

## 2. Core Concepts

### 2.1 Time Management
- Millisecond-based timing system
- Actions have specific durations
- Combat has a maximum duration
- Time advances based on action resolution

### 2.2 Spatial System
- Distance-based positioning system
- Maximum distance boundary
- Directional facing (left/right)
- Range-based attack validation

### 2.3 Resource Management
- Health Points (HP): Combat viability
- Stamina: Action execution resource
- Blocking Power: Defensive capability
- Position and Facing: Spatial resources

### 2.4 Combat Actions

#### 2.4.1 Action Categories
1. NEUTRAL Actions
   - Idle: Basic waiting state (10ms, 0 stamina)
   - Reset: Return to neutral stance (1000ms, 0 stamina)
   - Recover: Regain stamina (2000ms, 0 stamina)
   - Off Balance: Forced recovery state (800ms, 0 stamina)

2. MOVEMENT Actions
   - Move Forward: Reduce distance (700ms, 4 stamina)
   - Move Backward: Increase distance (700ms, 4 stamina)
   - Turn Around: Change facing direction (400ms, 2 stamina)

3. DEFENSE Actions
   - Try Block: Initiate blocking stance (200ms, 3 stamina)
   - Blocking: Active defense state (100ms, 1 stamina)
   - Keep Blocking: Maintain defense (1ms, 1 stamina)

4. EVASION Actions
   - Try Evade: Initiate evasion (300ms, 3 stamina)
   - Evading: Active evasion state (10ms, 1 stamina)

5. ATTACK Actions
   - Try Attack: Initiate attack (400ms, 10 stamina)
   - Release Attack: Execute attack (300ms, 0 stamina)
   - Stop Attack: Cancel attack (150ms, 2 stamina)

#### 2.4.2 Action Properties
- Execution Time: Duration in milliseconds
- Stamina Cost: Resource requirement
- State Effects: Changes to combatant state
- Interaction Rules: How actions interact with other actions

### 2.5 Combat Resolution

#### 2.5.1 Action Priority System
1. Attack actions (highest)
   - try_attack
   - release_attack
   - stop_attack
2. Defense actions
   - try_block
   - blocking
   - keep_blocking
3. Evasion actions
   - try_evade
   - evading
4. Movement actions
   - move_forward
   - move_backward
   - turn_around
5. Neutral actions (lowest)
   - idle
   - reset
   - recover
   - off_balance

#### 2.5.2 Interaction Outcomes
When an attack is released, it will result in one of these outcomes:

1. Missed
   - Condition: Target is not within the attacker's range
   - Effect: Attack fails, attacker becomes off-balance
   - State Changes: Attacker enters "off_balance" state

2. Hit
   - Condition: Target is within range and neither blocking nor evading
   - Effect: Full damage is applied to target's health
   - State Changes: 
     * Target's health reduced by damage amount
     * Both combatants enter "reset" state

3. Blocked
   - Condition: Target is blocking and their blocking power ≥ attack damage
   - Effect: Damage is fully absorbed by blocking power
   - State Changes:
     * Target's blocking power reduced by damage amount
     * Target enters "reset" state
     * Attacker enters "off_balance" state

4. Breached
   - Condition: Target is blocking but their blocking power < attack damage
   - Effect: Partial damage penetrates the block
   - State Changes:
     * Target's blocking power reduced to 0
     * Target's health reduced by (damage - original blocking power)
     * Both combatants enter "reset" state

5. Evaded
   - Condition: Target is in "evading" state
   - Effect: Attack completely misses
   - State Changes:
     * Target enters "reset" state
     * Attacker enters "off_balance" state

### 2.6 State Management

#### 2.6.1 Combatant States
- Health: Current and maximum HP
- Stamina: Current and maximum stamina points
- Position: Left or right side of the battlefield
- Facing: Direction the combatant is facing
- Action: Current action being performed
- Team: Challenger or defender
- Combat Stats:
  * Attack Power: Base damage potential
  * Accuracy: Hit chance modifier
  * Blocking Power: Damage absorption capacity
  * Evading Ability: Evasion success rate
  * Mobility: Movement distance
  * Range: Minimum and maximum attack distances
  * Stamina Recovery: Rate of stamina regeneration
  * Perception: Ability to detect opponent actions
  * Stealth: Ability to conceal actions

#### 2.6.2 Battle States
- Timer: Current battle time
- Duration: Maximum battle length
- Distance: Current distance between combatants
- Max Distance: Maximum allowed separation
- Events: Log of all battle actions and outcomes

### 2.7 Decision Making
- Action Availability: Based on stamina and conditions
- Range Considerations: Position relative to attack ranges
- Resource Management: Stamina and blocking power
- Opponent State Analysis: Reaction to opponent actions

## 3. Battle Flow

### 3.1 Initialization
1. Create battle with duration and distance parameters
2. Add combatants (maximum 2)
3. Assign teams (challenger/defender)
4. Set initial positions and facing directions

### 3.2 Combat Loop
1. Action Selection
   - Check available actions
   - Consider stamina costs
   - Evaluate tactical position
   - Assess opponent state

2. Action Resolution
   - Determine action timing
   - Apply priority rules
   - Process interactions
   - Update states

3. State Updates
   - Update positions
   - Modify resources
   - Apply effects
   - Check victory conditions

4. Event Logging
   - Record action details
   - Track state changes
   - Store interaction results
   - Enable replay capability

### 3.3 Victory Conditions
- Time expiration
- Combatant defeat (HP ≤ 0)
- Last combatant standing

## 4. Technical Considerations

### 4.1 Event-Driven Architecture
- Action events trigger state changes
- Priority-based event processing
- Chainable action sequences
- State validation at each step

### 4.2 State Management
- Immutable state updates
- Comprehensive state tracking
- Rollback capability
- State validation rules

### 4.3 Action Resolution Pipeline
1. Validate action requirements
2. Process action timing
3. Apply action effects
4. Handle interactions
5. Update states
6. Log results

### 4.4 Logging and Replay
- Detailed event logging
- State tracking at each step
- Replay functionality
- Battle analysis capabilities
