"""Item."""

import logging
import os
from typing import List, Optional

from cyberfusion.QueueSupport.exceptions import PathIsSymlinkError
from cyberfusion.QueueSupport.interfaces import OutcomeInterface
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import ChmodItemModeChangeOutcome
from cyberfusion.QueueSupport.utilities import get_decimal_permissions

logger = logging.getLogger(__name__)


class ChmodItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        path: str,
        mode: int,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
    ) -> None:
        """Set attributes."""
        self.path = path
        self.mode = mode
        self._reference = reference
        self._hide_outcomes = hide_outcomes

        if os.path.islink(self.path):
            raise PathIsSymlinkError(self.path)

    @property
    def outcomes(self) -> List[OutcomeInterface]:
        """Get outcomes of calling self.fulfill."""
        outcomes = []

        if not os.path.exists(self.path):
            outcomes.append(
                ChmodItemModeChangeOutcome(
                    path=self.path, old_mode=None, new_mode=self.mode
                )
            )
        else:
            old_mode = get_decimal_permissions(self.path)
            mode_changed = old_mode != self.mode

            if mode_changed:
                outcomes.append(
                    ChmodItemModeChangeOutcome(
                        path=self.path, old_mode=old_mode, new_mode=self.mode
                    )
                )

        return outcomes

    def fulfill(self) -> None:
        """Fulfill outcomes."""
        mode_change_outcomes = [
            x for x in self.outcomes if isinstance(x, ChmodItemModeChangeOutcome)
        ]

        if mode_change_outcomes:
            os.chmod(mode_change_outcomes[0].path, mode_change_outcomes[0].new_mode)

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, ChmodItem):
            return False

        return other.path == self.path and other.mode == self.mode
