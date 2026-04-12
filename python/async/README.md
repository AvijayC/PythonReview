# Python: Async Basics

This lesson directory is intentionally code-light.

The goal here is to build a clean mental model for Python async while you follow an outside tutorial and write the code yourself.

## Lesson Goals

- understand what problem async is trying to solve
- distinguish concurrency from parallelism at a practical level
- understand the roles of `async`, `await`, coroutines, tasks, and the event loop
- learn when async helps and when it adds unnecessary complexity
- be able to explain what your own async code is doing step by step

## Core Ideas To Lock In

### 1. Async Is About Cooperative Waiting

Async is most useful when a program spends time waiting on external work such as network responses, timers, streams, or other I/O. Instead of blocking the whole program during that wait, control can return to the event loop so some other pending work can move forward.

### 2. `async def` Does Not Mean "Runs In Parallel"

An `async def` function defines a coroutine function. Calling it does not immediately do the work in the same way a normal function call does. It creates a coroutine object that must later be awaited or scheduled.

### 3. `await` Means "Pause Here And Let Something Else Run"

When execution reaches `await`, the current coroutine yields control until the awaited operation is ready. That pause is the core behavior that makes async useful for I/O-heavy programs.

### 4. The Event Loop Orchestrates Everything

The event loop is the runtime coordinator. It tracks pending coroutines and tasks, resumes them when awaited work is ready, and keeps the program moving.

### 5. Tasks Let Coroutines Progress Independently

A task wraps coroutine execution so it can be scheduled and allowed to make progress without being awaited immediately at the exact moment it is created.

### 6. Async Does Not Automatically Speed Up CPU-Bound Work

If the program is spending time on heavy computation rather than waiting on I/O, async usually does not solve the bottleneck. That is where processes, threads, native extensions, or algorithmic improvements are more relevant.

## Questions To Keep Asking While Following The Tutorial

- what exactly is waiting here
- what owns the event loop in this example
- is this coroutine merely defined, or is it actually being awaited or scheduled
- if several operations are started, are they truly concurrent or just sequential with async syntax
- would normal synchronous code be simpler for this case
- is this example I/O-bound or CPU-bound

## Common Confusions To Watch For

- thinking `async def` immediately executes the body
- assuming `await` means "run this in the background"
- treating concurrency and parallelism as the same thing
- expecting async to improve CPU-heavy loops
- forgetting that blocking calls inside async code can stall the whole event loop

## Self-Check Prompts

Use these after each tutorial segment:

1. Define coroutine, task, and event loop in your own words.
2. Explain what changes when a normal function becomes an async function.
3. Describe what the program is doing at each `await` point.
4. Explain whether a given example is sequential, concurrent, or parallel.
5. Identify the real source of waiting in the example you just watched.
6. State whether async is justified for that example or just educational.

## Working Rule For This Lesson

- do not keep prewritten solution code in this directory before you need it
- keep explanations and checkpoints here, but write implementation code yourself
- use the `autolessons` log to track quiz attempts, confusions, and corrections

## Suggested Next Step

Follow the tutorial normally, but pause whenever a new async keyword or concept appears and explain it back in plain English before you keep going.
