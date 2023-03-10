#!/bin/sh
# Clone the main branch and install Vism.

perror() {
	printf '\x1b[1;31m❌️ %s\x1b[m\n' "$1" >&2
}

throw_error() {
	perror "$1"
	exit "$2"
}

if ! (git clone "git@github.com:qexat/PyVism.git" || git clone "https://github.com/qexat/PyVism.git"); then
	throw_error "Could not fetch the repository" 1
fi

cd ./PyVism/ || throw_error "An unknown error occured" 1

. ./install.sh

. "${VIRTUAL_ENV}/bin/activate"
