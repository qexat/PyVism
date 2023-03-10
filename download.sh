#!/bin/sh
# Clone the main branch and install Vism.

. ./utils.sh

check_binary "git"

if ! (git clone "git@github.com:qexat/PyVism.git" || git clone "https://github.com/qexat/PyVism.git"); then
	throw_error "Could not fetch the repository" 1
fi

. ./install.sh

. "${VIRTUAL_ENV}/bin/activate"
