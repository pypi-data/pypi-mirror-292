from typing import Coroutine
from textual.app import ComposeResult, App
from textual.binding import Binding
from textual.widgets import Label, Input, DataTable, Footer, Static
from rich.json import JSON
from textual.events import Event, Paste
from textual import work
from textual.reactive import reactive
# from header import FlameshowHeader
from ttui.lib.utils import parse_dict


#custom
from ttui.screens.modals import ModalAboutDialog, ModalInputDialog, ModalJumpDialog
from ttui.screens.about import about_text

"""
run pipelines to analyze video part!

video format ->
(time stamp in video, "file_path", above average score, total score),

"""

data = r"E:\Projects\2024\Video-Content-Pipeline\output-video\private\cery\text_cache\analyze_data.txt"


class MyApp(App):
    BINDINGS = [
        Binding("i", "show_input_dialog", "Input Dialog"),
        Binding("a", "show_about_dialog", "About Dialog"),
        Binding("j", "show_jump_dialog", "Jump Dialog"),
    ]


    def __init__( self, in_filename: str ) -> None:
        super().__init__()
        self.in_filename = in_filename

    def compose(self) -> ComposeResult:

        # yield FlameshowHeader("test, test21")
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

    @work(thread=True)
    def load_txt_file(self):
        table = self.query_one(DataTable)

        with open(self.in_filename, "r") as f:
            lines = f.readlines()

            if len(lines) < 1:
                raise ValueError("Your file is too empty, try a larger .txt file.")

            _ : dict = parse_dict(lines[0])
            #should have a parse function to return a iterator

            for col in tuple(_):
                table.add_column(col, key=col)
            for line in lines:
                converted_dict : tuple = parse_dict(line)
                table.add_row(*tuple(converted_dict.values()))

        if "points" in table.columns:
            table.sort("points")
        else:
            print("Column 'points' does not exist in the table.")




    # def action_todoactions
if __name__ == "__main__":
    MyApp().run()