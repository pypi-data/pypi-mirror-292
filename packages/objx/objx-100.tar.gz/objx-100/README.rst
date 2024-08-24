NAME

::

    OBJX - objects


SYNOPSIS

::

    objx  <cmd> [key=val] [key==val]


INSTALL

::

    $ pipx install objx
    $ pipx ensurepath


DESCRIPTION

::

    OBJX contains all the python3 code to program objects in a functional
    way. It provides a base Object class that has only dunder methods, all
    methods are factored out into functions with the objects as the first
    argument. It is called Object Programming (OP), OOP without the
    oriented.

    OBJX  allows for easy json save//load to/from disk of objects. It
    provides an "clean namespace" Object class that only has dunder
    methods, so the namespace is not cluttered with method names. This
    makes storing and reading to/from json possible.

    OBJX has all you need to program a unix cli program, such as disk
    perisistence for configuration files, event handler to handle the
    client/server connection, code to introspect modules for
    commands, deferred exception handling to not crash on an error, a
    parser to parse commandline options and values, etc.

    OBJX is Public Domain.


USAGE

::

    without any argument the program does nothing

    $ objx
    $

    see list of commands

    $ objx cmd
    cmd,err,mod,req,thr,ver

    list of modules

    $ objx mod
    cmd,err,fnd,irc,log,mod,req,rss,tdo,thr

    use -c to start a console

    $ objx -c
    >


COMMANDS

::

    cmd - commands
    fnd - find objects 
    log - log some text
    tdo - add todo


FILES

::

    ~/.objx
    ~/.local/bin/objx
    ~/.local/pipx/venvs/objx/

AUTHOR

::

    Bart Thate <rssbotd@gmail.com>

COPYRIGHT

::

    OBJX is Public Domain.
