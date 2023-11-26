from textual.containers import Horizontal
from textual.widgets import Button, Label, Input, RichLog
from textual.message import Message


class LabelInput(Horizontal):
    """An input box with a label next to it."""

    _label: Label
    _input: Input
    _pos: int
    
    def __init__(self, label:str, pos:int, width:int=50):
        self._pos = pos
        self._label = Label(
            label,
            classes="common--label"
            )
        self._input = Input(
            id=f"in_{label.replace(' ','')}_{pos}",
            classes="common--input"
            )
        super().__init__(
            self._label,
            self._input,
            id=f"LblIn_{label}_{self._pos}",
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
    
    def __init__(self) -> None:
        super().__init__(
            label="Save",
            classes="common--button"
        )

