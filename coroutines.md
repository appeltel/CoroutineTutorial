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

To understand what is happening, consider what happens when a regular function
is called. An instance of function is created with the arguments, it is placed
at the top of the stack, the instructions are executed, and then a value is
returned. With a coroutine function, an instance of the function - a coroutine
object - is created, but it is not immediately executed. This object is
returned, and it is up to a scheduler to actually execute the coroutine.
So how does one run a coroutine object?

A coroutine object has a `send` method which can be called with a single
argument. When `send` is called, the coroutine begins execution. In many cases
the `send` method will be called with `None` as an argument, but this argument
can in principle be used for a scheduler to send information to a running
coroutine. So here goes:

```
$ python -i example.py 
>>> coro = square(4)
>>> coro.send(None)
Starting square with argument 4!
Finishing square with argument 4!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration: 16
>>> quit()
```

Calling `send` caused the coroutine to run, but this raised a `StopIteration`
exception. The result of 16 was returned as the value of this exception. So
whatever runs a coroutine by calling `send` will need to catch this type of
exception and read the value to get the result. Notice that since we called
`send`, there was no `RuntimeWarning` about the coroutine never being awaited.

So far so good - not terribly useful yet - but at least it works. What about
the `cube` function that calls `square`? How does a function run a coroutine?
Technically it could create a coroutine object and call `send`, but this is not
a good practice. Generally speaking, functions never call coroutines and run
them - only coroutines can call and run other coroutines.

The way that a coroutine effectively "calls" another coroutine in the sense
that a function calls another function is with the `await` expression. When
a coroutine `awaits` a coroutine object, it delegates execution to that object,
so calls to the `send` method are passed on to the awaited coroutine until
it finishes. The coroutine that performed the await catches the `StopIteration`
exception and the value becomes the result of the expression. That is a lot to
digest, so here is it implemented in our example module:

```python
import time

async def square(x):
    print('Starting square with argument {}!'.format(x))
    time.sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

async def cube(x):
    print('Starting cube with argument {}!'.format(x))
    time.sleep(3)
    y = await square(x)
    print('Finishing cube with argument {}!'.format(x))
    return x * y
```

Now we can run the `cube` coroutine function:

```
>>> coro = cube(3)
>>> coro.send(None)
Starting cube with argument 3!
Starting square with argument 3!
Finishing square with argument 3!
Finishing cube with argument 3!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration: 27
```

That worked! But ultimately this is not doing anything that we could not
simply accomplish with the regular functions. What coroutines should be able
to do is pause execution when there is some reason to wait on IO or sleep.
So in the case of this example it would be useful for a coroutine to yield
control back to us when it encountered a `time.sleep` call.

Now `time.sleep` is a reuglar function. So clearly coroutines can call
regular functions, but while that function is executing the coroutine is
unable to yield control back to the caller or scheduler.

In order to make this useful we will replace `time.sleep` with a special
type of coroutine that will yield control back to the scheduler which called
`send` to run the coroutine. This is not something that you will need to
ever write in practice unless you are writing a framework for scheduling
coroutines, but we will need one here in order to schedule them "by hand":

```python
import types

@types.coroutine
def manual_sleep(n):
    yield "Please do not continue until {} seconds have elapsed.".format(n)


async def square(x):
    print('Starting square with argument {}!'.format(x))
    await manual_sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

async def cube(x):
    print('Starting cube with argument {}!'.format(x))
    await manual_sleep(3)
    y = await square(x)
    print('Finishing cube with argument {}!'.format(x))
    return x * y
```

The `manual_sleep` coroutine is a special generator-based coroutine, and
for the purposes of this tutorial we do not need to describe how that works
in its entirety. The important point is that it can yield back control
to whatever is running the coroutine by calling `send` - which is a human in
this case! So try running this version:

```
$ python -i example.py 
>>> coro = cube(3)
>>> coro.send(None)
Starting cube with argument 3!
'Please do not continue until 3 seconds have elapsed.'
```

The coroutine did not finish! It executed until it awaited the first
`manual_sleep` which yielded control back to us. We are the scheduler here,
so it sent us polite instructions to let the coroutine object "sleep" for at
least three seconds before continuing its execution with another `send`.
So now we can finish the execution by calling `send` and following instructions
until we get a `StopIteration`:

```
>>> coro.send(None)
Starting square with argument 3!
'Please do not continue until 3 seconds have elapsed.'
>>> coro.send(None)
Finishing square with argument 3!
Finishing cube with argument 3!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration: 27
```
