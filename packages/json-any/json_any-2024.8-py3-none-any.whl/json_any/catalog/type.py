"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import types as t

function_t = t.FunctionType
module_t = t.ModuleType

import typing as h

named_tuple_t = h.NamedTuple

from array import array as py_array_t
from datetime import date as date_t
from datetime import datetime as date_time_t
from datetime import time as time_t
from datetime import timedelta as time_delta_t
from datetime import timezone as time_zone_t
from decimal import Decimal as decimal_t
from enum import Enum as enum_t
from fractions import Fraction as fraction_t
from io import BytesIO as io_bytes_t
from io import StringIO as io_string_t
from pathlib import PurePath as path_pure_t
from uuid import UUID as uuid_t

from json_any.constant.json import MODULE_TYPE_SEPARATOR
from json_any.constant.module.networkx import NETWORKX_CLASSES
from json_any.constant.module.numpy import NUMPY_ARRAY_CLASSES, NUMPY_SCALAR_CLASSES
from json_any.constant.module.pandas import PANDAS_CLASSES
from json_any.constant.module.scipy import SCIPY_ARRAY_CLASSES
from json_any.constant.module.xarray import XARRAY_CLASSES
from json_any.constant.python import (
    PYTHON_BYTE_CONTAINERS,
    PYTHON_BYTE_CONTAINERS_NAMES,
    PYTHON_CONTAINERS,
    PYTHON_CONTAINERS_NAMES,
)


def TypeNameOfJsonType(json_type: str, /) -> str:
    """"""
    return json_type[(json_type.rindex(MODULE_TYPE_SEPARATOR) + 1) :]


def JsonTypeIsFromModule(json_type: str, module: module_t | None, /) -> bool:
    """"""
    if module is None:
        return False

    module_name = module.__name__
    return json_type.startswith(module_name) and (
        json_type[module_name.__len__()] in (".", MODULE_TYPE_SEPARATOR)
    )


def ContainerWithJsonType(json_type: str, /) -> type:
    """"""
    if json_type in PYTHON_BYTE_CONTAINERS_NAMES:
        return PYTHON_BYTE_CONTAINERS[PYTHON_BYTE_CONTAINERS_NAMES.index(json_type)]
    else:
        return PYTHON_CONTAINERS[PYTHON_CONTAINERS_NAMES.index(json_type)]


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
