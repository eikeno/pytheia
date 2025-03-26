# Pytheia

## About

Pytheia is an image viewer, based on Python 3 and Gtk 3,  compatible with X11 and Wayland.

The primary goals are:
- being keyboard driven as much as possible
- as little GUI as possible, most action being intended to be perform via keybindings.

I started this around 2010 / 2011, as a pure hobby project to improve Python skills. It remained unmodified for huge periods of time, simply occasionally performing some changes to allow running on new stuff (Python3, Gtk3 etc.).

Expect uselessly complex code in many aspects, bugs - a lot of bugs, missing features, incoherent sections and so on.

I Hope being able to get things better in the future, even if I consider this project as low priority (working on it when I find some time).

I don't encourage PR for now, unless this is for very short, targeted bugfixes - not implementing new features or causing deep changes, because the project will possibly be revamped from the ground up (or not, may create new project name instead). 
In all cases, don't expect any quick feedback. 

## Features

- Supports all regular Gdk supported image formats (that's a lot), and also images in archives: tar / cbt, zip / cbt,  rar / cbr, 7z etc. often used for Comics.
- Supports parsing directories recursively.
- Supports a few utility plugins.
- Supports looping over given files / paths.
- Support being passed one or several directories as arguments, as well as one or more image files paths.
- Thumbnails view.
- Being borderless, integrates quite nicely with Tiling or Dynamic Window Managers such as Hyprland (haven't tried others personally, but should be OK as well).
- 
## How to run
Install was previously  using Setuptools, but I've discarded it for now. An installer is on the todolist (below).

For now I suggest to simply get files via __git clone__ or download the zip Zip file and run directly from there:

```
git clone https://github.com/eikeno/pytheia
cd pytheia
python3 pytheia [PATH]
```
Where __[PATH]__ is a path to a directory containing images, or path(s) to image(s).

### Usage
```
usage: pytheia.py [-h] [--debug] [--loop] [--fullscreen] [--recursive] ...

Pytheia image viewer

positional arguments:
  remainders

options:
  -h, --help    show this help message and exit
  --debug       Enable console debugging output
  --loop        Loop over path/files lists
  --fullscreen  force fullscreen display, overrides saved state
  --recursive   Recurse into directories
```

# Hypothetic TODO list
Far from exhaustive:

- clean installer
- port to GTK4
- implement type hints were possible
- add relevant unit tests
- revamp the plugin system completely to reduce dirty/unsafe hacks used in the code
- fix --recursive mode, to also match archives (tar, zip, cbz anc such) not only image files
- revamp debug functions to use logger (and also reduce verbosity, too much details given now)
- add CI/CD 

Have Fun !