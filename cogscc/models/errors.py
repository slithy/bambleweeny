class BambleweenyException(Exception):
    """A base exception class."""
    def __init__(self, msg):
        super().__init__(msg)


class EvaluationError(BambleweenyException):
    """Raised when a cvar evaluation causes an error."""
    def __init__(self, original, expression=None):
        super().__init__(f"Error evaluating expression: {original}")
        self.original = original
        self.expression = expression

class ExternalImportError(BambleweenyException):
    """Raised when something fails to import."""
    def __init__(self, msg):
        super().__init__(msg)

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


class CharacterNotFound(BambleweenyException):
    """Raised when a character can't be found in the list of active characters."""
    def __init__(self, msg: str = "Character not found in the active list."):
        super().__init__(msg)


class AmbiguousMatch(BambleweenyException):
    """Raised when a search expression matches more than one item."""
    def __init__(self, msg: str = "Search expression is ambiguous, more than one result matches."):
        super().__init__(msg)


class CreditLimitExceeded(BambleweenyException):
    """Raised when there is insufficient funds."""
    def __init__(self, msg: str = "You do not have enough money."):
        super().__init__(msg)


class InvalidCoinType(BambleweenyException):
    """Raised when a coin type is unrecognised."""
    def __init__(self, msg: str = "Valid coin types are pp, gp, ep, sp, cp."):
        super().__init__(msg)


class OutOfRange(BambleweenyException):
    """Raised when a value is out of range."""
    def __init__(self, msg: str = "Value is out of range."):
        super().__init__(msg)


class InvalidArgument(BambleweenyException):
    """Raised when an argument is invalid."""
    pass


class NotAllowed(BambleweenyException):
    """Raised when a user tries to do something they are not allowed to do by role or dependency."""
    pass

