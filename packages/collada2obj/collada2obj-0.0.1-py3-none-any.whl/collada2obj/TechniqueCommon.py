import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass


@dataclass
class ParameterDescription:
    name: str
    type: type[object]

    @classmethod
    def from_element(cls, param_elt: ElementTree):
        """
        Description
        -----------
        Creates a ParameterDescription from an XML element.
        :param param_elt:
        :return:
        """
        return cls(
            name=param_elt.attrib["name"],
            type=param_elt.attrib["type"],
        )


@dataclass
class TechniqueCommon:
    source: str
    count: int
    stride: int
    param_description: list[ParameterDescription]
