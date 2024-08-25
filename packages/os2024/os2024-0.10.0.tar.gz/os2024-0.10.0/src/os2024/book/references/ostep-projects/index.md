# Projects

This repository holds a number of projects that can be used in an operating systems class aimed at upper-level undergraduates and (in some cases) beginning graduate students. They are based on years of teaching such a course at the University of Wisconsin-Madison.

Also (increasingly) available are some tests to see if your code works; eventually every project will have a set of tests available. The testing framework that is currently available is found [here](https://github.com/remzi-arpacidusseau/ostep-projects/tree/master/tester). A specific testing script, found in each project directory, can be used to run the tests against your code.

For example, in the initial utilities project, the relatively simple `hcat` program that you create can be tested by running the `test-hcat.sh` script. This could be accomplished by the following commands:

```shell
prompt> git clone https://github.com/remzi-arpacidusseau/ostep-projects
prompt> cd ostep-projects/initial-utilities/hcat
prompt> emacs -nw hcat.c
prompt> gcc -o hcat hcat.c -Wall
prompt> ./test-hcat.sh
test 1: passed
test 2: passed
test 3: passed
test 4: passed
test 5: passed
test 6: passed
test 7: passed
prompt>
```

Of course, this sequence assumes (a) you use `emacs` (you should!), (b) your code is written in one shot (impressive!), and (c) that it works perfectly (well done!). Even for simple assignments, it is likely that the compile/run/debug cycle might take a few iterations.

## C/Linux Projects

### Initial Projects

These projects are meant to get you warmed up with programming in the C/UNIX environment. None are meant to be particularly hard, but should be enough so that you can get more comfortable programming.

Realize the best thing you can do to learn to program in any environment is to program **a lot**. These small projects are only the beginning of that journey; you'll have to do more on your own to truly become proficient.

- [Unix Utilities](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/initial-utilities) (cat, grep, zip/unzip)
- Sort (text-based)
- Sort (binary)
- [Reverse](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/initial-reverse) (very simple reverse program)

### Processes and Scheduling

- [Shell](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/processes-shell)

### Virtual Memory

- Memory Allocator

### Concurrency

- [Web Server](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/concurrency-webserver)
- [Parallel Zip](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/concurrency-pzip)
- [MapReduce](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/concurrency-mapreduce)
- Web Crawler

### File Systems

- [File System Checker](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/filesystems-checker)

### Distributed Systems

## Kernel Hacking Projects (xv6)

These projects all are to be done inside the [xv6](https://pdos.csail.mit.edu/6.828/2017/xv6.html) kernel based on an early version of Unix and developed at MIT. Unlike the C/Linux projects, these give you direct experience inside a real, working operating system (albeit a simple one).

Read the [install notes](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/INSTALL-xv6.md) to see how to download the latest xv6 and install the tools you'll need.

### Initial Projects

- [Intro To xv6](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/initial-xv6)

### Processes and Scheduling

- [Scheduling (Lottery)](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/scheduling-xv6-lottery)

### Virtual Memory

- [Virtual Memory (Null Pointer and Read-Only Regions)](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/vm-xv6-intro)

### Concurrency

- [Kernel Threads (Basic Implementation)](https://github.com/remzi-arpacidusseau/ostep-projects/blob/master/concurrency-xv6-threads)

### File Systems
