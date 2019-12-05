# xC - aXes Controller

## Introduction
xC is a software to rule all robots.

### Screenshots
![x6](Screenshots/x6.png)

![Escriba](Screenshots/escriba.png)

<!--
## Videos
Watch this projects videos on [YouTube Playlist].
-->

## Changes
All notable changes to this project will be documented in this [Change log](CHANGELOG.md).

## Topology
![Topology](Documents/Pictures/xC.png)

## Terminology
- xC: aXes Controller, this software
- Host: The computer system running xC software
- Device: The device that will be controlled by xC, such as a robot, CNC, 3D Printer, and much more.
- User: It's you!

## Installation

### Download xC lastest version
``` bash
wget https://github.com/marcio-pessoa/xC/archive/0.58.zip
```

## Cloning
```
git clone --recurse-submodules https://github.com/marcio-pessoa/xC.git
```

### Uncompress
``` bash
unzip xc.zip
cd xc
```

### Install
``` bash
ansible-playbook xC.yaml
```

### Run
It's ready to run on Python 3.

Just type:
``` bash
xc
```

For help:
``` bash
xc -h
```

## Configuration file

### Macros
I recommend you use underline before macro name. It's usefull to quickly identify a macro.

### Keyboard map

To configure controls, take a look at [controls.md](Documents/controls.md).
