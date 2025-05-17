# Airy

> The hands-free desktop experience.

Control your mouse with just your hands and the camera.

## Install

To install make sure you have python3.12. Then setup the environment and install necessary dependencies.

### Environment

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install pip --upgrade
python -m pip install -r requirements.txt
```

### CLI Dependencies

The current code is designed to work with `Hyprland` and `ydotool`. Feel free to edit the code in `src/motion/` to get the motions to work with your desktop setup. Otherwise install necessary components.

On Arch Linux,

```sh
yay -S Hyprland ydotool
systemctl --now enable ydotool.service
```

_Note: Obviously swapping workspaces only work if Hyprland is active_

### Run

To run the program,

```sh
python src/main,py
```

## Gestures

### Swap Workspace

With an open palm on your right hand, smoothly drag your hand in one direction.

### Move Mouse

Pointing your right index finger up, move your hand around.

### Click

Point your left index finger up to left click.
