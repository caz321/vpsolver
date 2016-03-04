"""
This code is part of the Arc-flow Vector Packing Solver (VPSolver).

Copyright (C) 2013-2016, Filipe Brandao
Faculdade de Ciencias, Universidade do Porto
Porto, Portugal. All rights reserved. E-mail: <fdabrandao@dcc.fc.up.pt>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
from __future__ import division
from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from builtins import object

import random


class AFGUtils(object):
    """Tools for manipulating arc-flow graphs."""

    @staticmethod
    def read_graph(afg_file, labels=None):
        """Reads graphs from .afg files."""
        f = open(afg_file, "r")
        s = f.read()
        lst = s.split()

        lst = lst[lst.index("IDS:")+1:]
        ids = []
        while lst[0].isdigit():
            ids.append(int(lst.pop(0)))

        s = s[s.find("#GRAPH_BEGIN#"):]
        s = s[:s.find("#GRAPH_END#\n")]
        s = s.replace("#GRAPH_BEGIN#", "")
        lst = s.split()

        assert lst[0] == "NBTYPES:"
        lst.pop(0)  # ignore "NBTYPES:"
        NBTYPES = int(lst.pop(0))

        assert lst[0] == "S:"
        lst.pop(0)  # ignore "S:"
        S = int(lst.pop(0))

        assert lst[0] == "Ts:"
        lst.pop(0)  # ignore "Ts:"
        Ts = []
        for i in range(NBTYPES):
            Ts.append(int(lst.pop(0)))

        assert lst[0] == "LOSS:"
        lst.pop(0)  # ignore "LOSS:"
        LOSS = int(lst.pop(0))

        assert lst[0] == "NV:"
        lst.pop(0)  # ignore "NV:"
        NV = int(lst.pop(0))

        assert lst[0] == "NA:"
        lst.pop(0)  # ignore "NA:"
        NA = int(lst.pop(0))

        lst = list(map(int, lst))
        A = []
        V = set([])
        for i in range(0, len(lst), 3):
            u, v, i = lst[i:i+3]
            V.add(u)
            V.add(v)
            if i == LOSS:
                A.append((u, v, LOSS))
            elif labels is None:
                A.append((u, v, ids[i]))
            else:
                A.append((u, v, labels[ids[i]]))
        V = sorted(V)
        return V, A, S, Ts, LOSS

    @staticmethod
    def relabel(V, A, fv, fa=lambda x: x):
        """Relabels graphs."""
        V = set(map(fv, V))
        A = set((fv(u), fv(v), fa(i)) for (u, v, i) in A if fv(u) != fv(v))
        return list(V), list(A)

    @staticmethod
    def draw(svg_file, V, A, showlabels=False, ignore=None, back=None,
            loss=None, verbose=True):
        """Draws arc-flow graphs in .svg format."""
        from pygraphviz.agraph import AGraph
        if ignore is None:
            ignore = []
        if back is None:
            back = []
        if loss is None:
            loss = []
        elif not isinstance(loss, (tuple, list)):
            loss = [loss]
        g = AGraph(
            rankdir="LR", directed=True, bgcolor="white", text="black",
            font_color="white", ranksep="1.0", nodesep="0.10",
            strict=False
        )
        g.node_attr["shape"] = "circle"
        g.node_attr["color"] = "black"
        g.node_attr["fontcolor"] = "black"
        g.node_attr["penwidth"] = "2.0"

        lbls = sorted(
            set(i for (u, v, i) in A if i not in loss),
            key=lambda lbl: (repr(type(lbl)), lbl)
        )

        colors = Colors.uniquecolors(len(lbls)+1, v=0.5, p=0.0)
        #random.shuffle(colors)

        for (u, v, i) in A:
            if (u, v) in ignore:
                continue
            assert u != v
            if (u, v) in back:
                u, v = v, u
                d = "back"
            else:
                d = "front"
            if i in loss:
                g.add_edge(
                    u, v, color="black", style="dashed", penwidth=2, dir=d
                )
            else:
                lbl = str(i) if showlabels else ""
                g.add_edge(
                    u, v,
                    color=colors[lbls.index(i) % len(colors)],
                    penwidth="{0}".format(2),
                    label=lbl,
                    dir=d
                )

        g.draw(svg_file, format="svg", prog="dot")
        if verbose:
            print("SVG file '{0}' generated!".format(svg_file))


class Colors(object):
    """
    Finding N Distinct RGB Colors
    Based on code from StackOverflow: http://stackoverflow.com/a/2142206
    """

    @staticmethod
    def rgbcode(t):
        """Converts (r, g, b) tuples to hexadecimal."""
        r, g, b = t
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        return "#{0:0>2x}{1:0>2x}{2:0>2x}".format(r, g, b)

    @staticmethod
    def rgbcolor(h, f, v, p):
        """Converts colors specified by h-value and f-value to
        RGB three-tuples."""
        # q = 1 - f
        # t = f
        if h == 0:
            return v, f, p
        elif h == 1:
            return 1 - f, v, p
        elif h == 2:
            return p, v, f
        elif h == 3:
            return p, 1 - f, v
        elif h == 4:
            return f, p, v
        elif h == 5:
            return v, p, 1 - f

    @staticmethod
    def uniquecolors(n, v=0.5, p=0.0):
        """Computes a list of distinct colors, each of which is
        represented as an RGB three-tuple."""
        import math
        hues = list(360.0/n*i for i in range(n))
        hs = list(math.floor(hue/60) % 6 for hue in hues)
        fs = list((hue/60)%1 for hue in hues)
        return [
            Colors.rgbcode(Colors.rgbcolor(h, f, v, p))
            for h, f in zip(hs, fs)
        ]
