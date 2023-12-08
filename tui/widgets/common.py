from textual.containers import Horizontal
from textual.widgets import Button, Label, Input, RichLog
from textual.message import Message


class LabelInput(Horizontal):
    """An input box with a label next to it."""

    _label: Label
    _input: Input
    
    def __init__(self, label:str, id:str):
        self._label = Label(
            label,
            classes="common--label"
            )
        self._input = Input(
            id=id,
            classes="common--input"
            )
        super().__init__(
            self._label,
            self._input,
            classes="common--horizontal"
            )
        
class AddButton(Button):
    """A basic + button."""
    
    def __init__(self, id) -> None:
        super().__init__(
            label="+",
            id=id,
            classes="common--add-sub"
        )
        
class SubButton(Button):
    """A basic - button."""
    
    def __init__(self, id) -> None:
        super().__init__(
            label="-",
            id=id,
            classes="common--add-sub"
        )

class SaveButton(Button):
    """A basic Save button."""
    
    def __init__(self, id) -> None:
        super().__init__(
            id=id,
            label="Save",
            classes="common--button"
        )

