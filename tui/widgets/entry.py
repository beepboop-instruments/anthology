"""
Entry

Text input classes and functions.

"""

# Package imports
from __future__ import annotations
from dataclasses import field
from typing import List
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Button, Switch, Label, Select

# Module imports
from .common import AddButton, SubButton, SaveButton, LabelInput

class EntryForm(Static):
    """
    Custom widget to edit and store multiple parameters.
    """

    # List of entry parameters
    _params: list
    _pos: int
    
    def __init__(self, params: list, pos: int, id: str):
        self._params = params
        self._pos = pos
        super().__init__(
            id=id,
            classes="common--entryform"
            )
    
    def compose(self) -> ComposeResult:
        # Parameters
        for p in self._params:
            yield LabelInput(label=p, pos=self._pos)

class EntryRow(Static):
    """
    A row of object parameter entries.
    """
    
    # The formatted input list
    _entryform: EntryForm
    _select: Select
    _params: list
    _selection: list
    
    # Add and subtract buttons
    _add: AddButton
    _sub: SubButton
    
    # ID info
    _title: str
    _pos: int
    
    def __init__(self, params: list, selection: list(tuple), title: str, pos: int):
        self._params = params
        self._selection = selection
        self._title = title
        self._pos = pos
        super().__init__(
            id=f"{self._title}_{str(self._pos)}")
    
    def compose(self) -> ComposeResult:
        #self._selection.insert(0, ("New", "New"))
        self._entryform = EntryForm(self._params, pos=self._pos, id=f"entry_{self._title}_{self._pos}")
        self._select = Select(
            self._selection,
            prompt="New"
        )
        self._add = AddButton(id=f"add_{self._title}_{str(self._pos)}")
        self._sub = SubButton(id=f"sub_{self._title}_{str(self._pos)}")
        
        with Vertical(classes="common--entry-row"):
            yield self._select
            yield self._entryform
            with Horizontal(classes="common--button-row"):
                yield self._add
                if self._pos > 0:
                    yield self._sub
        
    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        select = self.query_one("Select")
        print(f"{self} : {self._select} : {select}")
        print(self._select.styles)
        print(select.styles)
        entryform = self.query_one("EntryForm")
        if event.value == None:
            entryform.display = True
        else:
            entryform.display = False

class EntryList(ScrollableContainer):
    """
    A vertical container for holding entry rows.
    """
    
    # Title of the entry section
    _title: str
    
    # Parameters
    _params: list
    _selection: list
    _rows: List = field(default_factory=EntryRow)
    _row_id: int
    
    def __init__(self, title: str, params: list, selection: list(tuple)):
        self._title = title
        self._params = params
        self._selection = selection
        self._row_id = 0
        self._rows = [EntryRow(self._params, self._selection, self._title, self._row_id)]
        super().__init__(
            classes="common--entrylist"
            )
        
    def on_mount(self) -> None:
        self._update_title()
        
    def compose(self) -> ComposeResult:
        for r in self._rows:
            yield r
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Add or subtract row based on button pressed.
        """
        # parse button id
        button_id = event.button.id
        button_id_row = int(button_id.split("_")[-1])
        row_id = f"{self._title}_{button_id_row}"
        
        if button_id[0:3] == "add":
            # add new row after the row where the add button was pressed
            self._row_id += 1
            new_row = EntryRow(self._params, self._selection, self._title, self._row_id)
            self._rows.append(new_row)
            self.mount(new_row, after=self.get_widget_by_id(row_id))
            new_row.scroll_visible()
        elif button_id[0:3] == "sub":
            # delete row where the sub button was pressed
            del_pos = int(button_id.split("_")[-1])
            del_row = self.get_widget_by_id(row_id)
            self._rows.remove(del_row)
            del_row.remove()
            
        self._update_title()
    
    def _update_title(self) -> None:
        """
        Pluralize or de-pluralize the title.
        """
        if len(self._rows) == 1:
            self.border_title = self._title
        else:
            self.border_title = self._title + "s"