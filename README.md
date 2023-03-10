<img src="./assets/logo/pyvism.svg" width="100" height="100" alt="Vism logo" />

# Vism

Vism (/vɪzᵊm/) is an esoteric programming language inspired from Vi(m) keystrokes, x86 ASM and Brainfuck.

## Specification

You can find the specification of the language [here](https://github.com/qexat/vism).

## Contributing

See [CONTRIBUTING.md](./.github/CONTRIBUTING.md).

## PyVism

### Install locally

```
curl https://raw.githubusercontent.com/qexat/PyVism/main/download.sh | bash
```

It will clone, set up and install PyVism in a virtual environment.

---

You can also clone manually and run [`install.sh`](./install.sh).

### REPL

```
vism
```

POSIX systems enjoy a better REPL, with a lot of fancy features.
If you still want to start the universal version, use the `--force-universal` flag.

### Run a file

```
vism run <file>
```
