# Hypeculator

Hypeculator is a fast, native desktop calculator for Linux. It uses Python and PySide6, with a compact dark interface and a Decimal-based calculation engine.

## Features

* Four basic operations, decimal input, percentage, sign change, and repeated equals.
* Clear handling of division by zero and recoverable error states.
* Shared calculation logic for keyboard input and on-screen buttons.
* Responsive compact window with a wide zero key.
* Linux desktop entry and `hypeculator` command-line launcher.

## Screenshot

![Hypeculator screenshot](assets/app.png)

## Install on Arch Linux

Install the required build tools:

```bash
sudo pacman -S --needed base-devel git
```

Clone Hypeculator:

```bash
git clone https://github.com/oxyth8/hypeculator.git
cd hypeculator/packaging/arch
```

Build and install:

```bash
makepkg -si
```

Run Hypeculator:

```bash
hypeculator
```

To uninstall:

```bash
sudo pacman -R hypeculator
```

## Requirements

For source installations:

* Python 3.11 or later
* PySide6

## Run from source

Clone the repository:

```bash
git clone https://github.com/oxyth8/hypeculator.git
cd hypeculator
```

Create a virtual environment and install Hypeculator:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
```

Run Hypeculator:

```bash
.venv/bin/hypeculator
```

Activating the virtual environment is optional when using its explicit launcher.

For development, this also works from the project root:

```bash
.venv/bin/python -m calculator
```

## Keyboard controls

| Key                | Action                       |
| ------------------ | ---------------------------- |
| `0`–`9`            | Enter a number               |
| `.` or `,`         | Enter a decimal separator    |
| `+`, `-`, `*`, `/` | Select an operation          |
| Enter, Return, `=` | Calculate                    |
| Delete             | Clear the calculation (`AC`) |
| Escape             | Close Hypeculator            |

Numpad number and operator keys use the same calculation actions.

## Desktop integration

The packaged desktop entry is [packaging/linux/hypeculator.desktop](packaging/linux/hypeculator.desktop).

System packages install the desktop entry to `/usr/share/applications/` and the application icon to `/usr/share/icons/hicolor/512x512/apps/`.

For a source checkout, `scripts/install-desktop-entry` installs a user-level launcher, icon, and `hypeculator` command. `scripts/uninstall-desktop-entry` removes only the files created for that checkout.

These scripts do not modify shell or compositor configuration files.

## Optional Hyprland rule

Hypeculator does not require Hyprland.

To keep it floating at a compact size, Hyprland users can optionally add:

```conf
windowrule {
    match:class = ^(hypeculator)$
    float = on
    center = on
    size = 360 560
}
```

## License

Hypeculator is licensed under the [MIT License](LICENSE).
