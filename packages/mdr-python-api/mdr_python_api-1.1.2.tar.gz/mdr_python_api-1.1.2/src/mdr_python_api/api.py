from typing import Tuple
from .http_api import ApiImpl
import json

MOCK = False


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


"""
Initialize server connection
"""

def init(new_host, new_port = 8080):
    ApiImpl.init(new_host, new_port)


def enable_mock():
    global MOCK
    MOCK = True


"""
    Register dependencies for a given dataset. 
    label and version determines the dataset for which we are adding dependencies.
    `dependencies` is an array of dependent datasets passed a tuples of label and version
    [(l1, v1), ..., (ln, vn)]
    `input_dep` is a flag determining if this is input or output dependency.
"""


def add_dependencies(
    label: str, version: str, dependencies: list[Tuple[str, str, str]], input_dep: bool
):
    if MOCK:
        return
    ApiImpl.add_dependencies(label, version, dependencies, input_dep)


"""
    Adding or updating meta data into the server
    label is the MD label
    version is the version of the MD
    md is the MD itself as a single python object (enclosed in {}). If a 
    meta data with the current label and version exists, the function
    simply updates the exisiting MD. Otherwise, it adds the new MD to DB.
    Returns the object unique ID of the new (updated) record.
"""


def register_meta_data(label: str, version: str, owner: str, url: str, md: str) -> str:
    if MOCK:
        if not is_json(md):
            raise Exception("MetaData has to be a json object")
        return
    return ApiImpl.register_meta_data(label, version, owner, url, md)


"""
    The function returns a list of matching data 
    MDs in the following format [<header><MD>, ...]
"""


def search_meta_data(search_string: str):
    if MOCK:
        return {}
    return ApiImpl.search_meta_data(search_string)


"""
    For each dataset MD, there is a separate LOCATOR object that keeps track of
    the relations for that objects (it's input/output MD objects).
    The function returns a list of matching data locators.
    
    Each MD locator have the same label of the corresponding MD with ":-- LOCATOR" suffix 
    An MD locator, keeps track of the inputs and outputs relations of the corresponding
    MD dataset object. Each locator has the same header as the original object and two lists, 
    inputs and outputs. So the result looks similar to this:
    [<name:-- LOCATOR><rest of header><input><output>, ...]
"""


def search_dependencies(search_string: str):
    if MOCK:
        return {}
    return ApiImpl.search_dependencies(search_string)


"""
   NOT FUNCTIONAL! 
   Transfer data from source dataset to dest dataset.
   source_label, source_version are source_path are the label and version and path in the the source dataset
   dest_label, dest_version are dest_path are the label and version and path in the the destination dataset
"""


def transfer_data(
    source_label, source_version, source_path, dest_label, dest_version, dest_path
):
    ApiImpl.transfer_data(
        source_label, source_version, source_path, dest_label, dest_version, dest_path
    )

"""
    Check if the server is up and running
"""
def health_check():
    return ApiImpl.health_check()