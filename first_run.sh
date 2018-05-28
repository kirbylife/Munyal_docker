#!/usr/bin/env bash

equo update &

while pip >> /dev/null; (($?)); do
    echo "3" | equo install dev-python/pip
done

while pip >> /dev/null; (($?)); do
    echo "3" | equo install dev-python/pip
done
