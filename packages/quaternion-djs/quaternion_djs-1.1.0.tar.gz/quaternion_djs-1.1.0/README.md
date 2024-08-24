# Quaternion

This package contains the code to enable calculations with Quaternions. Quaternion are in essence, 4-dimensional complex numbers that have applications in Mathematics, Physics and Computer Science. For more information check out (<https://en.wikipedia.org/wiki/Quaternion>)

This once was an area of study for myself during my undergraduate and I thought for a challenge I would make this package.

## Table of contents

- [Installation](#installation)
- [Documentation](#documentation)
- [Example](#example)
- [Contributing](#contributing)
- [License](#license)

## Installation

There are two sources for installation:

- GitHub, <https://github.com/DrJStrudwick/Quaternion>
- PyPi, ```pip install quaternion-djs```

As the package develops the changelog can be found [here](CHANGELOG.md)

## Documentation

Our documentation is hosted on ReadTheDocs and can be found here: <https://quaternion-djs.readthedocs.io/en/latest/>

## Example

The Quaternion class can be initialized easily by just supplying the corresponding values for the x, i, j, k components and then use in calculations as required. For the full list of methods and attributes available see the documentation.

```python
>>>from quaternion_djs import Quaternion
>>>quaternion_1 = Quaternion(1, 2, 0, 1.2)
```

## Contributing

If anyone wishes to contribute to improving this code base please see our [contributing guide](CONTRIBUTING.md) however please bear in mind our [code of conduct](CODE_OF_CONDUCT.md)

## License

This work is released under the MIT License which you can find [here](LICENSE)
