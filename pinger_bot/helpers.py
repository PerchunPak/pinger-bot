"""Module with functions to give help."""
from typing import Optional

from nextcord import Interaction
from structlog.stdlib import get_logger

log = get_logger()


class OnCommand:
    """Perform some actions when command executed."""

    def __init__(self, name: str, interaction: Interaction) -> None:
        """Main entrypoint.

        Args:
            name: Let it as ``__name__`` always.
            interaction: ``Interaction`` object. Dirrectly from ``nextcord`` API.
        """
        self.name = name
        self.interaction = interaction
        self.log()

    def get_full_nick(self) -> Optional[str]:
        """Return user nick and discriminator in human format."""
        if self.interaction.user is not None:
            return self.interaction.user.name + "#" + self.interaction.user.discriminator
        return None

    def handle_message_context(self) -> Optional[str]:
        """Handle message context.

        Returns:
            If message object is None, return None. Else return context of this message.
        """
        if self.interaction.message is not None:
            return self.interaction.message.clean_content
        return None

    def log(self) -> None:
        """One of final step of the class. Execute log method."""
        log.debug(self.name, user=self.get_full_nick(), message=self.handle_message_context())
