# Change log
All notable changes to this project will be documented in this file.

## [0.71] - 2019-01-02
### Removed
- Bash completion.

## [0.7] - 2019-01-01
### Added
- Python 3 ready!

## [0.61b] - 2018-11-22
### Removed
- Kanban features.

## [0.59b] - 2018-11-12
### Added
- Method to check files before opening it.

## [0.58b] - 2018-08-19
### Added
- Bash completion.

## [0.57b] - 2018-08-15
### Added
- Kanban command line.

## [0.56b] - 2018-07-27
### Added
- Program run: Featured colours to 'ok' and 'nok' received strings.

## [0.55b] - 2018-07-18
### Fixed
- List: Was showing all devices when required to return only connected devices.

## [0.54b] - 2018-06-20
### Fixed
- Pong easter egg: Ball spawn to never raize balls without angle.

## [0.53b] - 2018-06-19
### Added
- Pong easter egg.

## [0.52b] - 2018-06-05
### Added
- System Core number.

## [0.51b] - 2018-04-02
### Changed
- Only configured interfaces are shown in verify or upload cli options.

## [0.51b] - 2018-02-11
### Added
- List only enabled devices (new configuration in devices.json).
### Changed
- List device link status on debug option 4 (no more 3).

## [0.50b] - 2018-01-27
### Added
- Screen resolution customization.

## [0.49b] - 2017-11-11
### Added
- Terminal line feed and carriage return customization for each project.
- Terminal local echo customization for each project.

### Changed
- Supressed copyright messages from --version option.

## [0.48b] - 2017-07-27
### Added
- Memory information to GUI startup messages.

## [0.47b] - 2017-07-20
### Fixed
- Fan speed correction.

## [] - 2017-07-18
### Added
Documentation.

## [] - 2017-06-01
### Added
- Host platform machine detection.
- Status led blink when xc is running.

## [] - 2017-06-28
### Added
- Status LED control.

## [] - 2017-06-26
### Added
- Fan control and fan speed sensor.

## [] - 2017-06-13
### Added
- Detailed control start messages on GUI.

## [] - 2017-06-04
### Fixed
- DevTools() program execution check.
- Comment parser to caracters "()" in CommandParser().

## [] - 2017-06-02
### Added
- Comment parser to caracter ';' in CommandParser().

## [] - 2017-05-22
### Added
- Keyboard and mouse detection.

## [] - 2017-05-19
### Added
- Joystick buttons support.

## [] - 2017-05-17
### Fixed
- Correction applied to joystick precision.

## [] - 2017-05-12
### Added
- Joystick support.

## [] - 2017-05-11
### Added
- Mouse support.

## [] - 2017-05-10
### Added
- Automatically build object from JSON definition.
- Keyboard support.

## [] - 2017-05-08
### Added
- Check for TrueType fonts on start up.

## [] - 2017-04-30
### Added
- list command can now show only connected devices using -c or --connected options. Type "xc list -h" for more information.
- PWA interface.
- More documentation.

## [] - 2017-04-03
### Changed
- Scape caracter on xc (shell script) starter program.

## [] - 2017-03-06
### Added
- list command can force check on a specific interface.

## [] - 2017-03-05
### Changed
- Removed unused code. 

## [] - 2017-02-28
### Added
- G-code runner next step is trigged to start when 'ok' string is received.

## [] - 2017-02-27
### Fixed
- Auto detection was overlapping explicit device ID definition.
- Command list performance issues

## [] - 2017-02-26
### Added
- Device auto connection.
- Check external apps before execution.
- Optimized and removed repeated code blocks.

## [] - 2017-02-24
### Added
- Device auto detection feature.

## [] - 2017-02-21
### Added
- Check files before open.
- Display FPS (Frames Per Second) information on GUI.
### Changed
- Some changes to support future migration to Python 3.

## [] - 2017-02-20
### Added
- Improved graphics performance with Class Gui.

## [] - 2017-02-19
### Changed
- Code optimization, moved message_list() funtionalities to UserArgumentParser() class list() method.

## [] - 2017-02-18
### Changed
- Migrated DevTools class to devtools package.

## [] - 2017-02-17
### Added
- Network interface definition on terminal option.

## [] - 2017-02-15
### Added
- Run programs on CLI.
- Argparse support.
### Fixed
- Help messages and user input arguments and options.

## [] - 2017-02-12
### Added
- Connection status is available to list command.

## [] - 2017-02-07
### Changed
- Echo class, to control message level (error, warning, information, code).
- Help messages optimization.

## [] - 2017-02-03
### Changed
- Project renamed to xC.

## [] - 2016-12-11
### Added
- Accepting IP address or host name to network functions.

## [] - 2016-05-26
### Fixed
- Parameters used on miniterm.py to run on Ubuntu 16.04.

## [] - 2016-04-12
### Changed
- Code optionazation, separated into some package files.

## [] - 2015-10-18
### Fixed 
- list option fixed.

## [] - 2015-09-11
### Added
- Availability check for libraries check before import.

## [] - 2015-08-19
### Changed
- JSON device file optimization and organization.

## [] - 2015-08-08
### Added
- CLI arguments now can by inputed using any order.
- Device check before run some actions.

## [] - 2015-07-19
### Added
- Default command line option changed to run.

## [] - 2015-07-17
### Changed
- Converted original Bash code to Python. All features ported.
- Terminal is now based on miniterm.py.

## [] - 2015-02-06
### Changed
- Project renamed to xC.

## [] - 2014-08-18
### Added
- Command option "run"

## [] - 2014-02-07
### Fixed
- Minor bug fix.

## [] - 2014-02-06
### Added
- First version written in Bash.
