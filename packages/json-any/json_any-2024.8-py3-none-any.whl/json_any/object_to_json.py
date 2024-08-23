"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import importlib as imlb
import json
import pprint as pprt
import sys as sstm
import typing as h

from json_any.catalog.module import grph
from json_any.catalog.registration import REGISTERED_QUALIFIED_TYPES
from json_any.catalog.type import (
    date_t,
    date_time_t,
    decimal_t,
    enum_t,
    fraction_t,
    function_t,
    io_bytes_t,
    io_string_t,
    named_tuple_t,
    path_pure_t,
    py_array_t,
    time_delta_t,
    time_t,
    time_zone_t,
    uuid_t,
)
from json_any.constant.json import (
    CUSTOM_PREFIX,
    DATACLASS_PREFIX,
    DESCRIPTION_FOR_JSON,
    JSON_ABLE,
    JSON_ERROR,
    PATHLIB_PREFIX,
    TYPE_PREFIX,
)
from json_any.constant.module.matplotlib import MATPLOTLIB_CLASSES
from json_any.constant.module.networkx import NETWORKX_CLASSES
from json_any.constant.module.numpy import (
    JSON_TYPE_NUMPY_SCALAR,
    NUMPY_ARRAY_CLASSES,
    NUMPY_SCALAR_CLASSES,
)
from json_any.constant.module.pandas import PANDAS_CLASSES
from json_any.constant.module.scipy import SCIPY_ARRAY_CLASSES
from json_any.constant.module.xarray import XARRAY_CLASSES
from json_any.constant.python import (
    PYTHON_BYTE_CONTAINERS,
    PYTHON_CONTAINERS,
    PYTHON_TYPES,
)
from json_any.extension.module_.numpy import AsMostConciseRepresentation
from json_any.extension.type import (
    IsFullyDataclassBased,
    IsNamedTuple,
    QualifiedType,
    description_h,
    descriptors_h,
)

_HISTORY_INDENTATION = 4 * " "


def JsonStringOf(
    instance: h.Any,
    /,
    *,
    descriptors: descriptors_h = None,
    indent: int | str | None = None,
) -> tuple[str | None, h.Sequence[str] | None]:
    """"""
    out_issues = []

    jsonable = _JsonableVersionOf(
        instance, out_issues, 0, highest_level_call=True, descriptors=descriptors
    )
    try:
        out_jsoned = json.dumps(jsonable, indent=indent)
    except TypeError:
        out_jsoned = None
        out_issues.append(
            f"json.dumps error for instance:\n{pprt.pformat(instance)}\n"
            f"with representation:\n{pprt.pformat(jsonable)}"
        )

    if out_issues.__len__() == 0:
        return out_jsoned, None
    return out_jsoned, out_issues


