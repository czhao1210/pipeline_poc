from dtaf_core.lib.private.cl_utils.communication.session import Session, wait_for_message


def remote_execute(destination, func_name, mod_name, *args, **kwargs):
    session = Session(destination)
    result = session.execute_async(func_name, mod_name, *args, **kwargs)
    ret = wait_for_message(result['key'], 100)
    session.close()
    return ret


