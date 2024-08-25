#!/usr/bin/python
# -*- coding: utf-8 -*-

def getkeys(e):
    """
    Returns the keys or indices of the given element.

    Args:
        e (dict or list): The element to extract keys from.

    Returns:
        iterable: A set of keys if e is a dict, or a range of indices if e is a list.
    """
    if isinstance(e, dict):
        return e.keys()
    if isinstance(e, list):
        return range(len(e))
    return []

def make_patch(src, dst, ignore, precision):
    """
    Creates a patch (list of differences) that transforms the source (src) into the destination (dst).

    Args:
        src (dict or list): The original JSON-like structure.
        dst (dict or list): The target JSON-like structure.
        ignore (list): List of keys to ignore in the diff.
        precision (int): Number of decimal places or significant digits for comparing floating-point numbers.

    Returns:
        list: A list of operations ('add', 'remove', 'replace') representing the differences.
    """
    out = []
    make_patch_helper(src, dst, out, prefix=[], ignore=ignore, precision=precision)
    return out

def make_patch_helper(src, dst, out, prefix, ignore, precision):
    """
    Helper function to recursively create a patch list of differences between src and dst.

    Args:
        src (dict or list): The original JSON-like structure.
        dst (dict or list): The target JSON-like structure.
        out (list): The list to store the patch operations.
        prefix (list): The current path in the nested structure.
        ignore (list): List of keys to ignore in the diff.
        precision (int): Number of decimal places or significant digits for comparing floating-point numbers.
    """
    allkeys = set()
    dstkeys = getkeys(dst)
    srckeys = getkeys(src)
    allkeys.update(dstkeys)
    allkeys.update(srckeys)

    for k in allkeys:
        thisprefix = prefix + [str(k)]
        if k in ignore:
            continue
        if k not in dstkeys:
            out.append({'op': 'remove', 'path': thisprefix, "value": src[k]})
        elif k not in srckeys:
            out.append({'op': 'add', 'path': thisprefix, "value": dst[k]})
        elif type(src[k]) != type(dst[k]):
            out.append({'op': 'replace', 'path': thisprefix, 'orig': src[k], 'new': dst[k]})
        elif src[k] != dst[k]:
            if isinstance(src[k], list):
                for i in range(len(src[k])):
                    if i >= len(dst[k]) or src[k][i] != dst[k][i]:
                        out.append({'op': 'replace', 'path': thisprefix + [str(i)], 'orig': src[k][i], 'new': dst[k][i]})
            elif isinstance(src[k], dict):
                make_patch_helper(src[k], dst[k], out, thisprefix, ignore, precision)
            elif isinstance(src[k], str):
                out.append({'op': 'replace', 'path': thisprefix, 'orig': src[k], 'new': dst[k]})
            elif isinstance(src[k], float):
                # Compare based on a fine-tuned difference threshold
                difference = abs(src[k] - dst[k])
                if difference > 10 ** (-precision):
                    out.append({'op': 'replace', 'path': thisprefix, 'orig': src[k], 'new': dst[k]})
            else:
                out.append({'op': 'replace', 'path': thisprefix, 'orig': src[k], 'new': dst[k]})

def get(js, path):
    """
    Retrieves a value from a JSON-like structure based on a given path.

    Args:
        js (dict or list): The JSON-like structure to search in.
        path (list): A list representing the path to the desired element.

    Returns:
        value: The value found at the given path, or None if the path is invalid.
    """
    if not path:
        return js
    try:
        key = int(path[0])
    except ValueError:
        key = path[0]
    try:
        if len(path) == 1:
            return js[key]
        else:
            return get(js[key], path[1:])
    except (IndexError, KeyError):
        raise RuntimeError(f"Cannot find element {key} in container {js}")

def remove_substrings(s, substrings):
    """
    Removes all specified substrings from a string.

    Args:
        s (str): The original string.
        substrings (list): A list of substrings to remove from the original string.

    Returns:
        str: The string with all specified substrings removed.
    """
    while True:
        original_s = s
        for substr in substrings:
            s = s.replace(substr, '')
        if s == original_s:
            break
    return s    

def similar(str1, str2, substrings):
    """
    Compares two strings after removing specified substrings from both.

    Args:
        str1 (str): The first string to compare.
        str2 (str): The second string to compare.
        substrings (list): A list of substrings to remove from both strings before comparing.

    Returns:
        bool: True if the modified strings are identical, False otherwise.
    """
    reduced_str1 = remove_substrings(str1, substrings)
    reduced_str2 = remove_substrings(str2, substrings)
    return reduced_str1 == reduced_str2

def sort_lists_by_key(obj, sortkey):
    """
    Recursively sorts lists within a JSON-like structure based on a specified key.

    Args:
        obj (dict or list): The JSON-like structure containing the lists to sort.
        sortkey (str): The key to sort the lists by.

    Returns:
        dict or list: The JSON-like structure with all applicable lists sorted.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = sort_lists_by_key(value, sortkey)
    elif isinstance(obj, list):
        # Check if all elements in the list are dicts and contain the sortkey
        if all(isinstance(item, dict) and sortkey in item for item in obj):
            obj = sorted(obj, key=lambda x: (x[sortkey].lower(), x[sortkey]))
        else:
            obj = [sort_lists_by_key(item, sortkey) for item in obj]
    return obj

def diff_patch(args, patch):
    """
    Generates a list of colored strings representing the differences between two JSON-like structures.

    Args:
        args (Namespace): The parsed command-line arguments, expected to contain 'ignore_name_components'.
        patch (list): The list of patch operations generated by `make_patch`.

    Returns:
        list: A list of strings, each representing a difference with appropriate coloring.
    """
    output = []
    green = '\x1b[32m'
    red = '\x1b[31m'
    yellow = '\x1b[33m'
    endgreen = '\x1b[0m'
    endyellow = '\x1b[0m'        
    endred = '\x1b[0m'

    for op in patch:
        if op["op"] == 'add':
            output.append(green + "/".join(op["path"]) + ": "+str(op["value"])+endgreen)
        if op["op"] == 'replace':
            if op["path"][-1] == "name" and similar(op["orig"], op["new"], args.ignore_name_components):
                continue
            output.append(yellow + "/".join(op["path"]) + ": "+str(op["orig"]) + " <> "+str(op["new"])+endyellow)
        elif op["op"] == 'remove':
            output.append(red + "/".join(op["path"])+endred)
    return output
