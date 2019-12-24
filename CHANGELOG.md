# xc - aXes Controller

## Change log
All notable changes to this project will be documented in this file.

### [0.83] - 2019-12-16
#### Fixed
- Performance improvements.

### [0.8] - 2019-09-04
#### Removed
- Python 2 support.

### [0.77] - 2019-07-07
#### Added
- Ansible installer.
#### Removed
- Shell script installer

### [0.72] - 2019-01-08
#### Fixed
- Serial connection.

#### Fixed
- Pygame undesirable verbose message after ported to Python 3
- Terminal command doesn't display any keyboard input until Return is pressed

### [0.7] - 2019-01-01
#### Added
- Python 3 ready!

### [0.56] - 2018-07-27
#### Added
- Program run: Featured colours to 'ok' and 'nok' received strings.

### [0.50] - 2018-01-27
#### Added
- Screen resolution customization.

### [0.49] - 2017-11-11
#### Added
- Terminal line feed and carriage return customization for each project.
- Terminal local echo customization for each project.

#### Changed
- Supressed copyright messages from --version option.

### [0.48] - 2017-07-27
#### Added
- Memory information to GUI startup messages.

### [0.46] - 2017-07-20
#### Fixed
- Fan speed.

### [0.45] - 2017-06-01
#### Added
- Host platform machine detection.
- Status led blink when xc is running.

### [0.44] - 2017-06-28
#### Added
- Status LED control.

### [0.43] - 2017-06-26
#### Added
- Fan control and fan speed sensor.

### [0.42] - 2017-06-13
#### Added
- Detailed control start messages on GUI.

### [0.41] - 2017-06-02
#### Added
- Comment parser to caracter ';' in CommandParser().
- Comment parser to caracters "()" in CommandParser().

### [0.4] - 2017-05-22
#### Added
- Keyboard and mouse detection.

### [0.39] - 2017-05-17
#### Fixed
- Correction applied to joystick precision.

### [0.38] - 2017-05-12
#### Added
- Joystick support.

### [0.33] - 2017-05-11
#### Added
- Mouse support.

### [0.3] - 2017-05-10
#### Added
- Automatically build object from JSON definition.
- Keyboard support.

### [0.25] - 2017-05-08
#### Added
- Check for TrueType fonts on start up.

### [0.24] - 2017-04-30
#### Added
- list command can now show only connected devices.

### [0.2] - 2017-02-28
#### Added
- G-code runner next step is trigged to start when 'ok' string is received.

### [0.18] - 2017-02-27
#### Fixed
- Auto detection was overlapping explicit device ID definition.
- Command list performance issues

### [0.17] - 2017-02-26
#### Added
- Device auto connection.
- Check if external apps if found before execution.

### [0.16] - 2017-02-24
#### Added
- Device auto detection feature.

### [0.13] - 2017-02-21
#### Fixed
- Check files before open.
#### Added
- Display FPS (Frames Per Second) information on GUI.
#### Changed
- Preparing migration to Python 3.

### [0.12] - 2017-02-20
#### Added
- Improved graphics performance (class Gui).

### [0.1] - 2017-02-15
#### Added
- run option to execure programs on CLI.
- Argparse support.
#### Fixed
- Help messages and user input arguments and options.

### [0.09] - 2017-02-07
#### Changed
- Help messages optimization.

### [0.08] - 2016-05-26
#### Fixed
- Parameters used on miniterm.py to run on Ubuntu 16.04.

### [0.07] - 2015-08-08
#### Added
- CLI arguments now can by inputed using any order.
- Device check before run some actions.

### [0.05] - 2015-07-17
#### Added
- Terminal based on miniterm.py.

### [0.01] - 2015-02-06
#### Added
- First version
