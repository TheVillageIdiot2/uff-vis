#!/usr/bin/python
import sys
import itertools
import numpy as np

#Strings to match
UFF_DATASET_SEP         = "    -1\n"
UFF_NONE                = "NONE"

#Abscisaa and ordinate types
ORDINATE_REAL_SINGLE    = 2
ORDINATE_REAL_DOUBLE    = 4
ORDINATE_COMPLEX_SINGLE = 5
ORDINATE_COMPLEX_DOUBLE = 6

ABSCISSA_SPACING_UNEVEN = 0
ABSCISSA_SPACING_EVEN   = 1

#Axis names
AXIS_ABSCISSA       = "abscissa"
AXIS_ORDINATE       = "ordinate"
AXIS_DENOMINATOR    = "denominator"
AXIS_Z              = "z-axis"
ALL_AXIS_NAMES = [AXIS_ABSCISSA, AXIS_ORDINATE, AXIS_DENOMINATOR, AXIS_Z]

def _pair_iter(iterable, pair_cardinality):
    index = 0
    pair = []
    for elem in iterable:
        if index >= pair_cardinality:
            yield tuple(pair)
            pair = []
            index = 0

        #Build pair
        pair.append(elem)
        index += 1
    if index == pair_cardinality:
        yield tuple(pair)

class _str_consumer(object):
    def __init__(self,s):
        self.s = s

    def get(self, length):
        ret = self.s[:length]
        self.s = self.s[length:]
        return ret

def _get_sections(file_lines):
    '''
    Takes in an iterable over the lines of the file
    (note: not an iterator! an iterable. I don't want side
    effects mutating your shit)

    Returns an array of tuples of format
    (type, begin, end)
    Where type is of course the int representing the type,
    Start is the index of the datas beginning (After type)
    and end is the line index of where the data ends (the terminating -1)
    '''

    #Create list to hold returned values
    retvals = []

    #Create iterator to traverse file
    file_iter = enumerate(iter(file_lines))

    #Outer loop, scanning
    index,line = next(file_iter)
    try:
        while True:
            #On detect object, enter inner loop
            if line == UFF_DATASET_SEP:
                #The contents of the file truly start 2 after sep
                addendum_start = index+2 
                #The type is one after sep (IE 'next')
                _,addendum_type = next(file_iter)
                addendum_type = int(addendum_type)

                #Inner loop: Scan to end of file section
                index, line = next(file_iter)
                while line != UFF_DATASET_SEP:
                    index,line = next(file_iter)
                addendum_end = index

                #Add our entry
                retvals.append((addendum_type, addendum_start, addendum_end))

            #Loop till next datasep
            index,line = next(file_iter)
    except StopIteration:
        return retvals

def _iterate_sections(filename):
    '''
    Generator function.
    Yields the full text of sections, in sequence
    '''
    f = open(filename)
    lines = [line for line in f]
    f.close()

    sections = _get_sections(lines)
    for sect in sections:
        text = "".join(lines[sect[1] : sect[2]])
        yield UffEntry(sect[0], text)

class UffEntry(object):
    TYPE_NUMBER = -1 #-1 here used for flag of unassigned
    def __init__(self, type_num, text):
        self.type = type_num
        self.raw_text = text

    def get_type(self):
        return self.type

    def refine(self):
        #If already refined, don't bother
        if self.TYPE_NUMBER != UffEntry.TYPE_NUMBER:
            return self
        #Otherwise, try to find appropriate type
        else:
            UFF_TYPES = [UffHeader, UffUnits, UffNodes, UffElements, UffFunctionAtNode]
            for uff_type in UFF_TYPES:
                if self.type == uff_type.TYPE_NUMBER:
                    return uff_type(self.raw_text)

            #Failed to refine, just return base
            return self

