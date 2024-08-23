from typing import Coroutine
from textual.app import ComposeResult, App
from textual.binding import Binding
from textual.widgets import Label, Input, DataTable, Footer, Static
from rich.json import JSON
from textual.events import Event, Paste
from textual import work
from textual.reactive import reactive
from typing import Literal

# from header import FlameshowHeader
from ttui.lib.utils import pick_parser
#custom
from ttui.screens.modals import ModalAboutDialog, ModalInputDialog, ModalJumpDialog
from ttui.screens.about import about_text

class MyApp(App):
    BINDINGS = [
        Binding("i", "show_input_dialog", "Input Dialog"),
        Binding("a", "show_about_dialog", "About Dialog"),
        Binding("j", "show_jump_dialog", "Jump Dialog"),
    ]

    def __init__( self, in_filename: str, type : Literal['dict', 'tuple', 'list']) -> None:
        super().__init__()
        self.in_filename = in_filename
        self.type = type

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Static(id="content", expand=True)
        yield Footer()

    def action_show_input_dialog(self) -> None:
        self.push_screen(ModalInputDialog("Enter your name:"))

    def action_show_about_dialog(self) -> None:
        self.push_screen(ModalAboutDialog(about_text))

    def action_show_jump_dialog(self) -> None:
        self.push_screen(ModalJumpDialog("Jump to:"))

    def on_mount(self) -> None:

        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        self.load_txt_file()


    def on_paste(self, event : Paste):
        print("CONSOLE DEBUG", event.text)
        # self.query_one("#content").update(JSON(files))


    def get_parser(self, type: str):
        return pick_parser(type=type)
    
    @work(thread=True)
    def load_txt_file(self):
        table = self.query_one(DataTable)
        parser = self.get_parser(self.type)


        with open(self.in_filename, "r") as f:
            lines = f.readlines()

            if len(lines) < 1:
                raise ValueError("Your file is too empty, try a larger .txt file.")

            _ = parser(lines[0])
            #should have a parse function to return a iterator
            if self.type == "dict":

                #only add a column if we have a dict type since tuples don't
                #anything to identify it, same for list
                for col in tuple(_):
                    table.add_column(str(col), key=str(col))

                for line in lines:
                    converted_dict  = parser(line)
                    table.add_row(*tuple(converted_dict.values()))
            else:
                #add a filler column for the index if list or tuple
                for i in range(len(_)):
                    table.add_column(str(i), key=str(i))

                for line in lines:
                    converted = parser(line)
                    table.add_row(*tuple(converted))

        if "points" in table.columns:
            table.sort("points")
        else:
            print("Column 'points' does not exist in the table.")

    # def action_todoactions
if __name__ == "__main__":
    MyApp().run()