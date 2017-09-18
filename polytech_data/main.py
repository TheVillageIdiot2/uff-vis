#!/usr/bin/python
import sys
import uff
import pygame
import render
import numpy as np
from tabulate import tabulate


RENDER_LABELS = True
ID2_X_DISPLACEMENT = "Response X  Displacement"
ID2_Y_DISPLACEMENT = "Response Y  Displacement"
ID2_Z_DISPLACEMENT = "Response Z  Displacement"


#Class which holds the initial position and all displacements
#of a single vertex
class NodeData(object):
    #Gets node data out of given uff node entry
    def __init__(self, uff_nodes, node_id):
        #Store id
        self.id = node_id

        #Get position, exit on success
        for label, coord in zip(d.labels, d.coords):
            if label == target_node_id:
                self.postion = coord
                return

        #If reach this position, failed to find position
        raise Exception("Unable to find node id {} in uff_nodes".format(node_id))


class DisplacementData(object):
    def for_node(data_set, node_id):
        x,y,z = None,None,None
        for d in data_set:
            if isinstance(d, uff.UffFunctionAtNode) and d.response["node"] == node_id:
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
            return None

    def __init__(self, uff_x_func, uff_y_function, uff_z_function):
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


class ElementData(object):
    def __init__(self, uff_elements):
        

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
                node_data[label] = NodeData(d, label)

        #If 

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

