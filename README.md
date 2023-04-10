## Software-in-the-Loop for Autosar environment

This project demonstrates how to use Python to simulate the behavior of a Autosar application using a Software-in-the-Loop (SIL) approach. The Autosar application is compiled as a DLL (Dynamic Link Library) and loaded into the simulation environment. A virtual MCAL (Microcontroller Abstraction Layer) layer is also generated using textX and Jinja2, which allows for simulation of the hardware dependencies of the application.

## Installation

To use this project, you will need to have the following installed:

* Python 3.x - https://www.python.org/downloads/
* textX      - pip install textX
* Jinja2     - pip install Jinja2

Once you have these dependencies installed, you can clone this repository and run the main.py script.

## Usage

To use this project, you will need to provide an Autosar application as a DLL compiled with vMCAL functions. You can specify the path to the DLL in the config.ini file. The main.py script will load the DLL and use it to simulate the behavior of the application.

## Generating the Virtual MCAL Layer

To generate the virtual MCAL layer, you will need to modify the mcal.tx file. This file specifies the structure of the virtual MCAL layer using the textX syntax. Once you have modified this file, you can run the generate_mcal.py script. This script uses textX and Jinja2 to generate the virtual MCAL layer code.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
