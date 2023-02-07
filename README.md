<img src="./assets/logo/pyvism.svg" width="100" height="100" alt="Vism logo" />

# Vism

Vism (/vɪzᵊm/) is an esoteric programming language inspired from Vi(m) keystrokes, x86 ASM and Brainfuck.

## Specification

You can find the specification of the language [here](https://github.com/qexat/vism).

## Contributing

See [CONTRIBUTING.md](./.github/CONTRIBUTING.md).

## PyVism

You need to follow these steps to make it work. It is recommended to use a [virtual environment](https://virtualenv.pypa.io/en/latest/).

```
pip install -r requirements.txt
pip install -e .
```

### REPL

```
python3.11 -m src.pyvism
```

### Run a file

```
python3.11 -m src.pyvism run <file>
```
