from rich.table import Table as RichTable
from rich import box


class Table(RichTable):
    def __init__(self, *args, **kwargs):
        # Remove the "show_header_column" attribute (doesn't exist in RichTable)
        show_header_column = kwargs.pop("show_header_column", True)

        # Rename the "show_header" attribute to "show_header_row"
        kwargs.setdefault("show_header", kwargs.pop("show_header_row", True))

        # Use "python -m rich.box" to see available boxes
        kwargs.setdefault("box", box.SIMPLE)

        super().__init__(*args, **kwargs)

        # Add a header column if show_header_column
        if show_header_column:
            self.add_column(style="bold")
