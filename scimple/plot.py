"""
SCIMPLE, Parse and Plot scimply in 2 lines
Maintainer: enzobonnal@gmail.com
"""
import math
from collections import Collection, Iterable
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib import gridspec
from mpl_toolkits.mplot3d import Axes3D
import importlib
from .utils import *

_ = Axes3D


# #####
# PLOTS TOOLS
# #####
def xgrid(a, b, p):
    return flatten_n_times(1, [[i] * math.ceil((b - a) / p) for i in np.arange(a, b, p)])


def ygrid(a, b, p):
    return flatten_n_times(1, [[i for i in np.arange(a, b, p)] for _ in np.arange(a, b, p)])



# ######
# CHECKS
# ######


def is_color_code(color):
    """
    check if color is a valid color code like : '#457ef8'
    :param color: any
    :return: bool
    """
    if type(color) is not str:
        return False
    if len(color) != 7:
        return False
    if color[0] != '#':
        return False
    try:
        int('0x' + color[1:], 0)
        return True
    except ValueError:
        return False


# ######
# COLORS
# ######

def mult_array_mapped(a, f):
    """

    :param a: Collection
    :param f: function: elem of l --> float/int
    :return: product of the elements of a mapped by f
    """
    res = f(a[0])
    for i in range(1, len(a)):
        res *= f(a[i])
    return res


def random_color_well_dispatched(n):
    """

    :param n: number of color code well dispatched needed
    :return: list of n color codes well dispatched
    """
    pas = [1, 1, 1]
    while mult_array_mapped(pas, lambda x: x + 1) < n + 2 + (
            0 if pas[0] != pas[1] or pas[0] != pas[2] else pas[0] - 1):
        index_of_pas_min = pas.index(min(pas))
        pas[index_of_pas_min] += 1
    colors = []
    for r in range(pas[0] + 1):
        for v in range(pas[1] + 1):
            for b in range(pas[2] + 1):
                if not ((r == pas[0] and v == pas[1] and b == pas[2]) or (r == v == b == 0)):
                    if not (pas[0] == pas[1] == pas[2]) or not r == v == b:
                        colors.append([r, v, b])
    for i in range(len(colors)):
        color = colors[i]
        for j in range(3):
            color[j] = hex(int(255 / pas[j]) * color[j])[2:]
            if len(color[j]) == 1:
                color[j] = '0' + color[j]
        colors[i] = '#' + ''.join(color)
    return random.sample(colors, n)


def pastelize(color, coef_pastel=2, coef_fonce=0.75):
    """

    :param color: color code
    :param coef_pastel: merge les r v b
    :param coef_fonce: alpha coef
    :return: color code pastelized
    """
    if color[0] != '#':
        color = '#' + color
    colors = [int('0x' + color[1:3], 0), int('0x' + color[3:5], 0), int('0x' + color[5:7], 0)]
    for i in range(len(colors)):
        colors[i] = (colors[i] + (255 - colors[i]) / coef_pastel) * coef_fonce
    return '#' + ''.join(map(lambda x: hex(int(x))[2:], colors))


# ####
# PLOT
# ####


