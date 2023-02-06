<img src="./assets/logo/pyvism.svg" width="100" height="100" alt="Vism logo" />

# Vism

Vism (/vɪzᵊm/) is an esoteric programming language inspired from Vi(m) keystrokes, x86 ASM and Brainfuck.

## Specification

You can find the specification of the language [here](https://github.com/qexat/vism).

## Contributing

If you'd like to contribute to this project, please **make your PRs scoped**, even if this requires you to open several ones.
For example, if you fix a typo and enhance some code, propose these changes in two different PRs.

If you're fixing a bug, make sure to tag the corresponding issue in the title of your PR (look at the other closed PRs if you need to).
If no issue matches your PR, make sure to open one beforehand.

## PyVism

You need to follow these steps to make it working. It is recommended to use a [virtual environment](https://virtualenv.pypa.io/en/latest/).

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
