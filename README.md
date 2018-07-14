[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.com/SicariusNoctis/eagle-eye-tracker.svg?branch=master)](https://travis-ci.com/SicariusNoctis/eagle-eye-tracker)

## Eagle Eye Tracker

SFU Capstone Project (ENSC 405/440).

Group members: Mateen Ulhaq, Bud Yarrow, Arman Athwal, Naim Tejani, Victor Yun, Martin Leung

![GUI](https://i.imgur.com/DR9QPH2.png)

[![Simulation video](https://i.imgur.com/yu5lwIm.jpg)](https://streamable.com/kx8lq)

This project features a general-purpose object tracking system. Typical applications include:

 - Sports tracking (ball, puck, racing car)
 - Photography (moving car shots, moon)
 - Film industry (automated tracking of subject with adjustable parameters, e.g. rule of thirds, smoothness)
 - Drone alert system

This project makes use of the following custom built physical system with 2 degrees of freedom (azimuth, elevation):

![Solidworks model](https://i.imgur.com/rIKo1Ei.jpg)

## Installation

Install the following:

 - [Anaconda 3](https://www.anaconda.com/download/) (with matplotlib, opencv, numpy, ~~pyzmq~~)
 - ~~[Python 2](https://www.python.org/downloads/) (with pyusb, pyzmq, nxt-python)~~
 - ~~[BricxCC](http://bricxcc.sourceforge.net/test_releases/bricxcc_setup_33810_20130220.exe)~~
 - ~~[BricxCC test release](http://bricxcc.sourceforge.net/test_releases/test_release20131007.zip) (overwrite your existing BricxCC installation with this)~~
 - ~~[libusb-win32](https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/libusb-win32-devel-filter-1.2.6.0.exe) (install for port used by NXT USB)~~
 - ~~[NXT Fantom Drivers](https://www.lego.com/r/www/r/mindstorms/-/media/franchises/mindstorms%202014/downloads/firmware%20and%20software/nxt%20software/nxt%20fantom%20drivers%20v120.zip?l.r2=-964392510)~~
 - Node Package Manager (npm)
 - Electron

Also, clone:

 - [Eagle Eye Darknet](https://github.com/SicariusNoctis/eagle-eye-darknet)

To install additional Python libraries used by this repository:

    python3 setup.py install

To install Electron:

    cd gui
    npm install --save-dev electron

Set your `PATH` environment variable to include the following paths:

    Anaconda 3 installation directory
    Python 2   installation directory  [DEPRECATED]
    BricxCC    installation directory  [DEPRECATED]

To be sure that no other paths override these, it is recommended that you put these paths at the very beginning of your `PATH`.

~~Finally, be sure to upload the [NBC/NXC Enhanced Firmware](http://bricxcc.sourceforge.net/test_releases/lms_arm_nbcnxc_132_20130303_2051.rfw) to the NXT brick.~~

## Usage

We provide the following Make targets:

    make run_sim    # Run simulation on PC
    make run_gui    # Run GUI on PC
    make run_rpi    # Run on Raspberry Pi (ensure repo cloned onto rpi)
    make run_nxt    # Run on NXT and PC [DEPRECATED]
    make test       # Run tests
    make doc        # Build documentation
    make doc_run    # Build and view documentation

## Formal Documents

 - [Proposal](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1prop.pdf)
 - [Requirements](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1reqs.pdf)
 - [Design Specs](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1desi.pdf)
 - [Poster](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1post.pdf)

