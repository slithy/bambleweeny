class BambleweenyException(Exception):
    """A base exception class."""

    def __init__(self, msg):
        super().__init__(msg)


class NoCharacter(BambleweenyException):
    """Raised when a user has no active character."""

    def __init__(self):
        super().__init__("You have no character active.")


class ExternalImportError(BambleweenyException):
    """Raised when something fails to import."""

    def __init__(self, msg):
        super().__init__(msg)


class InvalidArgument(BambleweenyException):
    """Raised when an argument is invalid."""
    pass


class NotAllowed(BambleweenyException):
    """Raised when a user tries to do something they are not allowed to do by role or dependency."""
    pass


class EvaluationError(BambleweenyException):
    """Raised when a cvar evaluation causes an error."""

    def __init__(self, original, expression=None):
        super().__init__(f"Error evaluating expression: {original}")
        self.original = original
        self.expression = expression


class FunctionRequiresCharacter(BambleweenyException):
    """
    Raised when a function that requires a character is called without one.
    """

    def __init__(self, msg=None):
        super().__init__(msg or "This alias requires an active character.")


class InvalidSaveType(BambleweenyException):
    def __init__(self):
        super().__init__("Invalid save type.")


class ConsumableException(BambleweenyException):
    """A base exception for consumable exceptions to stem from."""
    pass


class CounterOutOfBounds(ConsumableException):
    """Raised when a counter is set to a value out of bounds."""

    def __init__(self, msg=None):
        super().__init__(msg or "The new value is out of bounds.")


class NoReset(ConsumableException):
    """Raised when a consumable without a reset is reset."""

    def __init__(self):
        super().__init__("The counter does not have a reset value.")


class InvalidSpellLevel(ConsumableException):
    """Raised when a spell level is invalid."""

    def __init__(self):
        super().__init__("The spell level is invalid.")


class SelectionException(BambleweenyException):
    """A base exception for message awaiting exceptions to stem from."""
    pass


class NoSelectionElements(SelectionException):
    """Raised when get_selection() is called with no choices."""

    def __init__(self, msg=None):
        super().__init__(msg or "There are no choices to select from.")


class SelectionCancelled(SelectionException):
    """Raised when get_selection() is cancelled or times out."""

    def __init__(self):
        super().__init__("Selection timed out or was cancelled.")


class CombatException(BambleweenyException):
    """A base exception for combat-related exceptions to stem from."""
    pass


class CombatNotFound(CombatException):
    """Raised when a channel is not in combat."""

    def __init__(self):
        super().__init__("This channel is not in combat.")


class RequiresContext(CombatException):
    """Raised when a combat is committed without context."""

    def __init__(self):
        super().__init__("Combat not contextualized.")


class ChannelInCombat(CombatException):
    """Raised when a combat is started with an already active combat."""

    def __init__(self):
        super().__init__("Channel already in combat.")


class CombatChannelNotFound(CombatException):
    """Raised when a combat's channel is not in the channel list."""

    def __init__(self):
        super().__init__("Combat channel does not exist.")


class NoCombatants(CombatException):
    """Raised when a combat tries to advance turn with no combatants."""

    def __init__(self):
        super().__init__("There are no combatants.")
