# A Brief Introduction to Concurrency and Coroutines

This is the content of my
[PyOhio 2017 tutorial](https://pyohio.org/schedule/presentation/289/)
in written form, suitable for studying offline.

## Abstract

This is a beginner-friendly introduction to concurrent programming using python
coroutines and the standard library asyncio module.
The tutorial will first cover the meaning of concurrent programming
and how it differs from parallelism.
It will then continue to explore the syntax introduced in python 3.5:
coroutine definitions, await expressions, async for statements, and
async with statements.
The need for a framework with a scheduler or event loop will be discussed,
with the standard library asyncio package used as an example for the tutorial.

A simple slow web service will be introduced as an example for understanding
how to use coroutines. We will write a simple client to make several
requests in sequence, and then use the aiohttp library to rewrite it using
coroutines to make concurrent requests.
Time permitting, we will also look at rewriting the web service itself
to use coroutines to handle multiple requests concurrently.

It will be assumed that the listener has a basic understanding of
functions, classes, and exceptions in Python, but no prior knowledge
of concurrent programming is required.

## Setup Instructions

This tutorial requires Python 3.5 or later. You can download the latest
version of Python [here](https://www.python.org/downloads/).
I personally use [pyenv](https://github.com/pyenv/pyenv) to manage multiple
python versions on my OSX development machine.

In addition to python 3.5 or later, some parts of the tutorial will require
the third party packages [requests](http://docs.python-requests.org/en/master/)
and [aiohttp](http://aiohttp.readthedocs.io/en/stable/). These can be installed
by the commands `pip install requests` and `pip install aiohttp`.

I will generally write example code in short modules and then explore using
them with `python -i module.py`. This will run the module and then continue
in interactive mode where any functions or classes defined in the module
are accessible. These short modules can be found in the [examples](examples)
area of this repository.

## Outline

1. [Cooking with Concurrency](cooking.md)
1. [Understanding python Coroutines](coroutines.md)
1. [Getting to Know asyncio](asyncio.md)
1. [Animals and aiohttp](animals.md)
1. [Server Side Animals](webserver.md)
1. [Publish and Subscribe](pubsub.md)
