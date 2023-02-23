#!/bin/sh
# Installs PyVism locally in a virtual environment along its dependencies.

PY_MIN_SUPPORTED="11"
python_bin="python3"


perror() {
	printf '\x1b[1;31m❌️ %s\x1b[m\n' "$1" >&2
}

psuccess() {
	printf '\x1b[32m✅️ %s\x1b[m\n' "$1"
}

pinfo() {
	printf '\x1b[36m=> %s\x1b[m\n' "$1"
}

pnewline() {
	printf '\n'
}

throw_error() {
	perror "$1"
	exit "$2"
}

check_binary() {
	if ! command -v "$1" > /dev/null 2>&1; then
		throw_error "$1 is not installed." 1
	fi
}

get_python_minor_version() {
	python3 -c 'import sys; print(sys.version_info[1])'
}

check_minor_version() {
	# $1 = current minor version we're checking
	# $2 = threshold ; must be set to the last Python minor version
	# $3 = minor version fallback ; must be set to `python3`'s minor version

	if [ "${1}" -le "${2}" ]; then
		if command -v "python3.$1" > /dev/null 2>&1; then
			echo "$1"
		else
			check_minor_version "$(($1 + 1))" "$2" "$3"
		fi
	else
		echo "$3"
	fi
}

check_binary "$python_bin"

py_minor_ver=$($python_bin -c 'import sys; print(sys.version_info[1])')

if [ "${py_minor_ver}" -lt "$PY_MIN_SUPPORTED" ]; then
	perror "'python3' version is 3.$py_minor_ver ; PyVism requires 3.11+."
	pnewline

	max_version_found=$(check_minor_version "$PY_MIN_SUPPORTED" 11 "$py_minor_ver")

	if [ "${max_version_found}" -eq "${py_minor_ver}" ]; then
		throw_error "The minimum Python version for PyVism is 3.11, but you have 3.${py_minor_ver}" 2
	fi

	pinfo "Found 'python3.$max_version_found'."
	psuccess "PyVism supports it! This binary will be used instead."
	pnewline

	python_bin="python3.$max_version_found"
fi

if [ -z "${VIRTUAL_ENV}" ]; then
	pinfo "Currently not in a virtual environment -- will create it for you!"

	check_binary 'virtualenv'
	virtualenv .venv --python "$python_bin" >/dev/null
	. .venv/bin/activate
else
	. "${VIRTUAL_ENV}/bin/activate"
fi

pnewline

pinfo 'Installing dependencies...'
pip install -r requirements.txt >/dev/null 2>&1
psuccess 'Dependencies installed.'

pinfo 'Installing PyVism...'
if pip install -e . >/dev/null 2>&1; then
	throw_error 'PyVism is not compatible with the version of Python present in the virtual environment.' 2
fi
psuccess 'PyVism installed locally.'

pnewline

cat <<EOF > "$VIRTUAL_ENV/bin/vism"
#!/usr/bin/env $python_bin
# Generated from install.sh
from pyvism.cli import main

if __name__ == "__main__":
	raise SystemExit(main())
EOF

chmod u+x "$VIRTUAL_ENV/bin/vism"

psuccess 'PyVism is now installed in the virtual environment.'
pinfo 'The command is accessible by typing "vism" inside the virtual environment.'
