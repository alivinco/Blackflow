#!/usr/bin/env bash

ROOT=./
SCRIPTS=scripts/debian
git describe --tags | sed 's/-\(alpha\|beta\|rc\)/~\1/' | cut -c2- > VERSION
chmod 0775 ${SCRIPTS}/dpkg-root/DEBIAN/*
cp ${SCRIPTS}/Makefile ${ROOT}
make clean deb

