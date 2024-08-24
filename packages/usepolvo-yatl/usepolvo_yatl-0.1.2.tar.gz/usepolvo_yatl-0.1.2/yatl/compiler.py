from typing import Dict, Any


class YATLCompiler:
    def __init__(self):
        pass

    def compile(self, parsed_yatl: Dict[str, Any]) -> Dict[str, Any]:
        compiled_yatl = {"name": parsed_yatl["name"], "initial_state": parsed_yatl["initial_state"], "states": {}}

        for state_name, state_data in parsed_yatl["states"].items():
            compiled_state = self._compile_state(state_name, state_data)
            compiled_yatl["states"][state_name] = compiled_state

        return compiled_yatl

    def _compile_state(self, state_name: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
        compiled_state = {
            "type": state_data.get("type", "normal"),
            "on_enter": state_data.get("on_enter", []),
            "on_exit": state_data.get("on_exit", []),
            "transitions": {},
        }

        for transition in state_data.get("transitions", []):
            event = transition["event"]
            target = transition["target"]
            compiled_state["transitions"][event] = target

        return compiled_state


# Usage example
compiler = YATLCompiler()
parsed_yatl = {
    "name": "TrafficLight",
    "initial_state": "Red",
    "states": {
        "Red": {
            "type": "normal",
            "on_enter": ["turnOnRed"],
            "transitions": [{"event": "TimerExpired", "target": "Green"}],
        }
    },
}
compiled_yatl = compiler.compile(parsed_yatl)
print(compiled_yatl)
