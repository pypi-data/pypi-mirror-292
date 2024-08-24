from typing import Dict, Any, List, Callable


class YATLRuntime:
    def __init__(self, compiled_yatl: Dict[str, Any]):
        self.name = compiled_yatl["name"]
        self.states = compiled_yatl["states"]
        self.current_state = compiled_yatl["initial_state"]
        self.action_handlers: Dict[str, Callable] = {}

    def register_action(self, action_name: str, handler: Callable):
        self.action_handlers[action_name] = handler

    def trigger_event(self, event: str) -> bool:
        if event not in self.states[self.current_state]["transitions"]:
            return False

        next_state = self.states[self.current_state]["transitions"][event]
        self._exit_state(self.current_state)
        self.current_state = next_state
        self._enter_state(self.current_state)
        return True

    def _exit_state(self, state: str):
        for action in self.states[state]["on_exit"]:
            self._execute_action(action)

    def _enter_state(self, state: str):
        for action in self.states[state]["on_enter"]:
            self._execute_action(action)

    def _execute_action(self, action: str):
        if action in self.action_handlers:
            self.action_handlers[action]()
        else:
            print(f"Warning: No handler for action '{action}'")


# Usage example
def turn_on_red():
    print("Red light on")


def turn_on_green():
    print("Green light on")


compiled_yatl = {
    "name": "TrafficLight",
    "initial_state": "Red",
    "states": {
        "Red": {"type": "normal", "on_enter": ["turnOnRed"], "on_exit": [], "transitions": {"TimerExpired": "Green"}},
        "Green": {"type": "normal", "on_enter": ["turnOnGreen"], "on_exit": [], "transitions": {"TimerExpired": "Red"}},
    },
}

runtime = YATLRuntime(compiled_yatl)
runtime.register_action("turnOnRed", turn_on_red)
runtime.register_action("turnOnGreen", turn_on_green)

print(f"Current state: {runtime.current_state}")
runtime.trigger_event("TimerExpired")
print(f"Current state: {runtime.current_state}")
runtime.trigger_event("TimerExpired")
print(f"Current state: {runtime.current_state}")
