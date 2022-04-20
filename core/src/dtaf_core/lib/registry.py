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
import abc
from functools import partial


def get_subtype_cls(cls, subtype, strict=True):
    """
    Return the subclass of cls named "subtype". If strict is True and "subtype" is not a subtype of cls, it will raise
    a KeyError. If strict is False, it will simply return cls.

    :param cls: Class object created by MetaRegistry (cls must use MetaRegistry as its metaclass).
    :param subtype: String representing the name of the desired subclass of cls.
    :param strict: If True, require that subtype exist and raise an exception if it doesn't.
    :return: The resolved class object (either a subclass of cls, or cls itself if subtype doesn't exist and not strict)
    """
    try:
        return cls.SUBTYPES[subtype]
    except KeyError:
        if strict:
            raise KeyError(subtype + " is not a valid constant option for the " + str(cls.__name__) +
                           " class! Valid options = " + str(cls.SUBTYPES.keys()))
        else:
            return cls


class MetaRegistry(type):
    """Metaclass for creating classes that register their subclasses."""
    def __init__(cls, name, bases, namespace):
        # Set up the class
        super(MetaRegistry, cls).__init__(name, bases, namespace)

        # Bind get_subtype_cls function to the new class
        if "get_subtype_cls" not in namespace.keys():
            cls.get_subtype_cls = partial(get_subtype_cls, cls)

        # Create the subtype registry if it doesn't already exist
        if not hasattr(cls, 'SUBTYPES'):
            cls.SUBTYPES = dict()

        # Add the new class to the registry. Note that this will maintain the base class name as well. This could
        # be useful later for multiple levels of inheritance. See MetaLeafRegistry if this is undesired behavior.
        cls.SUBTYPES[cls.__name__] = cls


class AbstractMetaRegistry(abc.ABCMeta, MetaRegistry):
    """
    Metaclass that yields an abstract class that tracks its subclasses.

    Use inspect.isabstract from the Python standard library if the class needs to be checked for unimplemented abstract
    methods at runtime.
    """
    pass


class MetaLeafRegistry(type):
    """Metaclass for registering leaf subclasses (only subclasses that do not have subclasses themselves)."""
    def __init__(cls, name, bases, namespace):
        # Set up the class
        super(MetaLeafRegistry, cls).__init__(name, bases, namespace)

        # Bind get_subtype_cls function to the new class
        if "get_subtype_cls" not in namespace.keys():
            cls.get_subtype_cls = partial(get_subtype_cls, cls)

        # Create the subtype registry if it doesn't already exist
        if not hasattr(cls, 'SUBTYPES'):
            cls.SUBTYPES = dict()

        # Add the new class to the registry.
        cls.SUBTYPES[cls.__name__] = cls

        # Remove the base classes from the registry
        for base_cls in bases:
            cls.SUBTYPES.pop(base_cls.__name__, None)


class AbstractMetaLeafRegistry(abc.ABCMeta, MetaLeafRegistry):
    """
    Metaclass that yields an abstract class that tracks its leaf subclasses.

    Use inspect.isabstract from the Python standard library if the class needs to be checked for unimplemented abstract
    methods at runtime.
    """
    pass
