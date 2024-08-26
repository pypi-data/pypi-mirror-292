from setuptools import find_packages, setup
import codecs
import os

if __name__ == "__main__":
    here = os.path.abspath(os.path.dirname(__file__))

    with codecs.open(
        os.path.join(here, "README.md"), encoding="utf-8"
    ) as f:
        long_description = "\n" + f.read()

    setup(
        name="collada2obj",
        version='0.0.1',
        author="Kwesi Rutledge",
        author_email="thesolitaryecrivain@gmail.com",
        url="https://github.com/kwesiRutledge/collada2obj",
        description="A library that can be used to easily convert a collada file (.dae) to a wavefront file (.obj).",
        long_description_content_type="text/markdown",
        long_description=long_description,
        packages=find_packages(),
        install_requires=['ipdb', 'typer', 'numpy'],
        keywords=["robotics", "3D Modelling", "dae", "obj"],
        # classifiers=[
        #     "Programming Language :: Python :: 3",
        # ]
    )