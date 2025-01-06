import typing
from dataclasses import dataclass
import yaml
from pathlib import Path


class UniverseError(Exception):
    pass


@dataclass
class Universe:
    name: str
    description: str
    symbols: typing.List[str]


class UniverseManager:
    def __init__(self, config_path: str = "src/fmd/config/universe.yml") -> None:
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileExistsError("Invalid configuration file path for universe data!")
        with open(self.config_path, "r") as yamlfile:
            self.universe_data = yaml.safe_load(yamlfile)

        self.universes_category_list = list(self.universe_data.keys())

    def get_universe(self, universe_name: str) -> Universe:
        """get Universe instance from config fle"""
        valid = self.validate_universe_category(universe_name=universe_name)
        if valid:
            return Universe(
                # fmt: off
                universe_name,
                description=self.universe_data[universe_name]["desc"],
                symbols=self.universe_data[universe_name]["symbols"]
                # fmt: on
            )

        else:
            raise UniverseError(f"Unexpected universe name input: {universe_name}")

    def validate_universe_category(self, universe_name: str) -> bool:
        """validate universe name"""
        return universe_name in self.universes_category_list

    def build_universe():  # with a constraint like micro caps under ???
        pass
