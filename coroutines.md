# Coroutines Run by Hand

One way to really understand coroutines well is to construct a simple
scheduling system to run them. A while back Brett Cannon wrote a
[great article](https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/)
on this very approach. Here I will go over coroutines using a simpler
task of just running a few coroutines "by hand".

But before getting in to how coroutines work in python and how to write them,
I want to look at some simple functions first, so here is a module that
we can call `example.py` with a few regular python functions:

```python
import time

def square(x):
    print('Starting square with argument {}!'.format(x))
    time.sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

def cube(x):
    print('Starting cube with argument {}!'.format(x))
    time.sleep(3)
    y = square(x)
    print('Finishing cube with argument {}!'.format(x))
    return x * y
```

These functions have been made artificially slow and are needlessly verbose
for what they actually do, but you could imagine that the functions needed
to fetch some information from a database somewhere in order to multiply
numbers. We will start by just running them:

```
$ python -i example.py
>>> square(4)
Starting square with argument 4!
Finishing square with argument 4!
16
>>> cube(3)
Starting cube with argument 3!
Starting square with argument 3!
Finishing square with argument 3!
Finishing cube with argument 3!
27
```

Then to create a goal for this section, consider running through a loop of
numbers and calculating the cube of each one:

```
$ python -i example.py
>>> for x in range(1, 4):
...     cube(x)
... 
Starting cube with argument 1!
Starting square with argument 1!
Finishing square with argument 1!
Finishing cube with argument 1!
1
Starting cube with argument 2!
Starting square with argument 2!
Finishing square with argument 2!
Finishing cube with argument 2!
8
Starting cube with argument 3!
Starting square with argument 3!
Finishing square with argument 3!
Finishing cube with argument 3!
27
```

This is very slow, and most of that time was spent sleeping. As with the
cooking example in the last section, what I would like is to be able to
run the function over all of the numbers in the range concurrently.

But before making coroutines, a few words about functions and how great they
are. When I call `square`, it does not care what it was called by, or anything
beyond what arguments it is called with. It behaves the same no matter
if it was called by `cube` or called directly, and simply returns a value
to whatever called it when it is done. Function calls in a program naturally
form a "stack" that grows as functions call other functions, and shrinks as
they finish and return to their callers. This makes sequential code generally
easy to reason about, as one can focus on a function as an isolated unit
independent of anything other than its arguments. Of course, things like
global variables and side effects ruin this simplicity, but in many cases
it serves to keep otherwise large and complex code comprehensible.

It would be nice to retain as much simplicity as possible when moving
from sequential code (functions) to concurrent code (coroutines or threads).
Keeping things simple is, in my mind, the key reason to consider using
coroutines. They make it easy to reason about exactly when in your code you
might switch between different tasks.

A regular function in python is defined using the keyword `def`. When you
call a function, you instantiate an instance of that function with the
arguments that you supplied. This function instance goes on the stack, is
executed, and then returns some result to you.

A coroutine function in python is defined with `async def`. We will go ahead
and modify our simple module to turn the `square` function into a coroutine
function:


