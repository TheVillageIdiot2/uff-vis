#!/usr/bin/python
import sys
import uff
import pygame
import render
import numpy as np
from tabulate import tabulate


TIMESCALE = 10

EXCEPTIONS=True
RENDER_LABELS = True
ID2_X_DISPLACEMENT = "Response X  Displacement"
ID2_Y_DISPLACEMENT = "Response Y  Displacement"
ID2_Z_DISPLACEMENT = "Response Z  Displacement"

'''
Philosophus:
    None of these classes should store their own id.
    That is the role of the calling function
'''

#Class which holds the initial position a node
class NodeData(object):
    def for_label(uff_nodes, node_label):
        for label, coord in zip(uff_nodes.labels, uff_nodes.coords):
            if label == node_label:
                return NodeData(coord)
        if EXCEPTIONS:
            raise Exception("Could not find NodeData for node_id={}".format(node_id))
        else:
            return None
            
    def __init__(self, position):
        self.position = position


#Class which holds all displacement data of a single node
class DisplacementData(object):
    #Takes the entire uff data set and scans for displacement data relevant to this node
    def for_label(data_set, node_label):
        x,y,z = None,None,None
        for d in data_set:
            if isinstance(d, uff.UffFunctionAtNode) and d.response["node"] == node_label:
                id2 = d.ids[1]
                if      id2 == ID2_X_DISPLACEMENT:
                    x = d
                elif    id2 == ID2_Y_DISPLACEMENT:
                    y = d
                elif    id2 == ID2_Z_DISPLACEMENT:
                    z = d

        if not any(e is None for e in (x,y,z)):
            return DisplacementData(x,y,z)
        else:
            if EXCEPTIONS:
                raise Exception("Could not find DisplacementData for node_id={}".format(node_id))
            else:
                return None

    #Creates displacement data object out of the given function data
    def __init__(self, uff_x_func, uff_y_func, uff_z_func):
        try:
            #Get displacements from each func set
            disp_x = uff_x_func.axis[uff.AXIS_ORDINATE]["data"]
            disp_y = uff_y_func.axis[uff.AXIS_ORDINATE]["data"]
            disp_z = uff_z_func.axis[uff.AXIS_ORDINATE]["data"]
            disp_times = uff_z_func.axis[uff.AXIS_ABSCISSA]["data"] #z is arbitrary 

            self.disp_vecs = [np.array([x,y,z], dtype=np.float32) for x,y,z in zip(disp_x, disp_y, disp_z)]
            self.disp_times = disp_times
        except AttributeError:
            raise Exception("Invalid uff data provided to DisplacementData")

#Class which holds a single "Element" in terms of constructed geometry
class ElementData(object):
    def for_label(uff_elements, element_label):
        #Find the label
        i = uff_elements.labels.index(element_label)
        if i == -1:
            if EXCEPTIONS:
                raise Exception("Could not find Element with id={}".format(element_id))
            else:
                return None

        #Yield
        color = uff_elements.colors[i]
        nodes = uff_elements.elements[i]
        return ElementData(color, nodes)
            
                            
    def __init__(self, color, node_labels): 
        self.color = color
        self.nodes = node_labels
        

#Draws all node objects
def draw_structure(all_node_data, all_disp_data, all_elem_data, disp_index=-1):
    #Rendering without displacement
    if disp_index == -1:
        for label, node in all_node_data.items():
            render.render_node(node)
        for label, elem in element_data.items():
            render.render_element(element)

    #Render with displacement
    else:
        for label, node in all_node_data.items():
            disp = all_disp_data[label]
            render.render_displaced_node(node, disp, disp_index)
        for label, elem in all_elem_data.items():
            render.render_displaced_element(elem, all_node_data, all_disp_data, disp_index)

    if RENDER_LABELS:
        ...
        #render_label(surface, pos, str(node_data.id))

def main(filename):
    #Open the UFF data
    data_set = uff.parse_file(filename)

    #Parse into more useful formats
    all_node_data = {}
    all_disp_data = {}
    all_elem_data = {} 

    for d in data_set:
        #If UffNodes, build node_data
        if isinstance(d, uff.UffNodes):
            for label in d.labels:
                all_node_data[label] = NodeData.for_label(d, label)

        #If UffElements, build element_data
        if isinstance(d, uff.UffElements):
            for label in d.labels:
                all_elem_data[label] = ElementData.for_label(d, label)

    #Once have nodes, gather specific data from them
    for node_label in all_node_data.keys():
        all_disp_data[node_label] = DisplacementData.for_label(data_set, node_label)


    #Get total number of displacements for loop purposes
    displacement_count = len(next(iter(all_disp_data.values())).disp_vecs)

    #Start rendrin
    render.init_render()

    #Main loop
    i=0
    while True:
        #Draw all points to screen.
        i = (i+TIMESCALE) % displacement_count
        draw_structure(all_node_data, all_disp_data, all_elem_data, i)

        #Write out and handle events
        if render.tick():
            break

    render.stop_render()

if __name__ == '__main__':
    #If given, read from a particular file
    if len(sys.argv) < 2:
        main("test.unv")
    else:
        for filename in sys.argv[1:]:
            print("Running for {}".format(filename))
            main(filename)

