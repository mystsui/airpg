import pytest
from uuid import uuid4
from src.combat.core.engine import CombatEngine
from src.combat.models.state import CombatState
from src.combat.models.combatant import CombatantState
from src.combat.models.actions import Action, ActionType, ActionResult, ActionRequirements, ActionCosts
from src.combat.events.event import CombatEvent, CombatStartEvent, ActionEvent, CombatEndEvent

class TestCombatEngine:
    @pytest.fixture
    def combat_engine(self) -> CombatEngine:
        """Create a basic combat engine instance."""
        return CombatEngine()

    @pytest.fixture
    def basic_state(self) -> CombatState:
        """Create a basic combat state with two combatants."""
        combatants = {
            "fighter1": CombatantState(
                id="fighter1",
                health=100,
                max_health=100,
                stamina=50,
                max_stamina=50
            ),
            "fighter2": CombatantState(
                id="fighter2",
                health=100,
                max_health=100,
                stamina=50,
                max_stamina=50
            )
        }
        return CombatState(combatants=combatants)

    @pytest.fixture
    def basic_action(self) -> Action:
        """Create a basic attack action."""
        return Action(
            type=ActionType.ATTACK,
            name="Basic Attack",
            parameters={"damage": 20},
            target_id="fighter2",
            requirements=ActionRequirements(min_stamina=10),
            costs=ActionCosts(stamina=10)
        )

    def test_engine_initialization(self, combat_engine):
        """Test combat engine initialization."""
        assert combat_engine._current_state is None
        assert len(combat_engine._action_queue) == 0

    def test_initialize_combat(self, combat_engine, basic_state):
        """Test combat initialization."""
        combat_engine.initialize_combat(basic_state)
        assert combat_engine._current_state is not None
        assert len(combat_engine._current_state.combatants) == 2
        assert combat_engine._current_state.round_number == 0

    def test_queue_action(self, combat_engine, basic_state, basic_action):
        """Test action queuing."""
        combat_engine.initialize_combat(basic_state)
        success = combat_engine.queue_action("fighter1", basic_action)
        assert success
        assert len(combat_engine._action_queue) == 1

    def test_queue_action_invalid_combatant(self, combat_engine, basic_state, basic_action):
        """Test queuing action for invalid combatant."""
        combat_engine.initialize_combat(basic_state)
        success = combat_engine.queue_action("invalid_fighter", basic_action)
        assert not success
        assert len(combat_engine._action_queue) == 0

    def test_process_round(self, combat_engine, basic_state, basic_action):
        """Test round processing."""
        combat_engine.initialize_combat(basic_state)
        combat_engine.queue_action("fighter1", basic_action)
        
        results = combat_engine.process_round()
        
        assert len(results) == 1
        assert isinstance(results[0], ActionResult)
        assert combat_engine._current_state.round_number == 1
        assert len(combat_engine._action_queue) == 0

    def test_event_publishing(self, combat_engine, basic_state):
        """Test event publishing during combat."""
        events = []
        def event_handler(event: CombatEvent):
            events.append(event)
        
        combat_engine.subscribe("combat.initialized", event_handler)
        combat_engine.initialize_combat(basic_state)
        
        assert len(events) == 1
        assert events[0].event_type == "combat.initialized"

    def test_multiple_actions_priority(self, combat_engine, basic_state):
        """Test multiple actions processed in priority order."""
        combat_engine.initialize_combat(basic_state)
        
        action1 = Action(
            id=uuid4(),
            type=ActionType.ATTACK,
            name="Slow Attack",
            priority=ActionType.LOW,
            target_id="fighter2",
            parameters={"damage": 30}
        )
        
        action2 = Action(
            id=uuid4(),
            type=ActionType.ATTACK,
            name="Quick Attack",
            priority=ActionType.HIGH,
            target_id="fighter1",
            parameters={"damage": 15}
        )
        
        combat_engine.queue_action("fighter1", action1)
        combat_engine.queue_action("fighter2", action2)
        
        results = combat_engine.process_round()
        
        assert len(results) == 2
        assert results[0].action_id == action2.id  # High priority should be first

    def test_invalid_state_operations(self, combat_engine, basic_action):
        """Test operations with invalid combat state."""
        with pytest.raises(RuntimeError):
            combat_engine.queue_action("fighter1", basic_action)
            
        with pytest.raises(RuntimeError):
            combat_engine.process_round()

    def test_state_cloning(self, combat_engine, basic_state, basic_action):
        """Test state cloning during combat."""
        combat_engine.initialize_combat(basic_state)
        initial_state = combat_engine._current_state
        
        combat_engine.queue_action("fighter1", basic_action)
        combat_engine.process_round()
        
        assert combat_engine._current_state is not initial_state
        assert combat_engine._current_state.id == initial_state.id

    def test_combat_resolution(self, combat_engine, basic_state):
        """Test combat resolution with defeated combatant."""
        combat_engine.initialize_combat(basic_state)
        
        # Create fatal attack
        fatal_action = Action(
            id=uuid4(),
            type=ActionType.ATTACK,
            name="Fatal Attack",
            target_id="fighter2",
            parameters={"damage": 999}
        )
        
        combat_engine.queue_action("fighter1", fatal_action)
        results = combat_engine.process_round()
        
        assert results[0].success
        assert combat_engine._current_state.combatants["fighter2"].health == 0

    def test_event_handling(self, combat_engine: CombatEngine, basic_state: CombatState):
        """Test event handling during combat."""
        events = []
        
        def event_handler(event: CombatStartEvent):
            events.append(event)
        
        combat_engine.subscribe("combat.start", event_handler)
        combat_engine.initialize_combat(basic_state)
        
        assert len(events) == 1
        assert isinstance(events[0], CombatStartEvent)
        assert events[0].event_type == "combat.start"
        assert events[0].combat_id == combat_engine._current_state.id
        assert isinstance(events[0].participants, list)
        assert len(events[0].initial_state.combatants) == 2