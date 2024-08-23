"""Item."""

import logging
from typing import List, Optional

from cyberfusion.QueueSupport.interfaces import OutcomeInterface
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    SystemdUnitEnableItemEnableOutcome,
)
from cyberfusion.SystemdSupport.units import Unit

logger = logging.getLogger(__name__)


class SystemdUnitEnableItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        name: str,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
    ) -> None:
        """Set attributes."""
        self.name = name
        self._reference = reference
        self._hide_outcomes = hide_outcomes

        self.unit = Unit(self.name)

    @property
    def outcomes(self) -> List[OutcomeInterface]:
        """Get outcomes of calling self.fulfill."""
        outcomes = []

        if not self.unit.is_enabled:
            outcomes.append(SystemdUnitEnableItemEnableOutcome(unit=self.unit))

        return outcomes

    def fulfill(self) -> None:
        """Fulfill outcomes."""
        systemd_unit_enable_outcomes = [
            x
            for x in self.outcomes
            if isinstance(x, SystemdUnitEnableItemEnableOutcome)
        ]

        if systemd_unit_enable_outcomes:
            systemd_unit_enable_outcomes[0].unit.enable()

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdUnitEnableItem):
            return False

        return other.name == self.name
