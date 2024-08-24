import json

import yaml  # type: ignore

from .builder import from_json


def make_branch(node: dict, nodes: list[dict]) -> dict:
    """`Recursive function that adds `nodes` to a position in the subtree
    represented by `node`.

    It presumes the result of a specific format (see `build_branch()`). If the first `node`
    passed is `{}` (an empty dict), this is considered the 'trunk' of
    the subtree which will be populated by `nodes` having the _raw_ hierarchical format of:

    ```yaml title="The variable is expressed in yaml to make the hierarchy readable."
    - id: 1.
    - id: 1.1.
    - id: 1.1.1.
      units:
      - id: 1.1.1.1.
    ```

    The reason it has this format is because of an sqlite json1 union of two queries:

    1. one that retrieves ascendant nodes of a target (1.1.1.) as a list; and
    2. one that retrieves descendants of the same target (1.1.1.) but retaining the hierarchy

    After running `branch` on this _raw_ hierarchical format, the expected structure is a subtree:

    ```yaml title="The variable is expressed in yaml to make the hierarchy readable."
    - id: 1.
      units:
      - id: 1.1.
        units:
        - id: 1.1.1.
          units:
          - id: 1.1.1.1.
    ```

    After the initial run, `node` can be returned to the invoking function and it
    will be populated by a 'units' key containing the list of `nodes`.

    Examples:
        >>> trunk = {}
        >>> nodes = [{'id': '1.1.', 'content': 'starts here'}, {'id': '1.1.1.', 'content': 'should be contained in 1.1.', 'units': [{'id': '1.1.1.1.'}]} ]
        >>> make_branch({}, nodes)
        {'units': [{'id': '1.1.', 'content': 'starts here', 'units': [{'id': '1.1.1.', 'content': 'should be contained in 1.1.', 'units': [{'id': '1.1.1.1.'}]}]}]}

    Args:
        node (dict): The most recent node via recursion
        nodes (list[dict]): Expects

    Returns:
        dict: The original node
    """  # noqa
    while True:
        try:
            if units := nodes.pop(0):
                node["units"] = [units]
                new_target_node = node["units"][0]
                make_branch(new_target_node, nodes)
        except IndexError:
            break

    return node


def make_branch_json_array(raw_nodes: list[dict] | str | None) -> str | None:
    """A wrapper around the `make_branch()` function which expects a sequence of
    `units` keyed nodes and returns a tree structure.

    Args:
        raw_nodes (list[dict] | str | None): base set of rows (a sequence). This is usually received from an sqlite query using json_array.

    Returns:
        str | None: Stringified sqlite usable `json_array`.
    """  # noqa: E501
    if not raw_nodes:
        return None

    node_list = from_json(raw_nodes)
    if not node_list:
        return None

    br = make_branch({}, node_list)
    content = br["units"][0]
    branch_json_string = json.dumps(content)
    return branch_json_string


class literal(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(literal, literal_presenter)


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode("tag:yaml.org,2002:map", value)


yaml.add_representer(dict, represent_ordereddict)


def walk(nodes: list[dict]):
    """Converts raw nodes into a suitably formatted object for `yaml.dump()`.
    Without this, there would be no formatting of content and the ordering
    of the key-value pairs would not be in sync with the intended design.
    """
    if isinstance(nodes, list):
        revised_nodes = []
        for node in nodes:
            data = []
            if node.get("item"):
                candidate = node["item"]
                if candidate := str(node["item"]).strip():
                    if candidate.isdigit():
                        candidate = int(candidate)
                data.append(("item", candidate))

            if node.get("caption"):
                data.append(("caption", node["caption"].strip()))

            if node.get("content"):
                formatted_content = literal(node["content"].strip())
                data.append(("content", formatted_content))

            if node.get("units", None):
                walked_units = walk(node["units"])
                data.append(("units", walked_units))
            revised_nodes.append(dict(data))
    return revised_nodes


def fetch_values_from_key(data: dict, key: str):
    """Stack based function applicable to nested dictionaries to yield values
    that match the key; e.g. `fetch_values_from_key(data, "history")` will go
    through the nested dictionary searching for the "history" key.

    Args:
        data (dict): The nested dictionary
        key (str): The key of the nested dictionary

    Yields:
        Iterator: [description]
    """
    stack = [data]

    while stack:
        # remove from stack
        evaluate_data = stack.pop()

        # yield if the key value pair is found
        if (
            not isinstance(evaluate_data, str)
            and key in evaluate_data
            and evaluate_data[key] is not None
        ):
            yield evaluate_data[key]

        # continue if the data being evaluated is a string;
        # if not, determine whether a list or a dict
        # if a dict, add the dictionary to the stacked list to evaluate later
        # if a list, extend the stacked list
        if not isinstance(evaluate_data, str):
            for v in evaluate_data.values():
                if isinstance(v, dict):
                    stack.append(v)
                if isinstance(v, list):
                    stack += v
