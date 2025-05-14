# Technical Design Doc: L4 Buoy Instrument Management & Control System

## Summary
The Instrument Management and Control System is an electronic control system designed for the Western Channel Observatory's (WCO) offshore long-term monitoring stations to manage power and log data from commissioned sensing instruments. The system provides multi-channel power distribution delivered to independent payload channels each with an optional analog/digital data interface for logging data to an industrial processor. Collected data is mirrored locally and transmitted remotely using a secure and redundant communication solution. The computer operates a power management system composed of a micro controller and an array of power management modules that measure voltages and electrical currents in each channel to monitor the power consumption of each attached system. 



## Background
The position of a robot in the physical world becomes the building block of collective information processing. In a recent work Litus et al. (2007) give a good summary of this idea: 

"The key insight that underlies our methods is that the physical locations of the robots themselves could be considered as an approximate solution to the entire problem. An individual robot can move itself, thus refining the current solution approximation. No representation of the problem, or the current solution, needs to be held by any robot: they manifest the solution by their physical configuration."

Modern mooring platforms are equipped with large arrays of sensing and communication equipment responsible for in-situ monitoring and scheduled data telemetry to local and remote destinations. These platforms, effectively robots, are now equipped with battery banks and possibly input generation sources to keep installed systems running. 

Common technical challenges that arise are instrument reliability;  interoperable payload systems integration; and effective systems monitoring (e.g. power consumption) onboard the platform.  The result of these incur heavy cost on the maintenance and upkeep of these platforms as they increase in size and complexity, and also as they degrade in production. The design emphasis of the IMCS focuses on these challenges by providing a suite of peripheral interfaces and flexible remote power management tools that provides an effective way to monitor and upkeep many 'system of systems'.  

## Problem
The IMCS is motivated by the need for a robust control system that can operate under minimal supervision and with low maintenance cycles at sea for long periods of time (>1year). 

In summary, the system should be equipped with the capability of data acquisition from integrated sensors; storage and telemetry of the data to a remote location; and the means to remotely monitor the platform's integrity. (It must do this very well)

Base requirements of the system:

- Provide stable power to attached payload instruments
- 'Plug and play' requirements for instrument testing
- Remote monitoring and configuration through a robust telemetry solution
- Low power: ideally should be sustainable within platform power constraints  (12V, 600Ah System with power generation dependent on solar/wind).
- Support a variety of low voltage systems (3.3V, 5V, 12V, 24V)
- Operate on platforms at sea for long periods (over one year)
The system should be modular so that it is easy to maintain and replace components during faults. 

The system must be designed to be supplied by a 12V 600Ah battery supply that is occasionally charged by an array of 12V 400W solar panels and a 12V 300W wind turbine. 

The system must have independent power distribution channels that protect the main components and payload channels with the appropriate safety circuity.

All components to be appropriately weathered for the environment, i.e. securely fastened in a ventilated watertight enclosure with regular refreshment of desiccants to maximize lifetime in harsh environments. 

Successful execution of this system will increase the productivity of this platform and reduce the cost to operate and maintain. Use of vessels for access will be minimized.



## Hardware Design
The system's primary purpose is to collect data and manage power. Collected data is to be transferred to shore using a provided telemetry solution.

Data is collected using industrial grade hardware. Telemetry from RS232, RS422, and RS485 protocols is handled by a USB Serial hub (Startech) and raw analog data is acquired through a 16bit ADC unit (ADAM-4017). Both systems are connected to a ruggedized PC (Cincoze) via USB and provide the data interface for attached instruments.

Power is managed using automotive grade hardware (infineon). A microcontroller (TC37X) is used to drive a series of power management modules (4xBTS7002-1EPP), each with a number of channels that provide power switching and current measurement via the microcontroller's I/O pins.  

The provided telemetry solution (Persistent systems) is a MIL-STD industrial grade MIMO radio with an Android computing stack (MPU5), adapted by Steatite (MMCU) for rugged use in marine environments.. This allows extension of local network systems over an L-Band communication link optimized for harsh and dynamic environments. This is connected to an 8-port L3 network switch (Ubiquiti ES-10X) to provide a communication interface for the ruggedized PC. Systems are linked to shore for control.



