#!/usr/bin/env python
# coding: utf-8
# Deven Bibikar
# 7/31/24 Version

##############################################################
# General bug-testing notes
##############################################################

# NOTE: This has been tested in version 2025.1, 2024.2, 2024.1

# NOTE: If you receive the following error: 
"""
"AttributeError: 'NoneType' object has no attribute 'ReleaseAedtObject'"
"""
# The program was able to connect to AEDT. 
# That usually means that the project has not been correctly selected in AEDT. 
# Make sure that the project is selected such that one of its child objects is the 'Thermal' tab 
# containing all the networks you wish to visualize

# NOTE: The following error: 
"""
PyAEDT INFO: AEDT 2025.1.0 Build Date 2024-03-20 02:22:03
Traceback (most recent call last):
  File "C:\Program Files\Python38\lib\site-packages\pyaedt\generic\grpc_plugin_dll_class.py", line 91, in __Invoke__
    ret = _retry_ntimes(
  File "C:\Program Files\Python38\lib\site-packages\pyaedt\generic\general_methods.py", line 825, in _retry_ntimes
    raise AttributeError("Error in Executing Method {}.".format(function.__name__))
AttributeError: Error in Executing Method InvokeAedtObjMethod.
"""
# First check that PyAEDT is fully intalled
# Open Icepak: Click Automation -> Install PyAEDT
# This should redirect you to a new webpage with instructions
# 
# If that doesn't work, then revert to an earlier version
# In my case, 2025.1 did not work, so I reverted to 2024.2
# This problem can also occur if your file is corrupted. Try a duplicate or another file and test if that works. 

# NOTE: The following error:
"""
Traceback (most recent call last):
  File "c:/Users/user_name/OneDrive - ANSYS, Inc/Documents/pyaedt/pyaedt_network.py", line 99, in <module>
    desktop = Desktop(
  File "C:\Program Files\Python38\lib\site-packages\pyaedt\generic\design_types.py", line 1538, in Desktop
    return app(
TypeError: __init__() should return None, not 'bool'
"""
# This can often be solved by ensuring that you only have one instance of AEDT open at a time
# Also double check that Python is recognizing the right version and process ID of AEDT 

# Currently (6/12/2024) conditional editors for each cell is not documented on Dash AG Grid, 
# but it's functionality can be found in the following forum post:
# https://community.plotly.com/t/ag-grid-many-editors-in-one-column/78109/2

# Ensure that you have an assets folder with the required dashAgGridFunctions.js and
# bootstrap.css. The former creates functions used for conditional dropdowns,
# the latter implements a dropdown fix and enables local generation of css.

# NOTE: If AEDT Network Editor runs but doesn't have the syling provided by ./assets:

# This can often be solved by ensuring that you only have one instance of the Python Network Editor
# running at a time. It is caused by multiple access to the /assets folder

# If you run across this error:
"""
Traceback (most recent call last):
  File "c:/Users/dbibikar/OneDrive - ANSYS, Inc/Documents/icepak/Toolkits_aedt/Network_editor/pyaedt_network.py", line 1097, in <module>
    nxG = generate_nx_graphv2(Network_Data[0])
IndexError: list index out of range
"""
#This means that you are trying to run the network editor on a Icepak Design that does not have any networks;
# so it's trying to read networks but they're coming up empty. 

##############################################################
# General program functionality
##############################################################
"""
All networks are listed in a list of objects stored in local_network_data list as a LocalNetworkData object;
This object contains positions, nodes, links, and elements in the format of pandas dataframes or dict (elems)

Saving relies on the AEDTNetworkEditor class, which utilizes the EditNetworkBoundary() function from PyAEDT to save the network

All callbacks are standalone, except for the table callbacks. 
Callbacks that are reliant on one another are (usually) sectioned together
"""
##############################################################
# Argument parsing 
##############################################################

print("Begin Argument Parsing...")

import argparse 
import sys
import psutil
import signal
import getpass

argument_parsed = False

# Parse all arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Communication between iron python and python 3.10 virtual env")
    parser.add_argument(
        "-py",
        "--python",
        default="",
        help="Enter location of python install  Ex: -i C:\\Python310\\Scripts\\python.exe",
    )
    parser.add_argument(
        "-pid",
        "--processid",
        default="",
        help="Enter process ID of active AEDT application Ex: -p 20564",
    )
    parser.add_argument("-v", "--version", default="", help="Enter AEDT version Ex: -v 2024.1")

    args = parser.parse_args()

    py_location = args.python
    aedt_process_id = str(args.processid)
    version = str(args.version)
    

# Account for if no arguments are passed into the script
if len(aedt_process_id) + len(version) == 0:
    #input("This is not running")
    py_location = sys.executable  
    version = '2025.1'

    try:
        for proc in psutil.process_iter():
            if proc.name() == "ansysedt.exe" and proc.username == getpass.getuser():
                aedt_process_id = proc.pid
    except:
        print("Search failed")
        aedt_process_id = input()   #Manually Enter PID if automatic search does not succeed.

# ver must be set to version, used in Desktop() definition in AEDT Connection setting
# in the next two sections, 'version' is rewritten to another value
ver = version

# Override default settings 
# ver = 2024.2
# aedt_process_id = 23140

print("Argument Parsing successful")

##############################################################
# Import Statements & Other required packages
##############################################################
# import packages built into python
import os
import pkg_resources

# Import all packages into python
from pyaedt import *
import networkx as nx
from dash import Dash, html, dcc, callback, DiskcacheManager, CeleryManager, Input, Output, html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
import dash_daq as daq
import webbrowser
from threading import Timer
import dash_ag_grid as dag
import numpy as np
import random
import diskcache

print("Package import successful")

##############################################################
# AEDT Connection, File Loading, & Setting up oDesktop & Thermal Object Data
##############################################################

print("Loading AEDT Connection...")
cyto.load_extra_layouts()
prevent_initial_callbacks='initial_duplicate'

# Define desktop
# Note: specified_version and new_desktop_session is depreciated, but still in usage. 
# 2025.1 version requires 'specified version' 

try:
    desktop = Desktop(
            specified_version=ver,
            aedt_process_id = aedt_process_id,
            new_desktop_session=False,
            non_graphical=False,
            close_on_exit=False,
            student_version=False,
        )

    #Code to construct network data
    oDesktop = desktop.odesktop
    oDesign = oDesktop.GetActiveProject().GetActiveDesign()
    Thermal_Object = oDesign.GetChildObject('Thermal')
    oModule = oDesign.GetModule("BoundarySetup")

    # account for face node ids
    oEditor = oDesign.SetActiveEditor("3D Modeler")

    print("AEDT Connection successful")

except:
    input("Program launch failed. Cannot initialize Desktop")
    os.kill(os.getpid(), signal.SIGTERM)

#############################################################
# Class Definitions (section header not updated)
#############################################################
# Node               : Node parent class
# InternalNode       : Child class of Node
# FaceNode           : Child class of Node
# BoundaryNode       : Child class of Node  
# Link               : Link parent class
# RLink              : Child class of Link
# CLink              : Child class of Link
# Network            : Interpret AEDT network using networkX
# NetworkHelper      : Define helper functions to get properties 
#                     of attributes
# AEDTNetworkEditor  : Format Data to enable saving from 
#                     Cytoscape Interface to AEDT
# LocalNetworkData   : stores easy structures for each
#                       local network loaded into the editor
# StylesheetManager  : manages which stylesheet 
#                        is in usage at a given time.
# CytoscapeIDManager : creates ID manager to handle name-id cytoscape
#                       differences
##############################################################

class Node:
    def __init__(self, name, type, Xlocation, Ylocation):
        self.Name = name
        self.Type = type
        self.Xlocation = Xlocation
        self.Ylocation = Ylocation
        
    def get_dictionary(self):
        attributes_dict = {}
        for attr_name in dir(self):
            if not attr_name.startswith("__") and not callable(getattr(self, attr_name)):
                attributes_dict[attr_name] = getattr(self, attr_name)
        return attributes_dict


class InternalNode(Node):
    def __init__(self, name, type, Xlocation, Ylocation, power, mass, specific_heat):
        # Call the constructor of the base class (Node)
        super().__init__(name, type, Xlocation, Ylocation)
        self.Power = power
        self.Mass = mass
        self.SpecificHeat = specific_heat


class FaceNode(Node):
    def __init__(self, name, type, Xlocation, Ylocation, 
                 resistancechoice, faceid, thickness="", 
                 material="", thermalresitance=""):
        # Call the constructor of the base class (Node)
        super().__init__(name, type, Xlocation, Ylocation)
        self.FaceID = faceid
        self.ResistanceChoice = resistancechoice
        self.Thickness = thickness
        self.Material = material
        self.ThermalResistance = thermalresitance

class BoundaryNode(Node):
    def __init__(self, name, type, Xlocation, Ylocation, 
                 thermalparameters, power="", temperature=""):
        # Call the constructor of the base class (Node)
        super().__init__(name, type, Xlocation, Ylocation)
        self.ThermalParameters = thermalparameters
        self.Power = power
        self.Temperature = temperature

##################################################################################
# Class                 : Link
# Purpose               : Define links (edges) in graph
##################################################################################

class Link:
    def __init__(self, name, from_node, to_node, type):
        self.name = name
        self.fromNode = from_node
        self.toNode = to_node
        self.LinkType = type

    def get_dictionary(self):
        attributes_dict = {}
        for attr_name in dir(self):
            if not attr_name.startswith("__") and not callable(getattr(self, attr_name)):
                attributes_dict[attr_name] = getattr(self, attr_name)
        return attributes_dict
    
class RLink(Link):
    def __init__(self, name, from_node, to_node, type, r_link_type="", thermalresistance="", htc=""):
        # Call the constructor of the base class (Link)
        super().__init__(name, from_node, to_node, type)

        self.rLinkType = r_link_type
        self.thermalResistance = thermalresistance
        self.heatTransferCoefficient = htc

class CLink(Link): 
    def __init__(self, name, from_node, to_node, type, mass_flow=""):
        # Call the constructor of the base class (Link)
        super().__init__(name, from_node, to_node, type)

        self.mass_flow = mass_flow

##################################################################################
# Class                 : Network
# Purpose               : Define network using networkx Python package
##################################################################################

class Network:
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.links = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_link(self, link):
        self.links.append(link)

    def get_all_nodes_info(self):
        return self.nodes

    def get_all_links_info(self):
        return self.links

    def print_network_information(self):
        print(self.name)
        for node in self.nodes:
            print(str(node.get_dictionary()))
        for link in self.links:
            print(str(link.get_dictionary()))

    def get_link_info(self):
        all_links_info = {}
        for link in self.links:
            all_links_info[link.get_dictionary()['name']] = link.get_dictionary()

        return all_links_info

    def get_name(self):
        return self.name

##################################################################################
# Class                 : NetworkHelper
# Purpose               : Define helper functions to get properties of attributes
#                         (used to directly extract data about nodes/links)
##################################################################################
class NetworkHelper:
      def __init__(self,attribute_name, bc_obj):
          self.attribute_name = attribute_name
          self.bc_obj = bc_obj
          self.Xlocation = -1
          self.Ylocation = -1

      def get(self,property):
          return self.bc_obj.GetPropValue(self.attribute_name+': Properties/'+property)

      def GetFaceNodeInformation(self):
          resistant_choice = self.get('ResistanceChoice')
          FaceID = self.get('FaceID')
          if resistant_choice == "NoResistance":
             node = FaceNode(node_name, "Face Node",self.Xlocation, self.Ylocation, resistant_choice, FaceID)

          elif resistant_choice == "Compute":
             thickness = self.get('Thickness')   
             material = self.get('Solid Material')[1]
             node = FaceNode(node_name, "Face Node", self.Xlocation, self.Ylocation, resistant_choice, FaceID, thickness, material)

          elif resistant_choice == "Specified":
             thermal_resistance = self.get('ThermalResistance')
             node = FaceNode(node_name, "Face Node", self.Xlocation, self.Ylocation, resistant_choice, FaceID, "", "", thermal_resistance)
             
          return node         
        
      def GetInternalNodeInformation(self):
          power = self.get('Power')  
          specific_heat = self.get('Specific Heat')
          mass = self.get('Mass') 
          node = InternalNode(node_name, "Internal Node", self.Xlocation, self.Ylocation, power, mass, specific_heat)
          return node
    
      def GetBoundaryNodeInformation(self):
          thermalparameters = self.get('ThermalParameters')
          if thermalparameters == "Power":
              power = self.get('Power') 
              node = BoundaryNode(node_name, "Boundary Node", self.Xlocation, self.Ylocation, thermalparameters, power)
              return node
          elif thermalparameters == "Temperature":
               temperature = self.get('Temperature')
               node = BoundaryNode(node_name, "Boundary Node", self.Xlocation, self.Ylocation, thermalparameters, "", temperature)
               return node    
    
      def GetNodeInformation(self):
        #Get locations
        nodeLocations = oModule.GetNetworkNodeLocations(self.bc_obj.GetPropValue('Name'))
        for nodeData in nodeLocations:
            if self.attribute_name +":" in nodeData:
                self.Xlocation = nodeData.split(":")[1].split(",")[0]
                self.Ylocation = nodeData.split(":")[1].split(",")[1]
                break 
                            
        node_type = self.get('NodeType')
        if node_type == "Face Node":
            return self.GetFaceNodeInformation()
        elif node_type == "Internal Node":
            return self.GetInternalNodeInformation()
        elif node_type == "Boundary Node":
            return self.GetBoundaryNodeInformation()
      
      def GetLinkInformation(self):    
        link_name = self.get("Link Name")
        from_node = self.get("Node 1")
        to_node = self.get("Node 2")    
        link_type = self.get("Link Type")
        if link_type == "R-Link": 
            r_link_type = self.get("R Link Type")
            if r_link_type == "Thermal Resistance": 
                thermalResistance = self.get("ThermalResistance") 
                return RLink(link_name, from_node, to_node, link_type, r_link_type, thermalResistance)
            if r_link_type == "Heat Transfer Coefficient":  
                htc = self.get("Heat Transfer Coefficient")
                return RLink(link_name, from_node, to_node, link_type, r_link_type, "", htc)
            
        if link_type == "C-Link": 
            mass_flow = self.get("Mass Flow")
            return CLink(link_name, from_node, to_node, link_type, mass_flow)     

