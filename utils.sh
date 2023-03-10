#!/bin/sh

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
