# Reddit Bot Framework (RBF)

![license](https://img.shields.io/github/license/jmhayes3/rbf)
![build](https://github.com/jmhayes3/rbf/actions/workflows/build.yml/badge.svg)
![release](https://img.shields.io/github/v/release/jmhayes3/rbf?display_name=tag&sort=semver)

## Overview

RBF is a framework for building and managing bots that interface with Reddit. It is designed to be easy to use and simple to extend.

This project was started with two primary goals in mind:

1. Lower the barrier to entry for creating Reddit bots.
2. Be scalable without depending on third-party cloud services.

## Installing

### Poetry

    $ git clone https://github.com/jmhayes3/rbf.git
    $ cd rbf
    $ poetry install

### Docker

Start the application using docker compose:

    $ docker compose -f docker-compose.dev.yml up

Then, point your browser at <http://localhost:8000> to access the web application. 
