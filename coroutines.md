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


```python
import time

async def square(x):
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

Now we will run this, call square, and see what happens!

```
$ python -i example.py
>>> square(2)
<coroutine object square at 0x10aa12410>
```

That might look odd. If you were to actually run the code in the coroutine
function, it should return the integer 4. But instead it is returning a
"coroutine object". What about running `cube`?

```
>>> cube(3)
Starting cube with argument 3!
Finishing cube with argument 3!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "coro_by_hand.py", line 14, in cube
    return x * y
TypeError: unsupported operand type(s) for *: 'int' and 'coroutine'
```

This makes sense when you look at the code for cube. `y` is just the result
of calling `square(x)`, which is again the funny "coroutine object".
Python does not know how to multiply an integer by a coroutine object, so
when the `cube` function tries to multiply `x * y` it raises a `TypeError`.

Now I will quit and then explain what is going on:

```
>>> quit()
sys:1: RuntimeWarning: coroutine 'square' was never awaited
```

This is also interesting. Upon exit, the system complains that this
"coroutine object" produced by calling `square` was never "awaited".

