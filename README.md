# portforwarder

TUI for managing SSH port forwarding tunnels, built with [Textual](https://textual.textualize.io/).

## Install

```bash
uv tool install .
```

## Dev Run (no install)


```bash
uv run python -m portforwarder
```
## Usage

```bash
portforwarder
```

## Keybindings

| Key              | Action                          |
|------------------|---------------------------------|
| `Space` / `Enter` | Toggle selected tunnel on/off  |
| `a`              | Add new tunnel                  |
| `e`              | Edit selected tunnel            |
| `d`              | Delete selected tunnel          |
| `q`              | Quit                            |

## Configuration

All tunnels are saved to `~/.port-forward/config.json`. Each entry has:

- **Name** — display label
- **Local Port** — port on your machine
- **Remote Host** — SSH destination (`user@host`)
- **Target Host** — host to reach from the remote side
- **Remote Port** — port on the target host

The SSH command run is:

```
ssh -N -L <local_port>:<target_host>:<remote_port> <remote_host>
```

## Port Collision

Turning on a tunnel with the same local port as an active one will auto-stop the old tunnel and start the new one. All tunnels are stopped when the TUI closes.
