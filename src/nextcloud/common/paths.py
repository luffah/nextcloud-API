try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from collections import OrderedDict

def sequenced_paths_list(folder_paths):
    '''
    Return the list of paths to minimize the number of operations while not missing a thing
    :param folder_path:  the folder tree (str or list or dict)
                         e.g. str 'foo/bar/A'
                         e.g. list ['foo/bar','foo/bar/A'],
                         e.g. dict {'foo': {'bar':{'A': {}}}
    :returns: ordered list of all paths to build
    '''
    list_paths = []
    if isinstance(folder_paths, str):
        tree = pathlib.PurePath(folder_paths)
        parents = list(tree.parents)
        list_paths = [str(subf) for subf in parents[:-1][::-1] + [tree]]
    elif isinstance(folder_paths, list):
        list_paths = nodes_from_tree(build_tree(folder_paths))
    elif isinstance(folder_paths, dict):
        list_paths = nodes_from_tree(folder_paths)
    return list_paths

def build_tree(paths):
    ''' Build a tree from a list of file '''
    _tree = OrderedDict()
    for k in paths:
        _build_tree_attach(k, _tree)
    return _tree

def _build_tree_attach(branch, trunk):
    parts = branch.split('/', 1)
    node = parts[0]
    if node not in trunk:
        trunk[node] = OrderedDict()
    if len(parts) == 2:
        _build_tree_attach(parts[1], trunk[node])

def nodes_from_tree(tree):
    list_folders = []
    for k in tree:
        list_folders.extend(_nodes_from_tree(tree[k], k ))
    return list_folders

def _nodes_from_tree(tree, parent_name):
    r = [parent_name]
    for k in tree:
        r.extend(_nodes_from_tree(tree[k], parent_name + '/' + k ))
    return r

if __name__ == '__main__':
    t = 'foo/A/B/C'
    assert sequenced_paths_list(t) == ['foo', 'foo/A', 'foo/A/B', 'foo/A/B/C']
    assert sequenced_paths_list([t]) == ['foo', 'foo/A', 'foo/A/B', 'foo/A/B/C']
    t = [
        'foo/A/B/C',
        'foo/A/C/B',
        'bar/A/B/C',
    ]
    assert sequenced_paths_list(t) == [
        'foo', 'foo/A', 'foo/A/B', 'foo/A/B/C', 'foo/A/C', 'foo/A/C/B',
        'bar', 'bar/A', 'bar/A/B', 'bar/A/B/C',
    ]
    t = OrderedDict([
        ('foo', OrderedDict([
            ('A', OrderedDict([
                ('B', {'C': {}}),
                ('C', {'B': {}})
            ]))
        ])),
        ('bar', {
            'A':{
                'B': {'C': {}},
            }
        })
    ])
    assert sequenced_paths_list(t) == [
        'foo', 'foo/A', 'foo/A/B', 'foo/A/B/C', 'foo/A/C', 'foo/A/C/B',
        'bar', 'bar/A', 'bar/A/B', 'bar/A/B/C',
    ]
