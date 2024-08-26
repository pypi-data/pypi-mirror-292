# collada2obj

This Python library can be used to easily convert collada (i.e., `.dae`) files
to wavefront (i.e., `.obj` ) files. This transformation between file formats for 3d
models is useful for a variety of applications, though this library was motivated
by the need for this transformation in some robotics applications.

At the moment, this library is a work in progress and is not yet fully functional.
However, the basic functionality is there and the library can be used to convert
simple collada files to obj files.

See the `examples` directory for example usages of the library.

## Installation

To install this library, you can use `pip`:

```bash
pip install collada2obj
```

### Local Installation

If you want to install this library locally, you can clone this repository and
install it using `pip` in the following way: Change to the root directory of this repo
and then run the following command:
 
```bash
pip install -e .
```

## Usage

```python
import ipdb
import typer
import xml.etree.ElementTree as ET
import numpy as np

from collada2obj import MeshConverter

def main(input_filename: str = "./base.dae", output_filename: str = "./out.obj"):
    # Setup

    # PARSE XML
    tree = ET.ElementTree(file=input_filename)

    # FIX xmlns problem
    # http://stackoverflow.com/questions/13412496/python-elementtree-module-how-to-ignore-the-namespace-of-xml-files-to-locate-ma
    for el in tree.iter():
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces

    # geometry_0
    meshes = tree.findall('library_geometries/geometry/mesh')

    models = []
    for ii, mesh_ii in enumerate(meshes):
        # Setup
        print(f"Processing mesh {ii}...")
        converter_ii = MeshConverter(mesh_ii)

        # model = reduce(MeshConverter.reduce, models)

        # Export
        converter_ii.export_obj(output_filename)

```