class UffHeader(UffEntry):
    TYPE_NUMBER = 151
    def __init__(self, raw_text):
        UffEntry.__init__(self, UffHeader.TYPE_NUMBER, raw_text)
        #Parse stuff out of raw
        lines = raw_text.splitlines()
        self.model_file = lines[0]
        self.model_description = lines[1]
        self.creation_program = lines[2]
        self.creation_date = lines[3][0:10]
        self.creation_time = lines[3][10:20]
        #Line 3 Version + subversion + type not exist
        #Line 4 Databse doesn't exist
        self.uff_creation_program = lines[5]
        self.uff_creation_date = lines[6][0:10]
        self.uff_creation_time = lines[6][10:20]


class UffUnits(UffEntry):
    TYPE_NUMBER = 164
    def __init__(self, raw_text):
        UffEntry.__init__(self,UffUnits.TYPE_NUMBER, raw_text)
        #We don't reallly care about this for now
        pass

class UffNodes(UffEntry):
    TYPE_NUMBER = 2411
    def __init__(self, raw_text):
        UffEntry.__init__(self,UffNodes.TYPE_NUMBER, raw_text)

        #Parse each pair of records 
        self.labels = []
        self.coord_systems = []
        self.disp_systems = []
        self.colors = []
        self.coords = []
        i = 0
        for rec1,rec2 in _pair_iter(raw_text.splitlines(), 2):
            i+= 1
            #Get label
            sc = _str_consumer(rec1)
            self.labels.append( int(sc.get(10)) )
            #Get coordinate system
            self.coord_systems.append( int(sc.get(10)) )
            #Get displacement system
            self.disp_systems.append( int(sc.get(10)) )
            #Get Color
            self.colors.append( int(sc.get(10)) )

            #Get position
            sc = _str_consumer(rec2)
            x = float(sc.get(25))
            y = float(sc.get(25))
            z = float(sc.get(25))
            vec = np.array([x,y,z])
            self.coords.append(vec)

class UffElements:
    TYPE_NUMBER = 2412
    def __init__(self, raw_text):
        UffEntry.__init__(self,UffElements.TYPE_NUMBER, raw_text)
        #In our parsing we just presume that these are all
        #non-beam elements
        lines = raw_text.splitlines()

        self.labels                 = []
        self.fe_descriptor_ids      = []
        self.physical_prop_tables   = []
        self.material_prop_tables   = []
        self.colors                 = []
        self.num_nodes              = []
        self.elements               = []
        for rec1,rec2 in _pair_iter(raw_text.splitlines(), 2):
            sc = _str_consumer(rec1)
            #Get label
            self.labels.append( int(sc.get(10)) )
            #Get coordinate system
            self.fe_descriptor_ids.append( int(sc.get(10)) )
            #Get physical/material properties
            self.physical_prop_tables.append( int(sc.get(10)) )
            self.material_prop_tables.append( int(sc.get(10)) )
            #Get Color
            self.colors.append( int(sc.get(10)) )
            #Get num nodes
            num_nodes = int(sc.get(10))
            self.num_nodes.append(num_nodes)

            #Get element nodes
            sc = _str_consumer(rec2)
            nodes = []
            for _ in range(num_nodes):
                nodes.append(int(sc.get(10)))

            self.elements.append(nodes)


