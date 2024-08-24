from typing import Dict, Any


class YATLValidator:
    def __init__(self):
        self.errors = []

    def validate(self, parsed_yatl: Dict[str, Any]) -> bool:
        self.errors = []

        self._validate_structure(parsed_yatl)
        self._validate_states(parsed_yatl.get("states", {}))
        self._validate_initial_state(parsed_yatl)

        return len(self.errors) == 0

    def _validate_structure(self, data: Dict[str, Any]):
        required_keys = ["name", "initial_state", "states"]
        for key in required_keys:
            if key not in data:
                self.errors.append(f"Missing required key: {key}")

    def _validate_states(self, states: Dict[str, Any]):
        if not isinstance(states, dict):
            self.errors.append("'states' must be a dictionary")
            return

        for state_name, state_data in states.items():
            self._validate_state(state_name, state_data)

    def _validate_state(self, state_name: str, state_data: Dict[str, Any]):
        if "type" not in state_data:
            self.errors.append(f"State '{state_name}' is missing 'type'")

        if "transitions" in state_data:
            if not isinstance(state_data["transitions"], list):
                self.errors.append(f"Transitions for state '{state_name}' must be a list")
            else:
                for transition in state_data["transitions"]:
                    if "event" not in transition or "target" not in transition:
                        self.errors.append(f"Invalid transition in state '{state_name}': {transition}")

    def _validate_initial_state(self, data: Dict[str, Any]):
        initial_state = data.get("initial_state")
        if initial_state not in data.get("states", {}):
            self.errors.append(f"Initial state '{initial_state}' is not defined in states")


# Usage example
validator = YATLValidator()
parsed_yatl = {
    "name": "TrafficLight",
    "initial_state": "Red",
    "states": {
        "Red": {"type": "normal", "transitions": [{"event": "TimerExpired", "target": "Green"}]},
        "Green": {"type": "normal", "transitions": [{"event": "TimerExpired", "target": "Yellow"}]},
        "Yellow": {"type": "normal", "transitions": [{"event": "TimerExpired", "target": "Red"}]},
    },
}

is_valid = validator.validate(parsed_yatl)
print(f"YATL is valid: {is_valid}")
if not is_valid:
    print("Validation errors:")
    for error in validator.errors:
        print(f"- {error}")
