#! /usr/bin/env python
# coding=utf-8

"""
"""

import os, shutil, time, sys, getopt
from pprint import pprint as pp

def _tree_from_abs_dir(rootdir):
    tree = {}
    if os.path.basename(rootdir) == "":
        rootdir = os.path.dirname(rootdir)
    for dirname, subdirname, filelist_noused in os.walk(rootdir):
        #pp("dirname: {}, subdirname: {}, other: {}".format(dirname, subdirname, filelist_noused))
        if dirname == rootdir and len(subdirname) == 0:
            return tree
        tree[os.path.basename(dirname)] = subdirname
    return tree

def _deal_tree(tree_dict, name, string, list_path):
    if len(tree_dict[name]) == 0:
        list_path.append(string + "/" + name)
    string += "/" + name
    for _name in tree_dict[name]:
        _deal_tree(tree_dict, _name, string, list_path)

def _makedirs(dest, list_path):
    mark_workspace = os.getcwd()
    _s = os.umask(0o0000)
    if not os.path.exists(dest):
        os.makedirs(dest, mode=0o777)
    os.chdir(dest)
    print("current path: <{}>".format(dest))
    for p in list_path:
        try:
            os.makedirs(p, mode=0o777)
        except FileExistsError:
            continue
    os.umask(_s)
    os.chdir(mark_workspace)
    print("current path: <{}>".format(mark_workspace))

def mimicry_dir(src, dst, diff):
    pp("src: {}\ndst: {}".format(src, dst))
    _list = []
    tree = _tree_from_abs_dir(src)
    if os.path.basename(src) == "":
        src = os.path.basename(os.path.dirname(src))
    src = os.path.basename(src)
    #pp("src(after deal): {}\ntree: {}".format(src, tree))
    _deal_tree(tree, src, '.', _list)
    _makedirs(dst, [ diff + '/' + i[2:]  for i in _list ])

def deal_cmdline(argv):
    src  = ''
    dest = ''
    diff = ''

    try:
       opts, args = getopt.getopt(argv,"hs:d:D:",["ifile=","ofile="])
    except getopt.GetoptError:
       sys.exit(2)

    for opt, arg in opts:
       if opt == '-h':
          print('master_mktree.py -s <src_dir> -d <dest_dir> -D <diff_string>')
          sys.exit()
       elif opt in ("-s", "--src"):
          src  = arg
       elif opt in ("-d", "--dest"):
          dest = arg
       elif opt in ("-D", "--diff"):
          diff = arg
    mimicry_dir(src, dest, diff)

if __name__ == "__main__":
    deal_cmdline(sys.argv[1:])
