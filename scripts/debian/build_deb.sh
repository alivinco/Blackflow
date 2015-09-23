#!/usr/bin/env bash

ROOT=./../../
chmod 0775 dpkg-root/DEBIAN/*
cp Makefile ${ROOT}
cd ${ROOT}
make deb