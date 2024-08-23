"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

.. py:data:: __all__
   :type: tuple[str, str, str]
   :value: ("dump_version", "write_version_to_path", "write_version_files")

   Module exports

.. py:data:: TEMPLATES
   :type: dict[str, str]

   Templates to support both .py and .txt version files

.. seealso::

   Sources:

   - `[dump_version.py] <https://github.com/pypa/setuptools_scm/blob/main/src/setuptools_scm/_integration/dump_version.py>`_
   - `[_get_version_impl.py] <https://github.com/pypa/setuptools_scm/blob/main/src/setuptools_scm/_get_version_impl.py>`_

   `[LICENSE:MIT] <https://github.com/pypa/setuptools_scm/blob/main/LICENSE>`_

"""

import warnings
from pathlib import Path

from setuptools_scm._version_cls import _version_as_tuple

__all__ = (
    "dump_version",
    "write_version_to_path",
    "write_version_files",
)

TEMPLATES = {
    ".py": """\
# file generated by setuptools_scm
# don't change, don't track in version control
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Tuple, Union
    VERSION_TUPLE = Tuple[Union[int, str], ...]
else:
    VERSION_TUPLE = object

version: str
__version__: str
__version_tuple__: VERSION_TUPLE
version_tuple: VERSION_TUPLE

__version__ = version = {version!r}
__version_tuple__ = version_tuple = {version_tuple!r}
""",
    ".txt": "{version}",
}


def dump_version(
    root,
    version,
    write_to,
    template=None,
) -> None:
    """Dump version file

    :param root: Absolute path of package base folder
    :type root: pathlib.Path
    :param version: Semantic version str
    :type version: str
    :param write_to: Should be relative path to version file
    :type write_to: pathlib.Path
    :param template: Default None. Template text
    :type template: str | None
    """
    assert isinstance(version, str)
    root = Path(root)
    write_to = Path(write_to)
    if write_to.is_absolute():
        # trigger warning on escape
        write_to.relative_to(root)
        warnings.warn(
            f"{write_to=!s} is a absolute path,"
            " please switch to using a relative version file",
            DeprecationWarning,
        )
        target = write_to
    else:
        target = Path(root).joinpath(write_to)

    write_version_to_path(target, template=template, version=version)


def _validate_template(
    target,
    template,
):
    """Provide a template or use built-in templates for .py or .txt target files

    :param target: absolute path to target file
    :type target: pathlib.Path
    :param template: Default None. Can pass in a custom template
    :type template: str | None
    :returns: template for _version file. Either ``.txt`` or ``.py``
    :rtype: str
    :meta private:
    :raises:

       - :py:exc:`ValueError` -- unsupported template file format.
         Support only ``*.txt`` and ``*.py``

    """
    is_empty = (
        template is not None
        and isinstance(template, str)
        and len(template.strip()) == 0
    )
    if is_empty:
        msg_warn = f"{template=} looks like a error, using default instead"
        warnings.warn(msg_warn)
        template = None
    else:  # pragma: no cover
        pass

    if template is None:
        template = TEMPLATES.get(target.suffix)
    else:
        pass

    if template is None:
        msg_exc = (
            f"bad file format: {target.suffix!r} (of {target})\n"
            "only *.txt and *.py have a default template"
        )
        raise ValueError(msg_exc)
    else:  # pragma: no cover
        pass

    return template


def write_version_to_path(
    target,
    template,
    version,
):
    """Write the version file

    :param target: Absolute path to _version.[suffix] file
    :type target: pathlib.Path
    :param template: Template str. Format fields version and version tuple
    :type template: str | None
    :param version: Semantic version str
    :type version: str
    :raises:

       - :py:exc:`ValueError` -- unsupported template file format.
         Support only ``*.txt`` and ``*.py``

    """
    try:
        final_template = _validate_template(target, template)
    except ValueError:
        raise
    # log.debug("dump %s into %s", version, target)

    # t_ver = SemVersion.as_tuple(version)
    t_ver = _version_as_tuple(version)

    content = final_template.format(version=version, version_tuple=t_ver)

    target.write_text(content, encoding="utf-8")


def write_version_files(
    version,
    root,
    write_to,
    version_file,
    is_only_not_exists=False,
):
    """Write the _version.py file

    Disabled passing in a custom template

    :param version: Semantic version str
    :type version: str
    :param root: package base folder Path
    :type root: pathlib.Path
    :param write_to: Testing target relative path
    :type write_to: str | None
    :param version_file: target relative path from pyproject.toml
    :type version_file: str | None
    :param is_only_not_exists: Default False. Write file only if it does not already exit
    :type is_only_not_exists: bool | None
    :raises:

       - :py:exc:`ValueError` -- unsupported template file format.
         Support only ``*.txt`` and ``*.py``

    .. note::

       Moved from setuptools_scm._get_version_impl

    """
    if is_only_not_exists is None or not isinstance(is_only_not_exists, bool):
        is_only_not_exists = False
    else:  # pragma: no cover
        pass

    def is_do_it(abs_path):
        nonlocal is_only_not_exists
        path_abs = Path(abs_path)
        if is_only_not_exists is False:
            ret = True
        else:
            if not Path(path_abs).exists():
                ret = True
            else:
                ret = False

        return ret

    if write_to is not None:
        # For testing?!
        is_run = is_do_it(write_to)
        if is_run:
            try:
                dump_version(
                    root=root,
                    version=version,
                    write_to=write_to,
                    template=None,
                )
            except ValueError:
                raise
        else:  # pragma: no cover
            pass
    else:  # pragma: no cover
        pass

    if version_file:
        # relative path from pyproject.toml
        version_file = Path(version_file)
        assert not version_file.is_absolute(), f"{version_file=}"
        target = root.joinpath(version_file)
        is_run = is_do_it(target)
        if is_run:
            try:
                write_version_to_path(
                    target,
                    template=None,
                    version=version,
                )
            except ValueError:  # pragma: no cover
                raise
        else:  # pragma: no cover
            pass
    else:  # pragma: no cover
        pass