##################################################################################
# Class                 : AEDTNetworkEditor
# Purpose               : Format Data to enable saving from Cytoscape Interface to AEDT
#                         Creates a long string to execute and format 
#                         a oModule.EditBoundary() command
##################################################################################
class AEDTNetworkEditor:
    def __init__(self):
        pass

    ##################################################################################
    # Function          : construct_header_info
    # Purpose           : Header information to start EditNetworkBoundary command
    # self [in]         : AEDTNetworkEditor Class instance
    # name [in]         : Current project name
    # Returns           : current line with AEDT command   
    ##################################################################################
    def construct_header_info(self, name):
        line = ''
        line += 'oModule.EditNetworkBoundary("'+name+'",'+'\n'
        line += '\t['+'\n'
        line += '\t\t"NAME:'+ name +'",'+'\n'
        line += '\t\t['+'\n'
        line += '\t\t\t"NAME:Nodes",'+'\n'
        return line

    ##################################################################################
    # Function          : construct_node_info
    # Purpose           : construct internal details about each node & link type
    #                       when saving. 
    # self [in]         : AEDTNetworkEditor Class instance
    # node_data [in]    : Information about nodes
    # Returns           : current line with AEDT command   
    ##################################################################################
    def construct_node_info(self, node_data, end=""):
        line = '\t\t\t[\n'
        # Common properties
        line += f'\t\t\t\t"NAME:{node_data["Name"]}",\n'

        if node_data['Type'] == 'Face Node':
            # Face Node specific properties
            line += f'\t\t\t\t"FaceID:="  ,{-1 if "FaceID" not in node_data else node_data["FaceID"]},\n'
            line += f'\t\t\t\t"ThermalResistance:="   , "{node_data.get("ResistanceChoice", "N/A")}",\n'
            
            thickness = node_data.get("Thickness", "1mm")
            if not thickness:  # This checks for both None and empty strings
                thickness = "1mm"
            line += f'\t\t\t\t"Thickness:="           , "{thickness}",\n'
            
            line += f'\t\t\t\t"Material:="           , "Al-Extruded",\n'
            
            resistance = node_data.get("ThermalResistance", "0cel_per_w")
            if not resistance:  # This checks for both None and empty strings
                resistance = "0cel_per_w"
            line += f'\t\t\t\t"Resistance:="           , "{resistance}",\n'            
                        
            line += '\t\t\t\t"Radiation:="             , "No Radiation",\n'
            line += '\t\t\t\t"Surface Material:="      , "Steel-oxidised-surface",\n'
            line += f'\t\t\t\t"Temperature:="          ,"{node_data.get("Temperature", "0")}",\n'
            line += '\t\t\t\t"View factor:="           , "1",\n'
            line += f'\t\t\t\t"X-Position:="           , {node_data["Xlocation"]},\n'
            line += f'\t\t\t\t"Y-Position:="           , {node_data["Ylocation"]}\n'

        elif node_data['Type'] == 'Internal Node':
            # Internal Node specific properties
            line += '\t\t\t\t"NodeType:="  , "InternalNode",\n'
            line += f'\t\t\t\t"Power:="   , "{node_data.get("Power", "0")}",\n'
            line += f'\t\t\t\t"Mass:="   , "{node_data.get("Mass", "0")}",\n'
            line += f'\t\t\t\t"SpecificHeat:="   , "{node_data.get("SpecificHeat", "0")}",\n'

            line += f'\t\t\t\t"X-Position:="           , {node_data["Xlocation"]},\n'
            line += f'\t\t\t\t"Y-Position:="           , {node_data["Ylocation"]}\n'

        elif node_data['Type'] == 'Boundary Node':
            # Internal Node specific properties
            line += '\t\t\t\t"NodeType:="  , "BoundaryNode",\n'
            if node_data.get('ThermalParameters') == "Power":
                line += '\t\t\t\t"ValueType:="  , "PowerValue",\n'

            elif node_data.get('ThermalParameters') == "Temperature":
                line += '\t\t\t\t"ValueType:="  , "TemperatureValue",\n'

            line += f'\t\t\t\t"Power:="   , "{node_data.get("Power", "N/A")}",\n'
            line += f'\t\t\t\t"Temperature:="   , "{node_data.get("Temperature", "N/A")}",\n'
            line += f'\t\t\t\t"X-Position:="           , {node_data["Xlocation"]},\n'
            line += f'\t\t\t\t"Y-Position:="           , {node_data["Ylocation"]}\n'

        line += '\t\t\t]'+end+'\n'
        return line
    
    ##################################################################################
    # Function          : construct_links_info
    # Purpose           : Construct line formatting for rlinks
    # self [in]         : AEDTNetworkEditor Class instance
    # links [in]        : Information about rlinks
    # Returns           : current line with AEDT command   
    ##################################################################################
    def construct_links_info(self, links):
        line = '\t\t[\n\t\t\t"NAME:Links",\n'
        for idx, link in enumerate(links):
            link_data = link.get_dictionary()
            end = ',' if idx < len(links) - 1 else ''

            if link_data["LinkType"] == "R-Link":
                if link_data["rLinkType"] == 'Thermal Resistance':
                    line += f'\t\t\t"{link_data["name"]}:="  , ["{link_data["fromNode"]}","{link_data["toNode"]}","{link_data["LinkType"]}","R","{link_data["thermalResistance"]}"]{end}\n'
                else:
                    line += f'\t\t\t"{link_data["name"]}:="  , ["{link_data["fromNode"]}","{link_data["toNode"]}","{link_data["LinkType"]}","HTC","{link_data["heatTransferCoefficient"]}"]{end}\n'
                    
            elif link_data["LinkType"] == "C-Link":
                line += f'\t\t\t"{link_data["name"]}:="  , ["{link_data["fromNode"]}","{link_data["toNode"]}","{link_data["LinkType"]}","C","{link_data["mass_flow"]}"]{end}\n'

        print(line)
        line += '\t\t]\n'
        return line
    

    ##################################################################################
    # Function          : edit_networks
    # Purpose           : Add oDesign and oModule lines, and run AEDT saving procedure
    # self [in]         : AEDTNetworkEditor Class instance
    # Network_Data [in] : Collection of network data from AEDT
    # Returns           : Nothing   
    ##################################################################################
    def edit_networks(self, Network_Data):
        for network in Network_Data:
            line = "oDesign = oDesktop.GetActiveProject().GetActiveDesign()"+'\n'
            line += "oModule = oDesign.GetModule(\"BoundarySetup\")" + "\n"

            line += self.construct_header_info(network.name)

            # get list of all Node objects
            all_nodes = network.get_all_nodes_info()

            # for each node, create saving entry in AEDT format
            for idx, node_info in enumerate(all_nodes):
                node_data = node_info.get_dictionary()
                end = "," if idx != len(all_nodes) - 1 else ""
                line += self.construct_node_info(node_data, end)
            line += '\t\t],\n'

            # get list of all List objects
            all_links = network.get_all_links_info()

            # for all links, create AEDT-saving formatted line
            line += self.construct_links_info(all_links)

            line += '\t])'

            # print command to console
            print(line)

            # execute large EditNetworkBoundary() command
            exec(line)
            
##################################################################################
# Class                 : LocalNetworkData
# Purpose               : Store internal data for  
#                         df_int, df_face, and other values
##################################################################################
class LocalNetworkData:

    def __init__(self, idx, networkName):
        #Establish more reference data for internal and face nodes and rlinks and boundary nodes
        self.networkName = networkName
        self.idx = idx
        self.int_index = [index for (index, d) in enumerate(Network_Cytoscape_Node_Data[idx]) if d['data']["Type"] == "Internal Node"]
        self.face_index = [index for (index, d) in enumerate(Network_Cytoscape_Node_Data[idx]) if d['data']["Type"] == "Face Node"]
        self.boundary_index = [index for (index, d) in enumerate(Network_Cytoscape_Node_Data[idx]) if d['data']["Type"] == "Boundary Node"]
        self.rlink_index  = [index for (index, d) in enumerate(Network_Cytoscape_Edge_Data[idx]) if d['data']["LinkType"] == "R-Link" or d['data']["LinkType"] == "C-Link"]

        self.internalNodeList = [Network_Cytoscape_Node_Data[idx][i]['data'] for i in self.int_index]
        self.faceNodeList = [Network_Cytoscape_Node_Data[idx][i]['data'] for i in self.face_index]
        self.rLinkList = [Network_Cytoscape_Edge_Data[idx][i]['data'] for i in self.rlink_index]
        self.boundaryNodeList = [Network_Cytoscape_Node_Data[idx][i]['data'] for i in self.boundary_index]

        # Define all reference values
        self.ref_df_int = pd.DataFrame(self.internalNodeList)
        self.ref_df_face = pd.DataFrame(self.faceNodeList)
        self.ref_df_links = pd.DataFrame(self.rLinkList)
        self.ref_df_boundary = pd.DataFrame(self.boundaryNodeList)

        #Add checks in case boundary nodes are empty
        self.ref_df_boundary_positions = pd.DataFrame([])
        if len(self.ref_df_boundary) > 0:
            self.ref_df_boundary_positions = self.ref_df_boundary[['Name','Xlocation','Ylocation']].copy()
            self.ref_df_boundary.drop(columns=['id','Xlocation','Ylocation'], inplace=True)

        self.ref_df_int_positions = self.ref_df_int[['Name','Xlocation','Ylocation']].copy()
        self.ref_df_face_positions = self.ref_df_face[['Name','Xlocation','Ylocation']].copy()
        self.ref_positions = pd.concat([self.ref_df_int_positions, self.ref_df_face_positions, self.ref_df_boundary_positions],ignore_index=True)
        self.ref_positions['Ylocation'] = self.ref_positions['Ylocation'].str.replace(" ", "")

        self.ref_df_int.drop(columns=['id','Xlocation','Ylocation'], inplace=True)
        self.ref_df_face.drop(columns=['id','Xlocation','Ylocation'], inplace=True)

        #Set network specific values
        self.df_int = self.ref_df_int.copy()
        self.df_face = self.ref_df_face.copy()
        self.df_links = self.ref_df_links.copy()
        self.df_boundary = self.ref_df_boundary.copy()
        self.df_positions = self.ref_positions.copy()
        self.elems = Network_Cytoscape_Data[idx]['elements']
        self.ref_elems = self.elems.copy()

        #define stylesheetManager
        self.stylesheetManager = StylesheetManager()

        #define ID management system
        self.id_manager = CytoscapeIDManager(self.elems)

        # edit elems to have display data
        self.update_elem_display_data()

    # return local id manager instance
    def get_id_manager(self):
        return self.id_manager

    # reset elems & all dataframes using reference data
    def reset_all_values(self):
        self.df_links = self.ref_df_links.copy()
        self.df_int = self.ref_df_int.copy()
        self.df_boundary = self.ref_df_boundary.copy()
        self.df_face = self.ref_df_face.copy()
        self.df_positions = self.ref_positions.copy()
        self.elems = self.ref_elems.copy()

    # update reference values from current dataframe data
    def update_ref_values(self):
        self.ref_df_links = self.df_links.copy()
        self.ref_df_int = self.df_int.copy()
        self.ref_df_boundary = self.df_boundary.copy()
        self.ref_df_face = self.df_face.copy()
        self.ref_positions = self.df_positions.copy()
        self.ref_elems = self.elems.copy()
    
    # update element names given old name & new name
    def update_elem_name(self, old_name, new_name):
        # change old names to new names and update source / target accordingly if link
        for item in self.elems:
            if 'Name' in item['data'].keys():
                if item['data']['Name'] == old_name:
                    item['data']['Name'] = new_name
        
    # update positions from locally stored elems dictionary
    def update_positions(self):
        for item in self.elems:
            if 'position' in item and 'position' in item:
                name = item['data']['Name']
                x_position = item['position']['x']
                y_position = item['position']['y']

                self.df_positions.loc[self.df_positions['Name'] == name, 'Xlocation'] = x_position
                self.df_positions.loc[self.df_positions['Name'] == name, 'Ylocation'] = y_position

    # use external elements to update both local elements & dataframes
    def update_positions_from_elems(self, elems):
        self.update_elems(elems)
        self.update_positions()

    # update elems (shallow copy)
    def update_elems(self, elems):
        self.elems = elems

    # replace underscore (_) with slash (/)
    def clean_display_string(self, s):
        value, unit = separateUnitAndNumber(s)

        # remove per with /
        unit = unit.replace("per", "/")

        # replace _ with nospace
        unit = unit.replace("_", "") 

        # reformat return value
        value = str(value) + " " + unit

        return value
    
    # update link values in elems from df_links info
    def update_elem_display_data(self):
        for entry in self.elems:
            name = entry['data']['Name']
            display_entry_name = 'link_value'

            # get the type of link
            link_type = self.df_links.loc[self.df_links['Name'] == name, 'LinkType'].values

            # check if the item has a link type (i.e. is it a link?)
            if link_type.size > 0:

                # get link_type from list
                link_type = link_type[0]

                # clean values depending on link type
                if link_type == 'R-Link':
                    rLink_type = self.df_links.loc[self.df_links['Name'] == name, 'rLinkType'].values[0]

                    if rLink_type == 'Thermal Resistance':
                        new_display_val = self.clean_display_string(self.df_links.loc[self.df_links['Name'] == name, 'thermalResistance'].values[0])
                        entry['data'][display_entry_name] = new_display_val

                    elif rLink_type == 'Heat Transfer Coefficient':
                        new_display_val = self.clean_display_string(self.df_links.loc[self.df_links['Name'] == name, 'heatTransferCoefficient'].values[0])
                        entry['data'][display_entry_name] = new_display_val
                        
                elif link_type == 'C-Link':
                    new_display_val = self.clean_display_string(self.df_links.loc[self.df_links['Name'] == name, 'mass_flow'].values[0])
                    entry['data'][display_entry_name] = new_display_val

    # given source and target, remove link
    def remove_link(self, source, target):
        # get all indices where source is equal to the given source
        drop_indices = self.df_links[((self.df_links['source'] == source))].index

        # remove all entries where target column equals param
        for index in drop_indices:
            if self.df_links.loc[index, 'target'] == target:
                self.df_links.drop(index, inplace=True)

    # given name remove node / link from all local structures
    def remove_items_with_name(self, selected_name, is_edge=False):

        # account for if the item is not an edge
        if not is_edge:
            # Remove items with the selected name across df_int, df_face, df_links, df_positions
            # drop_indices used to find all indices that match name / source / target
            drop_indices = self.df_positions[(self.df_positions.Name == selected_name)].index
            self.df_positions.drop(drop_indices, inplace=True)

            drop_indices = self.df_int[(self.df_int.Name == selected_name)].index
            self.df_int.drop(drop_indices, inplace=True)

            drop_indices = self.df_face[(self.df_face.Name == selected_name)].index
            self.df_face.drop(drop_indices, inplace=True)

            if len(self.df_boundary.index) > 0:
                drop_indices = self.df_boundary[(self.df_boundary.Name == selected_name)].index
                self.df_boundary.drop(drop_indices, inplace=True)

            drop_indices = self.df_links[(self.df_links['source'] == self.id_manager.get_id(selected_name))].index
            drop_indices = drop_indices.append(self.df_links[(self.df_links['target'] == self.id_manager.get_id(selected_name))].index)
            drop_indices = drop_indices.append(self.df_links[(self.df_links.Name == selected_name)].index)
            self.df_links.drop(drop_indices, inplace=True)

        # node or edge, remove from elems
        for item in self.elems:
            if item['data']['Name'] == selected_name:
                self.elems.remove(item)

            elif 'LinkType' in item['data'].keys() and is_edge:
                if item['data']['source'] == selected_name and item['data']['target'] == selected_name:
                    self.elems.remove(item)

            elif 'LinkType' in item['data'].keys():
                source = self.id_manager.get_name(item['data']['source'])
                target = self.id_manager.get_name(item['data']['target'])

                if source == selected_name:
                    self.elems.remove(item)

                elif target == selected_name:
                    self.elems.remove(item)

        # remove from id manager
        self.id_manager.remove_elem_name(selected_name)

    # used internally, generate unique id and name from id manager
    def gen_unique_id_and_name(self, prefix, n_clicks):
         # generate unique name
        new_name = prefix + str(n_clicks)
        while not self.id_manager.is_name_unique(new_name):
            n_clicks += 1
            new_name = prefix + str(n_clicks)

        # generate unique id
        new_id = prefix + str(random.randint(0, 10))

        while not self.id_manager.is_id_unique(new_id):
            new_id = new_id + str(random.randint(0, 10))

        return new_name, new_id

    # generate new positions using existing position
    def gen_new_positions(self, n_clicks):

        x = self.df_positions['Xlocation'].values[-1] + 30*n_clicks
        y = self.df_positions['Ylocation'].values[-1] + 30*n_clicks

        return x, y
    
    # Assumes elems are updated already
    # add internal node to elems & df_int (locally)
    def add_internal_node(self, n_clicks):

        # get unique id and name
        new_node_name, new_node_id = self.gen_unique_id_and_name("int", n_clicks)

        # generate new positions
        x, y = self.gen_new_positions(n_clicks)

        # create new dict entries for int node and its position
        new_node_dict = {'data': {'Mass': '1kg', 'Name': new_node_name, 
                                  'Power': '0W', 'SpecificHeat': '0.0J_per_Kelkg', 
                                  'Type':'Internal Node', 'id': new_node_id}, 
                         'group': 'nodes',
                         'classes': "Internal Node", 
                         'position':{'x': x,'y': y}}
        new_pos_dict = {'data': {'Name': new_node_name, 'Xlocation' : x, 'Ylocation': y}}

        # append the new entry into respective structures & format accordingly
        self.elems.append(new_node_dict)
        new_node_df = pd.DataFrame([new_node_dict['data']])
        new_pos_df = pd.DataFrame([new_pos_dict['data']])
        self.df_int = pd.concat([self.df_int, new_node_df], ignore_index=True)
        self.df_positions = pd.concat([self.df_positions, new_pos_df])

        # update IDManager to have most updated name
        self.id_manager.add_elem(new_node_name, new_node_id)

    # Assumes elems are updated already
    # add boundary node to elems and df_int (locally)
    def add_boundary_node(self, n_clicks):
        
        # get unique id and name
        new_node_name, new_node_id = self.gen_unique_id_and_name("Bound", n_clicks)

        # generate new positions
        x, y = self.gen_new_positions(n_clicks)

        # Create new entry for boundary node & its position
        new_node_dict = {'data': {'Name': new_node_name, 
                                  'Power': '0W', 'Temperature': '', 
                                  'ThermalParameters': 'Power', 
                                  'Type': 'Boundary Node', 'id': new_node_id}, 
                         'group': 'nodes',
                         'classes': "Boundary Node", 'position':{'x': x,'y': y}}
        new_pos_dict = {'data': {'Name': new_node_name, 'Xlocation' : x, 'Ylocation': y}}

        # append the new entry into respective structures & format accordingly
        self.elems.append(new_node_dict)
        new_node_df = pd.DataFrame([new_node_dict['data']])
        new_pos_df = pd.DataFrame([new_pos_dict['data']])
        self.df_boundary = pd.concat([self.df_boundary, new_node_df], ignore_index=True)
        self.df_positions = pd.concat([self.df_positions, new_pos_df], ignore_index=True)

        # update IDManager to have most updated name
        self.id_manager.add_elem(new_node_name, new_node_id)

    # check link existance, returns boolean
    def link_exists(self, id_1, id_2):
        cond1 = ((self.df_links['source'] == id_1) & (self.df_links['target'] == id_2)).any()
        cond2 = ((self.df_links['source'] == id_2) & (self.df_links['target'] == id_1)).any()
        
        return cond1 or cond2

    # add link given source_id, target_id and link type
    # n_clicks used to give new name
    def add_link(self, source_id, target_id, link_type, n_clicks):

        # get unique id and name
        new_name, new_id = self.gen_unique_id_and_name('new_link_', n_clicks)

        # create link entry
        new_edge_dict = {}

        # create new link entry for r-link
        if link_type == 'R-Link':
            new_edge_dict = {'data': {'LinkType': 'R-Link', 'heatTransferCoefficient': '', 'rLinkType': 'Thermal Resistance', 
                                'thermalResistance': '80.1777cel_per_w', 'source': source_id, 'target': target_id, 
                                'Name': new_name, 'id': new_id}, 
                                'group': 'edges', 'classes': 'R-Link'}
        
        # create new link entry for c-link
        elif link_type == 'C-Link':
            new_edge_dict = {'data': {'LinkType': 'C-Link', 'source': source_id, 'target': target_id, 
                                    'Name': new_name, 'id' : new_id,
                                    'mass_flow': 0,}, 'group': 'edges', 'classes': 'C-Link'}
            
        else:
            print("Link identifier not provided in add_link()")
            return
        
        # format and append link entry into df_links
        self.elems.append(new_edge_dict)
        new_edge_df = pd.DataFrame([new_edge_dict['data']])
        self.df_links = pd.concat([self.df_links, new_edge_df], ignore_index=True)

        # print log statments to show new link in elems
        print(self.df_links)
        print(["New link created.", self.elems])

        # add to id manager
        self.id_manager.add_elem(new_name, new_id)

    # restores positions in elems from ref_df_positions and df_positions
    def restore_positions(self):
        for item in self.elems:
            if 'position' in item and 'position' in item:
                name = item['data']['Name']
                if name in self.ref_positions['Name']:
                    self.ref_positions['Name']
                    self.ref_positions[self.ref_positions['Name'] == name].values[0]

                    item['position']['x'] = self.ref_positions[self.ref_positions['Name'] == name]['Xlocation'].values[0]
                    item['position']['y'] = self.ref_positions[self.ref_positions['Name'] == name]['Ylocation'].values[0]

                elif name in self.df_positions['Name']:
                    self.df_positions['Name']
                    self.df_positions[self.df_positions['Name'] == name].values[0]

                    item['position']['x'] = self.df_positions[self.df_positions['Name'] == name]['Xlocation'].values[0]
                    item['position']['y'] = self.df_positions[self.df_positions['Name'] == name]['Ylocation'].values[0]


    # zero out elems
    def zero_elem_positions(self): 
        for item in self.elems:
            if 'position' in item:
                #del item['position']
                item['position']['x'] = 0
                item['position']['y'] = 0

    # take name of link and find out if its source & target nodes are face nodes
    # currently used to show whether HTC should be shown on R-Link
    def link_adj_to_face(self, link_name):

        node0_id = self.df_links[self.df_links['Name'] == link_name]['source'].values[0]
        node1_id = self.df_links[self.df_links['Name'] == link_name]['target'].values[0]

        node0_name = self.id_manager.get_name(node0_id)
        node1_name = self.id_manager.get_name(node1_id)

        # return whether either node item are face nodes
        return node0_name in self.df_face['Name'].values or node1_name in self.df_face['Name'].values
    

    # get face id given face name
    def get_faceID(self, face_name):
        faceID_list  = self.df_face[self.df_face['Name'] == face_name]['FaceID'].values

        if len(faceID_list) > 0:
            faceID = faceID_list[0]
            return faceID
        
        return False

