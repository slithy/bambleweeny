class BambleweenyException(Exception):
    """A base exception class."""
    def __init__(self, msg):
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

class MissingArgument(BambleweenyException):
    """Raised when a command is missing a required argument."""
    def __init__(self, msg):
        super().__init__(msg)

class InvalidEquipmentAttribute(BambleweenyException):
    """Raised when an invalid attribute is applied to an item of equipment."""
    def __init__(self, attr: str):
        msg = f"{attr} is not a valid attribute in this context."
        if attr == 'ac':
            msg = f"Only wearable items can take an AC."
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

class InventorySectionNotFound(BambleweenyException):
    """Raised when trying to list something that is not a container or pre-defined inventory section."""
    def __init__(self, msg: str = "Inventory section not found."):
        super().__init__(msg)

class ItemNotFound(BambleweenyException):
    """Raised when an item can't be found in the inventory."""
    def __init__(self, msg: str = "Item not found."):
        super().__init__(msg)

class ItemNotMutable(BambleweenyException):
    """Raised on an attempt to change the attributes of an item when the context does not allow it."""
    def __init__(self, msg: str = "Item is not mutable."):
        super().__init__(msg)

class CharacterNotFound(BambleweenyException):
    """Raised when a character can't be found in the list of active characters."""
    def __init__(self, msg: str = "Character not found in the active list."):
        super().__init__(msg)

class AmbiguousMatch(BambleweenyException):
    """Raised when a search expression matches more than one item."""
    def __init__(self, msg: str = "Search expression is ambiguous, more than one result matches."):
        super().__init__(msg)

class UniqueItem(BambleweenyException):
    """Raised when there is an attempt to access more than one of the same item."""
    def __init__(self, msg: str = "Unique items can have only one instance."):
        super().__init__(msg)

class InvalidContainerItem(BambleweenyException):
    """Raised when there is an attempt to put an item in a container that cannot hold it."""
    def __init__(self, msg: str = "Item cannot be put in that container."):
        super().__init__(msg)

class NestedContainer(BambleweenyException):
    """Raised when there is an attempt to put a container inside another container."""
    def __init__(self, msg: str = "Containers cannot be nested."):
        super().__init__(msg)

class ContainerFull(BambleweenyException):
    """Raised when there is an attempt to add something to a container with insufficient capacity."""
    def __init__(self, msg: str = "Container full."):
        super().__init__(msg)

class ItemNotWieldable(BambleweenyException):
    """Raised when there is an attempt to wield an item that is not wieldable."""
    def __init__(self, msg: str = "Only weapons can be wielded."):
        super().__init__(msg)

class ItemNotWearable(BambleweenyException):
    """Raised when there is an attempt to wear an item that is not wearable."""
    def __init__(self, msg: str = "Only wearable items can be worn."):
        super().__init__(msg)

class NotWearingItem(BambleweenyException):
    """Raised when there is an attempt to take off an item that is not worn."""
    def __init__(self, msg: str = "Only items you are wearing can be taken off."):
        super().__init__(msg)

class CreditLimitExceeded(BambleweenyException):
    """Raised when there is insufficient funds."""
    def __init__(self, msg: str = "You do not have enough money."):
        super().__init__(msg)

class InvalidCoinType(BambleweenyException):
    """Raised when a coin type is unrecognised."""
    def __init__(self, msg: str = "Valid coin types are pp, gp, ep, sp, cp."):
        super().__init__(msg)

class MonsterNotUnique(BambleweenyException):
    """Raised when a unique method is called on a non-unique monster."""
    pass
