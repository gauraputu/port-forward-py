from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class EditScreen(ModalScreen[dict | None]):
    CSS = """
    EditScreen {
        align: center middle;
    }

    EditScreen > Container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $accent;
        padding: 2 3;
    }

    EditScreen Label {
        margin-top: 2;
    }

    EditScreen Input {
        width: 100%;
    }

    EditScreen #error-label {
        color: $error;
        height: 1;
        margin-top: 1;
    }

    EditScreen #buttons {
        margin-top: 2;
        width: 100%;
        align-horizontal: right;
    }

    EditScreen Button {
        margin-left: 1;
    }
    """

    def __init__(self, initial: dict | None = None):
        super().__init__()
        self._initial = initial or {}
        self._is_edit = bool(initial)

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Name" if not self._is_edit else "Name")
            yield Input(
                value=str(self._initial.get("name", "")),
                placeholder="e.g. my-db-tunnel",
                id="name",
            )
            yield Label("Local Port")
            yield Input(
                value=str(self._initial.get("local_port", "")),
                placeholder="e.g. 5432",
                id="local_port",
                type="integer",
            )
            yield Label("Remote Host (user@host)")
            yield Input(
                value=str(self._initial.get("remote_host", "")),
                placeholder="e.g. user@db.example.com",
                id="remote_host",
            )
            yield Label("Remote Port")
            yield Input(
                value=str(self._initial.get("remote_port", "")),
                placeholder="e.g. 5432",
                id="remote_port",
                type="integer",
            )
            yield Static("", id="error-label")
            with Container(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Save", variant="primary", id="save")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return

        if event.button.id == "save":
            name = self.query_one("#name", Input).value.strip()
            local_port_str = self.query_one("#local_port", Input).value.strip()
            remote_host = self.query_one("#remote_host", Input).value.strip()
            remote_port_str = self.query_one("#remote_port", Input).value.strip()

            errors = []
            if not name:
                errors.append("Name is required")
            if not local_port_str:
                errors.append("Local port is required")
            if not remote_host:
                errors.append("Remote host is required")
            if not remote_port_str:
                errors.append("Remote port is required")

            local_port = 0
            remote_port = 0
            try:
                local_port = int(local_port_str)
                if local_port < 1 or local_port > 65535:
                    errors.append("Local port must be 1-65535")
            except ValueError:
                errors.append("Local port must be a number")
            try:
                remote_port = int(remote_port_str)
                if remote_port < 1 or remote_port > 65535:
                    errors.append("Remote port must be 1-65535")
            except ValueError:
                errors.append("Remote port must be a number")

            if errors:
                self.query_one("#error-label", Static).update("\n".join(errors))
                return

            self.dismiss({
                "name": name,
                "local_port": local_port,
                "remote_host": remote_host,
                "remote_port": remote_port,
            })