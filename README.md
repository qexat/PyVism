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

**Options**

-   `--force-universal`: (POSIX only) by default, POSIX systems enjoy a better REPL, with a lot of fancy features. This flag forces starting the universal version instead.<sup>1</sup>
-   `--raise-python-exceptions`: by default, unhandled Python exceptions are silently ignored. This flag makes them raised.
-   `--store-invalid-input`: by default, invalid inputs are not saved in the history. This flag makes them stored.

<sup>1</sup> This flag has no effect on non-POSIX systems.

### Run a file

```
vism run <file>
```
