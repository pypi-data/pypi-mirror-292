> [!CAUTION]
>
> # THIS LIBRARY IS CURRENTLY PRE-RELEASE
>
> `pkl-python` is currently major version `v0`, and **breaking changes will happen** between versions.

# pkl-python - Pkl Bindings for Python
Python binding for [Apple's Pkl language](https://pkl-lang.org/index.html).

## Getting Started
### Installation

``` bash
pip install pkl-python
```

### Basic Usage
Here's how you can start using `pkl-python` to load a PKL module:

```python
import pkl

config = pkl.load("path/to/pkl/example_module.pkl")
config = pkl.loads("a: Int = 1 + 1")
```

### Code Generation
As Python is a dynamic language, codegen is not strictly necessary.
However, codegen lets you expect contents of pkl files within Python modules.

```
pkl-gen-python path/to/pkl/example_module.pkl
```

### TODO
* [x] (codgen) pip binary installation
* [ ] (codgen) gatherer depth-first ordering
* [ ] (codgen) clean up code


## Advanced Features

```python
import pkl

config = pkl.load("./tests/types.pkl")
config = pkl.load("./tests/types.pkl", expr="datasize")
config = pkl.load(None, module_text="a: Int = 1 + 1")
config = pkl.load("./tests/types.pkl", debug=True)
```

### `pkl.load` Parameters Detail
For details on the parameters, refer
* [`pkl eval`](https://pkl-lang.org/main/current/pkl-cli/index.html#command-eval)
* [Message Passing API](https://pkl-lang.org/main/current/bindings-specification/message-passing-api.html).

### Custom Readers
It is possible to add module or resource or module readers:
```python
from typing import List
from dataclasses import dataclass

import pkl
from pkl import (
    ModuleReader, ResourceReader, PathElement,
    ModuleSource, PreconfiguredOptions, PklError,
)

class TestModuleReader(ModuleReader):
    def read(self, url) -> str:
        return "foo = 1"

    def list_elements(self, url: str) -> List[PathElement]:
        return [PathElement("foo.pkl", False)]

opts = PreconfiguredOptions(
    moduleReaders=[TestModuleReader("customfs", True, True, True)]
)
opts.allowedModules.append("customfs:")
config = pkl.load("./tests/pkls/myModule.pkl", evaluator_options=opts)
```

## Appendix

### Type Mappings

While in pre-release they are subject to change.

| Pkl type         | TypeScript type            |
| ---------------- | -------------------------- |
| Null             | `None`                     |
| Boolean          | `bool`                     |
| String           | `str`                      |
| Int              | `int`                      |
| Int8             | `int`                      |
| Int16            | `int`                      |
| Int32            | `int`                      |
| UInt             | `int`                      |
| UInt8            | `int`                      |
| UInt16           | `int`                      |
| UInt32           | `int`                      |
| Float            | `float`                    |
| Number           | `float`                    |
| List             | `list`                     |
| Listing          | `list`                     |
| Map              | `dict`                     |
| Mapping          | `dict`                     |
| Set              | `set`                      |
| Pair             | `pkl.Pair`                 |
| Dynamic          | `dataclasses.dataclass`    |
| DataSize         | `pkl.DataSize`             |
| Duration         | `pkl.Duration`             |
| IntSeq           | `pkl.IntSeq`               |
| Class            | `dataclasses.dataclass`    |
| TypeAlias        | `typing`                   |
| Any              | `typing.Any`               |
| Unions (A\|B\|C) | `typing.Union[A\|B\|C]`    |
| Regex            | `pkl.Regex`                |

## Contributing
Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License
PKL is released under the MIT License. See the LICENSE file for more details.

## Contact
For support or to contribute, please contact jwyang0213@gmail.com or visit our GitHub repository to report issues or submit pull requests.
