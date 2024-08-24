from setuptools import setup

name = "types-caldav"
description = "Typing stubs for caldav"
long_description = '''
## Typing stubs for caldav

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`caldav`](https://github.com/python-caldav/caldav) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`caldav`.

This version of `types-caldav` aims to provide accurate annotations
for `caldav==1.3.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/caldav. All fixes for
types and metadata should be contributed there.

This stub package is marked as [partial](https://peps.python.org/pep-0561/#partial-stub-packages).
If you find that annotations are missing, feel free to contribute and help complete them.


See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit
[`53be87bbb45d0b294a4f5b12683e7684e20032d9`](https://github.com/python/typeshed/commit/53be87bbb45d0b294a4f5b12683e7684e20032d9) and was tested
with mypy 1.11.1, pyright 1.1.377, and
pytype 2024.4.11.
'''.lstrip()

setup(name=name,
      version="1.3.0.20240824",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/caldav.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-requests', 'types-vobject'],
      packages=['caldav-stubs'],
      package_data={'caldav-stubs': ['__init__.pyi', 'davclient.pyi', 'elements/__init__.pyi', 'elements/base.pyi', 'elements/cdav.pyi', 'elements/dav.pyi', 'elements/ical.pyi', 'lib/__init__.pyi', 'lib/error.pyi', 'lib/namespace.pyi', 'lib/url.pyi', 'lib/vcal.pyi', 'objects.pyi', 'requests.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
