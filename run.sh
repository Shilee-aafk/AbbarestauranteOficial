#!/bin/bash
gunicorn --worker-tmp-dir /dev/shm AbbaRestaurante.wsgi:application