class UffFunctionAtNode:
    TYPE_NUMBER = 58
    def __init__(self, raw_text):
        UffEntry.__init__(self,UffFunctionAtNode.TYPE_NUMBER, raw_text)

        #Theres quite a bit of data here :/
        lines = raw_text.splitlines()

        #Get ids from first 5 lines
        self.ids = lines[0:5]

        #Handle this clusterfuck of fields denoting force ref
        sc = _str_consumer(lines[5]) #Load record 6

        self.function                   = {}
        self.function["type"]           = int(sc.get(5))
        self.function["id_num"]         = int(sc.get(10))
        self.function["version_num"]    = int(sc.get(5))

        self.load_case_id_num           = int(sc.get(10))

        self.response                   = {}
        sc.get(1) #To handle '1X'
        self.response["entity_name"]    = sc.get(10)
        self.response["node"]           = int(sc.get(10))
        self.response["direction"]      = int(sc.get(4))

        self.reference                  = {}
        sc.get(1) #To handle '1X'
        self.reference["entity_name"]   = sc.get(10)
        self.reference["node"]          = int(sc.get(10))
        self.reference["direction"]     = int(sc.get(4))

        #Next line not quite as bad
        sc = _str_consumer(lines[6]) #Load record 7
        self.ord_data_type              = int(sc.get(10))
        self.num_data_pairs             = int(sc.get(10))

        self.abscissa = {}
        self.abscissa["spacing"]        = int(sc.get(10))
        self.abscissa["minimum"]        = float(sc.get(13))
        self.abscissa["increment"]      = float(sc.get(13))

        self.z_axis_value               = float(sc.get(13))

        #Wake me up inside. FIVE AXISSSSS. Records 7-11
        self.axis = {}
        for rec, axisname in zip(lines[7:], ALL_AXIS_NAMES):
            sc = _str_consumer(rec)
            self.axis[axisname]             = {}
            self.axis[axisname]["datatype"] = int(sc.get(10))
            self.axis[axisname]["len_exp"]  = int(sc.get(5))
            self.axis[axisname]["frc_exp"]  = int(sc.get(5))
            self.axis[axisname]["tmp_exp"]  = int(sc.get(5))
            self.axis[axisname]["label"]    = sc.get(20)
            self.axis[axisname]["unit"]     = sc.get(20)
            #Only create a data column if axis "exists"
            if UFF_NONE in self.axis[axisname]["label"]:
                self.axis[axisname]["data"] = None
            else:
                self.axis[axisname]["data"] = []
                
        #Load records 12-infinity. 
        #Use this helper to iterate over records
        def rec_yielder(per_line, width):
            for l in lines[11:]:
                for _ in range(per_line):
                    rec_sc = _str_consumer(l)
                    yield rec_sc.get(width)

        #Small helper function to give used axis
        #Takes in axis dict, and provides list of used
        #If abscissa_spacing is even, omits abscissa axis
        def get_data_axis():
            spacing = self.abscissa["spacing"]

            #Make initial candidates
            candidates = [n for n in ALL_AXIS_NAMES]
            #Remove abscissa if necessary
            if spacing == ABSCISSA_SPACING_EVEN:
                candidates.remove(AXIS_ABSCISSA)
            #Remove unused
            candidates = [n for n in candidates if self.axis[n]["data"] is not None]
            
            #Return axis dicts
            return [self.axis[n] for n in candidates]
                
        #Fills the absi
        def gen_abscissa():
            absc_data = self.axis[AXIS_ABSCISSA]["data"]
            absc_min = self.abscissa["minimum"]
            absc_incr = self.abscissa["increment"]
            for x in range(self.num_data_pairs):
                absc_data.append(absc_min + absc_incr * x)

        #Generate timeline vals if needed
        if self.abscissa["spacing"] == ABSCISSA_SPACING_EVEN:
            gen_abscissa()

        #Generate the column pattern to fill w/ data
        data_axis = get_data_axis()
        target_data_axis = itertools.cycle(data_axis)

        #Read data depending on ord type
        if  self.ord_data_type == ORDINATE_REAL_SINGLE:
            for rec in rec_yielder(6, 13):
                datum = float(rec)
                next(target_data_axis)["data"].append(rec)
        elif self.ord_data_type == ORDINATE_COMPLEX_SINGLE:
            for rec in rec_yielder(6, 26):
                real = float(rec[:13])
                imag = float(rec[13:])
                datum = (real, imag)
                next(target_data_axis)["data"].append(rec)
        else:
            raise Exception("Cannot yet handle this type: {}\n\n{}".format(self.ord_data_type, self.raw_text))




def parse_file(filename):
    '''
    Returns a list of UFF objects
    '''
    sections = [x for x in _iterate_sections(filename)]
    sections = [ue.refine() for ue in sections]
    return sections



def main():
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        fn = "test.unv"
    a = parse_file(fn)
    for elem in a:
        print(elem)        

if __name__ == "__main__":
    main()

