# Cooking with Concurrency

Working with coroutines is a lot like using recipes in cooking, so to explain
what concurrency is, here are a few simple recipes that I use to make a
quick dinner for the family after work:

### Salmon filets with orange-ginger dressing

<table><tr>
<td><image src="media/salmon.jpg" alt="salmon filets and dressing" /></td>
<td>
    <ul>
        <li>Preheat oven to 350 degrees F</li>
        <li>Arrange salmon filets on cooking sheet</li>
        <li>Slather each filet with 2 tbsp. of orange-ginger dressing</li>
        <li>Bake salmon in oven for 18 minutes</li>
    </ul>
</td>
</tr></table>

### Rice pilaf from a box

<table><tr>
<td><image src="media/rice.jpg" alt="box of rice pilaf" /></td>
<td>
    <ul>
        <li>Put 1 3/4 cup of water and 2 tbsp. butter in 2 qt pot</li>
        <li>Bring pot to a boil</li>
        <li>Stir in spice package and rice pilaf, cover, set to low</li>
        <li>Let simmer for 20-25 minutes</li>
        <li>Fluff, let stand for 5 minutes</li>
    </ul>
</td>
</tr></table>

### Steam in bag green beans

<table><tr>
<td><image src="media/beans.jpg" alt="steam in bag green beans" /></td>
<td>
    <ul>
        <li>Poke holes in bag, put on microwave-safe plate</li>
        <li>Microwave for 5 minutes</li>
    </ul>
</td>
</tr></table>

### Dinner!

![Salmon Dinner](media/dinner.jpg "Salmon Dinner!")

This whole dinner takes about 30 minutes to make. Most of that time is spent
just waiting for things to finish, and when I get one recipe into a state
where I am waiting on the oven to heat up, or water to boil, I switch to
another recipe and work on that for a while. Note that I never actually
do two things at the same time. I am only ever engaged in one thing at a
time, but I can handle multiple recipes going on at the same time.

With that in mind, here are some definitions:

* **Parallelism**: Doing multiple things at the same time.
* **Concurrency**: Dealing with multiple things going on at the same time.

Cooking this simple meal for the family in just 30 minutes requires me to
use concurrency. I have to deal with multiple recipes being executed
at the same time, i.e. *concurrently*. If I was only capable of working
on a single recipe at a time, the dinner would take over an hour to prepare.

If I had a recipe that contained a lot of actual work, perhaps chopping
lots of different vegetables, then the speed at which I could finish the
dinner would be limited by my ability to only do one thing at a time. I
could in this case get a family member to help me, so that we would
both be chopping at the same time - and this would be an example of
*parallelism*.

## Dinner in Python

Now reimagine this dinner as a python module:

```python
from time import sleep

from kitchen import (
    oven, stovetop, microwave,
    pot, baking_sheet, plate,
    salmon, orange_dressing, rice_box, water, butter, green_beans
)

def cook_salmon():
    oven.preheat(350)
    baking_sheet.place(salmon)
    for filet in salmon:
        filet.slater(ginger_dressing, amount=2)
    oven.insert(baking_sheet)
    sleep(18 * 60)
    return oven.extract_all()

def cook_rice():
    pot.insert(water, amount=1.75)
    pot.inster(butter, amount=2)
    stovetop.add(pot)
    stovetop.set_burner(5)
    pot.wait_for_boil()
    pot.insert(box_rice)
    sleep(22*60)
    stovetop.set_burner(0)
    pot.fluff_contents()
    sleep(5*60)
    return pot.extract_all()

def cook_beans():
    grean_beans.poke()
    microwave.insert(green_beans)
    microwave.cook(5*60, power=10)
    return microwave.extract_all()

def make_salmon_dinner():
    meat = cook_fish()
    starch = cook_rice()
    veggie = cook_beans()

    return (meat, starch, veggie)
```

The nice thing about this module is that the code is structured for reuse.
If I wanted to make a similar dinner with chicken I could use the
`cook_beans` and `cook_rice` functions, and only have to add another
function to cook the chicken.

Unfortunately, this will not execute concurrently. The `make_salmon_dinner`
function will first call `cook_salmon` and wait for that to complete before
moving on to `cook_rice`. That is a lot of wasted time!

What I want is to execute all the recipes like a human would execute them.
When the `cook_fish` function got to a place where it was simply waiting on
the oven or sleeping, it would somehow release control and allow
`cook_rice` to execute for a while, and then somehow come back to `cook_fish`
where it left off.

But this is not how functions work. A python function is called, executes, and
then returns. You cannot just stop it in the middle and come back to it later.
This is where python coroutines come in. As we will see in the next few
sections, a coroutine is executed by a special scheduler and has the ability
to release control back to the scheduler, and then continue where it left off.
If `cook_fish`, `cook_beans`, and `cook_rice` were coroutines rather than
functions, we could tell a scheduler to run them all concurrently and get
the dinner done in a reasonable amount of time.

While some applications require a lot of actual work to be done by the CPU,
and therefore need parallelism to be executed more quickly, many others
spend a lot of time waiting on network IO to complete. These sort of
applications are very much like cooking dinner. There is lots of waiting
around, and structuring the work with coroutines allows one to execute
it all concurrently while preserving the modularity that you get by splitting
the task into functions. 

## More Gratuitous Cooking Metaphors

There are a number of concepts and approaches to concurrency and parallelism,
and to some degree they can all be described through various cooking
metaphors. While this tutorial is really just focused on coroutines, it is
worth at least mentioning some of the major ones.

### Callbacks

