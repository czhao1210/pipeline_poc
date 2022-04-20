from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element


class Search(object):
    """
    Internal Usage. This class is used to provide a series of APIs to filter/get required XML Element from XML configuration file.
    """

    @staticmethod
    def filter(node, filters):
        # type: (Element, dict) -> list
        """
        query content in the specified XML node via filters

        :param node: XML Element Node
        :param filters: dictionary of search criteria
        :return: list of xml element nodes
        :raise TypeError: Incorrect Format
        """
        matched_subnodes = list()
        if not filters:
            for sub in node.findall(r"*"):
                matched_subnodes.append(ET.fromstring(ET.tostring(sub)))
            return matched_subnodes
        for k, v in filters.items():
            if v is not None:
                if k != r"any":
                    subnodes = node.findall(k.strip())
                else:
                    subnodes = node.findall(r"*")

                if not isinstance(v, dict):
                    raise TypeError(r"Can only accept search criteria as a dictionary.")
                else:
                    for subnode in subnodes:
                        if k == subnode.tag:
                            equal = True
                            if r"attrib" in v.keys():
                                for attrib_k, attrib_v in v[r"attrib"].items():
                                    if r"CentOS" == attrib_v:
                                        pass
                                    if attrib_k in subnode.attrib.keys() and subnode.attrib[attrib_k] != attrib_v:
                                        equal = False
                            if equal and (r"value" not in v.keys() or not v[r"value"]):
                                n = ET.fromstring(ET.tostring(subnode))
                                matched_subnodes.append(n)
                            elif equal and isinstance(v["value"], dict):
                                subs = Search.filter(subnode, v["value"])
                                if subs:
                                    n = Element(subnode.tag, attrib=subnode.attrib)
                                    n.extend(subs)
                                    matched_subnodes.append(n)
                            elif equal and v[r"value"] == subnode.text.strip():
                                n = Element(subnode.tag, attrib=subnode.attrib)
                                n.text = v[r"value"]
                                matched_subnodes.append(n)
                        elif k == r"any" and subnode.tag not in filters.keys():
                            n = ET.fromstring(ET.tostring(subnode))
                            matched_subnodes.append(n)
        return matched_subnodes

    @staticmethod
    def filter_dict(node, filters):
        # type: (dict, dict) -> list
        attrib = filters['sut']['attrib']
        matched_subnodes = list()
        for subnode, subnode_val in node.items():
            for k2, v2 in attrib.items():
                if v2 != subnode_val.get('@' + k2):
                    break
            else:
                matched_subnodes.append(subnode_val)
        return matched_subnodes
