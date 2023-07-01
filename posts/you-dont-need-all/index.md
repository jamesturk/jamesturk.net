---
date: "2023-07-01"
title: "You Don't Need `__all__`"
categories: ["python"]
toc: true
---

Every now and then, I get a PR from a well-meaning contributor trying to add `__all__` to a Python module for whatever reason. I always decline these, they are unnecessary (at least for the way I structure my code) and I thought I'd write a short post explaining why.

## Python import refresher

There are three distinct options for importing in Python: 

* `import module`
* `from module import name`
* `from module import *`

(The first two can also work with aliases via `as other_name`, but that isn't relevant here.)

When you run `import module`:

1. Python searches the filesystem for `module.py` or `module/__init__.py`.
2. If found, the contents are executed, otherwise an `ImportError` is raised.
3. The result is bound to the name `module` and made available in the current scope.

When you run `from module import name`, only the final step changes:

1. Python searches the filesystem for `module.py` or `module/__init__.py`.
2. If found, the contents are executed, otherwise an `ImportError` is raised.
3. A member named `name` is extracted from the module and made available in the current scope.

Based on some comments I've gotten, it seems some are under the impression `__all__` is used here. It isn't. **\_\_all\_\_ is only used when you run `from module import *`.**

When you run `from module import *`:

1. Python searches the filesystem for `module.py` or `module/__init__.py`.
2. If found, the contents are executed, otherwise an `ImportError` is raised.
3. If an `__all__` member is present, it is used to determine what names to make available in the current scope.
4. If not, all members that don't start with an underscore are made available in the current scope.

Step #4 is the key here, if you're following the common advice to never write code in `__init__.py`, then you don't need `__all__` at all.  Your `__init__.py` can import the names of the public API, and will work as intended without the duplication.

### More Details

* [Python Tutorial: `__all__`](https://docs.python.org/3/tutorial/modules.html#importing-from-a-package)
* [Python Reference: import](https://docs.python.org/3/reference/import.html)

## Example

```python
# module.py
_member = "hello!"

def func():
    print(_member)
```

```python
>>> default_globals = set(globals())
>>> from module import *
>>> print(set(globals()) - default_globals)
{'default_globals', 'func'}
```
Only `func` has been added to the current (global) scope.

If we add an `__all__` to our module, we can control what is imported when using `from module import *`.

```python
# module.py (with __all__)
_member = "hello!"

def func():
    print(_member)

__all__ = ["func", "_member"]
```

Repeating our test shows that now both `func` and `_member` are imported.

```python
>>> default_globals = set(globals())
>>> from module import *
>>> print(set(globals()) - default_globals)
{'default_globals', 'func', '_member'}
```

The idea here is that you could use `__all__` to ensure that modules only expose a specific API, and that API is "documented" in `__all__`.

We shouldn't be encouraging `*` imports though! Much has been written on why but the single most important reason is that they break a fundamental contract that makes Python easier to read than many languages: You should always be able to find the source of a symbol by examining the file you're in.

## Alternative to `__all__`

Perhaps you have a package like this:

```
datapackage/
    __init__.py
    importers.py
    exporters.py
    transformers/
        __init__.py
        fix_case.py
        fix_whitespace.py
```

This file structure shouldn't define your API, forcing users to write code like:

```python
from datapackage.importers import import_json, import_csv
from datapackage.exporters import export_json, export_csv
from datapackage.transformers.fix_case import fix_case
from datapackage.transformers.fix_whitespace import fix_whitespace
```

For a small package with a handful of functions, you might decide you want to expose everything at the top level, so you could write:

```python
# module/__init__.py
from .importers import import_json, import_csv
from .exporters import export_json, export_csv
from .transformers.fix_case import fix_case
from .transformers.fix_whitespace import fix_whitespace
```

No need for an `__all__`, the only names that will be exposed are the ones you import.

In a larger package, you might want to expose the submodules, but not the functions within them.  You could write:

```python
# module/__init__.py
from . import importers
from . import exporters
from . import transformers
```

This will expose `importers`, `exporters`, and `transformers` as members of the `module` namespace, but not the functions within them.

Those submodules could then define their own `__init__.py` files which import the names you'd like to be exposed within them.

## Bonus: Banning * Imports

If you're like me, you may wonder "can we *prevent* users from using `from module import *` syntax?"

(There's no real reason to enforce this at a module level. Let people do what they want. I guess I could imagine a situation where you want to enforce this, perhaps with a library used purely for educational purposes, but generally this seems like a jerk move.)

The first thing I tried was setting `__all__` to an empty list.  *-imports do not raise an error, but nothing is inserted into the namespace. This just seems cruel though, I can imagine a less experienced Python developer trying to debug this and being very confused.

Maybe if we set `__all__` to a non-iterable, we could prevent `from module import *` from working entirely:

```python
# no_all.py
__all__ = None
```

```python
>>> from no_all import *
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'NoneType' object does not support indexing
```

It works, but it isn't a helpful error message.  It seems that the first thing Python tries to do is index into the object (I expected iteration!) and that fails.

So what if we refine our module to contain this:

```python
# no_all.py

member = "hello!"

class NoImportStar(Exception):
    # shoving this all into one class to save typing
    # plus, this is a bad idea anyway
    def __init__(self):
        super().__init__(f"`from {__name__} import *` is not allowed!")

    def __getitem__(self, i):
        raise NoImportStar()

__all__ = NoImportStar()
```

```python
>>> from no_all import *
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "no_all.py", line 6, in __getitem__
    raise NoImportStar()
no_all.NoImportStar: `from no_all import *` is not allowed!
>>> from no_all import member # works fine!
```

:)