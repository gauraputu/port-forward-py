from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header

from .config import ForwardEntry, load_entries, save_entries
from .screens.edit_screen import EditScreen
from .tunnel import TunnelManager


class PortForwardApp(App):
    TITLE = "Port Forward"
    BINDINGS = [
        Binding("space,enter", "toggle", "Toggle", show=True),
        Binding("a", "add", "Add", show=True),
        Binding("e", "edit", "Edit", show=True),
        Binding("d", "delete", "Delete", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    DataTable {
        height: 1fr;
    }
    """

    def __init__(self):
        super().__init__()
        self._entries: list[ForwardEntry] = []
        self._tunnel = TunnelManager()

    def on_mount(self) -> None:
        self._entries = load_entries()
        dt = self.query_one(DataTable)
        dt.cursor_type = "row"
        dt.add_column("Status", width=8)
        dt.add_column("Name")
        dt.add_column("Forward")
        self._refresh_table()
        self.set_interval(2, self._refresh_table)

    def compose(self) -> ComposeResult:
        yield Header()
        dt = DataTable()
        dt.cursor_type = "row"
        yield dt
        yield Footer()

    def _refresh_table(self) -> None:
        dt = self.query_one(DataTable)
        dt.clear()
        for entry in self._entries:
            running = self._tunnel.is_running(entry.id)
            status = "[green]● ON[/]" if running else "[dim red]● OFF[/]"
            forward = f"{entry.local_port} → {entry.remote_host}:{entry.remote_port}"
            dt.add_row(status, entry.name, forward)

    def _stop_colliding(self, entry: ForwardEntry) -> list[str]:
        stopped: list[str] = []
        for other in self._entries:
            if other.id == entry.id:
                continue
            if other.local_port == entry.local_port and self._tunnel.is_running(other.id):
                self._tunnel.stop(other.id)
                stopped.append(other.name)
        return stopped

    def action_toggle(self) -> None:
        dt = self.query_one(DataTable)
        if dt.row_count == 0 or dt.cursor_row is None:
            return
        idx = dt.cursor_row
        entry = self._entries[idx]

        if self._tunnel.is_running(entry.id):
            self._tunnel.stop(entry.id)
            self.notify(f"Stopped: {entry.name}")
        else:
            stopped = self._stop_colliding(entry)
            ok, err_msg = self._tunnel.start(entry)
            if ok:
                msg = f"Started: {entry.name}"
                if stopped:
                    msg += f" (auto-stopped: {', '.join(stopped)})"
                self.notify(msg)
            else:
                err = err_msg or "unknown error"
                self.notify(f"Failed: {entry.name} — {err}", severity="error")

        self._refresh_table()

    def action_add(self) -> None:
        self.push_screen(EditScreen(), self._on_add_done)

    def action_edit(self) -> None:
        dt = self.query_one(DataTable)
        if dt.row_count == 0 or dt.cursor_row is None:
            return
        idx = dt.cursor_row
        entry = self._entries[idx]
        self._tunnel.stop(entry.id)
        initial = {
            "name": entry.name,
            "local_port": str(entry.local_port),
            "remote_host": entry.remote_host,
            "remote_port": str(entry.remote_port),
        }
        self.push_screen(EditScreen(initial), lambda result: self._on_edit_done(idx, result))

    def action_delete(self) -> None:
        dt = self.query_one(DataTable)
        if dt.row_count == 0 or dt.cursor_row is None:
            return
        idx = dt.cursor_row
        entry = self._entries[idx]
        self._tunnel.stop(entry.id)
        self._entries.pop(idx)
        save_entries(self._entries)
        self._refresh_table()
        self.notify(f"Deleted: {entry.name}")

    def _on_add_done(self, result: dict | None) -> None:
        if result is None:
            return
        self._entries.append(ForwardEntry(
            name=result["name"],
            local_port=result["local_port"],
            remote_host=result["remote_host"],
            remote_port=result["remote_port"],
        ))
        save_entries(self._entries)
        self._refresh_table()

    def _on_edit_done(self, idx: int, result: dict | None) -> None:
        if result is None:
            return
        entry = self._entries[idx]
        entry.name = result["name"]
        entry.local_port = result["local_port"]
        entry.remote_host = result["remote_host"]
        entry.remote_port = result["remote_port"]
        save_entries(self._entries)
        self._refresh_table()

    def on_unmount(self) -> None:
        self._tunnel.stop_all()


def main() -> None:
    app = PortForwardApp()
    app.run()