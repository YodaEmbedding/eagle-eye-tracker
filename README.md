## Eagle Eye Tracker

SFU Capstone Project (ENSC 405/440).

Group members: Mateen Ulhaq, Bud Yarrow, Arman Athwal, Naim Tejani, Victor Yun, Martin Leung

## Installation

Install the following:

 - [Anaconda 3](https://www.anaconda.com/download/) (with opencv, numpy, pyzmq)
 - [Python 2](https://www.python.org/downloads/) (with pyusb, pyzmq, nxt-python)
 - [BricxCC](http://bricxcc.sourceforge.net/test_releases/bricxcc_setup_33810_20130220.exe)
 - [BricxCC test release](http://bricxcc.sourceforge.net/test_releases/test_release20131007.zip) (overwrite your existing BricxCC installation with this)
 - [libusb-win32](https://sourceforge.net/projects/libusb-win32/files/libusb-win32-releases/1.2.6.0/libusb-win32-devel-filter-1.2.6.0.exe) (install for port used by NXT USB)
 - [NXT Fantom Drivers](https://www.lego.com/r/www/r/mindstorms/-/media/franchises/mindstorms%202014/downloads/firmware%20and%20software/nxt%20software/nxt%20fantom%20drivers%20v120.zip?l.r2=-964392510)
 - Node Package Manager (npm)
 - Electron

Set your `PATH` environment variable to include the following paths:

    Anaconda 3 installation directory
    Python 2   installation directory
    BricxCC    installation directory

To be sure that no other paths override these, it is recommended that you put these paths at the very beginning of your `PATH`.

Finally, be sure to upload the [NBC/NXC Enhanced Firmware](http://bricxcc.sourceforge.net/test_releases/lms_arm_nbcnxc_132_20130303_2051.rfw) to the NXT brick.

## Usage

Compile, download, and run the program on the NXT:

    nbc -EF -S=usb -d -r nxt.nxc

Now simply:

    python eagleeyetracker.py

To run the GUI, first ensure that Electron is present:

    cd gui
    npm install --save-dev electron

Then simply run:

    npm start

## TODO

Tracking:

 - Keep track of current position (using motor encoders)
 - Use Bud's formulas (e.g. dphi = dx / sin(curr.th); dth = dy + curr.th * sec(dphi) - ...)
 - Separate setpoint updating and PID motor control loop
 - RK4 prediction
 - PID motor control
 - Advanced control system
 - Deal with singularity at north pole (special case; unstable behavior; numerical stability)

General:

 - Write right proper robust code

## Formal Documents

 - [Proposal](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1prop.pdf)
 - [Requirements](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1reqs.pdf)
 - [Design Specs](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1desi.pdf)
 - [Poster](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1post.pdf)

