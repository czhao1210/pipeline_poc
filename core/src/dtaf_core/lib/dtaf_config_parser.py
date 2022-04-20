import json
import xmltodict


class DtafConfigParser(object):

    class ConfigOptions:
        XML = "xml"
        JSON = "json"
        TCF = "tcf"

    @classmethod
    def get_config_opts(cls, config_sources):
        """
        Takes in a list of configuration sources and returns a dict with the union of the sources.

        Each item in the list should be a tuple with the following information:
         name_of_config_source - Name used to identify the file type or config source; choices in ConfigOptions.
         configuration_source - Source of data. What this means depends on the ConfigOption selected.

        Note that the priority is determined by evaluation order - Whatever is first in the list will have priority. The
        parser will not overwrite values from sources earlier in the list if it finds two or more sources have specified
        a value for the same key.
        :raises AttributeError:
        :return: Python dictionary representation of the union of all configuration sources provided
        """
        cfg_opts = {}
        for source in reversed(config_sources):
            try:
                cls.merge_dicts(cfg_opts, getattr(cls, "_handle_" + source[0])(source[1]))
            except AttributeError:
                raise ValueError("Unsupported config source {}!".format(source[0]))
        return cfg_opts

    @classmethod
    def merge_dicts(cls, dict1, dict2):
        """Merge dict_b into dict_a, overriding dict_a's values with dict_b's if the key exists in both"""
        # inspired by https://stackoverflow.com/a/24837438 - no reason to reinvent the wheel
        # Base case, if either dict1 or dict2 are not a dict, then we have no more merging to do
        if not isinstance(dict1, dict) or not isinstance(dict2, dict):
            return dict2
        # Otherwise, overwrite each key in dict1 with the value from dict2
        # Note: This will replace nested dicts if dict2 has a leaf (non-dict) with the same key.
        for key in dict2:
            dict1[key] = cls.merge_dicts(dict1[key], dict2[key]) if key in dict1 else dict2[key]
        return dict1

    @staticmethod
    def _handle_xml(source):
        # type: (str) -> dict
        with open(source) as xml_file:
            return xmltodict.parse(xml_file)

    @staticmethod
    def _handle_json(source):
        with open(source) as json_file:
            return json.load(json_file)

    @staticmethod
    def _handle_tcf(source):
        """
        Handle TCF configuration data.

        :param source: List with (target, ic) pairs
        :return: dict with the Python dict form of the TCF configuration data, with raw TCF objects available as well
        """
        # For now, assuming 1 SUT and 1 IC from TCF, but this could change later.
        result = {"suts": {}}
        for sut in source:
            result["suts"][sut[0].kws['id']] = sut[0].kws['dtaf']  # DTAF provider configuration
            result["suts"][sut[0].kws['id']]['tcf_target'] = sut[0]
            result["suts"][sut[0].kws['id']]['tcf_ic'] = sut[1]
        return result