def _JsonableVersionOf(
    instance: h.Any,
    issues: list[str],
    issue_level: int,
    /,
    *,
    highest_level_call: bool = False,
    descriptors: descriptors_h = None,
) -> h.Any | description_h:
    """"""
    instance_type = type(instance)
    qualified_type = QualifiedType(instance_type)
    # Type label used to signal appropriate unJSONing operations.
    json_type = REGISTERED_QUALIFIED_TYPES.get(instance_type, instance_type.__name__)

    if descriptors is None:
        DescriptionForJSON = None
    elif qualified_type in descriptors:
        DescriptionForJSON = descriptors[qualified_type]
    elif highest_level_call and ("" in descriptors):
        # Empty key "" is equivalent to QualifiedType(instance) when instance is
        # the object passed to "JsonStringOf". It allows to avoid to have to call
        # QualifiedType in the first place.
        DescriptionForJSON = descriptors[""]
    else:
        DescriptionForJSON = None

    if DescriptionForJSON is None:
        DescriptionForJSON = getattr(instance_type, DESCRIPTION_FOR_JSON, None)

    # ORDER: Inside each section, builtin types appear first, and builtins and
    # non-builtins are in alphabetical order.
    if DescriptionForJSON is not None:
        json_type = f"{CUSTOM_PREFIX}{qualified_type}"
        jsonable = _JsonableVersionOf(
            DescriptionForJSON(instance),
            issues,
            issue_level + 1,
            descriptors=descriptors,
        )
    # --- "TYPE IS" TESTS OF SIMPLE TYPES.
    elif instance_type is complex:
        jsonable = (instance.real, instance.imag)
    elif instance_type is date_t:
        jsonable = (instance.year, instance.month, instance.day)
    elif instance_type is decimal_t:
        jsonable = instance.as_tuple()
    elif instance_type is fraction_t:
        jsonable = (instance.numerator, instance.denominator)
    elif instance_type is io_bytes_t:
        # Buffer is assumed to be open (i.e. no instance.closed check).
        jsonable = instance.getvalue().decode(encoding="iso-8859-1")
    elif instance_type is io_string_t:
        # Buffer is assumed to be open (i.e. no instance.closed check).
        jsonable = instance.getvalue()
    elif instance_type is py_array_t:
        jsonable = (instance.tolist(), instance.typecode)
    elif instance_type is slice:
        jsonable = (instance.start, instance.stop, instance.step)
    elif instance_type is time_delta_t:
        jsonable = (instance.days, instance.seconds, instance.microseconds)
    elif instance_type is uuid_t:
        jsonable = instance.int
    # --- "TYPE IS" TESTS OF COMPLEX TYPES.
    elif instance_type is date_time_t:
        jsonable = _JsonableVersionOf(
            (instance.date(), instance.timetz()),
            issues,
            issue_level + 1,
        )
    elif instance_type is dict:
        # json does not accept non-str dictionary keys, hence the json.dumps.
        jsonable = {
            json.dumps(
                _JsonableVersionOf(
                    _key,
                    issues,
                    issue_level + 1,
                    descriptors=descriptors,
                )
            ): _JsonableVersionOf(
                _vle,
                issues,
                issue_level + 1,
                descriptors=descriptors,
            )
            for _key, _vle in instance.items()
        }
    elif instance_type is function_t:
        annotations = _JsonableVersionOf(
            instance.__annotations__,
            issues,
            issue_level + 1,
            descriptors=descriptors,
        )
        documentation = instance.__doc__
        closure = _JsonableVersionOf(
            instance.__closure__,
            issues,
            issue_level + 1,
            descriptors=descriptors,
        )
        code = instance.__code__
        code = {
            _elm[3:]: getattr(code, _elm)
            for _elm in dir(code)
            if _elm.startswith("co_") and _elm not in ("co_lines", "co_positions")
        }
        code = _JsonableVersionOf(
            code,
            issues,
            issue_level + 1,
        )
        jsonable = (annotations, documentation, closure, code)
    elif instance_type is time_t:
        jsonable = (
            instance.hour,
            instance.minute,
            instance.second,
            instance.microsecond,
            _JsonableVersionOf(instance.tzinfo, issues, issue_level + 1),
            instance.fold,
        )
    elif instance_type is time_zone_t:
        jsonable = _JsonableVersionOf(
            (instance.utcoffset(None), instance.tzname(None)),
            issues,
            issue_level + 1,
        )
    elif instance_type is type:
        module = instance.__module__
        imported = sstm.modules.get(module, None)
        if imported is None:
            imported = imlb.import_module(module)

        for name in dir(imported):
            if name[0] == "_":
                continue
            if getattr(imported, name) is instance:
                json_type = f"{TYPE_PREFIX}{module}"
                jsonable = name
                break
        else:
            # This should not happen, but just in case...
            json_type, jsonable = JSON_ERROR, None
            issues.append(
                _FormattedIssue(
                    qualified_type, f"Not found in module {module}", issue_level
                )
            )
    # --- "ISSUBCLASS" TESTS OF SIMPLE TYPES.
    elif issubclass(instance_type, path_pure_t):
        json_type = f"{PATHLIB_PREFIX}{json_type}"
        jsonable = str(instance)
    # --- "ISSUBCLASS" TESTS OF COMPLEX TYPES.
    elif issubclass(instance_type, enum_t):
        json_type = f"{REGISTERED_QUALIFIED_TYPES[enum_t]}{qualified_type}"
        jsonable = _JsonableVersionOf(
            instance.value,
            issues,
            issue_level + 1,
            descriptors=descriptors,
        )
    # --- "TYPE IN" TESTS OF SIMPLE TYPES.
    elif instance_type in PYTHON_BYTE_CONTAINERS:
        # bytes.hex was initially used in place of bytes.decode.
        jsonable = instance.decode(encoding="iso-8859-1")
    elif instance_type in NUMPY_ARRAY_CLASSES:
        jsonable = AsMostConciseRepresentation(instance)
    elif instance_type in SCIPY_ARRAY_CLASSES:
        jsonable = AsMostConciseRepresentation(instance.toarray())
    elif instance_type in XARRAY_CLASSES:
        jsonable = instance.to_dict()
    # --- "TYPE IN" TESTS OF COMPLEX TYPES.
    elif instance_type in PYTHON_CONTAINERS:
        jsonable = [
            _JsonableVersionOf(
                _elm,
                issues,
                issue_level + 1,
                descriptors=descriptors,
            )
            for _elm in instance
        ]
    elif instance_type in MATPLOTLIB_CLASSES:
        fake_file = io_bytes_t()
        instance.canvas.draw()
        instance.savefig(
            fake_file,
            bbox_inches="tight",
            pad_inches=0.0,
            transparent=True,
            dpi=200.0,
            format="png",
        )
        jsonable = fake_file.getvalue().decode(encoding="iso-8859-1")
        fake_file.close()
    elif instance_type in NETWORKX_CLASSES:
        edges = grph.to_dict_of_dicts(instance)
        # /!\ Node attributes are added to the edges dictionary! This must be taken into
        # account when deJSONing. Note that several attempts to avoid this have been
        # made, including one relying on repr(node), which is based on hash(node). Since
        # the hash function gives different results across Python sessions, this could
        # not work.
        for node, attributes in instance.nodes(data=True):
            edges[node] = (attributes, edges[node])
        jsonable = _JsonableVersionOf(
            edges,
            issues,
            issue_level + 1,
            descriptors=descriptors,
        )
    elif instance_type in NUMPY_SCALAR_CLASSES:
        json_type = JSON_TYPE_NUMPY_SCALAR
        raw_instance = instance.item()
        if type(raw_instance) is instance_type:
            # When itemization would result in a precision loss, Numpy returns a scalar
            # array instead. This would produce an infinite loop. The string
            # representation is used as a fallback description.
            description = str(raw_instance)
        else:
            description = _JsonableVersionOf(
                raw_instance,
                issues,
                issue_level + 1,
            )
        jsonable = (instance.dtype.char, description)
    elif instance_type in PANDAS_CLASSES:
        if (columns := getattr(instance, "columns", None)) is None:
            column_names = None
        else:
            column_names = columns.names
        jsonable = _JsonableVersionOf(
            (instance.to_dict(), instance.index.names, column_names),
            issues,
            issue_level + 1,
            descriptors=descriptors,
        )
    # --- FUNCTION-BASED TESTS OF COMPLEX TYPES (with dataclass last since recursive).
    elif IsNamedTuple(instance):
        json_type = f"{REGISTERED_QUALIFIED_TYPES[named_tuple_t]}{qualified_type}"
        description = tuple(instance)
        jsonable = _JsonableVersionOf(
            description,
            issues,
            issue_level + 1,
            descriptors=descriptors,
        )
    elif d.is_dataclass(instance):
        if IsFullyDataclassBased(instance_type):
            json_type = f"{DATACLASS_PREFIX}{qualified_type}"
            # Do not use d.asdict(instance) since it recurses into dataclass
            # instances which, if they extend a "container" class like list or dict,
            # might lose information.
            description = {
                _fld.name: getattr(instance, _fld.name) for _fld in d.fields(instance)
            }
            jsonable = _JsonableVersionOf(
                description,
                issues,
                issue_level + 1,
                descriptors=descriptors,
            )
        else:
            json_type, jsonable = JSON_ERROR, None
            issues.append(
                _FormattedIssue(
                    qualified_type, '"Fully" dataclass check failed', issue_level
                )
            )
    else:
        # Left here instead of checking it first to avoid "dumps" call with potential
        # exception management (subjective choice).
        try:
            _ = json.dumps(instance)
        except TypeError:
            json_type, jsonable = JSON_ERROR, None
            issues.append(
                _FormattedIssue(
                    qualified_type, "No handling procedure found", issue_level
                )
            )
        else:
            if instance_type in PYTHON_TYPES:
                json_type = None
            else:
                # Non-builtin types might be handled by the defining library.
                json_type = JSON_ABLE
            jsonable = instance

    if json_type is None:
        return jsonable
    return json_type, jsonable


def _FormattedIssue(
    qualified_type: str,
    message: str,
    issue_level: int,
) -> str:
    """"""
    return f"{'    '*issue_level}{message} for type {qualified_type}."


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
