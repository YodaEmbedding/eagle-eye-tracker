## Eagle Eye Tracker

SFU Capstone Project (ENSC 405/440).

Group members: Mateen Ulhaq, Bud Yarrow, Arman Athwal, Naim Tejani, Victor Yun, Martin Leung

## Usage

Compile, download, and run the program on the NXT:

    nbc -d -r -S=usb nxt.nxc

Now simply:

    python eagleeyetracker.py

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

