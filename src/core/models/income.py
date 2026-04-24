from dataclasses import dataclass, field


@dataclass
class Income:
    salary: float = 0.0
    house_property: float = 0.0
    business: float = 0.0
    capital_gains: float = 0.0
    other_sources: float = 0.0

    @property
    def gross_total(self) -> float:
        return self.salary + self.house_property + self.business + self.capital_gains + self.other_sources
