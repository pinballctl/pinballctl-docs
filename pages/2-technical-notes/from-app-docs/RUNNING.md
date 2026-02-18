# Running pinballctl

This guide covers the supported ways to run the project:

- Local development (live/editable)
- Local install from a wheel (no source checkout)
- Install from a GitHub Release (3rd party style)
- (Future) Install from PyPI
- Managing services (systemd)
- Upgrading & uninstalling
- Troubleshooting

---

## Terminology

- **venv**: A per-project, isolated Python environment (recommended for everything).
- **Editable install** (`pip install -e .`): Runs your code “live” from the source folder—perfect for development.
- **Wheel** (`.whl`): A built package you can install without having the source repository.

---

## 1) Local Development (editable, “live”)

Best while you’re coding and testing changes.

```bash
# From the project root (where pyproject.toml lives)
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Run the app/bridge directly
pinballctl --version
pinballctl web --host 0.0.0.0 --port 5000
pinballctl bridge --port /dev/ttyUSB0 --baud 115200
```

**What this does**
- Installs an import link into `.venv` so edits to `src/pinballctl/...` take effect immediately—no rebuild needed.
- Installs the `pinballctl` CLI into `.venv/bin`.

**When to use**
- Daily development, quick iterations, working on features/bugfixes.

---

## 1b) Local Development + Services

You can also run your **dev build** under systemd:

```bash
# With the venv activated (created as above)
pinballctl service install                # renders venv-aware units, installs, enables, starts
pinballctl status                         # shows web/bridge states, Wi-Fi SSID/IP, ESP ports
```

- The installer prefers your current `.venv/bin` so services use the dev environment.
- When you change code, just restart services:
  ```bash
  pinballctl service restart all
  ```

**Great for**
- Testing real boot/lifecycle behavior with systemd, logs, restarts, etc.

---

## 2) Local Install from a Wheel (no source on target)

Package once, install anywhere—like a user would.

```bash
# On your dev machine (build once)
python -m venv .venv
source .venv/bin/activate
pip install build
python -m build
# -> dist/pinballctl-<ver>-py3-none-any.whl

# On the target (e.g., Pi)
python -m venv .venv
source .venv/bin/activate
pip install /path/to/dist/pinballctl-<ver>-py3-none-any.whl

# Optional services
pinballctl service install
pinballctl service start all
pinballctl status
```

**When to use**
- You want a clean installation without the source tree on the target machine.

---

## 3) Install from a GitHub Release (3rd party style)

After you publish a Release with attached artifacts:

```bash
python -m venv .venv
source .venv/bin/activate
pip install https://github.com/<you>/pinballctl/releases/download/vX.Y.Z/pinballctl-X.Y.Z-py3-none-any.whl

# Optional services
pinballctl service install
pinballctl service start all
pinballctl status
```

**When to use**
- Treat GitHub Releases as your “package registry.”
- Ideal for testers or other machines where you don’t want to build locally.

---

## 4) (Future) Install from PyPI

Once you publish:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pinballctl

pinballctl service install
pinballctl service start all
pinballctl status
```

**When to use**
- Public distribution with the simplest installation UX.

---

## Service Management (systemd)

All via the CLI:

```bash
# Install/uninstall units (venv-aware)
pinballctl service install
pinballctl service uninstall

# Control services
pinballctl service start|stop|restart web
pinballctl service start|stop|restart bridge
pinballctl service restart all

# Status (services, SSID/IP, ESP ports)
pinballctl status
```

**What service install does**
- Detects your `.venv/bin` and uses it for `ExecStart`.
- Creates a default `gunicorn.conf.py` in the working directory if missing.
- Copies rendered units to `/etc/systemd/system/`, runs daemon-reload, enables, and starts services.

---

## Upgrading

**Editable (dev) install**
```bash
# You’re running from source. Just edit files.
# If dependencies changed:
pip install -e .
pinballctl service restart all
```

**Wheel / Release / PyPI**
```bash
# Upgrade within the same venv
pip install --upgrade <wheel-or-package>
pinballctl service restart all
```

Examples:
```bash
pip install --upgrade pinballctl
# or from a new release:
pip install --upgrade https://github.com/<you>/pinballctl/releases/download/v0.2.0/pinballctl-0.2.0-py3-none-any.whl
```

*Tip:* bump the version in `pyproject.toml` for each release to avoid cache confusion.  
To reinstall the same version: `pip install --force-reinstall --no-deps <wheel-or-package>`.

---

## Uninstalling

```bash
# Stop and remove services
pinballctl service uninstall

# Remove the package from the active venv
pip uninstall pinballctl
```

---

## Troubleshooting

**`zsh: command not found: pinballctl`**
- You’re not in the venv or it’s not installed.  
  Activate and install:
  ```bash
  source .venv/bin/activate
  pip install -e .    # or pip install pinballctl / <wheel>
  ```
  Or run explicitly: `./.venv/bin/pinballctl`.

**Services don’t start**
- Check status/logs:
  ```bash
  pinballctl status
  journalctl -u pinballctl-web -e --no-pager
  journalctl -u pinballctl-bridge -e --no-pager
  ```
- Ensure `gunicorn` is installed in the same venv used by the services:
  ```bash
  . .venv/bin/activate && pip install gunicorn
  ```
- Reinstall units to point at the right venv:
  ```bash
  pinballctl service install
  ```

**ESP not detected**
- `pinballctl status` lists `/dev/ttyUSB*` and `/dev/ttyACM*`.  
  Check permissions: add your user to the `dialout` group (Debian/RPi OS):
  ```bash
  sudo usermod -a -G dialout $USER
  newgrp dialout
  ```
  Then try `pinballctl bridge --port /dev/ttyUSB0`.

**Network info missing**
- `status` uses `iwgetid`/`nmcli` and `hostname -I`. Install tools if needed:
  ```bash
  sudo apt install wireless-tools network-manager
  ```

---

## Quick decision table

| Goal | Best Method |
|------|-------------|
| Hack on code & test instantly | **Editable dev** (`pip install -e .`) |
| Deploy to a Pi with no source | **Wheel install** (local file or GitHub Release) |
| Public distribution | **PyPI** |
| Run as services | `pinballctl service install` + `pinballctl service start all` |
| Check everything | `pinballctl status` |
