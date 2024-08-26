import numpy as np
from typing import List, Dict, Tuple
import xml.etree.ElementTree as ElementTree

# Our imports
from .TechniqueCommon import TechniqueCommon, ParameterDescription

class MeshConverter(object):
    def __init__(
        self,
        mesh_element: ElementTree = None,
    ):
        # Input Processing
        if mesh_element is None:
            raise ValueError("The mesh_element cannot be None.")

        # Setup
        self.mesh_element = mesh_element

        # Helpful variables for the class
        self.v, self.vn, self.vt, self.f = None, None, None, None

        # Parse the mesh element
        self.sources = mesh_element.findall('source')
        self.vertices = mesh_element.find('vertices')
        self.triangles = mesh_element.find('triangles')
        self.triangles_p = self.triangles.find('p')

        # Compute the obj elements
        self.compute_obj_elements()


    def determine_sources_technique_common(self, source: ElementTree):
        """
        Description
        -----------
        Determines the sources technique common.

        :param source:
        :return:
        """
        # Try to find the "technique_common" element.
        tc = source.find("technique_common")
        if tc is None:
            raise ValueError("Could not find the 'technique_common' element.")

        # Try to find the "accessor" element.
        accessor = tc.find("accessor")
        if accessor is None:
            raise ValueError("Could not find the 'accessor' element.")

        # Now, try to find all param values in the accessor
        param_values = []
        for param_elt in accessor.findall("param"):
            param_values.append(ParameterDescription.from_element(param_elt))

        return TechniqueCommon(
            source=source.attrib["id"],
            count=int(accessor.attrib["count"]),
            stride=int(accessor.attrib["stride"]),
            param_description=param_values,
        )

    def find_data_sources_for_triangles(self) -> Tuple[Dict, Dict]:
        """
        Description
        -----------

        Requires
        --------
        This requires that the `self.triangles` member variable is defined.

        :return:
        """
        # Setup
        triangles = self.triangles
        vertices = self.vertices

        # Setup outputs of algorithm
        data_sources_dict = {'VERTEX': None, 'NORMAL': None}
        data_sources_offsets = {'VERTEX': None, 'NORMAL': None}

        # Algorithm
        for triangles_input in triangles.findall('input'):
            data_sources_offsets[triangles_input.attrib['semantic']] = int(triangles_input.attrib['offset'])
            if triangles_input.attrib['semantic'] == 'VERTEX':
                data_sources_dict['VERTEX'] = vertices.find('input').attrib['source'][1:]
            elif triangles_input.attrib['semantic'] == 'NORMAL':
                data_sources_dict['NORMAL'] = triangles_input.attrib['source'][1:]

        return data_sources_dict, data_sources_offsets

    def compute_obj_elements(self):
        """
        Description
        -----------
        Computes the obj elements .v, .vn, .vt, .f which are used
        to define the obj file.
        :return:
        """
        # Setup

        # Define the data sources which define the vertices
        # and the normals of a given mesh.
        self.data_source_for, self.data_sources_offsets = self.find_data_sources_for_triangles()

        # v and vn can be directly extracted from position arrays
        v_and_vn_dict = self.extract_vertices_and_normals()
        self.v = v_and_vn_dict[self.data_source_for['VERTEX']]
        self.vn = v_and_vn_dict[self.data_source_for['NORMAL']]

        # Extract f list
        self.extract_f() # Must occur after self.extract_vertices_and_normals()


    def get_obj_str(self):
        """
        Description
        -----------
        Exports the obj file to the specified path.
        :param obj3d_path:
        :return:
        """
        # Setup
        obj_str = []

        # Write the vertices
        for ii, v_ii in enumerate(self.v):
            obj_str.append('v %.4f %.4f %.4f\n' % tuple(v_ii))

        # Write the normals
        for ii, vn_ii in enumerate(self.vn):
            obj_str.append('vn %.4f %.4f %.4f\n' % tuple(vn_ii))

        # Write the texture coordinates
        if self.vt is not None:
            for ii, vt_ii in enumerate(self.vt):
                obj_str.append('vt %.4f %.4f %.4f\n' % tuple(vt_ii))

        # Write the faces
        f_str = []
        for ii, f_ii in enumerate(self.f):
            if len(f_ii) == 3:
                f_str.append('f %d %d %d\n' % tuple(f_ii))
            elif len(f_ii) == 6:
                f_str.append('f %d//%d %d//%d %d//%d\n' % tuple(f_ii))

        obj_str = obj_str + f_str

        # Write the obj_str to the file
        return obj_str

    def export_obj(self, obj3d_path='./out.obj'):
        """
        Description
        -----------
        Exports the obj file to the specified path.
        :param obj3d_path: Path to the output obj file.
        :return:
        """
        return open(obj3d_path, 'w').writelines(
            self.get_obj_str()
        )

    def extract_vertices_and_normals(
        self,
    ) -> Dict:
        """
        Description
        -----------
        Extracts the vertices and normals from the sources list.
        :return:
        """
        # Setup
        sources_list = self.sources
        v_and_vn_dict = {}

        # Algorithm
        for jj, source_jj in enumerate(sources_list):
            # Extract tc from the data
            tc_ii = self.determine_sources_technique_common(
                source_jj,
            )

            positions_array = np.array([
                float(x) for x in source_jj.find('float_array').text.split()
            ])
            positions_matrix_jj = positions_array.reshape(
                (-1, tc_ii.stride),
            )

            v_and_vn_dict[source_jj.attrib['id']] = positions_matrix_jj

        return v_and_vn_dict

    def extract_f(self):
        """
        Description
        -----------
        Extracts the f list from the triangles_p element.

        Requires
        --------
        This method assumes that v and vn are already constructed here.
        :return:
        """
        # Setup
        triangles_p = self.triangles_p
        offsets = self.data_sources_offsets
        v, vn = self.v, self.vn

        if v is None:
            raise ValueError("The vertices must be defined before extracting the f list; received v value which is None.")

        if vn is None:
            raise ValueError("The normals must be defined before extracting the f list; received vn value which is None.")

        # Transform the text into a list of integers
        p_text_str = triangles_p.text.split()
        p = np.array([
            int(x)+1 for x in p_text_str
        ])
        p = p.reshape((-1, 3*2))
        self.f = np.array([[
            p_ii[offsets['VERTEX']], p_ii[offsets['NORMAL']],
            p_ii[offsets['VERTEX'] + len(list(offsets))],
            p_ii[offsets['NORMAL'] + len(list(offsets))],
            p_ii[offsets['VERTEX'] + len(list(offsets)) * 2],
            p_ii[offsets['NORMAL'] + len(list(offsets)) * 2]
        ] for p_ii in p ])


    @staticmethod
    def reduce(ma, mb):
        # ma,mb -> mc
        # usage: mc = reduce(Model.reduce, model_list)
        mc = Model()
        mc.v = (ma.v + mb.v)
        mc.vn = (ma.vn + mb.vn)
        mc.vt = (ma.vt + mb.vt)
        num_va = len(ma.v)
        num_vna = len(ma.vn)
        num_vta = len(ma.vt)
        f = mb.f
        if f:
            if len(f[0]) == 3:
                # 'f 1 2 3'
                f = map(lambda fi: [x + num_va for x in fi], f)
            elif len(f[0]) == 6:
                # 'f 1//1 2//2 3//3'
                for fi in f:
                    # f[::2] = f[::2] + num_va
                    fi[::2] = [x + num_va for x in fi[::2]]
                    # f[1::2] = f[1::2] + num_vn
                    fi[1::2] = [x + num_vna for x in fi[1::2]]
            elif len(f[0]) == 9:
                # 'f 1/1/1 2/2/2 3/3/3'
                for fi in f:
                    # f[::3] = f[::3] + num_va
                    fi[::3] = [x + num_va for x in fi[::3]]
                    # f[1::3] = f[1::3] + num_vt
                    fi[1::3] = [x + num_vta for x in fi[1::3]]
                    # f[2::3] = f[2::3] + num_vn
                    fi[2::3] = [x + num_vna for x in fi[2::3]]
            mc.f = (ma.f + f)
        # mc.set_style(ma.style+mb.style)
        return mc

    @staticmethod
    def combine(mc1, mc2):
        """
        Description
        -----------
        Combines two mesh converter objects.
        :param mc1: One mesh converter object.
        :param mc2: Another mesh converter object to combine.
        :return:
        """
        # Setup
        out = MeshConverter()

        # Combine the vertices
        out.v = np.vstack((mc1.v, mc2.v))
        out.vn = np.vstack((mc1.vn, mc2.vn))

        # Combine the textures if they exist
        if mc1.vt is not None and mc2.vt is not None:
            out.vt = np.vstack((mc1.vt, mc2.vt))

        # Combine the faces
        out.f = np.vstack((mc1.f, mc2.f))