##################################################################################
# Class                 : StylesheetManager
# Purpose               : class to manage which stylesheet 
#                          is in usage at a given time.
##################################################################################
class StylesheetManager:

    # default stylesheet shared between all class  instances
    default_stylesheet = [
            # Group selectors
            {'selector' : 'node', 
             'style': {'content' : 'data(Name)', 
                       'text-opacity' : 1,
                       'font-size' : 10, 
                       'text-valign' : 'bottom',
                       'width' : '20%',
                       'height' : '20%',
                       'border-color' : 'black',
                       'border-width' : 1,
                       'border-opacity' : 1,
                       'background-color' : 'white'}
            },
            
            # Class selectors
            {'selector': 'node[Type = "Internal Node"]', 
             'style': {'background-color': '#E96245', 
                       'shape': 'circle',
                       'border-color':'black'}
            },
            {'selector': 'node[Type = "Internal Node"][Power ^= "0"]', 
             'style': {'background-color': '#CF9FFF', 
                       'shape': 'circle',
                       'border-color':'black'}
            },
            {'selector': 'node[Type = "Internal Node"][Power ^= "0."]', 
             'style': {'background-color': '#E96245', 
                       'shape': 'circle',
                       'border-color':'black'}
            },
            {'selector': 'node[Type = "Internal Node"][Power ^= "-"]', 
             'style': {'background-color': '#3B719F', 
                       'shape': 'circle',
                       'border-color':'black'}
            },

            {'selector': 'node[Type = "Face Node"]', 
             'style': {'background-color': 'orange', 
                       'shape': 'square'}
            },
            {'selector': 'node[Type = "Boundary Node"]', 
             'style': {'background-color': 'gray', 
                       'shape': 'diamond'}
            },
            {'selector': 'edge[LinkType = "R-Link"]',\
                         'style': {'content': 'data(Name)', 
                                   'text-opacity': 1, 
                                   'width': '1px', 
                                   'line-color': 'black',
                                   'text-background-opacity': 1, 
                                   'text-background-color': 'white',
                                   'text-background-shape': 'round-rectangle', 
                                   'text-background-padding': '2px',
                                   'text-border-opacity': 1, 
                                   'text-border-style': 'solid', 
                                   'text-border-color': 'black',
                                   'text-border-width': '1px',
                                   'font-size' : 10, 
                                   'text-rotation': 'autorotate', 
                                   'border-color':'red', 
                                   'border-width':3}
            },   
            {'selector': 'edge[LinkType = "C-Link"]',
                         'style': {'content': 'data(Name)', 
                                   'text-opacity': 1, 
                                   'width': '1px', 
                                   'line-color': 'blue', 
                                   'target-arrow-shape': 'triangle', 
                                   'target-arrow-color': 'blue', 
                                   'source-arrow-color': 'blue', 
                                   'curve-style': 'bezier',
                                   'text-background-opacity': 1, 
                                   'text-background-color': 'white', 
                                   'directed' : True, 
                                   'text-background-shape': 'round-rectangle', 
                                   'text-background-padding': '2px', 
                                   'text-border-opacity': 1, 
                                   'text-border-style': 'solid', 
                                   'text-border-color': 'black',
                                   'text-border-width': '1px',
                                   'font-size' : 10, 
                                   'text-rotation': 'autorotate'}
            }
        ]
    
    # define different kinds of stylesheets for each network 
    def __init__(self):
        self.labeled_stylesheet = []
        self.marker_stylesheet = []
        self.current_style_type = 'default'

    # toggle different kinds of labels using labels for c-links and r-links
    def update_labels(self, r_link_edge_label, c_link_edge_label, node_opacity):

        new_stylesheet = [
                            # Group selectors
                            {'selector': 'node', 
                             'style': {'content': 'data(Name)', 
                                       'text-opacity': node_opacity,
                                        'font-size' : 10, 
                                        'text-valign' : 'bottom',
                                        'width' : '20%',
                                        'height' : '20%',
                                        'border-color' : 'black',
                                        'border-width' : 1,
                                        'border-opacity' : 1,
                                        'background-color':'pink'}
                            },

                            # Class selectors
                            {'selector': 'node[Type = "Internal Node"]', 
                             'style': {'background-color': '#E96245', # Light Red color
                                       'shape': 'circle',
                                       'border-color':'black'}
                            },
                            {'selector': 'node[Type = "Internal Node"][Power ^= "0"]', 
                             'style': {'background-color': '#CF9FFF', # Light Purple color
                                       'shape': 'circle',
                                       'border-color':'black'}
                            },
                            {'selector': 'node[Type = "Internal Node"][Power ^= "0."]', 
                             'style': {'background-color': '#E96245', # Light Red color
                                       'shape': 'circle',
                                       'border-color':'black'}
                            },
                            {'selector': 'node[Type = "Internal Node"][Power ^= "-"]', 
                             'style': {'background-color': '#3B719F', # Dark Blue color
                                       'shape': 'circle',
                                       'border-color':'black'}
                            },

                            {'selector': 'node[Type = "Face Node"]', 
                             'style': {'background-color': 'orange', 
                                       'shape': 'square'}
                            },
                            {'selector': 'node[Type = "Boundary Node"]', 
                             'style': {'background-color': 'gray', 
                                       'shape': 'diamond'}
                            },
                            
                            {'selector': 'edge[LinkType = "R-Link"]',
                             'style': {'content': r_link_edge_label, 
                                       'text-opacity' : 1, 
                                       'width' : '1px', 
                                       'line-color' : 'black',
                                       'text-background-opacity' : 1, 
                                       'text-background-color' : 'white',
                                       'text-background-shape' : 'round-rectangle', 
                                       'text-background-padding' : '2px',
                                       'text-border-opacity' : 1, 
                                       'text-border-style' : 'solid', 
                                       'text-border-color' : 'black',
                                       'text-border-width' : '1px',
                                       'font-size' : 10, 
                                       'text-rotation' : 'autorotate'}},

                            {'selector': 'edge[LinkType = "C-Link"]',
                             'style': {'content' : c_link_edge_label, 
                                       'text-opacity' : 1, 
                                       'width' : '1px', 
                                       'line-color' : 'blue', 
                                       'target-arrow-shape' : 'triangle',
                                       'target-arrow-color' : 'blue', 
                                       'source-arrow-color' : 'blue', 
                                       'curve-style' : 'bezier',
                                       'text-background-opacity' : 1, 
                                       'text-background-color' : 'white', 
                                       'directed' : True, 
                                       'text-background-shape' : 'round-rectangle', 
                                       'text-background-padding' : '2px', 
                                       'text-border-opacity' : 1, 
                                       'text-border-style' : 'solid', 
                                       'text-border-color' : 'black',
                                       'text-border-width' : '1px',
                                       'font-size' : 10, 
                                       'text-rotation' : 'autorotate'}
                            }           
                        ]
        
        self.labeled_stylesheet = self.default_stylesheet + new_stylesheet
        self.current_style_type = 'labeled'

    # add markers, i.e. the outlines around nodes or edges given color, depth and element type
    def add_markers(self, name, color, width, elem_type):
        current_stylesheet = self.getCurrentStylesheet()
        self.marker_stylesheet = current_stylesheet.copy()
        strComp = elem_type + '[Name='+ '"' + name + '"' + ']'

        #check if item is a node & add accordingly
        if elem_type == 'node':
            # check if item already exists in current stylesheet
            item_exists = False

            for item in self.marker_stylesheet:
                if item['selector'] == strComp:
                    item['style']['border-color'] = color
                    item['style']['border-width'] = width
                    item_exists = True
                    break

            # if item doesn't exist, make an entry for it. 
            if (not item_exists):
                new_entry = {'selector': strComp, 
                             'style' : {'border-color': color,
                                        'border-width': width}
                            }
                self.marker_stylesheet.append(new_entry)
        
        # check if item is anything other than a node (edge) and add accordingly
        else:
            # check if item already exists in current stylesheet
            item_exists = False

            color_entries = ['text-border-color', 
                             'background-color', 
                             'line-color', 
                             'source-arrow-color', 
                             'target-arrow-color']

            for item in self.marker_stylesheet:
                if item['selector'] == strComp:
                    for color_entry in color_entries:
                        item['style'][color_entry] = color
                    item_exists = True
                    break
                    
            # if item doesn't exist, make an entry for it. 
            if (not item_exists):
                new_entry = {'selector' : strComp, 
                             'style' : {color_entry : color for color_entry in color_entries}
                            }
                self.marker_stylesheet.append(new_entry)

        #switch current_style_type
        if 'marker' not in self.current_style_type:
            self.current_style_type = 'marker-' + self.current_style_type

    # return the currently used stylesheet
    def getCurrentStylesheet(self):
        if self.current_style_type == 'labeled':
            return self.labeled_stylesheet
        
        elif self.current_style_type == 'default':
            return self.default_stylesheet
        
        elif self.current_style_type == 'marker-labeled' or self.current_style_type == 'marker-default':
            return self.marker_stylesheet
        
    #move from 'marker' stylesheet to currently operable stylesheet
    def resetStylesheetFromMarker(self):
        if self.current_style_type == 'marker-labeled':
            self.current_style_type = 'labeled'

        elif self.current_style_type == 'marker-default':
            self.current_style_type = 'default'

        # Remove every trace of node markers in all three stylesheets
        all_stylesheets = [self.marker_stylesheet, self.default_stylesheet, self.labeled_stylesheet]
        for stylesheet in all_stylesheets:
            for item in stylesheet:
                if 'node' in item['selector']:
                    item['style']['border-color'] = 'black'
                    item['style']['border-width'] = 1

    #Take int dataframe and reset stylesheet when resetting all nodes (names might change, etc)
    def resetStylesheetGivenInt(self, df_int):
        for name in df_int['Name']:
            str_power = df_int[df_int['Name'] == name]['Power'].values[0]
            self.addIntNodeColorFromStrVal(name, str_power)

    # add colors to internal nodes 
    def addInternalNodeColor(self, nodeName, nodeColor):
        strComp = 'node[Name='+ '"' + nodeName + '"' + ']'
        all_stylesheets = [self.marker_stylesheet, self.default_stylesheet, self.labeled_stylesheet]

        # Add new style into all stylesheets 
        for stylesheet in all_stylesheets:
            item_exists = False
            for item in stylesheet:
                if item['selector'] == strComp:
                    item['style']['background-color'] = nodeColor
                    item_exists = True

            # check if the internal node is not already colored inside the stylesheet
            if not item_exists:
                entry = {'selector': strComp, 
                         'style': {'background-color': nodeColor, 
                                   'shape': 'circle', 
                                   'border-color':'black'}
                        }
                stylesheet.append(entry)
    
    # Hardcoded colors for internal nodes
    def getInternalNodeColor(self, value):
        if value < 0:
            return '#3B719F' # blue 
        
        elif value == 0:
            return '#CF9FFF' # light purple
        else:  
            return '#E96245' # red
        
    # take string value and add color accordingly to node
    def addIntNodeColorFromStrVal(self, nodeName, str_value):
        value, units = separateUnitAndNumber(str_value)
        nodeColor = self.getInternalNodeColor(value)
        self.addInternalNodeColor(nodeName, nodeColor)


##################################################################################
# Class                 : CytoscapeIDManager
# Purpose               : Organize and manipulate dataframe of IDs
##################################################################################

class CytoscapeIDManager:

    # initialize IDManager object
    # elems -> dictionary of elems, formatted by cytoscape
    def __init__(self, elems):

        self.elem_ids = pd.DataFrame(columns=["Name", 'id'])

        for item in elems:

            # collect data from elems row
            name = item['data']['Name']

            # account for links, which don't have ID
            if 'id' in item['data']:
                id  = item['data']['id']
            else:                
                id  = name

            # add row of Name, ID to elem_ids dataframe
            self.elem_ids = pd.concat([pd.DataFrame([[name, id]], columns=self.elem_ids.columns), self.elem_ids], ignore_index=True)

    # add element to elem_ids dataframe
    def add_elem(self, name, id):
        self.elem_ids = pd.concat([pd.DataFrame([[name, id]], columns=self.elem_ids.columns), self.elem_ids], ignore_index=True)

    # update element name in elem_ids dataframe
    # takes in old name, new name
    def update_name(self, old_name, new_name):
        index = self.elem_ids.loc[self.elem_ids['Name'] == old_name].index[0]
        self.elem_ids.loc[index, 'Name'] = new_name
    
    # get ID given name from elem_ids dataframe
    def get_id(self, name):
        if len(self.elem_ids.loc[self.elem_ids['Name'] == name]['id'].values) > 0:
            return self.elem_ids.loc[self.elem_ids['Name'] == name]['id'].values[0]
        
        return "Name not found."
    
    # get name given ID in elem_ids dataframe
    def get_name(self, id):
        if len(self.elem_ids.loc[self.elem_ids['id'] == id]['Name'].values) > 0:
            return self.elem_ids.loc[self.elem_ids['id'] == id]['Name'].values[0]
        
        return "ID not found."
    
    # check if provided name is unique in elem_ids dataframe
    def is_name_unique(self, name):
        return name not in self.elem_ids['Name'].values
    
    # check if provided ID is unique in elem_ids dataframe
    def is_id_unique(self, id):
        return id not in self.elem_ids['id'].values
    
    # remove entry in elem_ids dataframe given name parameter
    def remove_elem_name(self, name):
        self.elem_ids = self.elem_ids[self.elem_ids['Name'] != name]

    # remove entry in elem_ids dataframe given ID parameter
    def remove_elem_id(self, id):
        self.elem_ids = self.elem_ids[self.elem_ids['id'] != id]