If you have ever programmed in Javascript, you have likely encountered
callbacks. Callbacks allow a scheduler (the cook) to execute some instructions
after something occurs. For example, we could attach a callback function
to the event that the oven is done preheating. Once this is done, the
specified callback would be executed. The `cook_salmon` recipe could be
broken up to use callbacks as follows:

```python
def cook_salmon():
    oven.preheat(350, callback=cook_salmon_cb1)
    return

def cook_salmon_cb1():
    baking_sheet.place(salmon)
    for filet in salmon:
        filet.slater(ginger_dressing, amount=2)
    oven.insert(baking_sheet)
    set_callback_timer(18 * 60, callback=cook_salmon_cb2)
    return

def cook_salmon_cb2():
    return oven.extract_all()
```

Here, each function returns when there is a waiting period, and the scheduler
will just call the next function in the chain when the callback condition
is satisfied. In the meantime, other work can get done. We could call
`cook_salmon()` which would get the oven going and immediately return. Then
we can call the next function for another recipe.

The annoying thing about this is that the recipe was broken into a
bunch of small functions and so it is harder to read. In other languages
it is a somewhat common practice to define the callback function where it
is passed as an argument as an anonymous function (lambda). This is generally
not possible in python as anonymous functions are restricted, but if you could
do it, then it might look like this:


```python
def cook_salmon():
    oven.preheat(350, callback=lambda : (
        baking_sheet.place(salmon)
        for filet in salmon:
            filet.slater(ginger_dressing, amount=2)
        oven.insert(baking_sheet)
        set_callback_timer(18 * 60, callback=lambda: (
            return oven.extract_all()
        )
    )
```

If there is a long chain of callbacks, then you can get a sort of cascading
pattern of anonymous functions, sometimes referred to as "callback hell".
This is also harder to read than a simple function.

### Coroutines

A coroutine executes like a function, except it has places where it will
yield control back to a scheduler when it is waiting on something, such as
the oven heating up. When it yields, the scheduler (cook) is free to run
another coroutine concurrently, and when that one yields it can continue
to the first.

Here is the `cook_salmon` recipe as a python coroutine:

```python
async def cook_salmon():
    await oven.preheat(350)
    baking_sheet.place(salmon)
    for filet in salmon:
        filet.slater(ginger_dressing, amount=2)
    oven.insert(baking_sheet)
    await asyncio.sleep(18 * 60)
    return oven.extract_all()
```

This is very nice as it looks much like a normal function, you can easily
see how the recipe progresses. When it gets to a special `await` expression,
it will yield control back to the scheduler to allow other recipes to run
while the oven heats or the salmon bakes. How exactly this works will be
described in detail in the next section.

### Threads

Threads offer a way to run multiple functions concurrently without even
changing the functions. A thread a separate unit of execution known to the
operating system kernel, which will schedule each thread to run without
you having to do anything. Python has a nice `threading` module in the
standard library that makes this easy:

```python
import threading

salmon_thread = threading.Thread(target=cook_salmon)
rice_thread = threading.Thread(target=cook_rice)
beans_thread = threading.Thread(target=cook_beans)

salmon_thread.start()
rice_thread.start()
beans_thread.start()

salmon_thread.join()
rice_thread.join()
beans_thread.join()
```

The call to `start()` will make each thread get scheduled for execution,
and the `join()` will wait until the thread is done. So in this case all three
recipes will run concurrently, and the code block will end once they are all
finished. Unfortunately this will not return your dinner to you, the return
value of the function called in the thread is lost, so the garbage collector
will eat your dinner. To keep your dinner, you would need to rewrite the
functions to put the dinner somewhere safe and shared, like a
[Queue](https://docs.python.org/3.6/library/queue.html) object.

The key thing that must be mentioned here is that threads are a form of
preemptive multitasking. This means that the operating system kernel
does not care exactly what you are doing in one thread, when it decides
to switch to a different thread. You might be right in the middle of
putting dressing on the salmon when the OS yells at you to get back to
work on the beans. When writing functions to be executed as threads, you
have no control over when the system switches between threads.

Additionally, threads generally share resources. This means that if one
thread is preheating the oven to 350, the OS could switch you to another
that wants to preheat the oven to 425. The only way to avoid anarchy in the
kitchen is to construct objects like
[Semaphores](https://docs.python.org/2/library/threading.html#semaphore-objects)
to control which thread is allowed to use the oven at any given time, forcing
threads to wait until others are done using the oven.

Finally, threads can in principle result in true parallelism. This means that
if your system has multiple CPU cores, the OS kernel can schedule multiple
threads to literally run at the same time. This is useful not just to avoid
IO waits, but to get additional computational work done. In python, however,
there is a Global Interpreter Lock (GIL) that prevents more than one thread
from executing python instructions at the same time. There are ways that
computational libraries like `numpy` avoid this restriction by releasing
the GIL and performing computation with C-extensions, but that is the
subject of a different tutorial.

### Multiprocessing

Python also has a nice
[multiprocessing](https://docs.python.org/3.6/library/multiprocessing.html)
module to allow running functions in entirely separate processes, each
with their own interpreter. This means that there is no GIL restriction,
and multiple functions may be executed in parallel if there are multiple
CPU cores available. It also means that no resources or memory are shared
unless explicit constructs are used to communicate between processes.

Think of this as running each recipe in its own kitchen. You have one
kitchen for the salmon, one for the rice, and one for the beans. If one
recipe was to call for the oven to be set to 350, and another to 425, then
it does not matter. Unless an oven was deliberately set as a shared
resource between the processes, then each kitchen has its own completely
separate oven.

Much like in the kitchen metaphor, in reality multiprocessing is more
expensive in terms of memory usage, as each process gets a complete
python interpreter and a copy of the full program in its own private
memory allocation.