class Plot:
    """
    Plot object, associated with a unique figure
    """
    __gs = gridspec.GridSpec(2, 2, width_ratios=[50, 1], height_ratios=[1, 50])
    plt.rcParams['lines.color'] = 'b'

    __cm_column_index = 'column_index'
    __cm_column_name = 'column_name'
    __cm_color_code = 'color_code'
    __cm_function_float = 'function_float'
    __cm_function_color_code = 'function_color_code'
    __cm_function_str = 'function_str'

    def __init__(self, dim=2, title=None, xlabel=None, ylabel=None, zlabel=None, borders=None, bg_color=None):
        """

        :param dim: 2 or 3
        :param title: str
        :param xlabel: str
        :param ylabel: str
        :param zlabel: str, do not set if dim is not 3 !
        :param borders: Collection of int of length dim*2, settings axes limits
        :param bg_color: a valid color code str
        """
        self.__magic = set()
        self.__at_least_one_label_defined = False
        self.__color_bar_nb = 0
        self.__fig = plt.figure()
        type_value_checks(dim, good_types=int, good_values={2, 3},
                          type_message='dim must be an integer',
                          value_message='dim value must be 2 or 3')
        if dim == 2:
            self.__ax = self.__fig.add_subplot(self.__gs[2])
        elif dim == 3:
            self.__ax = self.__fig.add_subplot(self.__gs[2], projection='3d')
        self.__dim = dim
        if borders is not None:
            type_value_checks(borders, good_types={list, tuple}, good_values=lambda borders_: len(borders_) == dim * 2,
                              type_message="borders must be a list or a tuple",
                              value_message="length of borders list for 3D plot must be 6")
            if borders[0] is not None and borders[1] is not None:
                self.__ax.set_xlim(borders[0], borders[1])
            if borders[2] is not None and borders[3] is not None:
                self.__ax.set_ylim(borders[2], borders[3])
            if dim == 3:
                self.__ax.set_zlim(borders[4], borders[5])
        if title is not None:
            type_value_checks(title, good_types=str, type_message="title type must be str")
            self.__ax.set_title(title)
        if xlabel is not None:
            type_value_checks(xlabel, good_types=str, type_message="xlabel type must be str")
            self.__ax.set_xlabel(xlabel)
        if ylabel is not None:
            type_value_checks(ylabel, good_types=str, type_message="ylabel type must be str")
            self.__ax.set_ylabel(ylabel)
        if zlabel is not None:
            type_value_checks(zlabel, good_types=str, good_values=lambda zlabel_: dim == 3,
                              type_message="zlabel type must be str",
                              value_message="zlabel is only settable on 3D plots")
            self.__ax.set_zlabel(zlabel)
        if bg_color is not None:
            type_value_checks(bg_color, good_types=str, good_values=is_color_code,
                              type_message="bg_color must be of type str",
                              value_message="bg_color_must be a valid hexadecimal color code, example : '#ff45ab'")
            self.__ax.set_facecolor(bg_color)

    def __getattr__(self, string):
        if string == 'axe':
            return self.__ax
        if string == 'fig':
            return self.__fig

    def save(self, name):
        """

        :param name: image name with correct image extension (bitmap not supported)
        :return: self
        """
        self.__fig.savefig(name)
        return self

    def __print_color_bar(self, mini, maxi, color_bar_label=None):
        """
        Called when colored_by of type function float is used : creates a 'legend subplot' describing the values
        Only 2 color bars can be plotted on a same plot        :param mini: int/float

        :param maxi: int/float
        :param color_bar_label: str
        :return: None
        """
        self.__color_bar_nb += 1
        if self.__color_bar_nb == 3:
            raise ScimpleError("only 2 function-colored plots available")
        if 'invert_color_bars' in self.__magic:
            self.__color_bar_nb = [2, 1][self.__color_bar_nb - 1]
        color_bar_subplot = self.__fig.add_subplot(self.__gs[3 if self.__color_bar_nb == 1 else 0])
        color_bar_subplot.imshow(
            [[i] for i in np.arange(maxi, mini, (mini - maxi) / 100)] if self.__color_bar_nb == 1 else
            [[i for i in np.arange(maxi, mini, (mini - maxi) / 100)]],
            interpolation='nearest',
            cmap=[cm.gray, cm.autumn][self.__color_bar_nb - 1],
            extent=[maxi / 70, mini / 70, mini, maxi] if self.__color_bar_nb == 1 else [maxi, mini, mini / 70,
                                                                                        maxi / 70])
        color_bar_subplot.ticklabel_format(axis='yx', style='sci', scilimits=(-2, 2))
        color_bar_subplot.legend().set_visible(False)
        if self.__color_bar_nb == 1:
            color_bar_subplot.set_xticks([])
            if color_bar_label:
                color_bar_subplot.set_ylabel(color_bar_label)
            color_bar_subplot.yaxis.tick_right()
        else:
            color_bar_subplot.set_yticks([])
            color_bar_subplot.xaxis.set_label_position('top')
            if color_bar_label:
                color_bar_subplot.set_xlabel(color_bar_label)
            color_bar_subplot.xaxis.tick_top()

    def magic(self, key):
        """

        :param key: str, one of :
            'invert_color_bars' : choose red to yellow colorbar first
        :return: self
        """
        self.__magic.add(key)
        return self

    @staticmethod
    def __coloring_mode(colored_by, test_index, xyz_tuple):
        """

        :param colored_by: argument given to Plot.add()
        :return: str describing the mode, one of the following :
                'column_index', 'column_name', 'color_code', 'function_float', 'function_color_code'
                'function_str' or None if no mode match
        """
        if type(colored_by) is int:
            return Plot.__cm_column_index
        if is_color_code(colored_by):
            return Plot.__cm_color_code
        if type(colored_by) is str:
            return Plot.__cm_column_name
        if callable(colored_by):
            if nb_params(colored_by) != 2:
                return None
            res = colored_by(test_index, xyz_tuple)
            if is_color_code(res):
                return Plot.__cm_function_color_code
            if type(res) is str:
                return Plot.__cm_function_str
            try:
                float(res)
                return Plot.__cm_function_float
            except:
                pass

        return None

    def add(self, table=None, x=None, y=None, z=None, first_line=0, last_line=None,
            label=None, colored_by=None, marker='.', markersize=None):
        """

        :param table:
            None
            scimple.Table
        :param x:
            int : table column index
            str : table column name
            collections.Collection : 1D array-like
        :param y:
            int : table column index
            str : table column name
            collections.Collection : 1D array-like
            function int index, 1D array x -> int/str
        :param z: Should be set if plot dimension is 3 and kept as None if dim != 3
            None
            int : table column index
            str : table column name
            collections.Collection : 1D array-like
            function int index, 1D array x, 1D array y -> int/str
        :param first_line:
            int : first row to be considered in table (indexing starts at 0)
        :param last_line:
            None
            int : last row (included) to be considered in table (indexing starts at 0)
        :param label:
            None
            str : label of the plot
            dict : {color_code color : str label} (when color_mode is function ... -> color_code
            dict : {str auto_label: str new_label} (when color_mode is column name/index)
        :param colored_by:
            None
            str : describing the mode, one of the following :
                int : column_index integer
                color code
                str : column_name
                function int : index, tuple : xyz_tuple ->floatable value (1,1.2,'15'...)
                function int : index, tuple : xyz_tuple ->color_code
                function int : index, tuple : xyz_tuple ->str_class (not floatable)
        :param marker:
            str : single character (matplotlib marker) or 'bar' to call plt.bar (bar plot)
        :param markersize:
            int : size of marker or alpha of color if bar plot
        :return:
        """
        # first_line
        type_value_checks(first_line, good_types=int,
                          type_message="first_line must be an integer",
                          good_values=lambda first_line: first_line >= 0,
                          value_message="first_line should be positive")
        # last_line
        if last_line is None and table is not None:
            last_line = len(table) - 1
        type_value_checks(last_line, good_types=(int, NoneType),
                          type_message="last_line must be an integer",
                          good_values=lambda last_line: type(last_line) is NoneType or last_line >= first_line,
                          value_message="last_line should be greater than or equal to first_line (default 0)")
        # variables:
        x_y_z_collections_len = last_line - first_line + 1 if last_line else None
        kwargs_plot = {}
        columns = []
        # table
        type_value_checks(table, good_values=lambda table: True if table is None else
        is_2d_array_like_not_empty(table),
                          value_message='table must be an instance of a 2D array-like or None')
        if isinstance(table, pd.DataFrame):
            columns = list(table.columns)
            table = table.values
        # x
        x_type = type_value_checks(x, good_types=(Collection, int, str),
                                   type_message="x must be a Collection (to plot) or (only if table set)" +
                                                "an int (table column index) or a str (table column name)",
                                   good_values=lambda x:
                                   0 <= x < len(table[first_line]) if table is not None and type(x) is int else
                                   False if table is None and type(x) is int else
                                   x in columns if table is not None and type(x) is str else
                                   len(x) == x_y_z_collections_len if table is not None else
                                   len(x) > 0,
                                   value_message="x value must verify : 0 <= x < len(table[first_line])"
                                   if table is not None and type(x) is int else
                                   "x can't be integer if table not set"
                                   if table is None and type(x) is int else
                                   "x must be in table[first_line]" if table is not None and type(x) is str else
                                   "x must be a collection " +
                                   "verifying : len(x) == last_line-first_line+1" if table is not None else
                                   "x must be a collection " +
                                   "verifying : len(x) > 0")
        if issubclass(x_type, Collection):
            x_y_z_collections_len = len(x)
        # y
        y_type = type_value_checks(y, good_types=(Collection, int, str, FuncType),
                                   type_message="y must be a Collection (to plot) or (only if table set)" +
                                                "an int (table column index) or a str (table column name)",
                                   good_values=lambda y:
                                   0 <= y < len(table[first_line]) if table is not None and type(y) is int else
                                   False if table is None and type(x) is int else
                                   y in columns if table is not None and type(y) is str else
                                   len(y) == x_y_z_collections_len if isinstance(y, Collection) else
                                   nb_params(y) == 2 if callable(y) else False,
                                   value_message="y value must verify : 0 <= y < len(table[first_line])"
                                   if table is not None and type(y) is int else
                                   "y can't be integer if table not set"
                                   if table is None and type(y) is int else
                                   "y must be in table[first_line]" if table is not None and type(y) is str else
                                   "y must be a collection " +
                                   "verifying : len(y) == len(x)" if table is not None and isinstance(y,
                                                                                                      Collection) else
                                   "y must be a collection verifying : len(y) > 0" if isinstance(y, Collection) else
                                   "y function must take exactly 2 argument (int index, type(x element))"
                                   if callable(y) else
                                   "y value invalid")

        # z
        z_type = type_value_checks(z, good_types=(Collection, int, str, FuncType, NoneType),
                                   type_message="z must be a Collection (to plot) or (only if table set)" +
                                                "an int (table column index) or a str (table column name) or None",
                                   good_values=lambda z:
                                   False if self.__dim != 3 and z is not None else
                                   True if z is None else
                                   0 <= z < len(table[first_line]) if table is not None and type(z) is int else
                                   False if table is None and type(x) is int else
                                   z in columns if table is not None and type(z) is str else
                                   len(z) == x_y_z_collections_len if isinstance(z, Collection) else
                                   nb_params(z) == 3 if callable(z) else False,
                                   value_message="z is only settable in 3D plots"
                                   if self.__dim != 3 and z is not None else
                                   "z value must verify : 0 <= z < len(table[first_line])"
                                   if table is not None and type(z) is int else
                                   "z can't be integer if table not set"
                                   if table is None and type(z) is int else
                                   "z must be in table[first_line]" if table is not None and type(z) is str else
                                   "z must be a collection " +
                                   "verifying : len(z) == len(x)" if table is not None and isinstance(z,
                                                                                                      Collection) else
                                   "z must be a collection verifying : len(z) > 0" if isinstance(z, Collection) else
                                   "z function must take exactly 3 argument " +
                                   "(int index, type(x element), type(y element)))"
                                   if callable(z)
                                   else "z value invalid")

        # marker
        type_value_checks(marker, good_types=str,
                          type_message="marker must be a string",
                          good_values=lambda marker: len(marker) == 1 or marker == 'bar' and self.__dim == 2,
                          value_message="'bar' plot is only available in 2D plot" if marker == 'bar' else
                          "marker can only be a matplotlib marker like 'o' or '-' " +
                          "(one character) or 'bar'")
        # markersize
        if not markersize:
            markersize = 9 if len(marker) == 1 else 1
        type_value_checks(markersize, good_types={int, float},
                          type_message="markersize must be an int or a float",
                          good_values=lambda markersize: (markersize >= 0 and type(markersize) is int) or
                                                         (marker == 'bar' and type(markersize) is float and
                                                          0 <= markersize <= 1),
                          value_message="marker must be a float between 0 and 1" if marker == 'bar' else
                          "marker must be a positive integer")
        if len(marker) == 1:
            kwargs_plot['markersize'] = markersize
        else:
            kwargs_plot['alpha'] = markersize

        # arrays to plot
        z_plot = None
        if x_type in {int, str}:
            if x_type is str:
                x = columns.index(x)
            try:
                x_plot = table[first_line:last_line + 1, x]
            except:
                x_plot = [line[x] for line in table[first_line:last_line + 1]]
        elif issubclass(x_type, Collection):
            if x_type is pd.Series:
                x_plot = x.as_matrix()
            else:
                x_plot = x
        else:
            raise Exception("should never happen 48648648")
        x_y_z_collections_len = len(x_plot)
        if y_type in {int, str}:
            if y_type is str:
                y = columns.index(y)
            try:
                y_plot = table[first_line:last_line + 1, y]
            except:
                y_plot = [line[y] for line in table[first_line:last_line + 1]]
        elif issubclass(y_type, Collection):
            if y_type is pd.Series:
                y_plot = y.as_matrix()
            else:
                y_plot = y
        elif y_type is FuncType:
            y_plot = [y(i, x_plot) for i in range(x_y_z_collections_len)]
        else:
            raise Exception("should never happen 86789455")

        if z_type is NoneType:
            pass
        elif z_type in {int, str}:
            if z_type is str:
                z = columns.index(z)
            try:
                z_plot = table[first_line:last_line + 1, z]
            except:
                z_plot = [line[z] for line in table[first_line:last_line + 1]]
        elif issubclass(z_type, Collection):
            if z_type is pd.Series:
                z_plot = z.as_matrix()
            else:
                z_plot = z
        elif z_type is FuncType:

            z_plot = [z(i, x_plot, y_plot) for i in range(x_y_z_collections_len)]
        else:
            raise Exception("should never happen 78941153")

        if x_plot is None or y_plot is None:
            raise Exception("should never happen 448789")

        # to_plot (need to be before # colored_by )

        if self.__dim == 3:  # 3D
            to_plot = (x_plot, y_plot, z_plot)
        else:  # 2D
            to_plot = (x_plot, y_plot)

        # colored_by:
        color_mode = self.__coloring_mode(colored_by, 0,
                                          [[to_plot[i][0]] for i in range(len(to_plot))])

        type_value_checks(color_mode, good_types=(str, NoneType),
                          type_message='colored_by is not a valid colored_by parameters, should be one of the' +
                                       'following :\n' + "'column_index integer', 'color_code'," +
                                       "'function int : index, tuple : xyz_tuple ->float/int'," +
                                       "'function int : index, tuple : xyz_tuple ->color_code'",
                          good_values=lambda color_mode:
                          False if color_mode is None and colored_by is not None else
                          False if (color_mode == Plot.__cm_column_index
                                    or color_mode == Plot.__cm_column_name)
                                   and table is None else True,
                          value_message="colored_by is not a valid mode"
                          if color_mode is None and colored_by is not None else
                          "colored_by can't be a column index/name if table parameter is not set"
                          if (color_mode == Plot.__cm_column_index
                              or color_mode == Plot.__cm_column_name)
                             and table is None else "is ok")
        # label
        type_value_checks(label, good_types=(str, NoneType, dict),
                          type_message="label must be a string or a dict colorcode : label",
                          good_values=lambda label: type(label) in {str, NoneType}
                          if color_mode in {None, 'color_code', 'function_float'} else
                          type(label) in {dict, NoneType}
                          if color_mode in {'column_index', 'column_name', 'function_color_code'} else
                          label is None if color_mode == 'function_str' else False,
                          value_message='label value error')

        # from column name to index
        if color_mode == Plot.__cm_column_name:
            colored_by = columns.index(colored_by)
            color_mode = Plot.__cm_column_index
        # Plots following the color_mode
        if color_mode is None:
            if type(label) is str and len(label) != 0:  # label != from None and ""
                kwargs_plot['label'] = label
                self.__at_least_one_label_defined = True
            self.__ax.plot(*(*to_plot, marker), **kwargs_plot) if len(marker) == 1 \
                else self.__ax.bar(*to_plot, **kwargs_plot)
        elif color_mode == Plot.__cm_color_code:
            if type(label) is str and len(label) != 0:  # label != from None and ""
                kwargs_plot['label'] = label
                self.__at_least_one_label_defined = True
            elif type(label) is dict and colored_by in label:
                kwargs_plot['label'] = label[colored_by]
                self.__at_least_one_label_defined = True
            kwargs_plot['color'] = colored_by
            self.__ax.plot(*(*to_plot, marker), **kwargs_plot) if len(marker) == 1 \
                else self.__ax.bar(*to_plot, **kwargs_plot)
        elif color_mode in [Plot.__cm_column_index, Plot.__cm_function_str]:
            self.__at_least_one_label_defined = True
            xyz = (x_plot, y_plot, z_plot) if self.__dim == 3 else (x_plot, y_plot)
            # build dict_groups
            dict_groups = {}
            for index in range(len(x_plot)):
                group = (table[index][colored_by] if color_mode == Plot.__cm_column_index
                         else colored_by(index, xyz))
                if group in dict_groups:
                    dict_groups[group] += [index]
                else:
                    dict_groups[group] = [index]
            colors_list = random_color_well_dispatched(len(dict_groups))
            for group in dict_groups:
                x_group, y_group, z_group = list(), list(), list()
                for index in dict_groups[group]:
                    x_group.append(x_plot[index])
                    y_group.append(y_plot[index])
                    if self.__dim == 3:
                        z_group.append(z_plot[index])
                if self.__dim == 2:
                    to_plot = (x_group, y_group)
                elif self.__dim == 3:
                    to_plot = (x_group, y_group, z_group)
                kwargs_plot['label'] = group if label is None or str(group) not in label else label[str(group)]
                self.__ax.plot(*(*to_plot, marker),
                               **{**kwargs_plot,
                                  'color': pastelize(colors_list.pop())}) if len(marker) == 1 \
                    else self.__ax.bar(*to_plot, **{**kwargs_plot,
                                                    'color': pastelize(colors_list.pop())})

        elif color_mode == Plot.__cm_function_color_code:
            if type(label) is str and len(label) != 0:  # label != from None and ""
                kwargs_plot['label'] = label
                self.__at_least_one_label_defined = True
            xyz = (x_plot, y_plot, z_plot) if self.__dim == 3 else (x_plot, y_plot)
            dict_color_to_lines = dict()  # hexa -> plotable lines
            for index in range(len(x_plot)):
                color = colored_by(index, xyz)
                if color in dict_color_to_lines:
                    dict_color_to_lines[color][0] += [x_plot[index]]
                    dict_color_to_lines[color][1] += [y_plot[index]]
                    if self.__dim == 3:
                        dict_color_to_lines[color][2] += [z_plot[index]]
                else:
                    if self.__dim == 2:
                        dict_color_to_lines[color] = [[x_plot[index]],
                                                      [y_plot[index]]]
                    else:
                        dict_color_to_lines[color] = [[x_plot[index]],
                                                      [y_plot[index]],
                                                      [z_plot[index]]]

            for color in dict_color_to_lines:
                if type(label) is dict and color in label:
                    kwargs_plot['label'] = label[color]
                    self.__at_least_one_label_defined = True
                else:
                    kwargs_plot['label'] = None
                if self.__dim == 2:
                    self.__ax.plot(*(dict_color_to_lines[color][0], dict_color_to_lines[color][1], marker),
                                   **{**kwargs_plot, 'color': color, 'solid_capstyle': "round"}) if len(marker) == 1 \
                        else self.__ax.bar(dict_color_to_lines[color][0], dict_color_to_lines[color][1],
                                           **{**kwargs_plot, 'color': color})
                elif self.__dim == 3:
                    self.__ax.plot(
                        *(dict_color_to_lines[color][0], dict_color_to_lines[color][1],
                          dict_color_to_lines[color][2],
                          marker), **{**kwargs_plot, 'color': color, 'solid_capstyle': "round"})
        elif color_mode == Plot.__cm_function_float:
            maxi = -inf
            mini = inf
            xyz = (x_plot, y_plot, z_plot) if self.__dim == 3 else (x_plot, y_plot)
            for i in range(len(x_plot)):
                try:
                    value = colored_by(i, xyz)
                    maxi = max(maxi, value)
                    mini = min(mini, value)
                except:
                    raise ValueError('colored_by function failed on parameters :' +
                                     '\ni=' + str(i) +
                                     '\nxyz_tuple=' + str(xyz))
            self.__print_color_bar(mini, maxi, label)
            dict_color_to_lines = {}  # hexa -> plotable lines
            for index in range(len(x_plot)):
                maxolo = max(0, colored_by(index, (x_plot, y_plot, z_plot)) - mini)
                minolo = min(255, maxolo * 255 / (maxi - mini))
                color_hexa_unit = hex(int(minolo))[2:]
                if len(color_hexa_unit) == 1:
                    color_hexa_unit = "0" + color_hexa_unit
                color = "#" + color_hexa_unit * 3 \
                    if self.__color_bar_nb == 1 else \
                    "#ff" + color_hexa_unit + "00"
                if color in dict_color_to_lines:
                    dict_color_to_lines[color][0] += [x_plot[index]]
                    dict_color_to_lines[color][1] += [y_plot[index]]
                    if self.__dim == 3:
                        dict_color_to_lines[color][2] += [z_plot[index]]
                else:
                    dict_color_to_lines[color] = [[x_plot[index]],
                                                  [y_plot[index]]]
                    if self.__dim == 3:
                        dict_color_to_lines[color] = [[x_plot[index]],
                                                      [y_plot[index]],
                                                      [z_plot[index]]]
            if self.__dim == 2:
                for color in dict_color_to_lines:
                    self.__ax.plot(*(dict_color_to_lines[color][0], dict_color_to_lines[color][1], marker),
                                   **{**kwargs_plot, 'color': color, 'solid_capstyle': "round"}) if len(marker) == 1 \
                        else self.__ax.bar(dict_color_to_lines[color][0], dict_color_to_lines[color][1],
                                           **{**kwargs_plot, 'color': color})
            elif self.__dim == 3:
                for color in dict_color_to_lines:
                    self.__ax.plot(
                        *(dict_color_to_lines[color][0], dict_color_to_lines[color][1], dict_color_to_lines[color][2],
                          marker), **{**kwargs_plot, 'color': color, 'solid_capstyle': "round"})

        else:
            raise Exception("should never happen 4567884565")
        if self.__at_least_one_label_defined:
            self.__ax.legend(loc='upper right', shadow=True, facecolor=self.__ax.get_facecolor()).draggable()
        if len(marker) != 1:
            for tick in self.__ax.get_xticklabels():
                tick.set_rotation(90)
            self.__fig.tight_layout()
        return self


