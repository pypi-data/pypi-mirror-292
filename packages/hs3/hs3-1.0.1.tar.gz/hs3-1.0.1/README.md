# HS3 Utilities

Python HS$^3$ Utilities (`hs3`) is a collection of command-line tools and
utilities designed to support the High-Energy Physics Statistics
Serialization Standard (HS$^3$). This package provides tools for working
with HS$^3$ JSON files, including functionality for generating GraphML
representations and diffing HS3 files.

## Features

- **`hs3diff`**: A tool to compare two HS$^3$ JSON files and generate a diff.
- **`hs3tographml`**: A tool to convert HS$^3$ JSON files into GraphML format for visualization.

## Installation

You can install HS3 Utilities from PyPI using pip:

```bash
pip install hs3
```

Alternatively, you can clone this repository and install the package locally:

```bash
git clone https://github.com/hep-statistics-serialization-standard/python-hep-statistics-serialization-standard
cd python-hep-statistics-serialization-standard
pip install .
```

## Usage

### hs3diff

`hs3diff` is used to compare two HS3 JSON files and output the differences.

### Usage Example:

```bash
hs3diff file1.json file2.json
```

This command will output the differences between file1.json and file2.json.

### hs3tographml

`hs3tographml* converts an HS3 JSON file into a GraphML file, which can be visualized using tools like Gephi.

### Usage Example:

```bash
hs3tographml -i model.json -o model.graphml
```

This command will convert model.json into model.graphml.

### Options
- `-i`, `--input`: Input JSON file (required).
- `-o`, `--output`: Output GraphML file (required).
- `-l`, `--likelihood`: Name of the likelihood to use (optional).

## Contributing

Contributions are welcome! If you’d like to contribute to HS3
Utilities, please follow these steps:

- Fork the repository.
- Create a new branch (`git checkout -b feature-branch`).
- Make your changes and commit them (git commit -am 'Add new feature').
- Push to the branch (git push origin feature-branch).
- Open a Pull Request.

Please ensure your code follows the project's coding standards and is
well-tested.

## License

This project is licensed under the BSD 3-Clause License. See the
LICENSE file for details.

## Authors

- Carsten Burgard - cburgard@cern.ch

## Acknowledgments

Special thanks to the contributors and the HEP statistics standard
community for their ongoing support and feedback.
