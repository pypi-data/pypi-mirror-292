# icepak-network-deps

### Purpose

The PyAEDT Network Editor has multiple open-source package dependencies. The Python package icepak-network-deps serves to encapsulate those imports to simplify installation workflows and create clear separation between open and closed source Ansys Icepak development

### What is the PyAEDT Network Editor? 

The PyAEDT Network Editor is a graph manipulation software intended to simplify thermal network visualization, manipulation, and workflow. The Editor enables a user-friendly browser-based UI to edit and organize graphical data in the Ansys AEDT software.  

### Dependencies
The PyAEDT Network Editor is reliant on the following dependencies: 

dependencies = [
  "pyaedt",
  "networkx",
  "dash",
  "dash-cytoscape",
  "dash-bootstrap-components", 
  "pandas", 
  "dash_daq", 
  "thread6", 
  "psutil", 
  "dash_ag_grid", 
  "numpy", 
  "celery", 
  "diskcache", 
  "dash[diskcache]", 
  "random2",
  "subprocess", 
  "os",
  "pkg_resources",
  "sys",
  "psutil",
  "signal",
  "getpass",
  "argparse"
]

### License

icepak-network-deps is licensed under the MIT license.

icepak-network-deps makes no commercial claim over Ansys whatsoever. This library extends the functionality of AEDT by adding a Python interface to AEDT without changing the core behavior or license of the original software. The use of icepak-network-deps requires a legally licensed local copy of AEDT.

To get a copy of AEDT, see the [Ansys Electronics](https://www.ansys.com/products/electronics) page on the Ansys website.

### More Information
https://pypi.org/project/pyaedt/