def show(block=True):
    plt.show(block=block)


def run_example(tag=None):
    if tag is None:
        source = r"""
        from scimple1.scimple.scimple import Plot, get_sample, xgrid, ygrid
import pandas as pd
import math
import random
tab = get_sample('xyz', pd.DataFrame)

tab.columns = ['atom', 'x', 'y', 'z']
charges = get_sample('charges')
Plot(2, title=':)').add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10),
                        marker='.', colored_by=lambda i, xy: xy[1][i], label='du noir au blanc') \
    .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 100,
         marker='.', colored_by='#ff00ff', label='rose') \
    .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 200,
         marker='.', colored_by=lambda i, xy: xy[1][i], label='du jaune au rouge') \
    .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 300,
         marker='x', colored_by=lambda i, xy: ['#ff0000', '#00ff00', '#0000ff'][int(xy[1][i]) % 3],
         label={'#ff0000': 'rouge', '#00ff00': 'vert', '#0000ff': 'bleu'}) \
    .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 400,
         marker='.', markersize=3,
         colored_by=lambda i, xy: '>-400' if xy[1][i] > -400 else '<=-400')

Plot(3, zlabel='z', bg_color='#aaaabb', title="molecule over graphene").magic('invert_color_bars') \
    .add(tab, 'x', 'y', 'z', first_line=101, markersize=4, marker='.',
         colored_by=lambda i, _: sum(charges[101 + i]), label='delta charge') \
    .add(tab, 'x', 'y', 'z', last_line=100
         , markersize=4, marker='o', colored_by='atom')
    
dict_atoms_colors={'H': '#ffffff', 'C':'#000000', 'N':'#0000aa', 'O':'#cc0000', 'Fe':'#aa00aa'}
dict_colors_atoms={c: a for a, c in dict_atoms_colors.items()}
print(dict_colors_atoms)
Plot(2, bg_color='#225522', title="2D z axis projection") \
    .add(tab, 'x', 'y', first_line=101, markersize=10, marker='.',
         colored_by=lambda i, _: sum(charges[101 + i][1:]), label='delta charge')\
    .add(tab, 'x', 'y', last_line=100, colored_by=lambda i, xy: dict_atoms_colors[tab['atom'][i]], marker='.',
        label=dict_colors_atoms)
    
Plot(2, bg_color='#cccccc', xlabel="x axis", ylabel="y axis", title="comparison") \
    .add(tab, 'x', 'y', first_line=101, markersize=6, marker='o',
         colored_by=lambda i, _: tab['z'][101 + i],
         label="z axis") \
    .add(tab, 'x', 'y', first_line=101, markersize=4, marker='x',
         colored_by=lambda i, _: sum(charges[101 + i][1:]),
         label="external electrons")
Plot(2, xlabel="atom", ylabel="z axis", title="z dispersion") \
    .add(tab, 'atom', 'z', markersize=6, marker='o', colored_by='atom')
Plot(2, bg_color="#88aa88").add(x=range(5), y=[15] + [random.randint(1, 10) for _ in range(4)], marker='bar',
                                colored_by=lambda i, xy: xy[1][i]) \
    .add(x=range(5), y=[15] + [random.randint(1, 10) for _ in range(4)], marker='bar',
         colored_by=lambda i, xy: xy[1][i], markersize=0.5) \
    .add(x=range(-1, 6), y=[5] * 7, colored_by='#bb5555')
    
Plot(3, title='simple color').add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2), z=lambda i, x, y: (x[i] * y[i]) ** 3 + 5000,
         marker='.', colored_by='#aa00aa', label='rose', markersize=2) 
Plot(3, title='color bars')\
    .add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2), z=lambda i, x, y: (x[i] * y[i]) ** 3 + 2000,
         marker='.', colored_by=lambda i, xy: xy[2][i], label='du jaune au rouge') \
    .add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2),
                        z=lambda i, x, y: (x[i] * y[i]) ** 3 + 8000,
                        marker='o', colored_by=lambda i, xy: xy[2][i], label='du noir au blanc', markersize=2) 
Plot(3, title='custom color').add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2), z=lambda i, x, y: (x[i] * y[i]) ** 3 - 1000,
         marker='.', colored_by=lambda i, xy: ['#aa0000', '#00aa00', '#0000aa'][int(xy[2][i]) % 3],
         label={'#aa0000': 'rouge', '#00aa00': 'vert', '#0000aa': 'bleu'}, markersize=2) 
Plot(3, title='custom color').add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2), z=lambda i, x, y: (x[i] * y[i]) ** 3 - 4000,
         marker='.', markersize=3,
         colored_by=lambda i, xy: 'exterieur' if math.sqrt(xy[0][i] ** 2 + xy[1][i] ** 2) > 1 else 'interieur')"""
        print(source)
        tab = get_sample('xyz', pd.DataFrame)

        tab.columns = ['atom', 'x', 'y', 'z']
        charges = get_sample('charges')
        Plot(2, title=':)').add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10),
                                marker='.', colored_by=lambda i, xy: xy[1][i], label='du noir au blanc') \
            .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 100,
                 marker='.', colored_by='#ff00ff', label='rose') \
            .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 200,
                 marker='.', colored_by=lambda i, xy: xy[1][i], label='du jaune au rouge') \
            .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 300,
                 marker='x', colored_by=lambda i, xy: ['#ff0000', '#00ff00', '#0000ff'][int(xy[1][i]) % 3],
                 label={'#ff0000': 'rouge', '#00ff00': 'vert', '#0000ff': 'bleu'}) \
            .add(x=range(100), y=lambda i, x: 50 * math.sin(x[i] / 10) - 400,
                 marker='.', markersize=3,
                 colored_by=lambda i, xy: '>-400' if xy[1][i] > -400 else '<=-400')

        Plot(3, zlabel='z', bg_color='#aaaabb', title="molecule over graphene").magic('invert_color_bars') \
            .add(tab, 'x', 'y', 'z', first_line=101, markersize=4, marker='.',
                 colored_by=lambda i, _: sum(charges[101 + i]), label='delta charge') \
            .add(tab, 'x', 'y', 'z', last_line=100
                 , markersize=4, marker='o', colored_by='atom')

        dict_atoms_colors = {'H': '#ffffff', 'C': '#000000', 'N': '#0000aa', 'O': '#cc0000', 'Fe': '#aa00aa'}
        dict_colors_atoms = {c: a for a, c in dict_atoms_colors.items()}
        print(dict_colors_atoms)
        Plot(2, bg_color='#225522', title="2D z axis projection") \
            .add(tab, 'x', 'y', first_line=101, markersize=10, marker='.',
                 colored_by=lambda i, _: sum(charges[101 + i][1:]), label='delta charge') \
            .add(tab, 'x', 'y', last_line=100, colored_by=lambda i, xy: dict_atoms_colors[tab['atom'][i]], marker='.',
                 label=dict_colors_atoms)

        Plot(2, bg_color='#cccccc', xlabel="x axis", ylabel="y axis", title="comparison") \
            .add(tab, 'x', 'y', first_line=101, markersize=6, marker='o',
                 colored_by=lambda i, _: tab['z'][101 + i],
                 label="z axis") \
            .add(tab, 'x', 'y', first_line=101, markersize=4, marker='x',
                 colored_by=lambda i, _: sum(charges[101 + i][1:]),
                 label="external electrons")
        Plot(2, xlabel="atom", ylabel="z axis", title="z dispersion") \
            .add(tab, 'atom', 'z', markersize=6, marker='o', colored_by='atom')
        Plot(2, bg_color="#88aa88").add(x=range(5), y=[15] + [random.randint(1, 10) for _ in range(4)], marker='bar',
                                        colored_by=lambda i, xy: xy[1][i]) \
            .add(x=range(5), y=[15] + [random.randint(1, 10) for _ in range(4)], marker='bar',
                 colored_by=lambda i, xy: xy[1][i], markersize=0.5) \
            .add(x=range(-1, 6), y=[5] * 7, colored_by='#bb5555')

        Plot(3, title='simple color').add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2),
                                          z=lambda i, x, y: (x[i] * y[i]) ** 3 + 5000,
                                          marker='.', colored_by='#aa00aa', label='rose', markersize=2)
        Plot(3, title='color bars') \
            .add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2), z=lambda i, x, y: (x[i] * y[i]) ** 3 + 2000,
                 marker='.', colored_by=lambda i, xy: xy[2][i], label='du jaune au rouge') \
            .add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2),
                 z=lambda i, x, y: (x[i] * y[i]) ** 3 + 8000,
                 marker='o', colored_by=lambda i, xy: xy[2][i], label='du noir au blanc', markersize=2)
        Plot(3, title='custom color').add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2),
                                          z=lambda i, x, y: (x[i] * y[i]) ** 3 - 1000,
                                          marker='.',
                                          colored_by=lambda i, xy: ['#aa0000', '#00aa00', '#0000aa'][int(xy[2][i]) % 3],
                                          label={'#aa0000': 'rouge', '#00aa00': 'vert', '#0000aa': 'bleu'},
                                          markersize=2)
        Plot(3, title='custom color').add(x=xgrid(-4, 4, 0.2), y=ygrid(-4, 4, 0.2),
                                          z=lambda i, x, y: (x[i] * y[i]) ** 3 - 4000,
                                          marker='.', markersize=3,
                                          colored_by=lambda i, xy: 'exterieur' if math.sqrt(
                                              xy[0][i] ** 2 + xy[1][i] ** 2) > 1 else 'interieur')
    elif tag == 'color_modes':
        source = r"""
        tab=[[i,i//2] for i in range(20)]
        Plot(title="rien").add(tab, 0, 1)
        Plot(title="colored_by=0").add(tab, 0, 1, colored_by=0,
                                       label={str(i):'label de '+str(i) for i in range(18)})
        Plot(title="colored_by='#000000'").add(tab, 0, 1, colored_by='#000000',
                                               label="noir")
        Plot(title="colored_by=lambda i, xy:xy[1][i]")\
            .add(tab, 0, 1, colored_by=lambda i, xy:xy[1][i],
                 label="jauge noir blanc")
        Plot(title="colored_by=lambda i, xy:'#ff8888' if xy[1][i]>5 else '#88ff88'")\
            .add(tab, 0, 1, colored_by=lambda i, xy:'#ff8888' if xy[1][i]>5 else '#88ff88',
                 label={'#ff8888' :"rouge (>5)", '#88ff88': "vert (<5)"})
        Plot(title="colored_by=lambda i, xy:'>5' if xy[1][i]>5 else '<5'")\
            .add(tab, 0, 1, colored_by=lambda i, xy:'>5' if xy[1][i]>5 else '<5')"""
        print(source)
        tab = [[i, i // 2] for i in range(20)]
        Plot(title="rien").add(tab, 0, 1)
        Plot(title="colored_by=0").add(tab, 0, 1, colored_by=0,
                                       label={str(i): 'label de ' + str(i) for i in range(18)})
        Plot(title="colored_by='#000000'").add(tab, 0, 1, colored_by='#000000',
                                               label="noir")
        Plot(title="colored_by=lambda i, xy:xy[1][i]") \
            .add(tab, 0, 1, colored_by=lambda i, xy: xy[1][i],
                 label="jauge noir blanc")
        Plot(title="colored_by=lambda i, xy:'#ff8888' if xy[1][i]>5 else '#88ff88'") \
            .add(tab, 0, 1, colored_by=lambda i, xy: '#ff8888' if xy[1][i] > 5 else '#88ff88',
                 label={'#ff8888': "rouge (>5)", '#88ff88': "vert (<5)"})
        Plot(title="colored_by=lambda i, xy:'>5' if xy[1][i]>5 else '<5'") \
            .add(tab, 0, 1, colored_by=lambda i, xy: '>5' if xy[1][i] > 5 else '<5')
    show(True)


def array_to_img(array, name=None):
    """

    :param array: 2D array of RVB triplets of 0-255 ints
    :param name: name (including extension) if None : no saving
    :return: plt fig of image
    """
    fig, ax = plt.subplots()
    if type(array) in {tuple, list}:
        if len(array) > 0 and type(array[0]) in {tuple, list}:
            if len(array[0]) > 0 and type(array[0][0]) in {tuple, list}:
                if len(array[0][0]) in {1, 3} and all([type(elem) is int and 0 <= elem < 256 for elem in array[0][0]]):
                    if len(array[0][0]) == 1:
                        array[0][0] = [array[0][0][0]] * 3
                elif len(array[0][0]) in {1, 3} and all(
                        [type(elem) is float and 0 <= elem <= 1 for elem in array[0][0]]):
                    if len(array[0][0]) == 1:
                        array[0][0] = [array[0][0][0]] * 3
    ax.imshow(array)
    if name:
        fig.savefig(name, bbox_inches='tight', pad_inches=0)
    return fig, ax