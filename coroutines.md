# Coroutines Run by Hand

One way to really understand coroutines well is to construct a simple
scheduling system to run them. A while back Brett Cannon wrote a
[great article](https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/)
on this very approach. Here I will go over coroutines using a simpler
task of just running a few coroutines "by hand".

### Just Functions to Start

Before getting in to how coroutines work in python and how to write them,
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

### On To Coroutines

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

### Yielding to the Scheduler

In order to the above example 
useful we will replace `time.sleep` with a special
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

To see how this really helps, consider two coroutine objects, `cube(5)` and
`cube(10)`. We (the human scheduler) are capable of getting one of the
objects running, and then while one is waiting three seconds, starting the
other one and running it concurrently. As the two coroutines yield back to
the scheduler, we can continue their execution by calling `send`:

```
>>> coro1 = cube(5)
>>> coro2 = cube(10)
>>> coro1.send(None)
Starting cube with argument 5!
'Please do not continue until 3 seconds have elapsed.'
>>> coro2.send(None)
Starting cube with argument 10!
'Please do not continue until 3 seconds have elapsed.'
>>> coro1.send(None)
Starting square with argument 5!
'Please do not continue until 3 seconds have elapsed.'
>>> coro2.send(None)
Starting square with argument 10!
'Please do not continue until 3 seconds have elapsed.'
>>> coro1.send(None)
Finishing square with argument 5!
Finishing cube with argument 5!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration: 125
>>> coro2.send(None)
Finishing square with argument 10!
Finishing cube with argument 10!
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration: 1000
```

From this it should be clear how using coroutines is an example of
cooperative rather than pre-emptive multitasking. The scheduler cannot
tell a coroutine that it is time to stop and allow another to run, it
has to wait until the coroutine willingly yields control back to the
scheduler.

To make this useful we need a framework to provide a scheduler that can
run coroutines without human intervention and return to us the
return value of each coroutine. It also will need a set of special
coroutines to perform basic I/O and sleep functions and can communicate
correctly with the scheduler.

### Using a Real Scheduler

Python is a "batteries included" language, and ships with the `asyncio`
library which provides such a framework. It has a scheduler to run
coroutines, called an "event loop", and special coroutines needed to
yield back to the event loop. For this example, we only need to use
`asyncio.sleep`. Awaiting `asyncio.sleep(n)` with a number `n` will yield
control to the asyncio event loop, and instruct it to wait at least `n`
seconds before resuming the coroutine. In order to use this, we need to
first slightly rewrite the example module to use `asyncio.sleep` rather than
our `manual_sleep` coroutine function:

```python
import asyncio

async def square(x):
    print('Starting square with argument {}!'.format(x))
    await asyncio.sleep(3)
    print('Finishing square with argument {}!'.format(x))
    return x * x

async def cube(x):
    print('Starting cube with argument {}!'.format(x))
    await asyncio.sleep(3)
    y = await square(x)
    print('Finishing cube with argument {}!'.format(x))
    return x * y
```

Now run this module interactively and schedule a `cube(5)` coroutine
to be executed:

```
$ python -i example.py
>>> loop = asyncio.get_event_loop()
>>> result = loop.run_until_complete(cube(5))
Starting cube with argument 5!
Starting square with argument 5!
Finishing square with argument 5!
Finishing cube with argument 5!
>>> result
125
```

Great! But how does one use this to execute coroutines concurrently? For this
asyncio provides an `asyncio.gather` coroutine function. This special
coroutine function takes any number of coroutine objects as arugments, and
tells the event loop to execute them all concurrently. When all of the
coroutines have finished running, it returns all their results in a list.
Here goes:

