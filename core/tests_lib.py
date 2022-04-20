import importlib
import os
import time
from typing import Optional, Callable, Any, Iterable, Mapping

path = "src/dtaf_core/lib/private/provider_config"
load_list = []


def get_load_list(path):
    for i in os.listdir(path):
        new_path = path + "/" + i
        if not os.path.isdir(new_path):
            if new_path.endswith(".py") and not "__" in new_path:
                load_list.append(new_path)
            continue
        get_load_list(path=new_path)

    return load_list


file_name = time.time()

ret = get_load_list(path)
for i in load_list:
    i = i[4:-3]
    from_list = i.split("/")
    try:
        module = importlib.import_module(i.replace('/', '.'))
    except ModuleNotFoundError:
        pass

    from_param = "from "
    for param in from_list:
        from_param += param + "."
    load_func = from_param[0:-1] + " import *" '\n'
    with open("%s" % (file_name), 'at') as file:
        file.write(load_func)