#!/usr/bin/python
import sys
import uff
import pygame
import render
import numpy as np
from tabulate import tabulate

EXCEPTIONS=True
RENDER_LABELS = True
ID2_X_DISPLACEMENT = "Response X  Displacement"
ID2_Y_DISPLACEMENT = "Response Y  Displacement"
ID2_Z_DISPLACEMENT = "Response Z  Displacement"


#Class which holds the initial position and id of a nodeclass NodeData(object):
class NodeData(object):
    #Gets a single node's data out of given uff node entry, or None if it does not exist
    def for_label(uff_nodes, node_label):
        for label, coord in zip(uff_nodes.labels, uff_nodes.coords):
            if label == node_label:
                return NodeData(node_label, coord)
        if EXCEPTIONS:
            raise Exception("Could not find NodeData for node_id={}".format(node_id))
        else:
            return None
            
    def __init__(self, label, position):
        #Store id
        self.label = label
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
            return DisplacementData(node_label, x,y,z)
        else:
            if EXCEPTIONS:
                raise Exception("Could not find DisplacementData for node_id={}".format(node_id))
            else:
                return None

    #Creates displacement data object out of the given function data
    def __init__(self, node_label, uff_x_func, uff_y_function, uff_z_function):
        try:
            #Get displacements from each func set
            disp_x = uff_x_func.axis[uff.AXIS_ORDINATE]["data"]
            disp_y = uff_y_func.axis[uff.AXIS_ORDINATE]["data"]
            disp_z = uff_z_func.axis[uff.AXIS_ORDINATE]["data"]
            disp_times = uff_z_func.axis[uff.AXIS_ABSCISSA]["data"] #z is arbitrary 

            self.label = node_label
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
        label = uff_elements.labels[i]
        color = uff_elements.colors[i]
        nodes = uff_elements.elements[i]
        return ElementData(label, color, nodes)
            
                            
    def __init__(self, label, color, node_labels): 
        self.label = label
        self.color = color
        self.nodes = node_labels
        

#Draws all node objects
def draw_structure(surface, node_data, element_data, disp_index=-1):
    if disp_index == -1:
        displacement = np.zeros(3)
    else:
        displacement = node_data.displacements[disp_index]
    #Build position of node at given time
    pos = (node_data.base_postion + displacement)

    #Draw
    render.render_node(surface, pos)

    if RENDER_LABELS:
        render_label(surface, pos, str(node_data.id))

def main(filename):
    #Open the UFF data
    data_set = uff.parse_file(filename)

    #Parse into more useful formats
    node_data, element_data, displacement_data = {}, {}, {}
    for d in data_set:
        #If UffNodes, build node_data
        if isinstance(d, uff.UffNodes):
            for label in d.labels:
                node_data[label] = NodeData.for_label(d, label)

        #If UffElements, build element_data
        if isinstance(d, uff.UffElements):
            for label in d.labels:
                element_data[label] = ElementData.for_label(label)

    #Once have nodes, gather specific data from them
    for node_label in node_data.keys():
        displacement_data[node_label] = DisplacementData.for_label()

    node_data = [NodeData(data_set, node_num) for node_num in range(1,25)]
    element_data = [ElementData(data_set
    displacement_count = len(node_data[0].displacements)

    screen = render.init_render()
    #Main loop
    i=0
    while True:
        #Handle events
        render.handle_events()

        #Draw all points to screen.
        i = (i+TIMESCALE) % displacement_count
        print(i)
        draw_structure(screen, node_data, element_data, i)

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