##################################################################################
# Function      : generate_nx_graphv2
# Purpose       : Main method used to generate networkX graph from AEDT Network Data
# network [in]  : AEDT network object 
# csG [out]     : networkX graph object
# Returns       : networkX-formatted graph
##################################################################################

def generate_nx_graphv2(network):

    # get list of all nodes and links
    node_list = network.get_all_nodes_info()
    edge_list = network.get_all_links_info()

    # define networkX graph
    G = nx.Graph(name=network.name)

    # add nodes into networkX graph
    for index, node_item in enumerate(node_list):
        G.add_nodes_from([(node_item.Name, node_item.get_dictionary())])

    # add links into networkX graph
    for index, edge_item in enumerate(edge_list):
        start_id = edge_item.get_dictionary()['fromNode']
        end_id = edge_item.get_dictionary()['toNode']
        G.add_edge(start_id,end_id)
        attrs = {(start_id,end_id):edge_item.get_dictionary()}
        nx.set_edge_attributes(G,attrs)
    
    # remove fromNode and toNode 
    for n1, n2, d in G.edges(data=True):
        for att in ['fromNode','toNode']:
            d.pop(att, None)
    
    return G
    
##################################################################################
# Function              : GetNodeAndLinkNames
# Purpose               : Get Node and Link names from Thermal Object Child Names
# bc_obj [in]           : Child Object (of Thermal Object) 
# node_names [out]      : Node Names
# edge_names [out]      : Edge Names
# Returns               : Information about Node & Edge names
# Note                  : Function is only used once
##################################################################################

def GetNodeAndLinkNames(bc_obj):

    node_names = []
    link_names = []

    # get prop names from object
    # usually run on child objects of Thermal Object
    for propname in bc_obj.GetPropNames():
        if "NodeType" in propname:
            node_names.append(propname.split(":")[0])
        if "Link Name" in propname:
            link_names.append(propname.split(":")[0])     

    return node_names, link_names  

##################################################################################
# Function      : generate_cs_graphv2
# Purpose       : Main method used to generate cytoscape graph from networkx Graph
# nxG [in]      : networkX graph object 
# csG [out]     : cytoscape graph object
# nodes [out]   : networkX formatted nodes
# edges [out]   : networkX formatted edges
# Returns       : networkX-formatted node and edge lists
##################################################################################

def generate_cs_graphv2(nxG):

    # get cytoscape formatted graph from networkX
    ls = nx.cytoscape_data(nxG)

    # set the network name
    csG = {}
    csG['networkName'] = [x[1] for x in ls['data']][0]

    # removed directed and multigraph from the data
    ls.pop('directed')
    ls.pop('multigraph')


    # format each node properly
    for d in ls['elements']['nodes']:
        d['classes'] = d.get('data').get('Type')
        d['group'] = 'nodes'
        xLocation = float(d.get('data').get('Xlocation'))
        yLocation = float(d.get('data').get('Ylocation'))

        d['position'] = {}
        d['position']['x'] = xLocation
        d['position']['y'] = yLocation

        d.get('data').pop('name')
        d.get('data').pop('value')

    # format each edge properly
    for d in ls['elements']['edges']:
        d['group'] = 'edges'
        d['classes'] = d.get('data').get('LinkType')
        d.get('data')['Name'] = d.get('data').pop('name')
        d['data']['id'] = d.get('data')['Name']

    # csG to have both nodes and edges
    csG['elements'] = ls['elements']['nodes'] + ls['elements']['edges'] 

    # return combined nodes + edges, nodes, edges
    return csG, ls['elements']['nodes'], ls['elements']['edges'] 

##################################################################################
# Function          : parseVariable
# Purpose           : check if item is in variable list, and if so, return it's value
# value [out]       : returns the item itself if not in variable list, or evaluated variable value.
# Note              : relies on all_variables dict defined below
##################################################################################

def parseVariable(var):
    # check if var is a variable
    if variableExists(var):
        return all_variables[var]
    
    return var

##################################################################################
# Function          : variableExists
# Purpose           : check if variable exists in all_variables
# value [out]       : returns True if item exists, otherwise returns false
# Note              : relies on all_variables dict defined below
##################################################################################

def variableExists(var):
    if var in all_variables.keys():
        return True
    
    return False


##################################################################################
# Function          : format_value_units
# Purpose           : format itme into value and units, accounts for variables
# item [out]        : edited row with the right entries
# Note              : relies on all_variables dict defined below
##################################################################################

def format_value_units(item):
    eval_variable = parseVariable(item['Value'])
    value, units = separateUnitAndNumber(eval_variable)
    item['Evaluated Value'] = str(value) + ' ' + units
    

    # set value to actual value if variable doesn't exist
    if item['Value'] == eval_variable:
        item['Value'] = value
        item['Units'] = units

    else: 
        item['Units'] = '' # display nothing if variable is present
        

    return item

##################################################################################
# Function          : separateUnitAndNumber
# Purpose           : Separate a number into units and number
# Source            : https://stackoverflow.com/questions/2240303/separate-number-from-unit-in-a-string-in-python
##################################################################################

def separateUnitAndNumber(s):

    # Change s into a string if it is not already
    s = str(s)

    # Account for the case where the item is just a value and nothing else.
    if len(s) <= 1:
        return [s, '']
    
    # Account for if the first value is just . (it's a decimal)
    if s[0] == '.':
        s = '0' + s
    
    # Find the last index at which s ceases to be a number
    for i, c in enumerate(s):
        if not c.isdigit() and c != '.':
            break
        
    # split number and unit based on index found
    if len(s[:i]) > 0:
        number=float(s[:i])
        unit= s[i:]

    # determine the case in which the string is empty and the first caller was not useful
    else:
        number=0
        unit=''

    # return number, unit pair. 
    return [number, unit]

##################################################################################
# Function          : is_number()
# Purpose           : Determine if a value is a number or not.
# Source            : https://stackoverflow.com/questions/2240303/separate-number-from-unit-in-a-string-in-python
##################################################################################

def is_number(str_val):

    # Account for if number is negative
    if str_val[0] == '-':
        str_val = str_val[1:]

    # Iterate through all characters in str_val to find non-digits
    for c in str_val:
        if not (c.isdigit() or c == '.'):
            return False
        
    return True

##################################################################################
# Function          : get_current_unit()
# Purpose           : Returns a the first unit out of a list of possible units for each attribute.
# NOTE              : currently not in use (8/15/24 version)
##################################################################################

def get_attr_unit(attr):

    if attr == "mass_units":
        return mass_units[0]

    elif attr == "SpecificHeat":
        return specific_heat_units[0]

##################################################################################
# Function          : layout_picker()
# Purpose           : Check if positions are valid & load default layout if no positions given
# idx [in]          : 
##################################################################################  

def layout_picker(idx, layout_type='preset', fit=False):
    
    default_layout = 'circle'
    layout = {'name': layout_type, "fit":False}

    # ref: https://stackoverflow.com/questions/54405704/check-if-all-values-in-dataframe-column-are-the-same
    def is_unique(s):
        a = s.to_numpy() # s.values (pandas<0.24)
        return (a[0] == a).all()
    
    # if x, y position is unique, return 
    if is_unique(local_network_data[idx].df_positions.Xlocation) and is_unique(local_network_data[idx].df_positions.Ylocation):
        if layout_type == 'preset':
            layout = {'name' : default_layout, 
                      "fit" : False}

    if fit:
        layout = {'name': layout_type, 
                  'positions': { node['data']['id'] : node['position']
                                 for node in local_network_data[idx].elems 
                                 if 'position' in node}, 
                  "fit": True}
            
        print("layout is set to ", layout["fit"])

    return layout

##################################################################################
# Function          : close_program()
# Purpose           : define shutdown sequence
##################################################################################  

def close_program():
    desktop.release_desktop(False, False) #Release AEDT desktop
    os.kill(os.getpid(), signal.SIGTERM) #Kill python instance

##################################################################################
# Function          : generate_local_network_obj()
# Purpose           : create LocalNetworkData object for network
#                     this helps with local management of cytoscape data & other data
# NOTE              : relies on local_network_data list             
##################################################################################  

def generate_local_network_obj(idx):
    #Generate Node/Edge Data given initial network in a Cytoscape-format
    nxG = generate_nx_graphv2(Network_Data[idx])
    c_links_with_directionality = network.get_link_info()
    csG, csGnodes, csGedges = generate_cs_graphv2(nxG)

    #Fix directionality in csGedges (c-links)
    for item in csGedges:
        if item['data']['LinkType'] == 'C-Link':
            name = item['data']['Name']
            if name in c_links_with_directionality:
                source = c_links_with_directionality[name]['fromNode']
                target = c_links_with_directionality[name]['toNode']

                item['data']['source'] = source
                item['data']['target'] = target

        Network_Cytoscape_Data[idx] = csG
        Network_Cytoscape_Node_Data[idx] = csGnodes
        Network_Cytoscape_Edge_Data[idx] = csGedges

    # Define large array to store each edited copy in. 
    local_network_data[idx] = LocalNetworkData(idx, networkNames[idx])

##################################################################################
# Section          : Main data transfer
# Purpose          : Set up all internal structures in Python
# NOTE             : defines some global items, such as local_network_data 
#                  : used in earlier classes / functions
##################################################################################

print("Loading first network & other network necessities...")

#Define all the units for each property in of each type

# Internal Node Units
mass_units = np.array(['ug', 
                       'mg', 
                       'gram', 
                       'kg', 
                       'ton', 
                       'oz', 
                       'lb'])

specific_heat_units = np.array(['mJ_per_Kelkg',
                                'J_per_Kelkg',
                                'J_per_Celkg',
                                'kG_per_Kelkg',
                                'btu_per_IbmFah',
                                'btu_per_IbmRank',
                                'cal_per_gKel',
                                'cal_per_gCel',
                                'erg_per_gKel',
                                'kcal_per_kgKel',
                                'kcal_per_kgCel'])

#Power units for Boundary / Internal Nodes
power_units = np.array(['fW',
                        'pW',
                        'nW',
                        'uW',
                        'mW',
                        'W',
                        'kW',
                        'megW',
                        'gW',
                        'Btu_per_hr',
                        'Btu_per_sec',
                        'dBm',
                        'dBW',
                        'HP',
                        'erg_per_sec'])

#Temperature units for Boundary Nodes
temperature_units = np.array(['mkel',
                              'ckel',
                              'dkel',
                              'kel',
                              'cel',
                              'rank',
                              'fah'])
#C-Link units
mass_flow_units = np.array(['g_per_s',
                            'kg_per_s',
                            'Ibm_per_min',
                            'Ibm_per_s'])

#R-Link Units
heat_units = np.array(['Kel_per_W',
                       'cel_per_W',
                       'FahSec_per_btu',
                       'Kels_per_J'])

# Pull list of all variables from AEDT
str_items = oDesign.GetNominalVariation() 
str_items = str_items.replace("'", "") #Remove extraneous ' apostrophe
if len(str_items) == 0:
    all_variables = {}
else: 
    all_variables = dict(item.split("=") for item in str_items.split(" ")) #Format variables into dictionary

# Pull networks from AEDT 
# GetPropvalue() takes time
Network_Data = []
for bc in Thermal_Object.GetChildNames():
    bc_obj = Thermal_Object.GetChildObject(bc)
    if bc_obj.GetPropValue('Type') == "Network":
        bc_name = bc_obj.GetPropValue('Name')
        network = Network(bc_name)
        node_names, link_names = GetNodeAndLinkNames(bc_obj)
        # Process Node Information
        for node_name in node_names:
            helper = NetworkHelper(node_name,bc_obj)
            node = helper.GetNodeInformation()
            network.add_node(node)
          
        for link_name in link_names:
            helper = NetworkHelper(link_name,bc_obj)
            link = helper.GetLinkInformation()
            network.add_link(link)
        Network_Data.append(network)

Network_Cytoscape_Data = np.full(len(Network_Data), None)
Network_Cytoscape_Node_Data = np.full(len(Network_Data), None)
Network_Cytoscape_Edge_Data = np.full(len(Network_Data), None)
networkNames = [network.get_name() for network in Network_Data]

# define array to hold all local network objects for each thermal network
local_network_data = [None for i in range(len(networkNames))]

# NOTE: The following code is also present in the callback for network switching
# Generate Node/Edge Data given initial network in a Cytoscape-format & add it to local_network_data
generate_local_network_obj(0)

#Initialize boolean value for checking if saving is in progress
saving_in_progress = False 

# set starting layout
starting_layout = layout_picker(0,  "preset", True)
current_idx = 0

app_closed = False

print("Loading successful")

##################################################################################
# Section          : Buttons & Stylesheet
# Purpose          : Define dash app, buttons, and stylesheet for UI
##################################################################################

# Ensure that DiskCacheManager is installed and running properly
# If DiskCacheManager is not working / cloud implementation is created, use CeleryManager
# Used for background callbacks (notably disabling buttons)

# Diskcache for non-production apps when developing locally
user_directory = os.path.expanduser("~")
cache = diskcache.Cache(os.path.join(user_directory, 'cacheNetworkEditor'))
background_callback_manager = DiskcacheManager(cache)

#define main dash app
app = Dash(__name__, 
           background_callback_manager = background_callback_manager, 
           suppress_callback_exceptions = True,
           )

#Define formatted buttons

# button to create internal nodes
Internal_node = dbc.Button("Internal Node", 
                           id = 'internal-node', 
                           size = "sm", 
                           className = "me-1", 
                           disabled = False)

# button to create boundary nodes
Boundary_node = dbc.Button("Boundary Node", 
                           id = 'boundary-node', 
                           size = "sm", 
                           className = "me-2")

# button to create r-links
R_link = dbc.Button("R Link", 
                    id = 'R-Link', 
                    size = "sm", 
                    className = "me-1")

# button to create c-links
c_link_button = dbc.Button("C Link", 
                           id = 'C-Link', 
                           size = "sm", 
                           className = "me-1")

# fit button to display entire graph as fit on cytoscape
fit_button = dbc.Button("Fit All", 
                        id = 'fit-button', 
                        n_clicks = 0, 
                        size = "sm", 
                        className = "me-1")

# Reset button to show what to change 
reset_button = dbc.Button("Reset", 
                          id = 'reset-button', 
                          size = "sm", 
                          className = "me-1")

# Informational tooltip for reset button
reset_popup = dbc.Popover(
                        [
                            dbc.PopoverHeader("Reset Current Network"),
                        ],
                        id = f"reset-popover-button",
                        target = f"reset-button",
                        placement = "bottom",
                        trigger = "hover",
                        is_open = False)

# Show All button to display Modal Dialogue
show_all_info = dbc.Button("Table", id='show-all-info', size='sm', className='me-1')

# Informational tooltip for Show All button
show_all_info_popup = dbc.Popover(
                        [
                            dbc.PopoverHeader("Show all node/link info"),
                        ],
                        id = f"show-info-popover-button",
                        target = f"show-all-info",
                        placement = "bottom",
                        trigger = "hover",
                        is_open = False)


#Define modal menu items
modal_nodes_button = dbc.Button("Nodes", 
                                id = 'modal-nodes-button', 
                                className = "me-1", 
                                active=True, 
                                outline=True, 
                                color="primary")
modal_links_button = dbc.Button("Links", 
                                id = 'modal-links-button', 
                                className = "me-1", 
                                active = True, 
                                outline = True, 
                                color = "primary")
modal_internal_button = dbc.Button("Internal Nodes", 
                                   id = 'modal-internal-button', 
                                   className = "me-1", 
                                   active = True, 
                                   outline = True, 
                                   color = "primary")
modal_face_node_button = dbc.Button("Face Nodes", 
                                    id = 'modal-face-node-button', 
                                    className = "me-1", 
                                    active = True, 
                                    outline = True, 
                                    color = "primary")
modal_boundary_node_button = dbc.Button("Boundary Nodes", 
                                        id = 'modal-boundary-node-button', 
                                        className = "me-1", 
                                        active = True, 
                                        outline = True, 
                                        color = "primary")

# Modal popup to display information about different kinds of nodes / links
large_modal_popup = dbc.Modal(
                        [
                            
                            dbc.ModalHeader(
                                children=[
                                    html.Div(
                                        [
                                            html.Label([modal_nodes_button]),
                                            html.Label([modal_links_button]),
                                            html.Label([modal_internal_button]),
                                            html.Label([modal_face_node_button]),
                                            html.Label([modal_boundary_node_button]),
                                        ],
                                        style={'border' : '1px solid black',
                                               'padding' : '5px', 
                                               'width' : 'max-content'}
                                        ),
                                        ],
                            ),
                        
        
                            dbc.ModalBody("A large model", 
                                          id='large-modal-body')
                        ],
                        id='large-modal-dlg',
                        size='xl',
                        is_open=False
)

# close button
close_button = dbc.Button("Close", 
                          id='close-button', 
                          size="sm", 
                          className="me-1")

# informational tooltip for close button
close_popup = dbc.Popover([dbc.PopoverHeader("Close Network Editor")],
                           id = f"close-popover-button",
                           target = f"close-button",
                           placement = "bottom",
                           trigger = "hover",
                           is_open = False)

