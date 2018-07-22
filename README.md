[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.com/SicariusNoctis/eagle-eye-tracker.svg?branch=master)](https://travis-ci.com/SicariusNoctis/eagle-eye-tracker)

## Eagle Eye Tracker

SFU Capstone Project (ENSC 405/440).

Group members: Mateen Ulhaq, Bud Yarrow, Arman Athwal, Naim Tejani, Victor Yun, Martin Leung

![GUI](https://i.imgur.com/DR9QPH2.png)

[![Simulation video](https://i.imgur.com/yu5lwIm.jpg)](https://streamable.com/2h9tx)

This project features a general-purpose object tracking system. Typical applications include:

 - Sports tracking (ball, puck, racing car)
 - Photography (moving car shots, moon)
 - Film industry (automated tracking of subject with adjustable parameters, e.g. rule of thirds, smoothness)
 - Drone alert system

This project makes use of the following custom built physical system with 2 degrees of freedom (azimuth, elevation):

![Solidworks model](https://i.imgur.com/rIKo1Ei.jpg)

## Installation

Install the following:

 - [Anaconda 3](https://www.anaconda.com/download/) (with matplotlib, opencv, numpy)
 - Node Package Manager (npm)
 - Electron

Set your `PATH` environment variable to include the Anaconda 3 directory. It is recommended that you put this path at the beginning of `PATH`.

To install additional Python libraries used by this repository:

    python3 setup.py install

To install Electron:

    cd gui
    npm install --save-dev electron

Also, clone:

 - [Eagle Eye Darknet](https://github.com/SicariusNoctis/eagle-eye-darknet)

For NXT installation instructions, see [this version of README.md](https://github.com/SicariusNoctis/eagle-eye-tracker/blob/3c9088a68bd91fd6cdebefabef11c298f70b376a/README.md).

## Usage

We provide the following Make targets:

    make run_sim    # Run simulation on PC
    make run_gui    # Run GUI on PC
    make run_rpi    # Run on Raspberry Pi (ensure repo cloned onto rpi)
    make test       # Run tests
    make doc        # Build documentation
    make doc_run    # Build and view documentation

## Formal Documents

 - [Proposal](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1prop.pdf)
 - [Requirements](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1reqs.pdf)
 - [Design Specs](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1desi.pdf)
 - [Poster](http://www2.ensc.sfu.ca/~whitmore/courses/ensc305/projects/2018/1post.pdf)