![imcs_hardware_schematic_v2.png](https://eraser.imgix.net/workspaces/OEOqimrT80VpRjrgjewf/rxf125FmeEfeL8oKbBgtvaDVbrf2/URj6JOQTlaT3G1GxdkOth.png?ixlib=js-3.7.0 "imcs_hardware_schematic_v2.png")



[﻿Figure 1: Architecture](https://app.eraser.io/workspace/OEOqimrT80VpRjrgjewf?elements=i4wirb4W51OwV3rgmQQcUQ) 

**System Power Supply:**

The system is powered from the onboard 12V 600Ah battery bank, regulated by a Tarom-4545 solar controller to 12V 45A through its load terminals. This is further protected by a C32A MCB with 2-core 6mm^2 CSA cable routing to the enclosure. The supply ground is used as the reference earth and the inner mounting plate is the chassis to which the earth is connected.

**System Power Distribution:**

The supply cable is connected to an array of 5 MCBs rated to 6A, wired with 2.0mm^2 CSA. One breaker protects the main control system with one breaker protecting each power management module. 

**Main Control System:**

The main control system is an Hitex Shieldbuddy TC375 - a tri-core 32bit microcontroller using an arduino compatible form factor. It is regulated by an onboard PMIC safety monitor and it has 4 UART ports, one of which connects to a Cincoze DA-1100 x86 rugged PC via USB-Serial. Another is connected to a Waveshare serial to ethernet gateway. 

16 Digital pins are connected to drive four 4-channel infineon PROFET 12+ power modules, with additional pins connected for toggling diagnostics and reading analog current sense pins.

Each power management module has 4 subchannels. Each subchannel is composed of a BTS7006-1EPP fused high-side switch with current sensing rated to 12.5A for power monitoring and remote switching. 

**Load Power Management:**

The source of each PMM subchannel is wired to an individual fused terminal block with 5A automotive fuses for additional protection. All payload channels are grounded to a terminal block common with the supply ground.

**Data Acquisition:**

Data acquisition is performed by interfacing payload instruments with a Startech multi-channel serial to usb hub. This supports RS-232, 422, 485, and MODBUS. An ADAM-4017 ADC module is integrated for potential analog sensors. Other interfaces (I2C, CAN, LIN, SPI, LVDS) are also available through the micro controller.

Data from the interfaces is collected by the PC. This also receives power and instrument status data from the micro controller via its USB serial connection. Collected data is mirrored onto a secondary SSD and synced to PML's shore servers every hour through the onboard switch. This platform will utilize an L-Band radio and forward data to a relay station, ultimately landing at PML.

[﻿Figure 2: Hardware Schem atic](https://app.eraser.io/workspace/OEOqimrT80VpRjrgjewf?elements=2PX1-MgarYixlvu5xlC6uA) 



**Networking and Telemetry:**

The PC and microcontroller's S2E (Serial to Ethernet) gateway are connected to a ubiquiti ES-10X network switch. During normal operation the PC will run a script to automatically collect data and make decisions regarding power management. The device can be interfaced via remote-access to the PC for standard administration, or directly via the S2E as a backup. 



**Payload Sensors:**

The platform must support a core set of payload instrumentation, with room to integrate additional sensors. Core payload sensors to be supported are in-water CTD, pH, surface PAR and network camera systems. 

The network cameras are connected to the platform's LAN via ethernet into the network switch, allowing the PC to collect image data through the camera's RTSP mode. 

The CTD and pH telemeter via RS-232 and stream data to one of the Startech serial interfaces for the PC to access over USB. 

The PAR sensor streams an analog signal to the ADAM ADC. The computer polls the ADC over an RS-485 connection for the PC to access over USB.

[﻿Figure 3: Systems Diagram](https://app.eraser.io/workspace/OEOqimrT80VpRjrgjewf?elements=0cdnOtKN6_5c0JdJuuJ4wg) 

![l4_buoy_system_diagram(1).png](https://eraser.imgix.net/workspaces/OEOqimrT80VpRjrgjewf/rxf125FmeEfeL8oKbBgtvaDVbrf2/P6J8tHIxYJ1EDtymL_1wK.png?ixlib=js-3.7.0 "l4_buoy_system_diagram(1).png")



 For additional instruments, a systems integration plan should be formulated to highlight the feasibility and necessary work to commission, operate and maintain. See "Further Systems Integration".

## Software Design
**Power Management Software**

The microcontroller was programmed with standard C++, utilizing additional low level driver libraries developed, tested and maintained by Infineon. The microcontroller initializes the I/Os for controlling the power management modules and streams information about each module: It reports the voltage of each module all channel states and current sense values to the onboard PC via USB Serial. The controller is programmed with a simple CLI can also be polled for this information and sent commands to toggle the state of or cycle a channel.  A secondary UART link is connected to a serial to ethernet gateway to provide a backup telemetry to the controller's CLI. 



![l4_buoy_power_management_flowchart(1).png](https://eraser.imgix.net/workspaces/OEOqimrT80VpRjrgjewf/rxf125FmeEfeL8oKbBgtvaDVbrf2/-0BvAK94dCsAi8pT1NQ8_.png?ixlib=js-3.7.0 "l4_buoy_power_management_flowchart(1).png")





A python script is used for the microcontroller information logging but also provides the ability to send commands manually/automatically. The supervision script onboard the PC uses this script to make decisions in order to automatically manage sensor power effectively.

The supervision script triggers on an automatic schedule to power on instruments and acquire data. It also digests power information from the power management modules. Each instrument channel is allocated a daily maximum power usage. If the channel exceeds this value, the system raises an alert to shore regarding excess power usage. 

The BTS7002-1EPPs are supplied by the solar controller output , which is used for the internal logic as well as supply for the power output stage. Each module has an undervoltage detection circuit, which prevents the activation of the power output stage and diagnosis in case the applied voltage is below the undervoltage threshold (VS < VS(OP) ). During power up, the internal power on signal is set when supply voltage exceeds the set minimum operating voltage. 

Therefore the system is adaptive to the case that the onboard battery levels measured by the micro controller drop close to the deep discharge protection cutoff set by the solar controller module.

A scheduling program onboard the datalogger PC(cron) will invoke rsync on an automatic schedule (@hourly) to copy backups of any collected data to a secondary SSD. A shore-based PC will be set up with an automatic sync to pull data from the platform. 



**Data Collection Software**

The onboard PC operates on Windows 10 and contains python scripts that passively log data from a payload instrument connected to a serial/analog peripheral. These are simple scripts that utilize PySerial to access the data acquisition hardware interfaces to listen for data streamed from a specified instrument. The Logging module is used to provide rolling logs in ISO-8601 format. 



![l4_buoy_data_logging_flowchart(1).png](https://eraser.imgix.net/workspaces/OEOqimrT80VpRjrgjewf/rxf125FmeEfeL8oKbBgtvaDVbrf2/FCzOquURORWIBVUNbXVtv.png?ixlib=js-3.7.0 "l4_buoy_data_logging_flowchart(1).png")





The base python scripts only consider the case of instruments streaming data on power-on without initial configuration.  Additional software must be implemented for instruments requiring initial configuration. 

Sometimes logged data is pre-calibrated by the instrument whereas some sensors provide raw measurements that require further processing. Additional software will be required to process the data from these sensors.

**Data Processing Flow**

The data collected from each of the core instruments is staged into raw and partially processed data, this is clearly defined by the following staging process which occurs locally onboard the platform:

- Level 0 Data: Raw files acquired directly from an instrument's telemetry interface and stored onboard the platform PC's primary and secondary storage in a basic format (i.e. "C:\data\instrument\instrument_data.dat"). Some of this data may already be calibrated due to onboard sensors, whereas some data will need to be converted with the appropriate calibration files.
- Level 1 Data: Accumulated files for each instrument over a 24hrs are collapsed into a single file (labelled as 'daily' file) containing a statistically filtered representation of the data. This will provide, in 1hr intervals, a mean and standard deviation for each measurement made by the instrument. Each instrument's daily file is then used to create a final daily file containing column separated hourly measurements of all considered instruments.
## Considerations and Remarks
### Test plan
What are the failure scenarios we are going to cover in our testing?

A base case of failure scenarios proposed:

> When a payload sensor is unresponsive

> When a main system component is unresponsive

> When remote data sync fails

> When scheduled or platform communications fail (temporary + permanently) 

> When primary and/or secondary control systems are inoperable for a length of time 

> When the platform is unresponsive for a sustained period of time (At what point do we decide field intervention, how do we best approach this economically?)

### Security and Maintenance
**Physical security** 

At sea restricted to cases where the mooring platform is at risk of collision or targeted for vandalism/salvage. In the former case, the platform is equipped with a navigation light and is a special mark on marine charts.

During site visits, any external marks/damage to the floats, chains, lifting eyes or mast/crown should be documented and monitored.

Mechanical hardware bolted on the crown should be checked during maintenance visits when possible. Additional mounts used to connect equipment (e.g. antennas, turbines) to crown fittings should also be checked. 

Electronics are mechanically bolted within IP65 rated enclosures with desiccants to maximize their lifetime. Consider further enclosing exposed electronics within the master enclosure.

Securing bolts and fasteners inside the mast should be checked and tightened if required during scheduled maintenance. Integrity of any enclosures should be monitored during maintenance visits to avoid potential heavy water ingress, ensuring that they are and can be closed properly.

Moonpool sensors and mounts should be inspected as well as possible and adjusted if necessary. 

**Software/Firmware Security:**

Critical platform systems must not be regularly updated during active commissioning, nor should any live integration testing of instruments/ software onboard the payload computer be performed. This may cause instability if not shore-tested to some levels of satisfaction. Advisable to test on a shore-based clone of the system as part of a full integration test. 

**Network security: **

The network switch provides a LAN for the PC and other connected devices. This is also where the telemetry gateways are connected. The switch sits on OSI Layer 3 and has VLAN capabilities to partition the platform's LAN appropriately if required. The main telemetry solution uses distributed end to end communication encrypted over OSI Layer 2 with high fault tolerance subject to good architecture practice and node density.

In situ (GPS Coords), the closest neighbour to the telemetry node are the directional antennae situated at the Rame Head NCI relay station. These antennae are connected to a network switch inside a cabinet at the relay station (get pics from jani) and route back over an underground EAD (Ethernet access direct) link to a demarcation device situated in PML's basement.

An ML-NGFW (Machine learning power next generation firewall) restricts the communications from this demarcation point such that only authorised PML can make outgoing connections to  registered devices and their services. This reduces the attack surface on PML's infrastructure and prevents untrusted traffic from entering PML. This remark deserved explanation as this defines the strategy of data transfer: data polling from PML-based systems. This architecture means that further setup must be required in order to automatically pass data from platform systems through to PML.

### Documentation changes
A list of core instruments and auxiliary instruments (instruments excel sheet)

A power budget of the main system and payload sensors

Completion of hardware diagrams, additional diagrams and software flowcharts, software UML diagrams 

Setup of CI/CD for L4 systems



## Definition of success
During shallow in-water tests, the system must successfully maintain power to core and auxiliary payload instruments and, for those with data interfaces, transmit data to the payload PC. The PC must log this data and successfully telemeter the data to a remote server on a defined schedule. It should be possible to successfully power cycle and remotely configure any attached instrument as required. When communications are available, it should be possible to remotely access the payload PC and attached payload instruments to inspect and verify nominal functionality.

During station tests, the system must be operable without physical intervention, with the exception to routine maintenance and pre-planned mechanical + electrical integration of additional instruments. It should be possible to configure and troubleshoot remotely as required, and any failure /anomaly in the system should be logged on-board for further analysis.



## Further Systems Integration
Systems integration for this platform, whether 3rd party or in-house, can be broadly broken into the following cases:

- [ ] Provision of physical space for mounting (Stand alone instruments)
- [ ] The above, with additional power requirements
- [ ] The above, with additional  local data telemetry/storage
- [ ] The above, with near real-time data and control


Feasibility must first be confirmed by discussing physical installation requirements and any additional factors desired in the integration. This includes existing instruments and the overall power factor of the payload system. Once positive, this can progress to a shore-side integration in a test environment identical to the remote platform systems. 

In any case realtime requirements to communicate with complex distributed PLCs, remote I/O modules, circuit breakers, actuators or sensor systems must be met once productivity throughput shall be running smoothly without interruptions or risking existing systems.

 



