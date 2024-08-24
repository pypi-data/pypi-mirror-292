import yaml
from typing import Dict, Any


class YATLParser:
    def __init__(self):
        pass

    def parse(self, yatl_string: str) -> Dict[str, Any]:
        try:
            parsed_data = yaml.safe_load(yatl_string)
            self._validate_structure(parsed_data)
            return parsed_data
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YATL: {str(e)}")

    def _validate_structure(self, data: Dict[str, Any]):
        required_keys = ["name", "initial_state", "states"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        if not isinstance(data["states"], dict):
            raise ValueError("'states' must be a dictionary")

        # Add more structure validation as needed


# Usage example
parser = YATLParser()
yatl_content = """
name: TrafficLight
initial_state: Red
states:
  Red:
    type: normal
    on_enter: [turnOnRed]
    transitions:
      - event: TimerExpired
        target: Green
"""
parsed_yatl = parser.parse(yatl_content)
print(parsed_yatl)
