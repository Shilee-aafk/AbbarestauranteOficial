#!/bin/bash
daphne -b 0.0.0.0 -p $PORT AbbaRestaurante.asgi:application