```
$ python -i example.py
>>> loop = asyncio.get_event_loop()
>>> coro = asyncio.gather(cube(3), cube(4), cube(5))
>>> results = loop.run_until_complete(coro)
Starting cube with argument 4!
Starting cube with argument 3!
Starting cube with argument 5!
Starting square with argument 4!
Starting square with argument 3!
Starting square with argument 5!
Finishing square with argument 4!
Finishing cube with argument 4!
Finishing square with argument 3!
Finishing cube with argument 3!
Finishing square with argument 5!
Finishing cube with argument 5!
>>> results
[27, 64, 125]
```

Notice that the order in which the coroutines are run is not deterministic. You
can try running this example again and see that it may or may not occur in
a different order. However, the list of results is returned in the order
in which the coroutine objects were given to `asyncio.gather` as arguments.

### Schedulers, Schedulers, Schedulers

A brief mention of twisted, curio, trio, uvloop

### A Bit More New Syntax

Before progressing to the next section, where the real fun will begin with
actual concurrent IO over an actual network, there is a bit more coroutine
syntax to understand.

First, consider a basic python for loop:

```python
for item in container:
    do_stuff(item)
    do_more_stuff(item)
```

In this example, the object `container` could be a lot of things. It could
be a list, a dict, a generator, or even a string. You can define your own
classes to adhere to the simple python
[iterator protocol](https://docs.python.org/3/library/stdtypes.html#iterator-types)
which can then be iterated over in for loops. The way this works is that a
special `__iter__` method is called on the container to provide an iterator
object, and then at the top of each pass through the loop, a special
`__next__` method is called on the iterator which returns a value to be
assigned to `item`. The point here is that this `__next__` method is a
regular function - not a coroutine function.

So imagine that we had a special `container` class that did not store its
data locally. Instead, in order to fetch each item with `__next__` it had to
make a network connection and get it from a remote database. This would
be bad to do in a coroutine, as it is a regular function, and a regular
function cannot yield control to the scheduler to run other coroutines
while we are waiting for this item to be fetched.

The solution to this problem is an
[async for](https://docs.python.org/3/reference/compound_stmts.html#async-for)
statement, which works much like a for statement, except that it calls slightly
different special methods on the container which should result in a
coroutine object that is awaited on to return the item used for each pass of
the loop. Basically, this means that while the async for loop is doing
its business to fetch the item from some remote database, it can yield
back to the scheduler in order to allow other coroutines to run.


```python
async for item in remote_container:  # Here we might yield to the scheduler!
    do_stuff(item)
    do_more_stuff(item)
```

The last new important piece of syntax involves
[context managers](https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers)
and the `with` statement. Consider an example of a hypothetical key-value
database that uses a context manager to handle connections. To set a
key in the database, your statement might look like this:

```python
with database.connect('proto://db.somedomain.net') as db:
    db.set_key('cow', 'Moo!')
```

What is going on behind the scenes is that the `database.connect` call returns
a context manager, and the interpreter calls a special `__enter__` method
that sets up the database connection (this involves waiting on the network)
and returns an object that is assigned to `db` for us to use inside the with
block to talk to the database.

Then when the with block is completed, or even if it does not complete
due to an exception, the context manager special `__exit__` method is called
which can close the connection and perform any needed cleanup (more waiting
on the network!).

Unfortunately, if one was to use such a `with` statement in a coroutine
that needed to make network connections on its enter and exit, the functions
for entering and exiting would be unable to yield control back to the
scheduler and allow other coroutines to run while waiting on the connection
setup or teardown.

To solve this, there is an `async with` statement which expects an
asynchronous context manager that provides coroutines on enter and exit that
are awaited on before entering or exiting the `async with` block. This allows
a coroutine containing the `async with` statement to yeild control to the
scheduler during this setup and allowing for other coroutines to run.
An example might look like this:

```python
async with database.connect('proto://db.somedomain.net') as db:
    await db.set_key('cow', 'Moo!')
```

Here the coroutine is able to yeild to the scheduler when the network
connection is being set up, when the data for the new key is being sent to
the database, and when it cleans up.

### One Last Word on Awaiting
