<div style="text-align: center;">

![callstack logo](./assets/logo_text.png)

‎

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/atriace)

</div>

# callstack


A Python module designed to address shortcomings in the standard Python stack inspection tools like `sys`, `inspect`, and `traceback`. Despite their utility, they do not provide the **name of the class** where a function originates, nor do they offer an easily digestable list of variables.

For comparison, here is a `frame` object from `sys` versus `callstack`...

### sys

```python
frame = {
    "f_back_": (frame),
    "f_builtins_": {dict: 153 entries}
    "f_code_": {
        "co_argcount" = (int),
        "co_cellvars" = (tuple),
        "co_code" = (bytes),
        "co_consts" = (tuple),
        "co_filename" =  'tests\callstack_test.py' (string),
        "co_firstlineno" = (int),
        "co_flags" = (int),
        "co_freevars" = (tuple: 0),
        "co_kwonlyargcount" = (int),
        "co_lnotab" = (bytes: 34),
        "co_name" = (string) 'hello',
        "co_names" = (tuple: 17)
        "co_nlocals" = (int)
        "co_posonlyargcount" = (int)
        "co_stacksize" = (int)
    },
    "f_globals_": {
        "__name__": (str) 'hello',
        "__doc__": (NoneType),
        "__package__": (str) 'tests',
        "__loader__": (SourceFileLoader),
        "__spec__": (NoneType),
        "__file__": (str),
        "_builtins_": (module),
        "_pydev_stop_at_break": (function),
        "callstack": (module),
        "__len__": (int)
    },
    "f_lasti": (int),
    "f_lineno": 47 (int),
    "f_locals_": {dict: 15 entries},
    "f_trace_": (NoneType),
    "f_trace_lines": (bool),
    "f_trace_opcodes": (bool),
    "__len__": (int)
}
```

Where do we find the properties we're looking for?

- path = `frame.f_code_["co_filename"]`
- package = `frame.f_globals_["__package__"]`
- module = *available, if you parse the filename*
- line = `frame.f_lineno`
- class = *completely missing*
- function = `frame.f_code_["co_name"]`

Obviously, there's a lot more data here that you could tap into (168 entries are hidden), but the variable locations are all over the place, and have fairly obtuse names.

### callstack

```python
frame = { 
    "path": 'tests\callstack_test.py' (string),     # The file path of the code in the frame.
    "package": 'tests' (string),                    # The package that contains the module.
    "module": 'callstack_test' (string),            # The module name.
    "line": 47 (int),                               # The line number in the source code.
    "cls": 'TestClass' (string),                    # The class name, if available.
    "function": 'hello' (string)                    # The name of the function
}
```

> **Note:**
> 
> Unlike other languages, Python's interpreter can't differentiate between `class` as a keyword versus a property. This deficiency in parsing a class declaration versus a variable definition necessitates using `cls` instead of `class`.

How is this done? `callstack` uses `sys` to pull in the 4 aforementioned available properties. We then parse the module name from the filename, but the real issue is the *class name*.
1. Every path in the `sys` callstack is parsed as text files.
2. Line numbers are attributed to the class they belong to, and saved for future reference.
3. On any given frame, we can query our dictionary by filepath & line number to return the matching class name.

If you have a large codebase and are concerned about the overhead, this currently happens **on demand at runtime** and will only scan files that are in the callstack (so the impact should be negligible).
However, **if you want to pre-scan your code** you may call `callstack.parseFile(filepath)` which will generate & cache the necessary lookup table per file.

# Methods

## get()
Accepts no arguments, and returns the callstack as a `list` of `Frames`.
You can easily access individual frames by index (bypassing the need to use a `while` loop, or traversing via `frame.f_back`).

*Example:*

```python
import callstack

class Alpha:
    def test():
        stack = callstack.get()
        print(f"Call stack has {len(stack)} entries...")
        
        for frame in stack:
            print(f"   {frame.cls}.{frame.function}():{frame.line}")
            
        print(f"\nStarted with {stack[0].cls} and ended with {stack[-1].cls}")

class Beta:
    def test():
        Alpha.test()
        
Beta.test()

# Call stack has 3 entries...
#   Alpha.test():5
#   Beta.test():13
#   <module>.__main__():15
#   
# Started with Alpha and ended with <module>
```


## getOrigin()
Accepts no arguments, and returns a Frame object representing the origin of the call, one level up the stack from where `getOrigin()` is called.  It provides a lightweight, lower-overhead way of retrieving this particular frame compared to `get()`.

*Example:*

```python
import callstack

class Alpha:
    def test():
        origin = callstack.getOrigin()
        print(f"test() called from {origin.cls}.{origin.function}():{origin.line}")
        
    def sibling():
        Alpha.test()

Alpha.test()
Alpha.sibling()

# test() called from <module>.__main__():11
# test() called from Alpha.sibling():9
```

## parseFile(*path*)
Accepts a string *path* (relative or absolute), and parses Python modules as text files.  It stores the matchup of line-ranges to class names in our internal cache, returning nothing.

*Example:*

```python
import callstack
callstack.parseFile("directory/path/to/module.py")
```

## getClassName(*path*, *linenumber*)
Accepts a *path* & matching *linenumber*, and returns a string name of the relavent class name.  This function is useful if you still use `sys` (or some other stack inspection tools that provide more data not provided here), but still need the name of the *class*.

Be aware that **if** the file hasn't already been parsed, it will be parsed when using this function.

*Example:*

```python
import callstack
cls = callstack.getClassName("directory/path/to/module.py", 76)
```