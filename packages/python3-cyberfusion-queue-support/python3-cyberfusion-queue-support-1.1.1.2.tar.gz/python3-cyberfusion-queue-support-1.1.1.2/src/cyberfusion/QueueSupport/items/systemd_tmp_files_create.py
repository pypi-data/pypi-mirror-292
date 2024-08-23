"""Item."""

import logging
from typing import List, Optional

from cyberfusion.QueueSupport.interfaces import OutcomeInterface
from cyberfusion.QueueSupport.items import _Item
from cyberfusion.QueueSupport.outcomes import (
    SystemdTmpFilesCreateItemCreateOutcome,
)
from cyberfusion.SystemdSupport.tmp_files import TmpFileConfigurationFile

logger = logging.getLogger(__name__)


class SystemdTmpFilesCreateItem(_Item):
    """Represents item."""

    def __init__(
        self,
        *,
        path: str,
        reference: Optional[str] = None,
        hide_outcomes: bool = False,
    ) -> None:
        """Set attributes."""
        self.path = path
        self._reference = reference
        self._hide_outcomes = hide_outcomes

    @property
    def outcomes(self) -> List[OutcomeInterface]:
        """Get outcomes of calling self.fulfill."""
        outcomes = []

        outcomes.append(SystemdTmpFilesCreateItemCreateOutcome(path=self.path))

        return outcomes

    def fulfill(self) -> None:
        """Fulfill outcomes."""
        systemd_tmp_files_create_outcomes = [
            x
            for x in self.outcomes
            if isinstance(x, SystemdTmpFilesCreateItemCreateOutcome)
        ]

        TmpFileConfigurationFile(
            systemd_tmp_files_create_outcomes[0].path
        ).create()

    def __eq__(self, other: object) -> bool:
        """Get equality based on attributes."""
        if not isinstance(other, SystemdTmpFilesCreateItem):
            return False

        return other.path == self.path
