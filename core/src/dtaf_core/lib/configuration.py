#!/usr/bin/env python
#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################
"""
XML Configuration Helper
"""
from xml.etree.ElementTree import Element
from dtaf_core.lib.private.search import Search


class ConfigurationHelper(object):
    """
    Provider Filter/Get APIs for user to pick up the specified provider configuration
    """

    @staticmethod
    def filter_sut_config(root, sut_ip, sut_filter, attrib=dict()):
        # type: (Element, str, dict, dict) -> list
        """
        DEPRECATED: Please use find_sut instead. Search from root to get the list of suts which match the search criteria (IP, platform info, attributes).

        :param root: XML Node
        :param sut_ip: SUT IP
        :param sut_filter: dictionary of search critera (e.g. platform, silicon).
        :param attrib: dictionary of find sut.
        :return: a list of XML nodes match the criteria
        :raise TypeError: Incorrect format
        """
        sut_dict = sut_filter
        sut_dict.update(dict(any={}))
        if attrib:
            filter_dict = dict(
                sut=dict(
                    attrib=attrib,
                    value=sut_dict
                )
            )
        else:
            filter_dict = dict(
                sut=dict(
                    attrib=dict(ip=sut_ip),
                    value=sut_dict
                )
            )
        suts = root.find(r"suts")
        return Search.filter(suts, filter_dict)

    @staticmethod
    def find_sut(root, attrib=dict()):
        # type: (Element, dict) -> list
        """
        search from root to get the list of suts which match the sut attributes

        :param root: XML Node
        :param attrib: dictionary of sut attributes.
        :return: a list of XML nodes match the criteria
        :raise TypeError: Incorrect format
        """
        filter_dict = dict(
            sut=dict(
                attrib=attrib
            )
        )
        if isinstance(root, dict):
            suts = root["core"]["suts"]
            return Search.filter_dict(suts, filter_dict)
        else:
            suts = root.find(r"suts")
            return Search.filter(suts, filter_dict)

    @staticmethod
    def get_sut_config(root):
        # type: (Element, str, dict) -> list
        """
        search from root to get the list of suts which match the search criteria

        :param root: XML Node
        :param sut_ip: SUT IP
        :param sut_filter: dictionary of search critera (e.g. platform, silicon).
        :return: one of XML nodes match the criteria, return None if no sut matched
        :raise TypeError: Incorrect format
        """
        filter_dict = dict(
            sut=dict(
                attrib=dict(),
                value=dict(any={})
            )
        )
        suts = root.find(r"suts")
        ret = Search.filter(suts, filter_dict)
        if ret:
            return ret[0]
        return None

    @staticmethod
    def get_provider_config(sut, provider_name, attrib=None):
        # type: (Element, str, dict) -> Element
        """
        get provider from SUT. return provider if only 1 provider matched. otherwise return None

        :param sut: XML Node of SUT
        :param provider_name: provider name
        :param attrib: attributes of provider to filter
        :return: XML Node of provider. If no provider matched, return None.
        :raise TypeError: Incorrect format
        """
        if isinstance(sut, dict):
            if sut.get('providers'):
                if sut['providers'].get(provider_name):
                    return {provider_name: sut['providers'][provider_name]}
            return None

        if attrib is None:
            attrib = dict()
        ret = ConfigurationHelper.filter_provider_config(
            sut=sut, provider_name=provider_name, attrib=attrib)
        if len(ret) == 1:
            return ret[0]
        return None

    @staticmethod
    def get_driver_config(provider, driver_name, attrib=None):
        # type: (Element, str, dict) -> Element
        """
        get driver from provider. If only 1 driver matched, it will be returned. Otherwise, None will be returned.

        :param provider: XML Node of Provider
        :param driver_name: driver name
        :param attrib: attributes of driver to filter
        :return: XML Node of driver. If no driver matched, return None.
        :raise TypeError: Incorrect format
        """
        if attrib is None:
            attrib = dict()
        ret = ConfigurationHelper.filter_driver_config(provider=provider, driver_name=driver_name, attrib=attrib)
        if len(ret) == 1:
            return ret[0]
        return None

    @staticmethod
    def filter_provider_config(sut, provider_name, attrib=None):
        # type: (Element, str, dict) -> list
        """
        filter providers from SUT and return a list

        :param sut: XML Node of SUT
        :param provider_name: provider name
        :param attrib: attributes of provider to filter
        :return: a list of XML nodes specifying the configuration of providers
        :raise TypeError: Incorrect format
        """
        if attrib is None:
            attrib = dict()
        provider_dict = dict(providers=dict(
            attrib={},
            value={
                provider_name: dict(
                    attrib=attrib,
                    value=dict(
                        driver={},
                        any=dict()))
            }))
        return Search.filter(sut, provider_dict)[0].findall(r"*")

    @staticmethod
    def filter_driver_config(provider, driver_name, attrib=None):
        # type: (Element, str, dict) -> Element
        """
        filter driver from provider and return a list

        :param provider: XML Node of Provider
        :param driver_name: driver name
        :param attrib: attributes of driver to filter
        :return: a list of XML nodes specifying the configuration of drivers
        :raise TypeError: Incorrect format
        """
        if attrib is None:
            attrib = dict()
        driver_dict = dict(driver=dict(
            attrib={},
            value={
                driver_name: dict(
                    attrib=attrib,
                    value={}
                )
            }))
        return Search.filter(provider, driver_dict)[0].findall(r"*")