# button to save a single network
save_single_button = dbc.Button("Save", 
                                size = "sm", 
                                id = "save-single-button") 

# informational tooltip for single network saving button
save_single_popup = dbc.Popover([dbc.PopoverHeader("Save Current Network")],
                                 id = f"save-single-popover-button",
                                 target = f"save-single-button",
                                 placement = "bottom",
                                 trigger = "hover",
                                 is_open = False)

# button to save all networks 
save_all_button = dbc.Button("Save All", size="sm", id='save-all-button')

# Save All Button informational tooltip
save_all_popup = dbc.Popover([dbc.PopoverHeader("Save All Networks")],
                              id=f"save-all-popover-button",
                              target=f"save-all-button",
                              placement="bottom",
                              trigger="hover",
                              is_open=False)

# Check button to check connectivity
check_button = dbc.Button("Check", size="sm", id='check-button')

# check button informational tooltip
check_popup = dbc.Popover([dbc.PopoverHeader("Check if all nodes are connected")],
                           id=f"check-popover-button",
                           target=f"check-button",
                           placement="bottom",
                           trigger="hover",
                           is_open=False)

# instructions button
instructions_button = dbc.Button(f"Info",
                                 id = f"popover-button-target", 
                                 className = "mx-2", 
                                 n_clicks = 0, 
                                 size = "sm", 
                                 color = "danger", 
                                 outline = True)

# instruction information button informational tooltip
instructions_popup = dbc.Popover(
                        [
                            dbc.PopoverHeader("Instructions"),
                            dbc.PopoverBody(
                                children=[
                                    "1: To move nodes around, press and drag",
                                    html.Br(),
                                    "2: To edit node or edge attributes, use the Properties box",
                                    html.Br(),
                                    "3: To add node, click on the add node button and choose location in the editor window"
                                ]               
                            ),
                        ],
                        id=f"popover-button",
                        target=f"popover-button-target",
                        placement="bottom",
                        trigger="hover",
                        is_open=False)

# Create Navigation bar with instructions button and AEDT Network Editor title
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem([instructions_button, instructions_popup]),
    ],
    brand = [html.B("AEDT Network Editor")],
    brand_href = "#",
    color = "white",
    light = True,
    style = {'border' : '1px solid black',
             'padding' : '5px'}
)

# define alert message (i.e. Saved : Check AEDT)
alert = dbc.Alert("Program Loaded",
                  id="alert-message",
                  dismissable=True,
                  is_open=True,
                  color='info')
        
##################################################################################
# Section          : App Layout
# Purpose          : Define the UI layout in Cytoscape
##################################################################################
app.layout = html.Div(
    children = [
        # Large XL Dialog popup
        large_modal_popup,

        # Dialog - Confirm Closing
        dcc.ConfirmDialog(
        id='confirm-danger',
        message='',
        ),

        # Dialog - Confirm Reset
        dcc.ConfirmDialog(
        id='confirm-reset',
        message='',
        ),

        # first row - top box (Select Network)
        html.Div([
            #Row - AEDT Network Editor Title
            html.Div([
                navbar,
            ],
            style =  {'display': 'inline-block',
                    'position': 'absolute', 
                    'right' : '1%', 
                    'left': '1%',
                    'top': '1%', 
                    'width': '98%', 
                    'bottom' : '1%'}
            ),

            # #Row - Select Network Dropdown menu
            html.Div([
                html.B('Select Network'),
                html.Div(
                    dcc.Dropdown(
                        id='dropdown-update-network',
                        value=networkNames[0],
                        clearable=False,
                        options=[
                            {'label': name, 'value': name}
                            for name in networkNames
                        ]
                    ),

                    style = {'border' : '1px solid black',
                             'padding' : '5px',
                             'justify-content' : 'center',
                             'align-items' : "left"}
                ), 
            ],
            style =  {'display' : 'inline-block',
                      'position': 'absolute', 
                      'right' : '1%', 
                      'left' : '1%', 
                      'top' : '12%', 
                      'width' : '98%', 
                      'bottom' : '1%'}
            ),

            #Row - (Visualize)
            html.Div([
                html.Label(html.B('Visualize')),
                html.Div([
                    # Toggle Nodes
                    html.Div([
                            daq.BooleanSwitch(
                                id='toggle-node-labels',
                                label='Show Node Names',
                                on=True,
                                style={'padding':'5px'},
                                color='#0c63e4'
                            ),
                            daq.BooleanSwitch(
                                id='toggle-edge-labels',
                                label='Show Link values',
                                on=False,
                                style={'padding':'5px'},
                                color='#0c63e4'
                            )
                        ],   
                        style = {'display': 'flex',
                                'flex-direction' : 'row', 
                                'justify-content' : 'center',  
                                'align-items': "left"}
                    ),
                ],
                    
                style = {'border' : '1px solid black',
                         'padding':'5px'}
                ),
            ],
            style = {'display': 'inline-block',
                     'position': 'absolute', 
                     'right' : '1%', 
                     'left': '1%', 
                     'top': '25%', 
                     'width': '98%', 
                     'bottom' : '1%'}
            ),
            
            #Row - Fit 
            html.Div([
                html.Label(html.B('Fit')),
                html.Div(
                    [
                        html.Label(fit_button, 
                                   style = {'padding' : '2px'}
                        ),
                    ],
                    style = {'border' : '1px solid black',
                            'padding' : '5px',
                            'display': 'flex',
                            'flex-direction' : 'row',
                            'justify-content' : 'center',
                            'align-items': "left"}
                    ),
                ],
                style = {'display': 'inline-block',
                        'position': 'absolute', 
                        'right' : '1%', 
                        'left': '1%', 
                        'top': '43%', 
                        'width': '98%', 
                        'bottom' : '1%'}
            ),
            

            #Row - (Create)
            html.Div([
                html.Label(html.B('Create')),
                html.Div(
                    [
                        html.Label([Internal_node]),
                        html.Label([Boundary_node]),
                        html.Label([R_link]),
                        html.Label([c_link_button]),
                    ],

                    style = {'display': 'flex', 
                            'flex-direction' : 'row', 
                            'justify-content' : 'center',  
                            'align-items': "center", 
                            'border':'1px solid black',
                            'padding':'5px'}
                    ),
                ],

                style = {'display': 'inline-block',
                        'position': 'absolute', 
                        'right' : '1%', 
                        'left': '1%', 
                        'top': '56%', 
                        'width': '98%', 
                        'bottom' : '1%'}
            ),

            # Row - (Network Options)
            html.Div([
                    html.Label(html.B('Network Options')),
                    html.Div([
                        
                        # Table button + tooltip popup
                        html.Label([show_all_info, show_all_info_popup]), 
        
                        # Check all button + tooltip popup
                        html.Label([check_button, check_popup]),

                        #Save single button + tooltip popup
                        html.Label([save_single_button, save_single_popup]),

                        # Save all button + tooltip popup
                        html.Label([save_all_button, save_all_popup]),     

                        # Reset button + tooltip popup
                        html.Label([reset_button, reset_popup]),

                        # Close button + tooltip popup
                        html.Label([close_button, close_popup]),
                        ], 

                        style = {'display' : 'flex', 
                                'flex-direction' : 'row', 
                                'justify-content' : 'center',  
                                'align-items' : "center", 
                                'border' : '1px solid black',
                                'padding' : '5px'}
                    ),
                ],

                style={'display' : 'inline-block',
                    'position' : 'absolute', 
                    'right' : '1%', 
                    'left' : '1%', 
                    'top' : '69%', 
                    'width' : '98%', 
                    'bottom' : '1%'}
            ),
                
            # Output section to display alert messages
            html.Div(
                [
                    html.Label(html.B("Output")),
                    html.Div([alert])
                ],

                style={'display' : 'inline-block', 
                    'position' : 'absolute', 
                    'right' : '1%', 
                    'left' : '1%', 
                    'top' : '81%', 
                    'width' : '98%', 
                    'bottom' : '1%'}
                ),
        ],
        
        style = {'display' : 'inline-block',
                'position' : 'absolute', 
                'left' : '1%', 
                'top' : '1%', 
                'width' : '20%', 
                'height': '60%',
                'border': '2px solid black', 
                'background-color': 'white',
                'padding':'10px'}
        ),

        # 2nd Right column - Cytoscape area
        html.Div(
            [cyto.Cytoscape(
            id='cytoscape-1',
            style={'display' : 'inline-block',
                   'position': 'absolute', 
                   'left' : '22%', 
                   'top' : '1%', 
                   'width' : '77%', 
                   'height' : '98%',
                   'border' : '2px solid black'},

            minZoom=0.1,
            maxZoom=6,
            zoomingEnabled=True,
            zoom=0.8,
            elements=local_network_data[0].elems,
            layout=starting_layout,
            autoRefreshLayout = True,
            autounselectify=False,
            
            # The menu that appears after right clicking in Cytoscape
            contextMenu=[
                    {
                        "id": "remove-item",
                        "label": "Remove",
                        "tooltipText": "Remove",
                        "availableOn": ["node", "edge"],
                    }

            ],   
            stylesheet=local_network_data[0].stylesheetManager.default_stylesheet,
            ),],

            id = 'cytoscape-1-div'
            
            ),

        # Property display location
        html.Div([
                html.B('Properties'),
                html.Br(),
                html.Div(id='table-container',style={'overflow':'scroll'}),
                dcc.Markdown(id='cytoscape-selectedNodeData-markdown'),
            ],
            style = {'position': 'absolute', 
                    'left': '1%', 
                    'top': '62%', 
                    'width': '20%', 
                    'height': '37%',
                    'display': 'inline-block', 
                    'border': '2px solid black',
                    'background-color': 'white',
                    'padding':'10px'}
        ),

    ],

    id = 'outermost-div-box',
)

###############################################################################
# Callbacks
###############################################################################
# load_network                   : select and load a specified AEDT network
# update_zoom                    : update zoom features when 'fit' button is clicked
# update_output_after_remove     : remove nodes/edges from elements
# reset_elem_layout              : reset all elements to default values
# close_app & update_output      : display pop-up and confirm app close
# update_labels                  : toggle r-link / node values on/off
# update_layout                  : switch between layout 
# display_editable_table         : display editable table information
# update_dataframe,              : update local data when table is edited (nodes)
#                   contains     : update_edge_with_new_node_name()
#
# display_edge_editable_table    : display other table properties
# update_edge_dataframe          : update local data when table is edited (rlinks)
# add_internal_nodes             : creation of internal nodes
# add_boundary_nodes             : creation of boundary nodes
# display_selected_node_data     : selection of a node (i.e. the red outline)
# add_rlink                      : create rlinks between selected nodes
# add_clink                      : create clinks between selected nodes
# save_all_to_AEDT,              : save all data back to AEDT
# -> save_single_network()       : save the single selected network
#
# save_singular_network          : Save currently viewed network
# check_connectivity             : Check if all nodes are connected, highlight
#                                : highlight unconnected nodes
# get_unconnected_nodes          : get all nodes that are not connected to first face
# open_modal_display             : open modal dialog to show all item information
# -> display_face_node_table     : open the face node table in modal view
# -> display_internal_node_table : open the internal node table in modal view
# -> display_boundary_node_table : open the boundary node table in modal view
# -> display_all_nodes_table     : open the table with all nodes in modal view
# -> display_all_links_table     : open the table with all links in modal view
# -> create_modal_table          : create AGGrid object with the right parameters
# -> format_modal_columns        : format columns of AGGrid
# -> format_rows                 : format rows of AGGrid
# -> format_link_dict_arr        : format links to show the right information
# -> format_boundary_dict_arr    : format boundary nodes to show the right info
# -> format_int_dict_arr         : format internal nodes to show the right info
# -> format_face_dict_arr        : format face nodes to show the right info
# shutdown                       : initiate shutdown sequence when tab closed
#                                : note: relies on check_closing.js 
###############################################################################

###############################################################################
# This section focuses on switching between different networks
###############################################################################

@callback([Output('cytoscape-1', 'elements', allow_duplicate=True),
           Output('cytoscape-1', 'layout', allow_duplicate=True),
           Output('cytoscape-1', 'stylesheet', allow_duplicate=True),
           Output('cytoscape-1','autoRefreshLayout',allow_duplicate=True)],
           Input('dropdown-update-network', 'value'),
           State('cytoscape-1', 'elements'),
           State('cytoscape-1','layout'),
           prevent_initial_call=True)
def load_network(networkName, default_elems, default_layout):
    global local_network_data, saving_in_progress, current_idx
    if saving_in_progress:
        return default_elems, default_layout, local_network_data[idx].stylesheetManager.getCurrentStylesheet(), False
    
    idx = networkNames.index(networkName)

    # Reset current stylesheet
    local_network_data[current_idx].stylesheetManager.resetStylesheetFromMarker()

    # Save current positions
    local_network_data[current_idx].update_positions_from_elems(default_elems)

    # set current idx
    current_idx = idx

    # if data is not already stored, create object
    if local_network_data[idx] is None:
        
        # generate local network object
        generate_local_network_obj(idx)

    # update display data
    local_network_data[idx].update_elem_display_data()
    
    # get elems / layout from local network object
    elems = local_network_data[idx].elems
    layout = layout_picker(idx)

    return elems, layout, local_network_data[idx].stylesheetManager.getCurrentStylesheet(), True

################################################################################
# Code to update zooming features 
# NOTE: updates both layout and elements, then removes positional data from layout
################################################################################

@callback([Output('cytoscape-1','elements',allow_duplicate=True), 
            Output('cytoscape-1', 'layout',allow_duplicate=True),
            Output('cytoscape-1','autoRefreshLayout',allow_duplicate=True)], 
            Input('fit-button', 'n_clicks'),
            State('cytoscape-1','elements'),
            State('cytoscape-1','layout'),
            State('dropdown-update-network', 'value'),
            prevent_initial_call=True)
def update_zoom(n_clicks, elems, layout, networkName):
    print("Zoom into objects by")

    idx = networkNames.index(networkName)

    if n_clicks > 0:

        # update positions 
        local_network_data[idx].update_positions_from_elems(elems)

        # zoom into objects by relying on positional values in layout
        new_layout = layout_picker(idx, layout['name'], fit=True)
        return local_network_data[idx].elems, new_layout, True

    else:
        print('else cond of zoom')
        return elems, layout, False
    
# since positional updates in layout mess with element positions,
# this callback removes positions in layout
# effectively zooming in, but not destroying positional functionality
@callback([Output('cytoscape-1','elements',allow_duplicate=True), 
            Output('cytoscape-1', 'layout',allow_duplicate=True),
            Output('cytoscape-1','autoRefreshLayout',allow_duplicate=True)], 
            Input('cytoscape-1','elements'), 
            Input('cytoscape-1', 'layout'),
            Input('cytoscape-1','autoRefreshLayout'),
            State('dropdown-update-network', 'value'),
            prevent_initial_call=True)
def refresh_zoom(elems, layout, autoRefreshLayout, networkName):
    if autoRefreshLayout:
        print("Layout refreshed.")
        idx = networkNames.index(networkName)

        return elems, layout_picker(idx, layout['name'], fit=False), True

################################################################################
# Code to remove nodes/edges from elements - uses contextmenudata
################################################################################

# open small right click context menu to show remove option
@callback(
    Output("cytoscape-1", "elements"),
    Input("cytoscape-1", "contextMenuData"),
    State("cytoscape-1", "elements"),
    State('dropdown-update-network','value')
)
def update_output_after_remove(ctxMenuData, elems, networkName):
    idx = networkNames.index(networkName)

    # no item clicked, return default
    if not ctxMenuData:
        return elems

    # Remove clicked
    if ctxMenuData["menuItemId"] == "remove-item":

        # run remove element process
        elems = remove_element(ctxMenuData, elems, idx)

        # log entry to show which element was clicked
        print(f"You clicked on: {str(ctxMenuData)}")

    # return elems after change
    return elems

# runs when remove option is clicked on context menu
def remove_element(ctxMenuData, elems, idx):

    # load all data
    local_data = local_network_data[idx]
    element_id = ctxMenuData['elementId']
    id_manager = local_data.get_id_manager()
    selected_name = id_manager.get_name(element_id)

    df_face = local_network_data[idx].df_face
    is_edge = False

    # update positions
    local_data.update_positions_from_elems(elems)

    # Account for if item is a face node:
    if selected_name in df_face['Name'].values:
        print("Clicked on Face Node. Cannot remove Face node. Ignoring.")
        return elems

    # Account for source and target if labelled as edgeTarget/edgeSource if the item is a link
    if 'edgeSource' in ctxMenuData and 'edgeTarget' in ctxMenuData:
        source = ctxMenuData['edgeSource']
        target = ctxMenuData['edgeTarget']
        
        local_data.remove_link(source, target)

        is_edge = True

    # Account for source and edge if the item is a link
    elif 'source' in ctxMenuData and 'target' in ctxMenuData:
        source = ctxMenuData['source']
        target = ctxMenuData['target']
        
        local_data.remove_link(source, target)

        is_edge = True

    # Remove items if not an edge / remove items from local elems structure
    local_data.update_elems(elems)
    local_data.update_positions()
    local_data.remove_items_with_name(selected_name, is_edge)

    # print log message to signify node removal
    print("Removed!")

    return local_data.elems

################################################################################
# Refresh Stylsheet 
################################################################################

@callback(Output('cytoscape-1','stylesheet', allow_duplicate=True),
          Input('cytoscape-1','stylesheet'),
          prevent_initial_call = True)

def refresh_stylesheet(stylesheet):
    print("Stylesheet refreshed")
    return stylesheet

################################################################################
# Reset elements to original state (doesn't reload all data from AEDT)
################################################################################

# open confirmation dialog for user to confirm if they want to reset
@callback(Output('confirm-reset', 'displayed'),
          Output('confirm-reset', 'message'),
          Input('reset-button','n_clicks'),
          prevent_initial_call = True)
def reset_dialogue(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        ret_dlg = 'Are you sure you want to reset the program?'
        return [True, ret_dlg]

    return [False, '']

# if confirmation OK, reset elems and layouts to default 
@callback([Output('cytoscape-1', 'elements', allow_duplicate=True),
           Output('cytoscape-1','layout',allow_duplicate=True),
           Output('cytoscape-1', 'stylesheet', allow_duplicate=True)],
           Input('confirm-reset', 'submit_n_clicks'),
           State('reset-button','n_clicks'),
           State('cytoscape-1', 'elements'),
           State('cytoscape-1','layout'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def reset_elem_layout(submit_n_clicks, n_clicks_reset, elems, default_layout, networkName):
    
    idx = networkNames.index(networkName)

    # set default layout
    layout = default_layout

    if submit_n_clicks:
        if n_clicks_reset is None:
            print('else cond of reset')
            raise PreventUpdate
        
        if n_clicks_reset is not None and n_clicks_reset > 0:

            # reset all values
            local_network_data[idx].reset_all_values()

            # Reset current stylesheet to refelect reset changes
            local_network_data[idx].stylesheetManager.resetStylesheetFromMarker()

            # reset stylesheet internal nodes
            local_network_data[idx].stylesheetManager.resetStylesheetGivenInt(local_network_data[idx].df_int)

            # set layout
            layout = layout_picker(idx)

    return local_network_data[idx].elems, layout, local_network_data[idx].stylesheetManager.getCurrentStylesheet()

################################################################################
# Close the app (referring to close button)
# NOTE: Doesn't 'close' tab or webUI, but closes the instance of Python entirely
################################################################################

# this displays the confirmation dialogue
@callback(Output('confirm-danger', 'displayed', allow_duplicate=True),
          Output('confirm-danger', 'message'),
          Input('close-button','n_clicks'),
          prevent_initial_call = True)
def close_app_confirmation(n_clicks):

    if n_clicks is not None and n_clicks > 0:

        confirmation_dlg_msg = 'Are you sure you want to close the program?'
        return [True, confirmation_dlg_msg]

    return False

# if confirmation dlg is clicked to say yes, this callback runs
# this switches to an alternate html view that shows that the editor is closed
@callback(Output('confirm-danger', 'displayed', allow_duplicate=True),
          Output('outermost-div-box', 'children', allow_duplicate=True),
          Output('outermost-div-box', 'style', allow_duplicate=True),
          Input('confirm-danger', 'submit_n_clicks'),
          State('outermost-div-box', 'children'),
          State('outermost-div-box', 'style'),
          prevent_initial_call = True)
def update_output(submit_n_clicks, default_html_children, default_style):
    global app_closed

    display_confirmation_dlg = False

    if submit_n_clicks:

        app_closed = True
        
        display_text = 'Network Editor Closed'
        text_style = {'min-height': 'auto', 
                      'min-width' : 'auto',
                      'display' : 'flex',
                      'justify-content' : 'center',
                      'align-items': 'center',
                      'border': '2px solid black', 
                      'background-color': 'white',
                      'padding':'10px'}
        
        html_children = [html.H1(display_text),]

        return display_confirmation_dlg, html_children, text_style
        
    return display_confirmation_dlg, default_html_children, default_style

# this callback runs after html view is changed
# this kills python & closes the program
@callback(Output('confirm-danger', 'submit_n_clicks', allow_duplicate=True),
          Input('confirm-danger', 'submit_n_clicks'),
          prevent_initial_call = True)
def kill_python(submit_n_clicks):
    global app_closed
    print("Program closed via close button")
    if submit_n_clicks:
        if app_closed:
            close_program()
            
    return submit_n_clicks


################################################################################
# Toggle node and r-link names/values
################################################################################

@callback(Output('cytoscape-1', 'stylesheet'),
          Output('cytoscape-1', 'elements', allow_duplicate = True),
          Input('toggle-node-labels', 'on'),
          Input('toggle-edge-labels', 'on'),
          State('dropdown-update-network', 'value'),
          State('cytoscape-1', 'elements'),
          prevent_initial_call=True)
def update_labels(btn2, btn3, networkName, elems):
    idx = networkNames.index(networkName)
    node_opacity = 1 if btn2 else 0

    #update element positions
    local_network_data[idx].update_positions_from_elems(elems)

    #update edge data in elems from df_links
    local_network_data[idx].update_elem_display_data()

    # set stylesheet to reflect current data
    r_link_edge_label = 'data(link_value)' if btn3 else 'data(Name)'
    c_link_edge_label = 'data(mass_flow)' if btn3 else 'data(Name)'

    # update labels given link data
    local_network_data[idx].stylesheetManager.update_labels(r_link_edge_label, c_link_edge_label, node_opacity)      

    return local_network_data[idx].stylesheetManager.getCurrentStylesheet(), local_network_data[idx].elems
    
################################################################################
# This section enables the left-side selection of layouts (change layout, not in usage)
# This is an attempt to go around an active bug in cytoscape where positions are not saved (?)
# NOTE: not in usage
################################################################################

@callback(Output('cytoscape-1-div', 'children', allow_duplicate=True),
              Input('dropdown-update-layout', 'value'), 
              State('dropdown-update-network', 'value'),
              State('cytoscape-1', 'elements'),
              prevent_initial_call=True)
def update_layout(layout_type, networkName, elems):

    idx = networkNames.index(networkName)
    #local_network_data[idx].restore_positions()
    local_network_data[idx].zero_elem_positions()

    if layout_type is not None:

        # define new cytoscape object without positional data in layout
        refreshed_cytoscape = cyto.Cytoscape(
            id = 'cytoscape-1',
            style = {'display' : 'inline-block', 
                   'position' : 'absolute', 
                   'left' : '22%', 
                   'top' : '1%', 
                   'width' : '77%', 
                   'height' : '98%',
                   'border' : '2px solid black'},

            minZoom = 0.1,
            maxZoom = 6,
            zoomingEnabled = True,
            zoom = 0.8,
            elements = [],
            layout = {'name' : 'preset'},
            autoRefreshLayout = True,
            autounselectify = False,
            
            #The menu that appears after right clicking in cytoscape
            contextMenu=[
                    {
                        "id" : "remove-item",
                        "label" : "Remove",
                        "tooltipText" : "Remove",
                        "availableOn" : ["node", "edge"],
                    }

            ],   
            stylesheet=local_network_data[idx].stylesheetManager.default_stylesheet,
            )

        return refreshed_cytoscape
    
@callback(Output('cytoscape-1-div', 'children', allow_duplicate=True),
              Input('cytoscape-1-div', 'children'), 
              State('dropdown-update-layout', 'value'), 
              State('dropdown-update-network', 'value'),
              State('cytoscape-1', 'elements'),
              State('cytoscape-1', 'layout'),
              prevent_initial_call=True)
def refresh_layout(misc_cytoscape_obj, layout_type, networkName, elems, layout):

    idx = networkNames.index(networkName)

    if not (elems and layout):
        refreshed_cytoscape = cyto.Cytoscape(
                id='cytoscape-1',
                style={'display':'inline-block','position': 'absolute', 'left': '22%', 'top': '1%', 'width': '77%', 'height': '98%',
                    'border':'2px solid black'},

                minZoom=0.1,
                maxZoom=6,
                zoomingEnabled=True,
                zoom=0.8,
                elements=local_network_data[idx].elems,
                layout=layout_picker(idx, layout_type, fit=True),
                autoRefreshLayout=True,
                autounselectify=False,
                
                #The menu that appears after right clicking in cytoscape
                contextMenu=[
                        {
                            "id": "remove-item",
                            "label": "Remove",
                            "tooltipText": "Remove",
                            "availableOn": ["node", "edge"],
                        }

                ],   
                stylesheet=local_network_data[idx].stylesheetManager.default_stylesheet,
                )
        
        return refreshed_cytoscape
    
################################################################################
# Display the table when a node is clicked (reliant on dashAgGridFunctions.js file)
################################################################################

@callback(Output('table-container','children',allow_duplicate=True),
            Input('cytoscape-1','tapNodeData'), 
            State('dropdown-update-network', 'value'),
            prevent_initial_call=True)
def display_editable_table(tapNodeData, networkName):
    if tapNodeData:
        #Load local values
        idx = networkNames.index(networkName)
        df_int = local_network_data[idx].df_int
        df_face = local_network_data[idx].df_face
        df_boundary = local_network_data[idx].df_boundary

        # define columns for table (reliant on external .js)
        custom_columns = [
            {
                'field' : 'Name',
                'editable' : False 
            },
            {
                'field' : 'Value',
                'editable' : {"function" : "editable(params, 'Node')"},
                "cellEditorSelector" : {"function" : "dynamicCellEditor(params, '')"},
                'singleClickEdit' : True
            },
            {
                'field' : 'Units',
                'editable' : {"function" : "editable(params, 'Units')"},
                "cellEditorSelector": {"function" : "unitsDropdown(params)"},
                'singleClickEdit' : True
            },
            {
                'field' : 'Evaluated Value',
                'editable' : False,
            },
        ] 
        
        # case where node is internal node
        if tapNodeData['Type'] == 'Internal Node':

            # foramt data into two columns 
            dff = df_int[df_int['Name'] == tapNodeData['Name']]
            dff2 = dff.T.reset_index().set_axis(['Name', 'Value'], axis=1)
            temp_rows = dff2.to_dict('records') 

            # define rows for table
            custom_rows = [None for i in range(5)] 

            # format all rows to fit Internal Node properties
            for item in temp_rows:
                if item['Name'] == 'Name':
                    custom_rows[0] = item

                elif item['Name'] == 'Type':
                    custom_rows[1] = item

                elif item['Name'] == 'Mass':
                    custom_rows[2] = format_value_units(item)

                elif item['Name'] == 'SpecificHeat':
                    custom_rows[3] = format_value_units(item)

                elif item['Name'] == 'Power':
                    custom_rows[4] = format_value_units(item)

        # case if node is face node
        elif tapNodeData['Type'] == 'Face Node':
            dff = df_face[df_face['Name'] == tapNodeData['Name']]

            # check if face nodes exist
            if dff.empty:
                return []

            # reformat into two column data
            dff2 = dff.T.reset_index().set_axis(['Name', 'Value'], axis=1)
            temp_rows = dff2.to_dict('records') 

            # get the current resistance choice -> specified, compute, etc
            # (to show / hide data)
            resistance_choice = dff['ResistanceChoice'].values[0]

            # define rows for table
            custom_rows = [None for i in range(4)]

            # Add extra rows if Specified, notably add thermal resistance
            is_specified = False
            if resistance_choice == 'Specified':
                custom_rows.append(None)
                is_specified = True

            # Add extra rows if Compute, notably add thermal resistance
            is_compute = False
            if resistance_choice == 'Compute':
                custom_rows.append(None)
                custom_rows.append(None)
                is_compute = True

            # format all rows to fit Face Node properties
            for item in temp_rows:
                if item['Name'] == 'Name':
                    custom_rows[0] = item

                elif item['Name'] == 'Type':
                    custom_rows[1] = item

                elif item['Name'] == 'FaceID':
                    custom_rows[2] = item

                elif item['Name'] == 'ResistanceChoice':
                    custom_rows[3] = item

                elif item['Name'] == 'ThermalResistance':
                    if is_specified:
                        custom_rows[4] = format_value_units(item)

                elif item['Name'] == 'Thickness':
                    if is_compute:
                        custom_rows[4] = format_value_units(item)

                elif item['Name'] == 'Material':
                    if is_compute:
                        custom_rows[5] = item
        
        # case if node is boundary node
        elif tapNodeData['Type'] == 'Boundary Node':

            # format data into 2 columns
            dff = df_boundary[df_boundary['Name'] == tapNodeData['Name']]
            dff2 = dff.T.reset_index().set_axis(['Name', 'Value'], axis=1)
            temp_rows = dff2.to_dict('records') 

            # define rows for table
            custom_rows = [None for i in range(4)]

            # get current thermal parameter (to show / hide data)
            thermalparameter = dff['ThermalParameters'].values[0]

            # format all rows to fit Boundary Node properties
            for item in temp_rows:
                if item['Name'] == 'Name':
                    custom_rows[0] = item

                elif item['Name'] == 'Type':
                    custom_rows[1] = item

                elif item['Name'] == 'ThermalParameters':
                    custom_rows[2] = item

                elif item['Name'] == 'Power':
                    if thermalparameter == 'Power':
                        custom_rows[3] = format_value_units(item)

                elif item['Name'] == 'Temperature':
                    if thermalparameter == 'Temperature':
                        custom_rows[3] = format_value_units(item)

        # create table 
        editable_table = dag.AgGrid(id='editable-table',
                                    defaultColDef = {'editable': True},
                                    columnDefs = custom_columns,
                                    rowData = custom_rows, 
                                    style = {'height': '30vh'},
                                    dashGridOptions= {
                                         'autoSizeStrategy' : {
                                            'type' : 'fitCellContents',
                                            'defaultMinWidth' : 100,
                                         }
                                    }
                                    )

        # return table to update display
        return editable_table
    
    # return nothing if no changes made 
    else:
        return []
        
################################################################################
# Update node after table values are changed
################################################################################

@callback(Output('table-container','children', allow_duplicate=True),
          Output('cytoscape-1', 'elements', allow_duplicate=True),
          Output('cytoscape-1', 'stylesheet', allow_duplicate=True),
          Input('editable-table','cellValueChanged'),
          State('cytoscape-1','tapNodeData'),
          State('cytoscape-1', 'elements'),
          State('dropdown-update-network', 'value'),
          State('cytoscape-1', 'selectedNodeData'),
          prevent_initial_call=True)
def update_dataframe(data, tapNodeData, elems, networkName, selected_nodes):
    #Load local values
    idx = networkNames.index(networkName)
    localNetworkItem = local_network_data[idx]
    df_int = local_network_data[idx].df_int
    df_face = local_network_data[idx].df_face
    df_boundary = local_network_data[idx].df_boundary
    df_positions = local_network_data[idx].df_positions
    name_updated = False

    # update local values
    localNetworkItem.update_elems(elems)

    if data and tapNodeData:
        for i in range(len(data)):

            name_updated = False

            # set name of row, e.g what property is being edited
            row_name = data[i]['data']['Name']

            # set units & account for empty units
            units = ''
            if 'Units' in data[i]['data']:
                units = data[i]['data']['Units']

                if units == '':
                    units = ''

            # load in value
            value = str(data[i]['data']['Value'])

            # account for empty values column
            if len(value) == 0:
                value = str(0)

            # prevent dropdown menus and Name from being overriden
            # set updated value
            dropdown_names = ['ResistanceChoice', 'ThermalParameters', 'Name']
            if not variableExists(value) and row_name not in dropdown_names:
                # Check for malicious input, i.e. value is not an integer
                if is_number(value):
                    updated_value = str(value) + units

                # if value is not an integer, reset to 0
                else:
                    updated_value = str(0) + units

            else:
                updated_value = value

            # check if name is unique if name is edited
            if row_name == 'Name':
                id_manager = localNetworkItem.id_manager()
                if id_manager.is_name_unique(updated_value):
                    name_updated = True

                else:
                    break
            
            # depending on what type of node it is, edit data accordingly
            if tapNodeData['Type'] == 'Internal Node':

                # get row that matches the node name
                selectedRow = df_int.loc[df_int['Name']==tapNodeData['Name']]
                indices = list(df_int.index.values) 

                # update that value for all rows that match the node name
                for j in indices:
                    selectedRow[row_name][j] = updated_value
                    df_int.loc[df_int['Name'] == tapNodeData['Name']] = selectedRow

                # add internal node color accordingly 
                if row_name == 'Power':
                    local_network_data[idx].stylesheetManager.addIntNodeColorFromStrVal(tapNodeData['Name'], updated_value)

            elif tapNodeData['Type'] == 'Face Node':

                # get row that matches the node name
                selectedRow = df_face.loc[df_face['Name'] == tapNodeData['Name']]
                indices = list(df_face.index.values) 

                # update that value for all rows that match the node name
                for j in indices:
                    selectedRow[row_name][j] = updated_value
                    df_face.loc[df_face['Name']==tapNodeData['Name']] = selectedRow

            elif tapNodeData['Type'] == 'Boundary Node':

                # get row that matches the node name
                selectedRow = df_boundary.loc[df_boundary['Name']==tapNodeData['Name']]
                indices = list(df_boundary.index.values) 

                # update that value for all rows that match the node name
                for j in indices:
                    selectedRow[row_name][j] = updated_value
                    df_boundary.loc[df_boundary['Name']==tapNodeData['Name']] = selectedRow

            # Add fix for if name is updated
            if name_updated:
                
                # set old name & new name
                old_name = tapNodeData['Name']
                new_name = updated_value

                # get id manager & update value
                id_manager = localNetworkItem.get_id_manager()

                # update elements to reflect new name
                localNetworkItem.update_elem_name(old_name, new_name)

                # changes names on df_positions
                df_positions.loc[df_positions['Name'] == old_name, 'Name'] = new_name

                # Change cytoscape name
                tapNodeData['Name'] = new_name

                # update name in id_manager
                id_manager.update_name(old_name, new_name)

                # update stylesheet by deselecting item
                local_network_data[idx].stylesheetManager.resetStylesheetFromMarker()

                # log that the name has been updated
                return [], localNetworkItem.elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()

    return display_editable_table(tapNodeData, networkName), elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()

################################################################################
# Display the table when an edge is clicked (reliant on dashAgGridFunctions.js file)
################################################################################

@callback(Output('table-container','children',allow_duplicate=True),
              Input('cytoscape-1','tapEdgeData'), 
              State('dropdown-update-network', 'value'),
              prevent_initial_call=True)
def display_edge_editable_table(tapEdgeData, networkName):
    if tapEdgeData:
        idx = networkNames.index(networkName)
        df_links = local_network_data[idx].df_links

        # reformat df_links into 2 column data & dictionaries
        chosen_link_name = tapEdgeData['Name']
        dff = df_links[df_links['Name'] == chosen_link_name]
        dff2 = dff.T.reset_index().set_axis(['Name', 'Value'], axis=1)
        temp_row_data = dff2.to_dict('records')

        # set custom cell editor
        link_value_type = {"function": "dynamicCellEditor(params, "")"}

        # check if link is adjacent to any face nodes
        if local_network_data[idx].link_adj_to_face(chosen_link_name):
            link_value_type = {"function": "dynamicCellEditor(params, 'Face')"}

        # create columns with dynamic editing / not editing power
        custom_columns = [
            {
                'field' : 'Name',
                'editable' : False 
            },
            {
                'field' : 'Value',
                'editable' : {"function": "editable(params, 'Link')"},
                "cellEditorSelector" : link_value_type,
                'singleClickEdit' : True
            },
            {
                'field' : 'Units',
                'editable' : {"function": "editable(params, 'Units')"},
                "cellEditorSelector": {"function": "unitsDropdown(params)"},
                'singleClickEdit' : True
            },
            {
                'field' : 'Evaluated Value',
                'editable' : False
            }

        ] 

        # get id manager from local network data
        id_manager = local_network_data[idx].get_id_manager()

        # Acccount for C-Link case
        if tapEdgeData['LinkType'] == 'C-Link':
            
            # Set rows
            custom_rows = [None for i in range(5)]

            # propagate each row using local network data
            for item in temp_row_data:
                if item['Name'] == 'Name':
                    custom_rows[0] = item

                elif item['Name'] == 'source':
                    custom_rows[1] = item
                    custom_rows[1]['Name'] = 'Node 1'
                    custom_rows[1]['Value'] = id_manager.get_name(custom_rows[1]['Value'])

                elif item['Name'] == 'target':
                    custom_rows[2] = item
                    custom_rows[2]['Name'] = 'Node 2'
                    custom_rows[2]['Value'] = id_manager.get_name(custom_rows[2]['Value'])

                elif item['Name'] == 'LinkType':
                    custom_rows[3] = item

                elif item['Name'] == 'mass_flow':
                    # Separate Units and Values in Mass Flow
                    custom_rows[4] = format_value_units(item)

        # Acccount for R-Link case
        elif tapEdgeData['LinkType'] == 'R-Link':

            # Set rows
            custom_rows = [None for i in range(6)]

            # propagate each row using local network data
            for item in temp_row_data:
                if item['Name'] == 'Name':
                    custom_rows[0] = item

                elif item['Name'] == 'source':
                    custom_rows[1] = item
                    custom_rows[1]['Name'] = 'Node 1'
                    custom_rows[1]['Value'] = id_manager.get_name(custom_rows[1]['Value'])

                elif item['Name'] == 'target':
                    custom_rows[2] = item
                    custom_rows[2]['Name'] = 'Node 2'
                    custom_rows[2]['Value'] = id_manager.get_name(custom_rows[2]['Value'])

                elif item['Name'] == 'LinkType':
                    custom_rows[3] = item

                elif item['Name'] == 'rLinkType':
                    custom_rows[4] = item

                elif item['Name'] == 'heatTransferCoefficient' or item['Name'] == 'Heat Transfer Coefficient':
                    if 'heatTransferCoefficient' in dff['rLinkType'].values or 'Heat Transfer Coefficient' in dff['rLinkType'].values:
                        custom_rows[5] = format_value_units(item)

                elif item['Name'].replace(" ", "") == 'thermalResistance':
                    if 'ThermalResistance' in (dff['rLinkType'].values) or 'Thermal Resistance' in (dff['rLinkType'].values):
                        custom_rows[5] = format_value_units(item)

        # create new table, reliant on accompanied .js file
        editable_table2 = dag.AgGrid(id='editable-table2',
                                     defaultColDef={'editable' : True},
                                     columnDefs=custom_columns,
                                     rowData=custom_rows, 
                                     style={'height': '30vh'},
                                     dashGridOptions= {
                                         'autoSizeStrategy' : {
                                            'type' : 'fitCellContents',
                                            'defaultMinWidth' : 100,
                                         }
                                    }
                                     )
        return editable_table2
    else:
        return []

################################################################################
# Update edge after table values are changed
################################################################################

@callback(Output('table-container','children',allow_duplicate=True),
          Output('cytoscape-1', 'elements', allow_duplicate=True),
          Output('cytoscape-1', 'stylesheet', allow_duplicate=True),
          Input('editable-table2','cellValueChanged'),
          State('cytoscape-1','tapEdgeData'),
          State('cytoscape-1', 'elements'),
          State('dropdown-update-network', 'value'),
          prevent_initial_call=True)
def update_edge_dataframe(data, tapEdgeData, elems, networkName):
    #Load local values
    idx = networkNames.index(networkName)
    localNetworkItem = local_network_data[idx]
    df_links = localNetworkItem.df_links

    # update local values
    localNetworkItem.update_elems(elems)
    
    if data and tapEdgeData:
        for i in range(len(data)):

            # set name to not be updated 
            name_updated = False

            # load in name of row (e.g. what property needs to be updated)
            row_name = data[i]['data']['Name']
            
            # find unit if unit exists
            units = ''
            if 'Units' in data[i]['data']:
                units = data[i]['data']['Units']
                if units == '':
                    units = ''
            
            # set value from edge
            value = str(data[i]['data']['Value'])

            # account for empty values column
            if len(value) == 0:
                value = str(0)

            # set entries to ignore for variable values
            dropdown_names = ['rLinkType', 'Name']

            # check if item is valid and update value accordingly
            if not variableExists(value) and row_name not in dropdown_names:
                # Check for malicious input, i.e. value is not an integer
                if is_number(value):
                    updated_value = str(value) + units

                # if value is not an integer, reset to 0
                else:
                    updated_value = str(0) + units

            else:
                updated_value = value

            # check if name is unique if name is edited
            if row_name == 'Name':
                id_manager = localNetworkItem.get_id_manager()
                if id_manager.is_name_unique(updated_value):
                    name_updated = True

                else:
                    break

            # update element internal structures
            selectedRow = df_links.loc[df_links['Name']==tapEdgeData['Name']]
            indices = list(df_links.index.values) 
            for j in indices:
                selectedRow[row_name][j] = updated_value
                df_links.loc[df_links['Name']==tapEdgeData['Name']] = selectedRow

            # update elems if name is changed
            if name_updated:

                # set old name & new name
                old_name = tapEdgeData['Name']
                new_name = updated_value

                # update elements to have new name
                local_network_data[idx].update_elem_name(old_name, new_name)

                # update edge to have new name
                tapEdgeData['Name'] = updated_value

                # update id manager
                id_manager = local_network_data[idx].get_id_manager()
                id_manager.update_name(old_name, new_name)

                # reset marker around stylesheet
                local_network_data[idx].stylesheetManager.resetStylesheetFromMarker()

                return [], local_network_data[idx].elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()

        # update elems to include link valuse
        localNetworkItem.update_elem_display_data()

    return display_edge_editable_table(tapEdgeData, networkName), elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()

################################################################################
# This section looks at creation of internal nodes
################################################################################

@callback(Output('cytoscape-1', 'elements', allow_duplicate=True), 
          Output('cytoscape-1', 'stylesheet', allow_duplicate=True),
          Input('internal-node', 'n_clicks'),
          State('cytoscape-1', 'elements'),
          State('dropdown-update-network', 'value'),
          prevent_initial_call = True,
          running=[(Output("internal-node", "disabled"), True, False)])
def add_internal_nodes(n_clicks, elems, networkName):

    # Load values
    idx = networkNames.index(networkName)
    local_data = local_network_data[idx]

    # find unique name for new internal node
    if n_clicks is not None and n_clicks > 0:

        # update positions
        local_data.update_positions_from_elems(elems)

        # add internal node
        local_data.add_internal_node(n_clicks)

        # get newest added entry and add it to elems
        # (this prevents total refresh)
        new_created_item = local_data.elems[-1]
        elems.append(new_created_item)

    # return newest elems & latest stylesheet
    # stylesheet returned to ensure color updates
    return elems, local_data.stylesheetManager.getCurrentStylesheet()

################################################################################
# This section looks at creation of Boundary Nodes
################################################################################
@callback(Output('cytoscape-1', 'elements', allow_duplicate=True), 
            Input('boundary-node', 'n_clicks'),
            State('cytoscape-1', 'elements'),
            State('dropdown-update-network', 'value'),
            prevent_initial_call = True,
            running=[(Output("boundary-node", "disabled"), True, False)])
def add_boundary_nodes(n_clicks, elems, networkName):
    idx = networkNames.index(networkName)

    if n_clicks is not None and n_clicks > 0:
        #Load values
        local_data = local_network_data[idx]

        # update positions
        local_data.update_positions_from_elems(elems)

        # add boundary node
        local_data.add_boundary_node(n_clicks)

        # get newest added entry and add it to elems
        # (this prevents total refresh)
        new_created_item = local_data.elems[-1]
        elems.append(new_created_item)

    # return updated elems
    return elems

################################################################################
# This allows the selection of a node (i.e. the red outline when node is clicked)
################################################################################

@callback(Output('cytoscape-1','stylesheet',allow_duplicate=True),
          Input('cytoscape-1', 'selectedNodeData'),
          State('dropdown-update-network', 'value'),
          prevent_initial_call=True)
def display_selected_node_data(data_list, networkName):
    #load index where networkName is located
    idx = networkNames.index(networkName)
    local_data = local_network_data[idx]

    # reset any existing markers
    local_data.stylesheetManager.resetStylesheetFromMarker()

    # check if item is selected
    if data_list is None:
        return "No node selected.", local_data.stylesheetManager.getCurrentStylesheet()
    else:
        d_list = [d['Name'] for d in data_list]
        if len(d_list) > 0 and len(d_list) < 3: #only select 1-2 at a time

            #for each item selected, add border & selet face
            for i in range(len(d_list)):
                node_name = d_list[i]

                # show selection in AEDT
                faceID = local_data.get_faceID(node_name)

                if faceID:
                    oDesign.SelectFaces(faceID)

                # change border color to red
                node_color = 'red'
                width = 3
                item_type = 'node'
                local_data.stylesheetManager.add_markers(node_name, node_color, width, item_type)
            return local_data.stylesheetManager.getCurrentStylesheet() #edited stylesheet
        else:
            return local_data.stylesheetManager.getCurrentStylesheet() #+default_stylesheet
        
################################################################################
# This allows the selection of a edge (i.e. the red outline)
################################################################################

@callback(Output('cytoscape-1','stylesheet',allow_duplicate=True),
          Input('cytoscape-1', 'selectedEdgeData'), 
          State('dropdown-update-network', 'value'),
          prevent_initial_call=True)
def displaySelectedNodeData(data_list, networkName):
    #load index where networkName is located
    idx = networkNames.index(networkName)

    # reset any existing markers
    local_network_data[idx].stylesheetManager.resetStylesheetFromMarker()

    # check if item is selected
    if data_list is None:
        return "No node selected.", local_network_data[idx].stylesheetManager.getCurrentStylesheet()
    else:
        d_list = [d['Name'] for d in data_list]
        if len(d_list) == 1: #only select 1 at a time

            #for each item selected, change edge color to red
            for i in range(len(d_list)):

                edge_color = 'red'
                width = 0 # width is not used for edges
                item_type = 'edge'

                local_network_data[idx].stylesheetManager.add_markers(d_list[i], edge_color, width, item_type)
            return local_network_data[idx].stylesheetManager.getCurrentStylesheet() #edited stylesheet
        else:
            return local_network_data[idx].stylesheetManager.getCurrentStylesheet() #+default_stylesheet

################################################################################
# this is a helper function for r-links and c-links
################################################################################
def add_link_callback(n_clicks, data_list, elems, networkName, link_type):
    #load index where networkName is located
    idx = networkNames.index(networkName)

    # update local elems with new positions
    local_network_data[idx].update_elems(elems)

    # Account for if two nodes are not selected for link creation
    if data_list is None or len(data_list) < 2:
        return ["Select two nodes first.", True, "warning", local_network_data[idx].elems]
    
    elif n_clicks is not None and n_clicks > 0 and data_list is not None:
        #Load all local values
        type1 = data_list[0]['Type']
        type2 = data_list[1]['Type']
        source_id = data_list[0]['id']
        target_id = data_list[1]['id']

        # Check if link is being created between boundary & face (not allowed for r-links)
        if type1  == 'Face Node' and type2 == 'Boundary Node':
            return [link_type + " cannot be created between boundary and face node", True, "danger", elems]
        
        elif type1 == 'Boundary Node' and type2 == 'Face Node':
            return [link_type + " cannot be created between boundary and face node", True, "danger", elems]
        
        # Check if link is being created between two boundary nodes:
        if type1  == 'Boundary Node' and type2 == 'Boundary Node':
            return [link_type + " cannot be created between two Boundary Nodes", True, "danger", elems]

        # Check if link already exists between two nodes
        if local_network_data[idx].link_exists(source_id, target_id):
            return ["Link already exists between nodes", True, "danger", elems]

        # add r-link to local network
        local_network_data[idx].add_link(source_id, target_id, link_type, n_clicks)
        
        # return message for r-link creation
        return ["New " + link_type + " created.", True, "success", local_network_data[idx].elems]
    
    # Account for if two nodes are not selected for link creation
    elif n_clicks is not None and n_clicks > 0 and data_list is None:
        return ["Select two nodes first.", True, "warning", local_network_data[idx].elems]
    
################################################################################
# This enables the connection of R-links
################################################################################

@callback([Output('alert-message','children',allow_duplicate=True),
           Output("alert-message", "is_open",allow_duplicate=True),
           Output("alert-message", "color",allow_duplicate=True),
           Output('cytoscape-1','elements',allow_duplicate=True)],
           Input('R-Link','n_clicks'),
           State('cytoscape-1','selectedNodeData'),
           State('cytoscape-1','elements'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True,
           running=[(Output("R-Link", "disabled"), True, False)])
def add_rlink(n_clicks, data_list, elems, networkName):
    return add_link_callback(n_clicks, data_list, elems, networkName, "R-Link")
    
################################################################################
# This enables the connection of C-links
################################################################################

@callback([Output('alert-message','children',allow_duplicate=True),
           Output("alert-message", "is_open",allow_duplicate=True),
           Output("alert-message", "color",allow_duplicate=True),
           Output('cytoscape-1','elements',allow_duplicate=True)],
           Input('C-Link','n_clicks'),
           State('cytoscape-1','selectedNodeData'),
           State('cytoscape-1','elements'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True,
           running=[(Output("C-Link", "disabled"), True, False)])
def add_clink(n_clicks,data_list, elems, networkName):
    return add_link_callback(n_clicks, data_list, elems, networkName, "C-Link")
    
################################################################################
# This callback looks at saving data
################################################################################

@callback([Output('alert-message','children', allow_duplicate=True),
           Output("alert-message", "is_open", allow_duplicate=True),
           Output("alert-message", "color",allow_duplicate=True),
           Output('cytoscape-1','elements', allow_duplicate=True),
           Output('cytoscape-1','stylesheet',allow_duplicate=True),],
           State('dropdown-update-network', 'value'),
           Input('save-all-button','n_clicks'), 
           State('cytoscape-1','elements'),
           prevent_initial_call=True)
def save_all_to_AEDT(networkName, n_clicks, elems):
    global saving_in_progress
    if n_clicks is not None and n_clicks > 0:
        print("------------------------\n")
        
        # Make sure elems is saved properly
        idx = networkNames.index(networkName)
        local_network_data[idx].update_elems(elems)

        # Make sure that saving is not already in progress
        if saving_in_progress:
            return ["Saving already in progress", True, "warning", elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()]
        
        #Set saving in progress
        saving_in_progress = True

        # check that current network is connected & highlight if not
        lst = check_connectivity(1, networkName)
        if lst[2] == 'danger':
            lst.insert(3, elems)
            saving_in_progress = False
            return lst

        # For each network, use all saved values to 
        for localNetworkItem in local_network_data:
            if localNetworkItem is not None:
                if get_unconnected_nodes(localNetworkItem):
                    saving_in_progress = False
                    return ["Saving interrupted. Not all nodes connected in " + networkName, True, "danger", local_network_data[idx].stylesheetManager.getCurrentStylesheet()]
                save_single_network(localNetworkItem)

        #Set saving complete
        saving_in_progress = False

        return ["Saved : Check AEDT", True, "success", elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()]

def save_single_network(localNetworkItem):

    # Save local network values
    # move current -> REF in localNetworkItem
    localNetworkItem.update_ref_values()

    # Update positional from elements
    localNetworkItem.update_positions()
    
    #Load local network values
    df_positions = localNetworkItem.df_positions
    df_int = localNetworkItem.df_int
    df_face = localNetworkItem.df_face
    df_links = localNetworkItem.df_links
    df_boundary = localNetworkItem.df_boundary

    merged_df_int = pd.merge(df_int, df_positions, on='Name') #could set index and then figure out the merge from there. 
    merged_df_face = pd.merge(df_face, df_positions, on='Name')

    # order data properly to fit into Node / Link classes
    # Account for whether there are no boundary nodes. 
    if not df_boundary.empty:
        merged_df_boundary = pd.merge(df_boundary, df_positions, on='Name')
        merged_df_boundary = merged_df_boundary[['Name', 'Type', 'Xlocation', 'Ylocation', 'ThermalParameters', 'Power', 'Temperature']]
    else:
        merged_df_boundary = df_boundary

    merged_df_int = merged_df_int[['Name','Type','Xlocation','Ylocation','Power','Mass','SpecificHeat']]
    merged_df_face = merged_df_face[['Name','Type','Xlocation','Ylocation','ResistanceChoice','FaceID','Thickness','Material','ThermalResistance']]

    #Account for the case where there are no c-links: 
    if 'mass_flow' not in df_links:
        merged_df_links = df_links[['Name','source','target', 'LinkType','rLinkType','thermalResistance','heatTransferCoefficient']].copy()
    else:
        merged_df_links = df_links[['Name','source','target','LinkType','rLinkType','thermalResistance','heatTransferCoefficient', 'mass_flow']].copy()

    # replace source and target from id manager
    id_manager = localNetworkItem.get_id_manager()

    for i, source_id in enumerate(merged_df_links['source']):
        merged_df_links.loc[i, 'source'] = id_manager.get_name(source_id)

    for i, target_id in enumerate(merged_df_links['target']):
        merged_df_links.loc[i, 'target'] = id_manager.get_name(target_id)

    # format dataframes into lists for classes
    int_node_list = merged_df_int.to_numpy()
    face_node_list = merged_df_face.to_numpy()
    link_list = merged_df_links.to_numpy()
    boundary_list = merged_df_boundary.to_numpy()

    # aggregate all data into singular list
    network_info_list = [*int_node_list,*face_node_list,*link_list, *boundary_list]

    #print information
    print(network_info_list)

    # Set current network
    updated_network = Network(localNetworkItem.networkName)
    
    # Add items into updated network
    for entry in network_info_list:
        if entry[1] == 'Internal Node':
            entry = [x if str(x) != 'nan' else 0 for x in entry ] # account for vales not present
            node = InternalNode(*entry)
            updated_network.add_node(node)

        elif entry[1] == 'Face Node':
            node = FaceNode(*entry)            
            updated_network.add_node(node)

        elif entry[3] == 'R-Link':
            entry = [x for x in entry if str(x) != 'nan'] # account for values not present, i.e. mass_flow
            edge = RLink(*entry)
            updated_network.add_link(edge)

        elif entry[3] == 'C-Link':
            entry = [x for x in entry if str(x) != 'nan'] # account for values not present, i.e. rLinkType
            edge = CLink(*entry) 
            updated_network.add_link(edge)

        elif entry[1] == 'Boundary Node':
            entry = [x if str(x) != 'nan' else 0 for x in entry ]
            node = BoundaryNode(*entry)
            updated_network.add_node(node)

    # Attempt to save code gracefully     
    try:
        editor = AEDTNetworkEditor()
        editor.edit_networks([updated_network])

        oDesktop.GetActiveProject().Save()
        print("Project Saved")
        return True

    # Prevent cytoscape crash
    except Exception as e:
        print(e)
        return False
            
#################################################################################
# Save a single network (instead of all), refers to functions defined above. 
#################################################################################  
@callback([Output('alert-message','children', allow_duplicate=True),
           Output("alert-message", "is_open", allow_duplicate=True),
           Output("alert-message", "color",allow_duplicate=True),
           Output('cytoscape-1','elements', allow_duplicate=True),
           Output('cytoscape-1','stylesheet',allow_duplicate=True),],
           State('dropdown-update-network', 'value'),
           Input("save-single-button",'n_clicks'), 
           State('cytoscape-1','elements'),
           prevent_initial_call=True)
def save_singular_network(networkName, n_clicks, elems):
    global saving_in_progress
    if n_clicks is not None and n_clicks > 0:
        print("------------\n------------\n------------\n")
        
        # Make sure elems is saved properly
        idx = networkNames.index(networkName)
        local_network_data[idx].update_elems(elems)
        open_alert_message = True

        # Make sure that saving is not already in progress
        if saving_in_progress:
            update_message = "Saving already in progress"
            message_color = "warning"
            return [update_message, open_alert_message, message_color, elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()]
        
        # Set saving in progress
        saving_in_progress = True

        #check that the network is connected
        lst = check_connectivity(1, networkName)
        if lst[2] == 'danger':
            lst.insert(3, elems)
            saving_in_progress = False
            return lst

        # For each network, use all saved values to 
        save_single_network(local_network_data[idx])

        # Finish saving
        saving_in_progress = False

        # set successful messages
        update_message = 'Saved : Check AEDT'
        message_color = 'success'

        return [update_message, open_alert_message, message_color, elems, local_network_data[idx].stylesheetManager.getCurrentStylesheet()]

#################################################################################
# Check if all the nodes are connected
#################################################################################

@callback([Output('alert-message','children', allow_duplicate=True),
           Output("alert-message", "is_open", allow_duplicate=True),
           Output("alert-message", "color",allow_duplicate=True),
           Output('cytoscape-1','stylesheet',allow_duplicate=True)],
           Input('check-button','n_clicks'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def check_connectivity(n_clicks, networkName):
    if n_clicks is not None and n_clicks > 0:
        # Make sure elems is saved properly
        idx = networkNames.index(networkName)
        
        # get all unconnected nodes
        unconnected_nodes = get_unconnected_nodes(local_network_data[idx])

        # check if list of unconnected nodes is empty -> connected nodes
        if not unconnected_nodes:
            return ["All nodes connected", True, "success", local_network_data[idx].stylesheetManager.getCurrentStylesheet()]
        
        # reset any markers around nodes
        local_network_data[idx].stylesheetManager.resetStylesheetFromMarker()

        # add yellow marker to signify nodes that are unconnected
        for node_name in unconnected_nodes:
            node_color = 'yellow'
            item_type = 'node'
            width = 3

            local_network_data[idx].stylesheetManager.add_markers(node_name, node_color, width, item_type)

        # return popup display & marker coloring for non-connected nodes
        return ["Not all nodes connected in " + networkName, True, "danger", local_network_data[idx].stylesheetManager.getCurrentStylesheet()]

def get_unconnected_nodes(localNetworkItem):
        # Load in local data
        df_links = localNetworkItem.df_links
        df_face = localNetworkItem.df_face
        df_int = localNetworkItem.df_int
        df_boundary = localNetworkItem.df_boundary

        unconnected_node_names = []

        # aggregate all names from df_face, df_boundary, and df_int into unconnected_node_names
        if 'Name' in df_face:
            unconnected_node_names.extend(df_face['Name'])
                
        if 'Name' in df_boundary:
            unconnected_node_names.extend(df_boundary['Name'])
            
        if 'Name' in df_int:
            unconnected_node_names.extend(df_int['Name'])

        # create list of all targets and sources [(source, target), (s, t), ...)
        all_links = list(zip(df_links['source'], df_links['target']))

        # iterate through all targets and sources
        # remove all items that match target or source name 
        for link in all_links:
            for node_id in link:
                
                # get name of node from id
                id_manager = localNetworkItem.get_id_manager()
                node_name = id_manager.get_name(node_id)

                # try and delete node name if it exists in unconnected_node_names
                try:
                    unconnected_node_names.remove(node_name)

                except:
                    continue

        return unconnected_node_names


#################################################################################
# Create XL Modal Dialog & Display item information
#################################################################################

# Callback to open the modal dialogue and send a default table (Face Nodes)
@callback(Output('large-modal-dlg', 'is_open', allow_duplicate=True),
           Output('large-modal-body','children',allow_duplicate=True),
           Input('show-all-info','n_clicks'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def open_modal_display(n_clicks, network_name):
    if n_clicks:
        return True, create_modal_table(network_name, 'All Nodes')

# Callback to open the face node table
@callback(Output('large-modal-body','children',allow_duplicate=True),
           Input('modal-face-node-button','n_clicks'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def display_face_node_table(n_clicks, network_name):
    if n_clicks:
        return True, create_modal_table(network_name, 'Face Node')
    
# Callback to open the internal node table
@callback(Output('large-modal-body','children',allow_duplicate=True),
           Input('modal-internal-button','n_clicks'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def display_internal_node_table(n_clicks, network_name):
    if n_clicks:
        return True, create_modal_table(network_name, 'Internal Node')
    
# Callback to open the boundary node table
@callback(Output('large-modal-body','children',allow_duplicate=True),
           Input('modal-boundary-node-button','n_clicks'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def display_boundary_node_table(n_clicks, network_name):
    if n_clicks:
        return True, create_modal_table(network_name, 'Boundary Node')
    
# Callback to open the table with all nodes
@callback(Output('large-modal-body','children',allow_duplicate=True),
           Input('modal-nodes-button','n_clicks'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def display_all_nodes_table(n_clicks, network_name):
    if n_clicks:
        return True, create_modal_table(network_name, 'All Nodes')
    
# Callback to open the table with all links
@callback(Output('large-modal-body','children',allow_duplicate=True),
           Input('modal-links-button','n_clicks'),
           State('dropdown-update-network', 'value'),
           prevent_initial_call=True)
def display_all_links_table(n_clicks, network_name):
    if n_clicks:
        return True, create_modal_table(network_name, 'Links')
    
# Generate modal table of network given type of information to display
def create_modal_table(network_name, display_type):
    # load values
    idx = networkNames.index(network_name)
    localNetworkItem = local_network_data[idx]

    # create instance of AgGrid with custom formatted cols / rows
    editable_table = dag.AgGrid(id='modal-editable-table',
                                    defaultColDef={'editable' : False},
                                    columnDefs=format_modal_columns(display_type),
                                    rowData=format_rows(localNetworkItem, display_type),
                                    style={'height': '30vh'},
                                    dashGridOptions= {
                                         'autoSizeStrategy' : {
                                            'type' : 'fitCellContents',
                                            'defaultMinWidth' : 100,
                                         }
                                    })

    return editable_table

# Format columns of AGGrid to display the right information 
def format_modal_columns(display_type):

    custom_columns = []

    # create formatted columns depending on menu option
    if display_type == 'Face Node':
        custom_columns = [
                {
                    'field' : name,
                    'editable' : False 
                } for name in ['Name', 'Type', 'FaceID', 
                               'Resistance Choice', 'Thermal Resistance', 
                               'Thickness', 'Material']]
        
    elif display_type == 'Links':
        custom_columns = [
                {
                    'field' : name,
                    'editable' : False 
                } for name in ['Name', 'LinkType', 'Node 1', 'Node 2', 
                               'rLinkType', 'Heat Transfer Coefficient',
                               'Thermal Resistance',
                               'Mass Flow']]
        
    elif display_type == 'Boundary Node':
        custom_columns = [
                {
                    'field' : name,
                    'editable' : False 
                } for name in ['Name', 'Type', 'Thermal Parameters', 
                               'Temperature', 'Power']]
        
    elif display_type == 'Internal Node':
        custom_columns = [
                {
                    'field' : name,
                    'editable' : False 
                } for name in ['Name', 'Type', 'Mass', 
                               'Specific Heat', 'Power']]
        
    elif display_type == 'All Nodes':
        custom_columns = [
                {
                    'field' : name,
                    'editable' : False 
                } for name in ['Name', 'Type', 'FaceID', 'Resistance Choice', 
                               'Thermal Resistance', 'Thickness', 'Material',
                               'Mass', 'Specific Heat', 'Thermal Parameters', 
                               'Temperature', 'Power']]

    return custom_columns

# call various format functions to format nodes / links depending on display selection
def format_rows(localNetworkItem, display_type):

    data = []

    # clean up data to display on modal dialogue
    if display_type == 'Face Node':
        data = localNetworkItem.df_face.to_dict('records')
        data = format_face_dict_arr(data)

    elif display_type == 'Boundary Node':
        data = localNetworkItem.df_boundary.to_dict('records')
        data = format_boundary_dict_arr(data)
    
    elif display_type == 'Internal Node':
        data = localNetworkItem.df_int.to_dict('records')
        data = format_int_dict_arr(data)

    elif display_type == 'Links':
        data = localNetworkItem.df_links.to_dict('records')
        data = format_link_dict_arr(data)

    elif display_type == 'All Nodes':
        face_data = localNetworkItem.df_face.to_dict('records')
        face_data = format_face_dict_arr(face_data)

        bound_data = localNetworkItem.df_boundary.to_dict('records')
        bound_data = format_boundary_dict_arr(bound_data)
    
        int_data = localNetworkItem.df_int.to_dict('records')
        int_data = format_int_dict_arr(int_data)

        data = [*face_data, *bound_data, *int_data]

    return data

# format links to have the right info, not show source/target, and either show or not show mass_flow
def format_link_dict_arr(data):
    #Rename columns
    for link_dict in data:          
        link_dict['Heat Transfer Coefficient'] = link_dict.pop('heatTransferCoefficient')
        link_dict['Thermal Resistance'] = link_dict.pop('thermalResistance')
        link_dict['Node 1'] = link_dict.pop('source')
        link_dict['Node 2'] = link_dict.pop('target')

        if 'mass_flow' in link_dict:
            link_dict['Mass Flow'] = link_dict.pop('mass_flow')

    return data

# format boundary nodes so that 'Thermal Parameters' is cleaner looking
def format_boundary_dict_arr(data):
    #Rename columns
    for boundary_dict in data: 
        boundary_dict['Thermal Parameters'] = boundary_dict.pop('ThermalParameters')

    return data

# format internal nodes so that 'specificheat' appears as separate words
def format_int_dict_arr(data):
    #Rename columns
    for int_dict in data:          
        int_dict['Specific Heat'] = int_dict.pop('SpecificHeat')

    return data

# Format face nodes s.t. Resistance Choice and Thermal Resistance appear as separate words
def format_face_dict_arr(data):
    #Rename columns
    for face_dict in data: 
        face_dict['Resistance Choice'] = face_dict.pop('ResistanceChoice')
        face_dict['Thermal Resistance'] = face_dict.pop('ThermalResistance')

    return data

#################################################################################
# detect program shutdown if tab is closed
# reliant on onbeforeunload and beforeunload in check_closing.js
# source : https://community.plotly.com/t/automatic-server-shutdown-upon-browser-tab-closure/79538
#################################################################################

@app.server.route("/shutdown", methods=["POST"])
def shutdown():
    print("Tab has been closed")
    close_program()


#################################################################################
# Section: Program launching 
#################################################################################
# is_port_in_use() : determine if port is in use
# open_browser()   : open browser automatically given port
#################################################################################

#################################################################################
# Select port & open app into default browser
#################################################################################

# set default port 
port = 1024

# Check if port is in use -> if so, find a free port
# source: https://stackoverflow.com/questions/2470971/fast-way-to-test-if-a-port-is-in-use-using-python
def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
    
while is_port_in_use(port):
    port = random.randrange(1024, 49151)

# function to new link in default web browser
# source: https://community.plotly.com/t/auto-open-browser-window-with-dash/31948
def open_browser():
    webbrowser.open_new("http://localhost:{}".format(port))

# run the dash app
if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, port=port, dev_tools_ui=True, use_reloader=False)
