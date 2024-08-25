# -*- coding: utf-8 -*-
"""
A testing library intended to support automatic exercise feedback for 
students in an intro to programming course. Includes capabilities for
mocking input and setting up checks for the results and/or printed output
of arbitrary expressions. Also includes:

- Basic AST checking tools. These are good for making sure students solve
    an exercise using particular concepts, but make sure to describe the
    requirements so that students aren't confused by why their code that
    "works" doesn't pass the checks.
- Doctest-checking tools, so that you can require students to write
    diverse working doctests, and you can check them against a solution
    (which is easiest to do on some separate server so as not to give
    away the answers).
- [PLANNED] A reverse tracing feature where comments specifying the
    evolution of program state can be checked.

## Example usage

### Basic test cases

See `examples/basic.py` for an extended example file showing basic usage
of core functions. Here is a very short example:

>>> import optimism
>>> optimism.messagesAsErrors(False)
>>> optimism.colors(False)
>>> def f(x, y):
...     "Example function"
...     return x + y + 1
...
>>> # Simple test for that function
>>> tester = optimism.testFunction(f)
>>> case = tester.case(1, 2)
>>> case.checkReturnValue(4) # doctest: +ELLIPSIS
✓ ...
True
>>> case.checkReturnValue(5) # doctest: +ELLIPSIS
✗ ...
  Result:
    4
  was NOT equivalent to the expected value:
    5
  Called function 'f' with arguments:
    x = 1
    y = 2
False

For code in files, the filename and line number are shown instead of
stdin:1 as shown above. Note that line numbers reported for function
calls that span multiple lines may be different between Python versions
before 3.8 and versions 3.8+.


### Code Structure Checking

The `examples/code.py` file has a longer example of how to use the
AST-checking mechanisms for checking code structures. Here is a simple
one:

>>> import optimism
>>> def askNameAge():
...     "A function that uses input."
...     name = input("What is your name? ")
...     age = input("How old are you? ")
...     return (name, age)
...
>>> tester = optimism.testFunction(askNameAge)
>>> tester.checkCodeContains(optimism.Call('input')) # doctest: +ELLIPSIS
✓ ...
True
>>> tester.checkCodeContains(optimism.Loop()) # doctest: +ELLIPSIS
✗ ...
  Code does not contain the expected structure:
    at least 1 loop(s) or generator expression(s)
  checked code of function 'askNameAge'
False

The `TestManager.checkCodeContains` function and the various
code-structure classes (see `ASTRequirement`) can be used to ensure that
the Abstract Syntax Tree (AST) of the code associated with a test manager
has certain structures.


### Reverse Tracing [PLANNED]

Note: This functionality is planned, but not implemented yet.

The `examples/reverse_tracing.py` file contains more thorough examples of
this functionality. Here is a simple one:

>>> import optimism
>>> code = '''\\
... x = 5
... ## x = 5
... y = x + 3
... ## y=8
... print(x, '\\\\n', y)
... ## prints:
... ## '5 '
... ## ' 8'
... x, y = y, x
... ## x = 8, y = 5
... z = x + y
... # this last trace assertion is incorrect
... ## z = 14
... '''
>>> tester = optimism.testBlock(code)
>>> tester.validateTrace() # doctest: +SKIP +ELLIPSIS
✗ ...
  Trace assertions were not completely valid:
    First failing assertion was on line 13:
      z = 14
    The actual value of z was:
      13
False
>>> functionBlock = '''\\
... def f(x, y):
...     #: x = 3, y = 4
...     x += 1
...     ## x = 4
...     return x + y
...     ## returns: 8
...
... # These trace blocks replay the most-recently defined trace suite ('#:')
... # using different initial values.
... #> x = 1, y = 1
... ## x = 2
... ## returns: 3
...
... #> x=2, y=2
... ## x=3
... ## returns: 5
... '''
>>> tester2 = optimism.testBlock(functionBlock)
>>> tester2.validateTrace() # doctest: +SKIP +ELLIPSIS
✓ ...
True


## Core functionality

The main functions you'll need are:

- `trace` works like `print`, but shows some extra information, and you
  can use it as part of a larger expression since it returns the value
  it gets as an argument. It only accepts a single argument though. Use
  this for figuring out what's going wrong when your tests don't pass.
- `expect` takes two arguments and prints a check-mark if they're
  equivalent or an x if not. If they aren't equivalent, it prints
  details about values that are part of the first expression. Use this
  for expectations-based debugging.
- `expectType` works like `expect`, but the second argument is a type,
  and it checks whether the value of the first argument is an instance
  of that type or not. For more serious type-checking without having to
  run your program and without slowing it down when it does run, use MyPy
  or another actual type-checking system.
- `testFunction` establishes a test manager object, which can be used to
  create test cases. When you call `testFunction` you specify the
  function that you want to test. The `.case` method of the resulting
  `TestManager` object can be used to set up individual test cases. The
  `.checkCodeContains` method can be used to check for certain structural
  properties of the code of the function.
- `testFile` establishes a test manager object just like `testFunction`,
  but for running an entire file instead of for calling a single
  function.
- `testBlock` establishes a test manager object just like `testFunction`,
  but for running a block of code (given as a string).
- The `TestManager.case` method establishes a test case by specifying
  what arguments are going to be used with the associated function. It
  returns a `TestCase` object that can be used to establish
  expectations. For test managers based on files or blocks, no arguments
  are needed.
- The `TestCase.checkReturnValue`, `TestCase.checkVariableValue`,
  `TestCase.checkPrintedLines`, and/or `TestCase.checkCustom` methods can
  be used to run checks for the return value and/or printed output and/or
  variables defined by a test case.
- Normally, output printed during tests is hidden, but `showPrintedLines`
  can be used to show the text that's being captured instead.
- `TestCase.provideInputs` sets up inputs for a test case, so that
  interactive code can be tested without pausing for real user input.
- The `TestManager.checkCodeContains` method can be used to check the
  abstract syntax tree of of the function, file or block associated with
  a test manager. The argument must be an instance of the
  `ASTRequirement` class, which has multiple sub-classes for checking for
  the presence of various different code constructs.
- The `TestManager.validateTrace` method can be used to check trace
  assertion comments within the code of a function, file, or code block.
  **TODO: This function is not implemented yet.**
- `detailLevel` can be called to control the level of detail printed in
  the output. It affects all tracing, expectation, and testing output
  produced until it gets called again.
- `showSummary` can be used to summarize the number of checks which
  passed or failed.
- `colors` can be used to enable or disable color codes for printed text.
  Disable this if you're getting garbled printed output.

TODO: Workaround for tracing in interactive console?

## Changelog

- Version 3.1 adds doctest-management functionality, and updates the
  module docstring to better describe the revised project aims.
  Specifically `TestManager` instances now have methods `getDocstring`,
  `getDocTests`, `checkHasDocstring`, `checkDocTestsPass`, and
  `checkDocTestCount`, most of which are implemented by calling out to a
  new `DocChecks` instance.
- Version 3.0 adds type hints to the file, and as a result is less
  accessible to novices but has more clarity on the structure of
  various data types. It also adds scopes to function case results,
  using the global scope for the function that was run, and instead of
  having a 'skipped' key for outcome dictionaries of skipped checks, it
  uses a new `Skipped` object as the 'result' value.
- Version 2.9.1 fixes pluralization of missing items reports in
  `yieldMemoryReportDifferences`. It also adds a monkey-patch to
  asyncio.base_events which attempts to work around the "error ignored"
  messages that are happening in Jupyter notebooks. Replacing that with
  an actual fix for whatever the underlying problem is should be a
  priority.
- Version 2.9.0 upgrades `memoryReport` with the ability to report on
  multiple objects at once and to have named variables/references.
  It also adds `yieldMemoryReportDifferences` for memory reports that
  can show differences between reports while still handling reports that
  use different numerical references. This upgrades
  `checkVariableStructure` and `checkReturnedStructure` to use
  `yieldMemoryReportDifferences`.
- Version 2.8.3 adds `showOverview` for summarizing results from all
  test suites.
- Version 2.8.2 fixes a bug that prevents matching of literals by type
  when their values cannot be computed from the code alone.
- Version 2.8.1 normalizes newlines in `checkFileLines`.
- Version 2.8.0 adds `memoryMap` and `memoryReport` functions for
  creating text-based memory diagrams of object references. It also adds
  `checkVariableStructure` and `checkReturnedStructure` functions for
  checking for expected memory report.
- Version 2.7.10 adds `Literal` class for matching literals, and
  `getLiteralValue` function for extracting well-defined literal values
  from an AST. It also changes the type= keyword argument for `Constant`
  to be `types=` to avoid the name clash with the built-in `type`
  function (`Literal` also uses `types=`).
- Version 2.7.9 fixes minor bugs from 2.7.7 and 2.7.8 (e.g., formatting).
  It also adds `Reference` for matching variable references.
- Version 2.7.8 adds the `type=` argument to `Constant` for finding
  constants w/ unconstrained values but particular type(s).
- Version 2.7.7 adds the `Operator` class for code checking.
- Version 2.7.6 monkey-patches the `input` function in addition to
  overriding `stdin` during payload runs, to try to deal with notebook
  environments better where `input` doesn't read from `stdin` by
  default. This may cause more problems with other input-capturing
  solutions that also mock `input`...
- Version 2.7.5 allows the code value for a function test manager to be
  `None` when the code for the function cannot be found using
  `inspect.getsource`, instead of letting the associated `OSError`
  bubble out.
- Version 2.7.4 flips this changelog right-side-up (i.e., newest-first).
  Also introduces the `code` slot for `TestManager` objects, so that
  they store raw code in addition to a derived syntax tree. This change
  also means that `BlockManager` objects no longer store their code in
  the `target` slot, which is now just a fixed string. It also changes
  `listAllCases` to `listAllTrials` and changes 'cases' to 'trials' in a
  few other places since code checks are not associated with test cases
  but are trials. Common functionality is moved to the `Trial` class.
- Version 2.7.3 introduces the `mark` function, and removes
  `testCodeWithSuite`, adding `testMarkedCode` instead. This helps
  prevent suites (previously required for marking code blocks) from being
  started when you need another suite to be active.
- Version 2.7.2 introduces `listOutcomesInSuite` and registers outcomes
  from `expect` and `expectType` calls. These will also be included in
  `showSummary` results. It renames `startTestSuite` to just `testSuite`,
  and introduces `freshTestSuite` which deletes any old results instead
  of extending them.
- Version 2.7.1 sets the `SKIP_ON_FAILURE` back to `None`, since default
  skipping is a potential issue for automated test reporting. It adds
  `SUPPRESS_ON_FAILURE` to compensate for this and enables it by default,
  suppressing error details from checks after one failure per manager. It
  also adds `checkVariableValue` for checking the values of variables set
  in files or code blocks (it does not work on function tests).
- Version 2.7 introduces the `ASTRequirement` class and subclasses, along
  with the `TestManager.checkCodeContains` method for applying them. It
  reorganizes things a bit so that `Trial` is now a super-class of both
  `TestCase` and the new `CodeChecks` class.
- Version 2.6.7 changes default SKIP_ON_FAILURE back to 'case', since
  'all' makes interactive testing hard, and dedicated test files can call
  skipChecksAfterFail at the top. Also fixes an issue where comparing
  printed output correctly is lenient about the presence or absence of a
  final newline, but comparing file contents didn't do that. This change
  means that extra blank lines (including lines with whitespace on them)
  are ignored when comparing strings and IGNORE_TRAILING_WHITESPACE is
  on, and even when IGNORE_TRAILING_WHITESPACE is off, the presence or
  absence of a final newline in a file or in printed output will be
  copied over to a multi-line expectation (since otherwise there's no way
  to specify the lack of a final newline when giving multiple string
  arguments to `checkPrintedLines` or `checkFileLines`).
- Version 2.6.6 changes from splitlines to split('\\n') in a few places
  because the latter is more robust to extra carriage returns. This
  changes how some error messages look and it means that in some places
  the newline at the end of a file actually counts as having a blank line
  there in terms of output (behavior is mostly unchanged). Also escaped
  carriage returns in displayed strings so they're more visible. From
  this version we do NOT support files that use just '\\r' as a newline
  as easily. But `IGNORE_TRAILING_WHITESPACE` will properly get rid of
  any extra '\\r' before a newline, so when that's on (the default) this
  shouldn't change much. A test of this behavior was added to the file
  test example.
- Version 2.6.5 fixes a bug with displaying filenames when a file does
  not exist and `checkFileLines` is used, and also sets the default
  length higher for printing first differing lines in
  `findFirstDifference` since those lines are displayed on their own line
  anyways. Fixes a bug where list differences were not displayed
  correctly, and improves the usefulness of first differences displayed
  for dictionaries w/ different lengths. Also fixes a bug where strings
  which were equivalent modulo trailing whitespace would not be treated
  as equivalent.
- Version 2.6.4 immediately changes `checkFileContainsLines` to
  `checkFileLines` to avoid confusion about whether we're checking
  against the whole file (we are).
- Version 2.6.3 introduces the `checkFileContainsLines` method, and also
  standardizes the difference-finding code and merges it with
  equality-checking code, removing `checkEquality` and introducing
  `findFirstDifference` instead (`compare`) remains but just calls
  `findFirstDifference` internally. Also fixes a bug w/ printing
  tracebacks for come checkers (need to standardize that!). Also adds
  global skip-on-failure and sets that as the default!
- Version 2.6.2 fixes a bug with dictionary comparison which caused a
  crash when key sets weren't equal. It also adds unit tests for the
  `compare` function.
- Version 2.4.0 adds a more object-oriented structure behind the scenes,
  without changing any core API functions. It also adds support for
  variable specifications in block tests.
- Version 2.3.0 adds `testFunctionMaybe` for skippable tests if the
  target function hasn't been defined yet.
- Version 2.2.0 changed the names of `checkResult` and `checkOutputLines`
  to `checkReturnValue` and `checkPrintedLines`
- Version 2.0 introduced the `TestManager` and `TestCase` classes, and
  got rid of automatic tracking for test cases. The old test case
  functionality was moved over to the `expect` function. This helps make
  tests more stable and makes meta-reasoning easier.
"""

# TODO: Cache compiled ASTs!

__version__ = "3.1"

from typing import (
    Any, Dict, List, Optional, Tuple, TypeAlias, Literal as LiteralType,
    Callable, TypedDict, cast, Iterable, Iterator, Protocol, TextIO,
    Union, Sequence, Type, TypeVar, Generic, Collection, Set, get_args
)
from types import NoneType, FunctionType, ModuleType, FrameType

import sys, traceback, inspect, linecache, ast, copy, io, os, re, types,\
       builtins, cmath, textwrap, warnings, functools, token, tokenize

import doctest
from typing import Callable, Any


# Flags for feature-detection on the ast module
HAS_WALRUS = hasattr(ast, "NamedExpr")
SPLIT_CONSTANTS = hasattr(ast, "Num")


#
try:
    from typing import Unpack
except ImportError:
    # We need to ignore "already defined by import" error here
    class Unpack:  # type: ignore
        """
        A fake stub for `typing.Unpack` on Python versions where that's
        not available; allows get-item just like `Unpack` but returns
        `Any` no matter what the index value is.
        """
        def __getitem__(self, _):
            return Any


#----------------#
# Monkey Patches #
#----------------# 

# This code monkey-patches the BaseEventLoop class in
# asyncio.base_events to avoid an attribute error when an attribute-less
# event loop is destroyed. I have no idea why this is happening, this is
# a workaround to prevent "error ignored" spam until I can figure out
# more. TODO: Figure out why we're getting attribute-less
# _UnixSelectorEventLoop objects and why they're being deleted. Does it
# have to do with deepish_copy, or is the association just a
# coincidence?

from asyncio import base_events  # noqa

destructor = base_events.BaseEventLoop.__del__  #type: ignore


def safeDestrutor(self, _warn=warnings.warn):
    # Regenerate _closed attribute if it's missing:
    self._closed = getattr(self, "_closed", True)
    # Proceed with deletion as normal:
    destructor(self, _warn)


base_events.BaseEventLoop.__del__ = safeDestrutor  # type: ignore


#---------#
# Globals #
#---------#

PRINT_TO: TextIO = sys.stderr
"""
Where to print messages. Defaults to `sys.stderr` but you could set it to
`sys.stdout` (or another open file object) instead.
"""

ALL_TRIALS: Dict[str, List["Trial"]] = {}
"""
All test cases and code checks that have been created, organized by
test-suite names. By default all trials are added to the 'default' test
suite, but this can be changed using `testSuite`. Each entry has a test
suite name as the key and a list of `Trial` (i.e., `CodeChecks` and/or
`TestCase`) objects as the value.
"""

Outcome: TypeAlias = Tuple[bool, str, str]
"""
An `Outcome` is a 3-tuple with a boolean followed by two strings. The
boolean indicates whether the outcome was a success (`True`) or failure
(`False`). The first string is a tag, indicating the file name and line
number where the outcome originated. The final string is a message
explaining the outcome.
"""

ALL_OUTCOMES: Dict[str, List[Outcome]] = {}
"""
The outcomes of all checks, including independent expectations (via
`expect` or `expectType`) and `Trial`-based expectations (via methods
like `TestManager.checkCodeContains`, `TestCase.checkReturnValue`, etc.).

These are stored per test suite as lists with the suite name (see
`_CURRENT_SUITE_NAME`) as the key. They are ordered in the order that
checks happen in, but may be cleared if `resetTestSuite` is called.

Each list entry is a 3-tuple with a boolean indicating success/failure, a
tag string indicating the file name and line number of the test, and a
string indicating the message that was displayed (which might have
depended on the current detail level or message suppression, etc.).
"""

_CURRENT_SUITE_NAME: str = "default"
"""
The name of the current test suite, which organizes newly-created test
cases within the `ALL_TRIALS` variable. Use `testSuite` to begin/resume a
new test suite, and `currentTestSuite` to retrieve the value.
"""

_MARKED_CODE_BLOCKS: Dict[str, Optional[str]] = {}
"""
A cache for notebook cells (or other code blocks) in which `mark` has
been called, for later retrieval in `testMarkedCode`. Keys are mark
names (arguments to `mark`) and values are strings containing the entire
contents of the marked cell/file/block.
"""

COMPLETED_PER_LINE: Dict[str, Dict[Tuple[str, int], int]] = {}
"""
A dictionary mapping function names to dictionaries mapping (filename,
line-number) pairs to counts. Each count represents the number of
functions of that name which have finished execution on the given line
of the given file already. This allows us to figure out which expression
belongs to which invocation if `get_my_context` is called multiple times
from the same line of code.
"""

LevelOfDetail: TypeAlias = LiteralType[-1, 0, 1]
"""
The available detail levels. See `detailLevel`.
"""

DETAIL_LEVEL: LevelOfDetail = 0
"""
The current detail level, which controls how verbose our messages are.
See `detailLevel`.
"""

SkipMode: TypeAlias = LiteralType[None, 'all', 'case', 'manager']
"""
The different modes we can use to skip checks when a check fails. See
`SKIP_ON_FAILURE`.
"""

SKIP_ON_FAILURE: SkipMode = None
"""
Controls which checks get skipped when a check fails. If set to `'all'`,
ALL checks will be skipped once one fails, until `clearFailure` is
called. If set to `'case'`, subsequent checks for the same test case will
be skipped when one fails. If set to `'manager'`, then all checks for any
case from a case manager will be skipped when any check for any case
derived from that manager fails. Any other value (including the default
`None`) will disable the skipping of checks based on failures.
"""

SUPPRESS_ON_FAILURE: LiteralType[None, 'all', 'case', 'manager'] = None
"""
Controls how failure messages are suppressed after a check fails. By
default, details from failures after the first failure for a given test
manager will printed as if the detail level were -1 as long as the
default level is 0. You can set this to `'case'` to only suppress details
on a per-case basis, or `'all'` to suppress all detail printing after any
failure. `clearFailure` can be used to reset the failure status, and
setting the base detail level above 1 will also undo the suppression.

Set this to `None` or any other value that's not one of the strings
mentioned above to disable this functionality.
"""

CHECK_FAILED: bool = False
"""
Remembers whether we've failed a check yet or not. If True and
`SKIP_ON_FAILURE` is set to `'all'`, all checks will be skipped, or if
`SUPPRESS_ON_FAILURE` is `'all'` and the detail level is 0, failure
details will be suppressed. Use `clearFailure` to reset this and resume
checking without changing `SKIP_ON_FAILURE` if you need to.
"""

COLORS: bool = True
"""
Whether to print ANSI color control sequences to color the printed output
or not.
"""

MessageCategory: TypeAlias = LiteralType[
    "succeeded",
    "skipped",
    "failed",
    "reset"
]

MSG_COLORS: Dict[MessageCategory, str] = {
    "succeeded": "34",  # blue
    "skipped": "33",  # yellow
    "failed": "1;31",  # bright red
    "reset": "0",  # resets color properties
}

IGNORE_TRAILING_WHITESPACE: bool = True
"""
Controls equality and inclusion tests on strings, including multiline
strings and strings within other data structures, causing them to ignore
trailing whitespace. True by default, since trailing whitespace is hard
to reason about because it's invisible.

Trailing whitespace is any sequence whitespace characters before a
newline character (which is the only thing we count as a line break,
meaning \\r\\n breaks are only accepted if IGNORE_TRAILING_WHITESPACE is
on). Specifically, we use the `rstrip` method after splitting on \\n.

Additionally, in multi-line scenarios, if there is a single extra line
containing just whitespace, that will be ignored, although that's not the
same as applying `rstrip` to the entire string, since if there are
multiple extra trailing newline characters, that still counts as a
difference.
"""

_SHOW_OUTPUT: bool = False
"""
Controls whether or not output printed during tests appears as normal or
is suppressed. Control this using the `showPrintedLines` function.
"""

FLOAT_REL_TOLERANCE: float = 1e-8
"""
The relative tolerance for floating-point similarity (see
`cmath.isclose`).
"""

FLOAT_ABS_TOLERANCE: float = 1e-8
"""
The absolute tolerance for floating-point similarity (see
`cmath.isclose`).
"""

_RUNNING_TEST_CODE: bool = False
"""
Will be set to `True` while testing code is running, allowing certain
functions to behave differently (usually to avoid infinite recursion).
"""

INLINE_STRINGS_IN_MEMORY_REPORTS: bool = False
"""
Whether strings will be shown as references or not in memory reports.
False means show them as references, True means show them inline.
"""


TrialDetails: TypeAlias = Tuple[str, Optional[str]]
"""
Trial details include base details, and optional extra details. The
`DETAIL_LEVEL` controls whether the extra details are reported (assuming
they're not `None`).
"""


class CaseResults(TypedDict):
    """
    Represents the results from running a test case, which might be a
    code block, an entire file, or a single function with specific
    parameters. Results get cached so that we don't need to re-run stuff
    as often. The fields are:

    - 'result': Holds the result from a function call. For other kinds
        of cases, holds the special value `NoResult`. If the trial was
        skipped, it holds the special value `Skipped`.
    - 'output': Anything printed to standard output during the trial, as
        a single (usually multi-line) string. Will be the empty string
        if nothing is printed.
    - 'error': Ether an `Exception` object holding an error raised by
        the code being tested, or `None` if no exception was raised.
    - 'traceback': `None` if there is no 'error', or a string containing
        a formatted traceback for the exception that was raised.
    - 'scope': A dictionary mapping variable names to values, holding
        a copy of the scope for the code that was run at the end of the
        run. For function tests, this holds the global scope within
        which the function was defined (and where it might have modified
        global variables, for example). Note that this is NOT the
        function's local scope, nor is it the function's containing
        scope for nested functions.

        Note that if the payload for a trial crashes, the resulting
        scope will usually be an empty dictionary.
    """
    result: Any
    output: str
    error: Optional[Exception]
    traceback: Optional[str]
    scope: Dict[str, Any]


class EnhancedCaseResults(CaseResults):
    """
    Case results that also have a 'case' slot with the test case in it.
    """
    case: "TestCase"


class CustomCheck(Protocol):
    """
    A custom check needs to accept an `EnhancedCaseResults` dictionary
    as its first argument and may accept any additional arguments. See
    `TestCase.checkCustom`.

    Although it may return anything to be printed as part of a failure
    message, it should return `True` to indicate success and `False` for
    generic failure.
    """
    def __call__(
        self,
        results: EnhancedCaseResults,
        *args: Any,
        **kwargs: Any
    ) -> Union[bool, Any]:
        ...


PayloadResult: TypeAlias = Tuple[Any, Dict[str, Any]]
"""
Represents the outcome of running some kind of code as part of testing.

A payload function needs to return a tuple containing two things: a
result value for the code being run, and a dictionary mapping strings to
values representing the scope after running the trial.
the trial code came from or which is created by running the trial code.

For trials testing things like running a file or a block of code where
there is no "result value" the special `NoResult` object is used as the
result. These trials include the full scope for the file/block as the
scope part.

For function trials, the return value is the result part, and the scope
part is the global scope of the function (NOT the local scope that
contains function-local variables).

Resulting scopes are usually constructed using `deepish_copy`, so that
modifications to them are somewhat disentangled from the original (but
e.g., a function in a copied scope will still have the original scope as
its `__globals__` and might affect that if it uses global variables).
"""


T = TypeVar('T')
"""
Type variable for `ClassInfo` definition.
"""


ClassInfo: TypeAlias = Union[type[T], Tuple['ClassInfo', ...], type[Union]]
"""
The kinds of things that can be passed as the second argument of
`instanceof`: types, tuples of types (perhaps nested) and `Union`s.
"""


#--------#
# Errors #
#--------#

class TestError(Exception):
    """
    An error with the testing mechanisms, as opposed to an error with
    the actual code being tested.
    """
    pass


#-------------#
# Trial Class #
#-------------#

class Trial:
    """
    Base class for both code checks and test cases, delineating common
    functionality like having outcomes. All trials are derived from a
    manager.
    """
    def __init__(self, manager: 'TestManager') -> None:
        """
        A manager must be specified, but that's it. This does extra
        things like registering the trial in the current test suite (see
        `testSuite`) and figuring out the location tag for the trial.
        """
        self.manager = manager

        # Location and tag for trial creation
        self.location = get_my_location()
        self.tag = tag_for(self.location)

        # List of outcomes of individual checks/tests based on this
        # trial. Each is a triple with a True/False indicator for
        # success/failure, a string tag for the expectation, and a full
        # result message.
        self.outcomes: List[Outcome] = []

        # Whether or not a check has failed for this trial yet.
        self.any_failed = False

        # How to describe this trial; should be overridden
        self.description = "an unknown trial"

        # Register as a trial
        ALL_TRIALS.setdefault(_CURRENT_SUITE_NAME, []).append(self)

    def trialDetails(self) -> TrialDetails:
        """
        Returns a pair of strings containing base and extra details
        describing what was tested by this trial. If the base details
        capture all available information, the extra details value will
        be `None`.

        This method is abstract and only sub-class implementations
        actually do anything.
        """
        raise NotImplementedError(
            "Cannot get trial details for a Trial or TestCase; you must"
            " create a specific kind of trial like a FunctionCase to be"
            " able to get trial details."
        )

    def _create_success_message(
        self,
        tag: str,
        details: str,
        extra_details: Optional[str]=None,
        include_test_details: bool=True
    ) -> str:
        """
        Returns an expectation success message (a string) for an
        expectation with the given tag, using the given details and
        extra details. Unless `include_test_details` is set to False,
        details of the test expression/block will also be included (but
        only when the detail level is at least 1). The tag should be a
        filename:lineno string indicating where the expectation
        originated.
        """
        # Detail level 1 gives more output for successes
        if DETAIL_LEVEL < 1:
            result = f"✓ {tag}"
        else:  # Detail level is at least 1
            result = (
                f"✓ expectation from {tag} met for {self.description}"
            )
            detail_msg = indent(details, 2)
            if not detail_msg.startswith('\n'):
                detail_msg = '\n' + detail_msg

            if DETAIL_LEVEL >= 2 and extra_details:
                extra_detail_msg = indent(extra_details, 2)
                if not extra_detail_msg.startswith('\n'):
                    extra_detail_msg = '\n' + extra_detail_msg

                detail_msg += extra_detail_msg

            # Test details unless suppressed
            if include_test_details:
                test_base, test_extra = self.trialDetails()
                detail_msg += '\n' + indent(test_base, 2)
                if DETAIL_LEVEL >= 2 and test_extra is not None:
                    detail_msg += '\n' + indent(test_extra, 2)

            result += detail_msg

        return result

    def _create_failure_message(
        self,
        tag: str,
        details: str,
        extra_details: Optional[str]=None,
        include_test_details: bool=True
    ) -> str:
        """
        Creates a failure message string for an expectation with the
        given tag that includes the details and/or extra details
        depending on the current global detail level. Normally,
        information about the test that was run is included as well, but
        you can set `include_test_details` to False to prevent this.
        """
        # Detail level controls initial message
        if DETAIL_LEVEL < 1:
            result = f"✗ {tag}"
        else:
            result = (
                f"✗ expectation from {tag} NOT met for"
                f" {self.description}"
            )

        # Assemble our details message
        detail_msg = ''

        # Figure out if we should suppress details
        suppress = self._should_suppress()

        # Detail level controls printing of detail messages
        if (DETAIL_LEVEL == 0 and not suppress) or DETAIL_LEVEL >= 1:
            detail_msg += '\n' + indent(details, 2)
        if DETAIL_LEVEL >= 1 and extra_details:
            detail_msg += '\n' + indent(extra_details, 2)

        # Test details unless suppressed
        if include_test_details:
            test_base, test_extra = self.trialDetails()
            if (DETAIL_LEVEL == 0 and not suppress) or DETAIL_LEVEL >= 1:
                detail_msg += '\n' + indent(test_base, 2)
            if DETAIL_LEVEL >= 1 and test_extra is not None:
                detail_msg += '\n' + indent(test_extra, 2)

        return result + detail_msg

    def _print_skip_message(self, tag: str, reason: str) -> None:
        """
        Prints a standard message about the trial being skipped, using
        the given tag and a reason (shown only if detail level is 1+).
        """
        # Detail level controls initial message
        if DETAIL_LEVEL < 1:
            msg = f"~ {tag} (skipped)"
        else:
            msg = (
                f"~ expectation at {tag} for {self.description}"
                f" skipped ({reason})"
            )
        print_message(msg, color=msg_color("skipped"))

    def _should_skip(self) -> bool:
        """
        Returns True if this trial should be skipped based on a previous
        failure and the `SKIP_ON_FAILURE` mode.
        """
        return (
            (SKIP_ON_FAILURE == "all" and CHECK_FAILED)
         or (SKIP_ON_FAILURE == "case" and self.any_failed)
         or (SKIP_ON_FAILURE == "manager" and self.manager.any_failed)
        )

    def _should_suppress(self) -> bool:
        """
        Returns True if failure details for this trial should be
        suppressed based on a previous failure and the
        `SUPPRESS_ON_FAILURE` mode.
        """
        return (
            (SUPPRESS_ON_FAILURE == "all" and CHECK_FAILED)
         or (SUPPRESS_ON_FAILURE == "case" and self.any_failed)
         or (SUPPRESS_ON_FAILURE == "manager" and self.manager.any_failed)
        )

    def _register_outcome(self, passed: bool, tag: str, message: str) -> None:
        """
        Registers an outcome for this trial. `passed` should be either
        True or False indicating whether the check passed, `tag` is a
        string to label the outcome with, and `message` is the message
        displayed by the check. This appends an entry to `self.outcomes`
        with the passed boolean, the tag, and the message in a tuple, and
        it sets `self.any_failed` and `self.manager.any_failed` if the
        outcome is a failure.
        """
        global CHECK_FAILED
        self.outcomes.append((passed, tag, message))
        _register_outcome(passed, tag, message)
        if not passed:
            CHECK_FAILED = True
            self.any_failed = True
            self.manager.any_failed = True


#------------------#
# Code Check Class #
#------------------#

class CodeChecks(Trial):
    """
    Represents one or more checks performed against code structure
    (without running that code) rather than against the behavior of code.
    Like a `TestCase`, it can have outcomes (one for each check
    performed) and is tracked globally.
    """
    def __init__(self, manager: 'TestManager') -> None:
        """
        A manager must be specified, but that's it.
        """
        super().__init__(manager)

        # How to describe this trial
        self.description = f"code checks for {self.manager.tag}"

    def trialDetails(self) -> TrialDetails:
        """
        The base details describe what kind of code was run; the full
        details include the AST dump.
        """
        baseDetails = self.manager.checkDetails()

        # Get representation of the AST we checked:
        if self.manager.syntax_tree is not None:
            if sys.version_info < (3, 9):
                astRepr = ast.dump(self.manager.syntax_tree)
            else:
                astRepr = ast.dump(self.manager.syntax_tree, indent=2)
            return (
                baseDetails,
                "The code structure is:" + indent(astRepr, 2)
            )
        else:
            return (
                baseDetails,
                "No code was available for checking."
            )

    def performCheck(self, checkFor: "ASTRequirement") -> Optional[bool]:
        """
        Performs a check for the given `ASTRequirement` within the AST
        managed by this code check's manager. Prints a success/failure
        message, registers an outcome, and returns True on success and
        False on failure (including when there's a partial match).
        Returns `None` if the check is skipped (which can happen based on
        a previous failure depending on settings, or when the AST to
        check is not available.
        """
        tag = tag_for(get_my_location())

        # Skip the check if there's nothing to test
        if self._should_skip() or self.manager.syntax_tree is None:
            self._print_skip_message(tag, "source code not available")
            return None
        else:
            # Perform the check
            matches = checkFor.allMatches(self.manager.syntax_tree)
            if not matches.isFull:
                passed = False
                if checkFor.maxMatches == 0:
                    contains = "contains a structure that it should not"
                elif (
                    checkFor.minMatches is not None
                and checkFor.minMatches > 1
                ):
                    contains = (
                        "does not contain enough of the expected"
                        " structures"
                    )
                else:
                    contains = "does not contain the expected structure"
            else:
                passed = True
                if checkFor.maxMatches == 0:
                    contains = (
                        "does not contain any structures it should not"
                    )
                elif (
                    checkFor.minMatches is not None
                and checkFor.minMatches > 1
                ):
                    contains = "contains enough expected structures"
                else:
                    contains = "contains the expected structure"

            structureString = checkFor.fullStructure()
            base_msg = f"""\
Code {contains}:
{indent(structureString, 2)}"""
            if matches.isPartial:
                base_msg += f"""
Although it does partially satisfy the requirement:
{indent(str(matches), 2)}"""

            # TODO: have partial/full structure strings?
            extra_msg = ""

            msg_cat: MessageCategory
            if passed:
                msg = self._create_success_message(tag, base_msg, extra_msg)
                msg_cat = "succeeded"
            else:
                msg = self._create_failure_message(tag, base_msg, extra_msg)
                msg_cat = "failed"

            # Print our message
            print_message(msg, color=msg_color(msg_cat))

            # Record outcome
            self._register_outcome(passed, tag, msg)
            return passed


#-------------------#
# Test Case Classes #
#-------------------#

class NoResult:
    """
    A special class used to indicate the absence of a result when None
    is a valid result value.
    """
    pass


class Skipped:
    """
    A special class used in the 'result' fields to indicate that a trial
    was skipped.
    """
    pass


def mimicInput(prompt: Any = '') -> str:
    """
    A function which mimics the functionality of the default `input`
    function: it prints a prompt (default `''`), reads input from stdin,
    and then returns that input. Unlike normal input, it prints what it
    reads from stdin to stdout, which in normal situations would result
    in that stuff showing up on the console twice, but when stdin is set
    to an alternate stream (as we do when capturing input/output) that
    doesn't happen.
    """
    print(str(prompt), end='')
    incomming = sys.stdin.readline()
    # TODO: Check for '' here meaning EOF & generate a nice error
    # Strip newline on incomming value
    incomming = incomming.rstrip('\n\r')
    print(incomming, end='\n')
    return incomming


class TestCase(Trial):
    """
    Represents a specific test to run, managing things like specific
    arguments, inputs or available variables that need to be in place.
    Derived from a `TestManager` using the `TestManager.case` method.

    `TestCase` is abstract; subclasses should override a least the `run`
    and `trialDetails` functions.
    """
    def __init__(self, manager: 'TestManager') -> None:
        """
        A manager must be specified, but that's it. This does extra
        things like registering the case in the current test suite (see
        `testSuite`) and figuring out the location tag for the case.
        """
        super().__init__(manager)

        # How to describe this trial
        self.description = f"test case at {self.tag}"

        # Inputs to provide on stdin
        self.inputs: Optional[Iterable[str]] = None

        # Results of running this case
        self.results: Optional[CaseResults] = None

        # Whether to echo captured printed outputs (overrides global)
        self.echo: Optional[bool] = None

    def provideInputs(self, *inputLines: str) -> None:
        """
        Sets up fake inputs (each argument must be a string and is used
        for one line of input) for this test case. When information is
        read from stdin during the test, including via the `input`
        function, these values are the result. If you don't call
        `provideInputs`, then the test will pause and wait for real user
        input when `input` is called.

        You must call this before the test actually runs (i.e., before
        `TestCase.run` or one of the `check` functions is called),
        otherwise you'll get an error.
        """
        if self.results is not None:
            raise TestError(
                "You cannot provide inputs because this test case has"
                " already been run."
            )
        self.inputs = inputLines

    def showPrintedLines(self, show: bool=True) -> None:
        """
        Overrides the global `showPrintedLines` setting for this test.
        Use None as the parameter to remove the override.
        """
        self.echo = show

    def _run(
        self,
        payload: Callable[[], Tuple[Any, Dict[str, Any]]]
    ) -> CaseResults:
        """
        Given a payload (a zero-argument function that returns a tuple
        with a result and a scope dictionary), runs the payload while
        managing things like output capturing and input mocking. Sets the
        `self.results` field to reflect the results of the run, which
        will be a dictionary that has the following slots:

        - "result": The result value from a function call. This key
            will have the value `NoResult` for tests that don't have a
            result, like file or code block tests. To achieve this with
            a custom payload, have the payload return `NoResult` as the
            first part of the tuple it returns.
        - "output": The output printed during the test. Will be an empty
            string if nothing gets printed.
        - "error": An Exception object representing an error that
            occurred during the test, or None if no errors happened.
        - "traceback": If an exception occurred, this will be a string
            containing the traceback for that exception. Otherwise it
            will be None.
        - "scope": The second part of the tuple returned by the payload,
            which should be a dictionary representing the scope of the
            code run by the test. If the payload crashes, an empty
            dictionary will be used as the scope.

        In addition to being added to the results slot, this dictionary
        is also returned.
        """
        # Set up the `input` function to echo what is typed, and to only
        # read from stdin (in case we're in a notebook where input would
        # do something else).
        original_input = builtins.input
        builtins.input = mimicInput

        # Set up a capturing stream for output
        outputCapture = CapturingStream()
        outputCapture.install()
        if self.echo or (self.echo is None and _SHOW_OUTPUT):
            outputCapture.echo()

        # Set up fake input contents. Note the input function has been
        # monkey-patched above already to always read from stdin.
        # TODO: Set things up to fail with an EOF error or nicer rather
        # than providing infinite blank inputs if we run out of provided
        # inputs...
        if self.inputs is not None:
            fakeInput = io.StringIO('\n'.join(self.inputs))
            original_stdin = sys.stdin
            sys.stdin = fakeInput

        # Set up default values before we run things
        error = None
        tb = None
        value = NoResult
        scope: Dict[str, Any] = {}

        # Actually run the test
        try:
            value, scope = payload()
        except Exception as e:
            # Catch any error that occurred
            error = e
            tb = traceback.format_exc()
        finally:
            # Release stream captures and reset the input function
            outputCapture.uninstall()
            builtins.input = original_input
            if self.inputs is not None:
                sys.stdin = original_stdin

        # Grab captured output
        output = outputCapture.getvalue()

        # Create self.results w/ output, error, and maybe result value
        self.results = {
            "result": value,
            "output": output,
            "error": error,
            "traceback": tb,
            "scope": scope
        }

        # Return new results object
        return self.results

    def run(self) -> CaseResults:
        """
        Runs this test case, capturing printed output and supplying fake
        input if `TestCase.provideInputs` has been called. Stores the
        results in `self.results`. This will be called once
        automatically the first time an expectation method like
        `TestCase.checkReturnValue` is used, but the cached value will
        be re-used for subsequent expectations, unless you manually call
        this method again.

        This method is overridden by specific test case types.
        """
        raise NotImplementedError(
            "Cannot run a TestCase; you must create a specific kind of"
            " test case like a FunctionCase to be able to run it."
        )

    def fetchResults(self) -> CaseResults:
        """
        Fetches the results of the test, which will run the test if it
        hasn't already been run, but otherwise will just return the
        latest cached results.

        `run` describes the format of the results.
        """
        if self.results is None:
            self.run()
        assert self.results is not None
        return self.results

    def checkReturnValue(self, expectedValue: Any) -> Optional[bool]:
        """
        Checks the result value for this test case, comparing it against
        the given expected value and printing a message about success or
        failure depending on whether they are considered different by
        the `findFirstDifference` function.

        If this is the first check performed using this test case, the
        test case will run; otherwise a cached result will be used.

        This method returns True if the expectation is met and False if
        it is not, in addition to printing a message indicating
        success/failure and recording that message along with the status
        and tag in `self.outcomes`. If the check is skipped, it returns
        None and does not add an entry to `self.outcomes`.
        """
        results = self.fetchResults()

        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Figure out whether we've got an error or an actual result
        if results["error"] is not None:
            # An error during testing
            tb = results["traceback"]
            assert tb is not None
            tblines = tb.splitlines()
            if len(tblines) < 12:
                base_msg = "Failed due to an error:\n" + indent(tb, 2)
                extra_msg = None
            else:
                short_tb = '\n'.join(tblines[:4] + ['...'] + tblines[-4:])
                base_msg = "Failed due to an error:\n" + indent(short_tb, 2)
                extra_msg = "Full traceback is:\n" + indent(tb, 2)

            msg = self._create_failure_message(
                tag,
                base_msg,
                extra_msg
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        elif results.get("result", NoResult) is NoResult:
            # Likely impossible, since we verified the category above
            # and we're in a condition where no error was logged...
            msg = self._create_failure_message(
                tag,
                (
                    "This test case does not have a result value. (Did"
                    " you mean to use checkPrintedLines?)"
                )
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        else:
            # We produced a result, so check equality

            # Check equivalence
            passed = False
            firstDiff = findFirstDifference(results["result"], expectedValue)
            if firstDiff is None:
                equivalence = "equivalent to"
                passed = True
            else:
                equivalence = "NOT equivalent to"

            # Get short/long versions of result/expected
            short_result = ellipsis(repr(results["result"]), 72)
            full_result = repr(results["result"])
            short_expected = ellipsis(repr(expectedValue), 72)
            full_expected = repr(expectedValue)

            # Create base/extra messages
            if (
                short_result == full_result
            and short_expected == full_expected
            ):
                base_msg = (
                    f"Result:\n{indent(short_result, 2)}\nwas"
                    f" {equivalence} the expected value:\n"
                    f"{indent(short_expected, 2)}"
                )
                extra_msg = None
                if (
                    firstDiff is not None
                and differencesAreSubtle(short_result, short_expected)
                ):
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
            else:
                base_msg = (
                    f"Result:\n{indent(short_result, 2)}\nwas"
                    f" {equivalence} the expected value:\n"
                    f"{indent(short_expected, 2)}"
                )
                extra_msg = ""
                if (
                    firstDiff is not None
                and differencesAreSubtle(short_result, short_expected)
                ):
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
                if short_result != full_result:
                    extra_msg += (
                        f"Full result:\n{indent(full_result, 2)}\n"
                    )
                if short_expected != full_expected:
                    extra_msg += (
                        f"Full expected value:\n"
                        f"{indent(full_expected, 2)}\n"
                    )

            if passed:
                msg = self._create_success_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("succeeded"))
                self._register_outcome(True, tag, msg)
                return True
            else:
                msg = self._create_failure_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("failed"))
                self._register_outcome(False, tag, msg)
                return False

    def checkReturnedStructure(
        self,
        expectedStructure: Any
    ) -> Optional[bool]:
        """
        Works like `checkReturnValue` but checks the memory structure of
        the result using `yieldMemoryReportDifferences`. The
        `expectedStructure` may be a string, in which case the
        `memoryReport` of the return value must match it, or if it's not
        a string, it's `memoryReport` will be compared against the
        `memoryReport` of the result.
        """
        results = self.fetchResults()

        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Figure out whether we've got an error or an actual result
        if results["error"] is not None:
            # An error during testing
            tb = results["traceback"]
            assert tb is not None
            tblines = tb.splitlines()
            if len(tblines) < 12:
                base_msg = "Failed due to an error:\n" + indent(tb, 2)
                extra_msg = None
            else:
                short_tb = '\n'.join(tblines[:4] + ['...'] + tblines[-4:])
                base_msg = "Failed due to an error:\n" + indent(short_tb, 2)
                extra_msg = "Full traceback is:\n" + indent(tb, 2)

            msg = self._create_failure_message(
                tag,
                base_msg,
                extra_msg
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        elif results.get("result", NoResult) is NoResult:
            # Likely impossible, since we verified the category above
            # and we're in a condition where no error was logged...
            msg = self._create_failure_message(
                tag,
                (
                    "This test case does not have a result value. (Did"
                    " you mean to use checkPrintedLines?)"
                )
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        else:
            # We produced a result, so check the structure

            # Check equivalence
            passed = False
            actualStructure = memoryReport(results["result"])
            if not isinstance(expectedStructure, str):
                expectedStructure = memoryReport(expectedStructure)

            parsedActual = parseMemoryReport(actualStructure)
            parsedExpected = parseMemoryReport(expectedStructure)
            # Attempt to force a more direct error message if it seems
            # reasonable to do so:
            if (
                len(parsedActual) > 0
            and len(parsedActual) == len(parsedExpected)
            ):
                targets = list(parsedActual)[0], list(parsedExpected)[0]
            else:
                targets = None
            differences = list(
                yieldMemoryReportDifferences(
                    parsedActual,
                    parsedExpected,
                    targets
                )
            )
            if len(differences) == 0:
                equivalence = "equivalent to"
                passed = True
            else:
                equivalence = "NOT equivalent to"

            # Create base/extra messages
            base_msg = (
                f"Structure of the result:"
                f"\n{indent(actualStructure, 2)}\nwas"
                f" {equivalence} the expected structure:\n"
                f"{indent(expectedStructure, 2)}"
            )
            extra_msg = None
            if len(differences) > 0:
                allDiffs = '\n'.join(differences)
                base_msg += f"\nDifferences:\n{indent(allDiffs, 2)}"

            if passed:
                msg = self._create_success_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("succeeded"))
                self._register_outcome(True, tag, msg)
                return True
            else:
                msg = self._create_failure_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("failed"))
                self._register_outcome(False, tag, msg)
                return False

    def checkVariableValue(
        self,
        varName: str,
        expectedValue: Any
    ) -> Optional[bool]:
        """
        Checks the value of a variable established by this test case,
        which should be a code block or file test (use `checkReturnValue`
        instead for checking the result of a function test). It checks
        that a variable with a certain name (given as a string) has a
        certain expected value, and prints a message about success or
        failure depending on whether the actual value and expected value
        are considered different by the `findFirstDifference` function.

        If this is the first check performed using this test case, the
        test case will run; otherwise a cached result will be used.

        This method returns True if the expectation is met and False if
        it is not, in addition to printing a message indicating
        success/failure and recording that message along with the status
        and tag in `self.outcomes`. If the check is skipped, it returns
        None and does not add an entry to `self.outcomes`.
        """
        results = self.fetchResults()

        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Figure out whether we've got an error or an actual result
        if results["error"] is not None:
            # An error during testing
            tb = results["traceback"]
            assert tb is not None
            tblines = tb.splitlines()
            if len(tblines) < 12:
                base_msg = "Failed due to an error:\n" + indent(tb, 2)
                extra_msg = None
            else:
                short_tb = '\n'.join(tblines[:4] + ['...'] + tblines[-4:])
                base_msg = "Failed due to an error:\n" + indent(short_tb, 2)
                extra_msg = "Full traceback is:\n" + indent(tb, 2)

            msg = self._create_failure_message(
                tag,
                base_msg,
                extra_msg
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        else:
            # No error, so look for our variable
            scope = results["scope"]

            if scope is None:
                raise RuntimeError(
                    "Used checkVariableValue for a test case that does"
                    " not have a result scope. It can only be used with"
                    " block or file cases"
                )

            if varName not in scope:
                msg = self._create_failure_message(
                    tag,
                    f"No variable named '{varName}' was created.",
                    None
                )
                print_message(msg, color=msg_color("failed"))
                self._register_outcome(False, tag, msg)
                return False

            # Check equivalence
            passed = False
            value = scope[varName]
            firstDiff = findFirstDifference(value, expectedValue)
            if firstDiff is None:
                equivalence = "equivalent to"
                passed = True
            else:
                equivalence = "NOT equivalent to"

            # Get short/long versions of result/expected
            short_value = ellipsis(repr(value), 72)
            full_value = repr(value)
            short_expected = ellipsis(repr(expectedValue), 72)
            full_expected = repr(expectedValue)

            # Create base/extra messages
            if (
                short_value == full_value
            and short_expected == full_expected
            ):
                base_msg = (
                    f"Variable '{varName}' with"
                    f" value:\n{indent(short_value, 2)}\nwas"
                    f" {equivalence} the expected value:\n"
                    f"{indent(short_expected, 2)}"
                )
                extra_msg = None
                if (
                    firstDiff is not None
                and differencesAreSubtle(short_value, short_expected)
                ):
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
            else:
                base_msg = (
                    f"Variable '{varName}' with"
                    f" value:\n{indent(short_value, 2)}\nwas"
                    f" {equivalence} the expected value:\n"
                    f"{indent(short_expected, 2)}"
                )
                extra_msg = ""
                if (
                    firstDiff is not None
                and differencesAreSubtle(short_value, short_expected)
                ):
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
                if short_value != full_value:
                    extra_msg += (
                        f"Full value:\n{indent(full_value, 2)}\n"
                    )
                if short_expected != full_expected:
                    extra_msg += (
                        f"Full expected value:\n"
                        f"{indent(full_expected, 2)}\n"
                    )

            if passed:
                msg = self._create_success_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("succeeded"))
                self._register_outcome(True, tag, msg)
                return True
            else:
                msg = self._create_failure_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("failed"))
                self._register_outcome(False, tag, msg)
                return False

    def checkVariableStructure(
        self,
        varName: str,
        expectedStructure: Any
    ) -> Optional[bool]:
        """
        Checks the memory structure of a variable established by this
        test case, which should be a code block or file test (use
        `checkReturnedStructure` instead for checking the result of a
        function test). If the `expectedStructure` value is a string,
        then the `memoryReport` of the specified variable must match
        that string. Alternatively, if `expectedStructure` is not a
        string, then `memoryReport` will be applied to it and that
        result must match the memory report of the actual value.

        Matches are determined by `yieldMemoryReportDifferences`.

        It prints a message about success or failure depending on
        these comparisons.

        If this is the first check performed using this test case, the
        test case will run; otherwise a cached result will be used.

        This method returns True if the expectation is met and False if
        it is not, in addition to printing a message indicating
        success/failure and recording that message along with the status
        and tag in `self.outcomes`. If the check is skipped, it returns
        None and does not add an entry to `self.outcomes`.
        """
        results = self.fetchResults()

        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Figure out whether we've got an error or an actual result
        if results["error"] is not None:
            # An error during testing
            tb = results["traceback"]
            assert tb is not None
            tblines = tb.splitlines()
            if len(tblines) < 12:
                base_msg = "Failed due to an error:\n" + indent(tb, 2)
                extra_msg = None
            else:
                short_tb = '\n'.join(tblines[:4] + ['...'] + tblines[-4:])
                base_msg = "Failed due to an error:\n" + indent(short_tb, 2)
                extra_msg = "Full traceback is:\n" + indent(tb, 2)

            msg = self._create_failure_message(
                tag,
                base_msg,
                extra_msg
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        else:
            # No error, so look for our variable
            scope = results["scope"]

            if scope is None:
                raise RuntimeError(
                    "Used checkVariableValue for a test case that does"
                    " not have a result scope. It can only be used with"
                    " block or file cases"
                )

            if varName not in scope:
                msg = self._create_failure_message(
                    tag,
                    f"No variable named '{varName}' was created.",
                    None
                )
                print_message(msg, color=msg_color("failed"))
                self._register_outcome(False, tag, msg)
                return False

            # Check equivalence
            passed = False
            value = scope[varName]
            if not isinstance(expectedStructure, str):
                expectedStructure = memoryReport(
                    **{varName: expectedStructure}
                )
            actualStructure = memoryReport(**{varName: value})
            differences = list(
                yieldMemoryReportDifferences(
                    actualStructure,
                    expectedStructure,
                    (varName, varName)
                )
            )
            if len(differences) == 0:
                equivalence = "structurally equivalent to"
                passed = True
            else:
                equivalence = "NOT structurally equivalent to"

            # Create base/extra messages
            base_msg = (
                f"Variable '{varName}' had"
                f" structure:\n{indent(actualStructure, 2)}\nwhich was"
                f" {equivalence} to the expected"
                f" structure:\n{indent(expectedStructure, 2)}"
            )
            extra_msg = None
            if len(differences) > 0:
                allDiffs = '\n'.join(differences)
                base_msg += f"\nDifferences:\n{indent(allDiffs, 2)}"

            if passed:
                msg = self._create_success_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("succeeded"))
                self._register_outcome(True, tag, msg)
                return True
            else:
                msg = self._create_failure_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("failed"))
                self._register_outcome(False, tag, msg)
                return False

    def checkPrintedLines(self, *expectedLines: str) -> Optional[bool]:
        """
        Checks that the exact printed output captured during the test
        matches a sequence of strings each specifying one line of the
        output. Note that the global `IGNORE_TRAILING_WHITESPACE`
        affects how this function treats line matches.

        If this is the first check performed using this test case, the
        test case will run; otherwise a cached result will be used.

        This method returns True if the check succeeds and False if it
        fails, in addition to printing a message indicating
        success/failure and recording that message along with the status
        and tag in `self.outcomes`. If the check is skipped, it returns
        None and does not add an entry to `self.outcomes`.
        """
        # Fetch captured output
        results = self.fetchResults()
        output = results["output"]

        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Figure out whether we've got an error or an actual result
        if results["error"] is not None:
            # An error during testing
            tb = results["traceback"]
            assert tb is not None
            tblines = tb.splitlines()
            if len(tblines) < 12:
                base_msg = "Failed due to an error:\n" + indent(tb, 2)
                extra_msg = None
            else:
                short_tb = '\n'.join(tblines[:4] + ['...'] + tblines[-4:])
                base_msg = "Failed due to an error:\n" + indent(short_tb, 2)
                extra_msg = "Full traceback is:\n" + indent(tb, 2)

            msg = self._create_failure_message(
                tag,
                base_msg,
                extra_msg
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        else:
            # We produced printed output, so check it

            # Get lines/single versions
            expected = '\n'.join(expectedLines) + '\n'
            # If the output doesn't end with a newline, don't add one to
            # our expectation either...
            if not output.endswith('\n'):
                expected = expected[:-1]

            # Figure out equivalence category
            equivalence = None
            passed = False
            firstDiff = findFirstDifference(output, expected)
            if output == expected:
                equivalence = "exactly the same as"
                passed = True
            elif firstDiff is None:
                equivalence = "equivalent to"
                passed = True
            else:
                equivalence = "NOT the same as"
                # passed remains False

            # Get short/long representations of our strings
            short, long = dual_string_repr(output)
            short_exp, long_exp = dual_string_repr(expected)

            # Construct base and extra messages
            if short == long and short_exp == long_exp:
                base_msg = (
                    f"Printed lines:\n{indent(short, 2)}\nwere"
                    f" {equivalence} the expected printed"
                    f" lines:\n{indent(short_exp, 2)}"
                )
                if not passed:
                    assert firstDiff is not None
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
                extra_msg = None
            else:
                base_msg = (
                    f"Printed lines:\n{indent(short, 2)}\nwere"
                    f" {equivalence} the expected printed"
                    f" lines:\n{indent(short_exp, 2)}"
                )
                if not passed:
                    assert firstDiff is not None
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
                extra_msg = ""
                if short != long:
                    extra_msg += f"Full printed lines:\n{indent(long, 2)}\n"
                if short_exp != long_exp:
                    extra_msg += (
                        f"Full expected printed"
                        f" lines:\n{indent(long_exp, 2)}\n"
                    )

            if passed:
                msg = self._create_success_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("succeeded"))
                self._register_outcome(True, tag, msg)
                return True
            else:
                msg = self._create_failure_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color="1;31" if COLORS else None)
                self._register_outcome(False, tag, msg)
                return False

    def checkPrintedFragment(
        self,
        fragment: str,
        copies: int=1,
        allowExtra: bool=False
    ) -> Optional[bool]:
        """
        Works like checkPrintedLines, except instead of requiring that
        the printed output exactly match a set of lines, it requires that
        a certain fragment of text appears somewhere within the printed
        output (or perhaps that multiple non-overlapping copies appear,
        if the copies argument is set to a number higher than the
        default of 1).

        If allowExtra is set to True, more than the specified number of
        copies will be ignored, but by default, extra copies are not
        allowed.

        The fragment is matched against the entire output as a single
        string, so it may contain newlines and if it does these will
        only match newlines in the captured output. If
        `IGNORE_TRAILING_WHITESPACE` is active (it's on by default), the
        trailing whitespace in the output will be removed before
        matching, and trailing whitespace in the fragment will also be
        removed IF it has a newline after it (trailing whitespace at the
        end of the string with no final newline will be retained).

        This function returns True if the check succeeds and False if it
        fails, and prints a message either way. If the check is skipped,
        it returns None and does not add an entry to `self.outcomes`.
        """
        # Fetch captured output
        results = self.fetchResults()
        output = results["output"]

        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Figure out whether we've got an error or an actual result
        if results["error"] is not None:
            # An error during testing
            tb = results["traceback"]
            assert tb is not None
            tblines = tb.splitlines()
            if len(tblines) < 12:
                base_msg = "Failed due to an error:\n" + indent(tb, 2)
                extra_msg = None
            else:
                short_tb = '\n'.join(tblines[:4] + ['...'] + tblines[-4:])
                base_msg = "Failed due to an error:\n" + indent(short_tb, 2)
                extra_msg = "Full traceback is:\n" + indent(tb, 2)

            msg = self._create_failure_message(
                tag,
                base_msg,
                extra_msg
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        else:
            # We produced printed output, so check it
            if IGNORE_TRAILING_WHITESPACE:
                matches = re.findall(
                    re.escape(trimWhitespace(fragment, True)),
                    trimWhitespace(output)
                )
            else:
                matches = re.findall(re.escape(fragment), output)
            passed = False
            if copies == 1:
                copiesPhrase = ""
                exactly = ""
                atLeast = "at least "
            else:
                copiesPhrase = f"{copies} copies of "
                exactly = "exactly "
                atLeast = "at least "

            fragShort, fragLong = dual_string_repr(fragment)
            outShort, outLong = dual_string_repr(output)

            if len(matches) == copies:
                passed = True
                base_msg = (
                    f"Found {exactly}{copiesPhrase}the target"
                    f" fragment in the printed output."
                    f"\nFragment was:\n{indent(fragShort, 2)}"
                    f"\nOutput was:\n{indent(outShort, 2)}"
                )
            elif allowExtra and len(matches) > copies:
                passed = True
                base_msg = (
                    f"Found {atLeast}{copiesPhrase}the target"
                    f" fragment in the printed output (found"
                    f" {len(matches)})."
                    f"\nFragment was:\n{indent(fragShort, 2)}"
                    f"\nOutput was:\n{indent(outShort, 2)}"
                )
            else:
                passed = False
                base_msg = (
                    f"Did not find {copiesPhrase}the target fragment"
                    f" in the printed output (found {len(matches)})."
                    f"\nFragment was:\n{indent(fragShort, 2)}"
                    f"\nOutput was:\n{indent(outShort, 2)}"
                )

            extra_msg = ""
            if fragLong != fragShort:
                extra_msg += f"Full fragment was:\n{indent(fragLong, 2)}"

            if outLong != outShort:
                if not extra_msg.endswith('\n'):
                    extra_msg += '\n'
                extra_msg += f"Full output was:\n{indent(outLong, 2)}"

            if passed:
                msg = self._create_success_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("succeeded"))
                self._register_outcome(True, tag, msg)
                return True
            else:
                msg = self._create_failure_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color="1;31" if COLORS else None)
                self._register_outcome(False, tag, msg)
                return False

    def checkFileLines(self, filename: str, *lines: str) -> Optional[bool]:
        """
        Works like `checkPrintedLines`, but checks for lines in the
        specified file, rather than checking for printed lines.
        """
        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Fetch the results to actually run the test!
        expected = '\n'.join(lines) + '\n'
        results = self.fetchResults()

        # Figure out whether we've got an error or an actual result
        if results["error"] is not None:
            # An error during testing
            tb = results["traceback"]
            assert tb is not None
            tblines = tb.splitlines()
            if len(tblines) < 12:
                base_msg = "Failed due to an error:\n" + indent(tb, 2)
                extra_msg = None
            else:
                short_tb = '\n'.join(tblines[:4] + ['...'] + tblines[-4:])
                base_msg = "Failed due to an error:\n" + indent(short_tb, 2)
                extra_msg = "Full traceback is:\n" + indent(tb, 2)

            msg = self._create_failure_message(
                tag,
                base_msg,
                extra_msg
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        else:
            # The test was able to run, so check the file contents

            # Fetch file contents
            try:
                with open(filename, 'r', newline='') as fileInput:
                    fileContents = fileInput.read()
            except (OSError, FileNotFoundError, PermissionError):
                # We can't even read the file!
                msg = self._create_failure_message(
                    tag,
                    f"Expected file '{filename}' cannot be read.",
                    None
                )
                print_message(msg, color=msg_color("failed"))
                self._register_outcome(False, tag, msg)
                return False

            # Make complex newlines into single newlines to match how
            # the expectation is constructed:
            fileContents = re.sub(r'\r\n', '\n', fileContents)

            # If the file doesn't end with a newline, don't add one to
            # our expectation either...
            if not fileContents.endswith('\n'):
                expected = expected[:-1]

            # Get lines/single versions
            firstDiff = findFirstDifference(fileContents, expected)
            equivalence = None
            passed = False
            if fileContents == expected:
                equivalence = "exactly the same as"
                passed = True
            elif firstDiff is None:
                equivalence = "equivalent to"
                passed = True
            else:
                # Some other kind of difference
                equivalence = "NOT the same as"
                # passed remains False

            # Get short/long representations of our strings
            short, long = dual_string_repr(fileContents)
            short_exp, long_exp = dual_string_repr(expected)

            # Construct base and extra messages
            if short == long and short_exp == long_exp:
                base_msg = (
                    f"File contents:\n{indent(short, 2)}\nwere"
                    f" {equivalence} the expected file"
                    f" contents:\n{indent(short_exp, 2)}"
                )
                if not passed:
                    assert firstDiff is not None
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
                extra_msg = None
            else:
                base_msg = (
                    f"File contents:\n{indent(short, 2)}\nwere"
                    f" {equivalence} the expected file"
                    f" contents:\n{indent(short_exp, 2)}"
                )
                if not passed:
                    assert firstDiff is not None
                    base_msg += (
                        f"\nFirst difference was:\n{indent(firstDiff, 2)}"
                    )
                extra_msg = ""
                if short != long:
                    extra_msg += f"Full file contents:\n{indent(long, 2)}\n"
                if short_exp != long_exp:
                    extra_msg += (
                        f"Full expected file"
                        f" contents:\n{indent(long_exp, 2)}\n"
                    )

            if passed:
                msg = self._create_success_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color=msg_color("succeeded"))
                self._register_outcome(True, tag, msg)
                return True
            else:
                msg = self._create_failure_message(
                    tag,
                    base_msg,
                    extra_msg
                )
                print_message(msg, color="1;31" if COLORS else None)
                self._register_outcome(False, tag, msg)
                return False

    def checkCustom(
        self,
        checker: CustomCheck,
        *args: Any,
        **kwargs: Any
    ) -> Optional[bool]:
        """
        Sets up a custom check using a testing function. The provided
        function will be given one argument, plus any additional
        arguments given to this function. The first and/or only argument
        to the checker function will be a dictionary with the following
        keys:

        - "case": The test case object on which `checkCustom` was called.
            This could be used to do things like access arguments passed
            to the function being tested for a `FunctionCase` for
            example.
        - "output": Output printed by the test case, as a string.
        - "result": the result value (for function tests only, otherwise
            this key will not be present).
        - "error": the error that occurred (or None if no error
            occurred).
        - "traceback": the traceback (a string, or None if there was no
            error).
        - "scope": For file and code block cases, the variable dictionary
            created by the file/code block. `None` for function cases.

        The testing function must return True to indicate success and
        False for failure. If it returns something other than True or
        False, it will be counted as a failure, that value will be shown
        as part of the test result if the `DETAIL_LEVEL` is 1 or higher,
        and this method will return False.

        If this check is skipped (e.g., because of a previous failure),
        this method returns None and does not add an entry to
        `self.outcomes`; the custom checker function won't be called in
        that case.
        """
        results = self.fetchResults()
        # Add a 'case' entry
        checker_input: EnhancedCaseResults = cast(
            EnhancedCaseResults,
            copy.copy(results)
        )
        checker_input["case"] = self

        # Figure out the tag for this expectation
        tag = tag_for(get_my_location())

        # Skip this check if the case has failed already
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            # Note that we don't add an outcome here, and we return None
            # instead of True or False
            return None

        # Only run the checker if we're not skipping the test
        test_result = checker(checker_input, *args, **kwargs)

        if test_result is True:
            msg = self._create_success_message(tag, "Custom check passed.")
            print_message(msg, color=msg_color("succeeded"))
            self._register_outcome(True, tag, msg)
            return True
        elif test_result is False:
            msg = self._create_failure_message(tag, "Custom check failed")
            print_message(msg, color="1;31" if COLORS else None)
            self._register_outcome(False, tag, msg)
            return False
        else:
            msg = self._create_failure_message(
                tag,
                "Custom check failed:\n" + indent(str(test_result), 2),
            )
            print_message(msg, color="1;31" if COLORS else None)
            self._register_outcome(False, tag, msg)
            return False

class FileCase(TestCase):
    """
    Runs a particular file when executed. Its manager should be a
    `FileManager`.
    """
    # __init__ is inherited
    manager: 'FileManager'  # manager must be a FileManager

    def run(self) -> CaseResults:
        """
        Runs the code in the target file in an empty environment (except
        that `__name__` is set to `'__main__'`, to make the file behave
        as if it were run as the main file).

        Note that the code is read and parsed when the `FileManager` is
        created, not when the test case is run.
        """
        def payload() -> PayloadResult:
            "Payload function to run a file."
            global _RUNNING_TEST_CODE

            # Fetch syntax tree from our manager
            node = self.manager.syntax_tree

            if node is None:
                raise RuntimeError(
                    "Manager of a FileCase was missing a syntax tree!"
                )

            # Compile the syntax tree
            # TODO: This type:ignore is because of a bug in mypy, I
            # think, where an overloaded compile handling AST input has
            # not been provided. Remove it if that gets fixed?
            code = compile(node, self.manager.target, 'exec')  # type:ignore

            # Run the code, setting __name__ to __main__ (this is
            # why we don't just import the file)
            env = {"__name__": "__main__"}
            try:
                _RUNNING_TEST_CODE = True
                exec(code, env)
            finally:
                _RUNNING_TEST_CODE = False

            # Running a file doesn't have a result value, but it does
            # provide a module scope.
            return (NoResult, deepish_copy(env))

        return self._run(payload)

    def trialDetails(self) -> TrialDetails:
        """
        Returns a pair of strings containing base and extra details
        describing what was tested by this test case. If the base
        details capture all available information, the extra details
        value will be None.
        """
        return (
            f"Ran file '{self.manager.target}'",
            None  # no further details to report
        )


class FunctionCase(TestCase):
    """
    Calls a particular function with specific arguments when run.
    """
    manager: 'FunctionManager'

    def __init__(
        self,
        manager: 'FunctionManager',
        args: Optional[Sequence[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        The arguments and/or keyword arguments to be used for the case
        are provided after the manager (as a list/tuple and a dictionary,
        NOT as actual arguments). If omitted, the function will be called
        with no arguments.
        """
        super().__init__(manager)
        self.args = args or ()
        self.kwargs = kwargs or {}

    def run(self) -> CaseResults:
        """
        Runs the target function with the arguments specified for this
        case. The 'result' slot of the `self.results` dictionary that it
        creates holds the return value of the function. The 'scope' slot
        will hold a copy of the global scope that the function runs in,
        which includes the definition of the function itself. Note that
        this is NOT the local scope of the function containing the
        function's local variables.
        """
        def payload() -> PayloadResult:
            "Payload for running a function with specific arguments."
            global _RUNNING_TEST_CODE
            try:
                # Deepish copy of function's module's dict or of its
                # __globals__, otherwise dict w/ just function defined
                # in it.
                targetScope = self.manager.buildScope()

                # Run the function with specified arguments
                _RUNNING_TEST_CODE = True
                result = (
                    self.manager.target(*self.args, **self.kwargs),
                    targetScope
                )
            finally:
                _RUNNING_TEST_CODE = False
            return result

        return self._run(payload)

    def trialDetails(self) -> TrialDetails:
        """
        Returns a pair of strings containing base and extra details
        describing what was tested by this test case. If the base
        details capture all available information, the extra details
        value will be None.
        """
        # Show function name + args, possibly with some abbreviation
        fn = cast(FunctionType, self.manager.target)
        msg = f"Called function '{fn.__name__}'"

        args = self.args if self.args is not None else []
        kwargs = self.kwargs if self.args is not None else {}
        all_args = len(args) + len(kwargs)

        argnames = fn.__code__.co_varnames[:all_args]
        if len(args) > len(argnames):
            msg += " with too many arguments (!):"
        elif all_args > 0:
            msg += " with arguments:"

        # TODO: Proper handling of *args and **kwargs entries!

        # Create lists of full and maybe-abbreviated argument
        # strings
        argstrings = []
        short_argstrings = []
        for i, arg in enumerate(args):
            if i < len(argnames):
                name = argnames[i]
            else:
                name = f"extra argument #{i - len(argnames) + 1}"
            short_name = ellipsis(name, 20)

            argstrings.append(f"{name} = {repr(arg)}")
            short_argstrings.append(
                f"{short_name} = {ellipsis(repr(arg), 60)}"
            )

        # Order kwargs by original kwargs order and then by natural
        # order of kwargs dictionary
        keyset = set(kwargs)
        ordered = list(filter(lambda x: x in keyset, argnames))
        rest = [k for k in kwargs if k not in ordered]
        for k in ordered + rest:
            argstrings.append(f"{k} = {repr(kwargs[k])}")
            short_name = ellipsis(k, 20)
            short_argstrings.append(
                f"{short_name} = {ellipsis(repr(kwargs[k]), 60)}"
            )

        full_args = '  ' + '\n  '.join(argstrings)
        # In case there are too many arguments
        if len(short_argstrings) < 20:
            short_args = '  ' + '\n  '.join(short_argstrings)
        else:
            short_args = (
                '  '
              + '\n  '.join(short_argstrings[:19])
              + f"...plus {len(argstrings) - 19} more arguments..."
            )

        if short_args == full_args:
            return (
                msg + '\n' + short_args,
                None
            )
        else:
            return (
                msg + '\n' + short_args,
                "Full arguments were:\n" + full_args
            )


class BlockCase(TestCase):
    """
    Executes a block of code (provided as text) when run. Per-case
    variables may be defined for the execution environment, which
    otherwise just has builtins.
    """
    manager: 'BlockManager'

    def __init__(
        self,
        manager: 'BlockManager',
        assignments: Optional[Dict[str, Any]] = None
    ):
        """
        A dictionary of variable name : value assignments may be
        provided and these will be inserted into the execution
        environment for the code block. If omitted, no extra variables
        will be defined (this means that global variables available when
        the test manager and/or code block is set up are NOT available to
        the code in the code block by default).
        """
        super().__init__(manager)
        self.assignments = assignments or {}

    def run(self) -> CaseResults:
        """
        Compiles and runs the target code block in an environment which
        is empty except for the assignments specified in this case (and
        builtins).
        """
        def payload() -> PayloadResult:
            "Payload for running a code block specific variables active."
            global _RUNNING_TEST_CODE
            env = dict(self.assignments)
            try:
                _RUNNING_TEST_CODE = True
                exec(self.manager.code, env)
            finally:
                _RUNNING_TEST_CODE = False
            return (NoResult, deepish_copy(env))

        return self._run(payload)

    def trialDetails(self) -> TrialDetails:
        """
        Returns a pair of strings containing base and extra details
        describing what was tested by this test case. If the base
        details capture all available information, the extra details
        value will be None.
        """
        block = self.manager.code
        short = limited_repr(block)
        if block == short:
            # Short enough to show whole block
            return (
                "Ran code:\n" + indent(block, 2),
                None
            )

        else:
            # Too long to show whole block in short view...
            return (
                "Ran code:\n" + indent(short, 2),
                "Full code was:\n" + indent(block, 2)
            )


class SkipCase(TestCase):
    """
    A type of test case which actually doesn't run checks, but instead
    prints a message that the check was skipped.
    """
    # __init__ is inherited

    def run(self) -> CaseResults:
        """
        Since there is no real test, our results are fake. The keys
        "error" and "traceback" have None as their value, and "output"
        also has None. We add a key "skipped" with value True.
        """
        self.results: CaseResults = {
            "result": Skipped,
            "output": '',
            "error": None,
            "traceback": None,
            "scope": {}
        }
        return self.results

    def trialDetails(self) -> TrialDetails:
        """
        Provides a pair of topic/details strings about this test.
        """
        return (f"Skipped check of '{self.manager.target}'", None)

    def checkReturnValue(self, _: Any) -> None:
        """
        Skips the check.
        """
        self._print_skip_message(
            tag_for(get_my_location()),
            "testing target not available"
        )

    def checkVariableValue(self, *_: Any, **__: Any) -> None:
        """
        Skips the check.
        """
        self._print_skip_message(
            tag_for(get_my_location()),
            "testing target not available"
        )

    def checkPrintedLines(self, *_: Any, **__: Any) -> None:
        """
        Skips the check.
        """
        self._print_skip_message(
            tag_for(get_my_location()),
            "testing target not available"
        )

    def checkPrintedFragment(self, *_: Any, **__: Any) -> None:
        """
        Skips the check.
        """
        self._print_skip_message(
            tag_for(get_my_location()),
            "testing target not available"
        )

    def checkFileLines(self, *_: Any, **__: Any) -> None:
        """
        Skips the check.
        """
        self._print_skip_message(
            tag_for(get_my_location()),
            "testing target not available"
        )

    def checkCustom(self, *_: Any, **__: Any) -> None:
        """
        Skips the check.
        """
        self._print_skip_message(
            tag_for(get_my_location()),
            "testing target not available"
        )


class SilentCase(TestCase):
    """
    A type of test case which actually doesn't run checks, and also
    prints nothing. Just exists so that errors won't be thrown when
    checks are attempted. Testing methods return `None` instead of `True`
    or `False`, although this is not counted as a test failure.
    """
    # __init__ is inherited

    def run(self) -> CaseResults:
        "Returns fake empty results."
        self.results = {
            "result": Skipped,
            "output": '',
            "error": None,
            "traceback": None,
            "scope": {}
        }
        return self.results

    def trialDetails(self) -> TrialDetails:
        """
        Provides a pair of topic/details strings about this test.
        """
        return ("Silently skipped check", None)

    def checkReturnValue(self, _: Any) -> None:
        "Returns `None`."
        return None

    def checkVariableValue(self, *_: Any, **__: Any) -> None:
        "Returns `None`."
        return None

    def checkPrintedLines(self, *_: Any, **__: Any) -> None:
        "Returns `None`."
        return None

    def checkPrintedFragment(self, *_: Any, **__: Any) -> None:
        "Returns `None`."
        return None

    def checkFileLines(self, *_: Any, **__: Any) -> None:
        "Returns `None`."
        return None

    def checkCustom(self, *_: Any, **__: Any) -> None:
        "Returns `None`."
        return None


#------------------------------#
# Docstring & Doctest Handling #
#------------------------------#

def extractLiteralStrings(
    src: Union[str, ast.AST],
    offset: int = 0
) -> List[Tuple[str, int]]:
    """
    Given a string containing Python source code, or an `ast.AST` node
    representing parsed source code, extracts all literal strings
    defined anywhere in the code and returns a list of them, where each
    string is paired with the line number within the string that it
    starts on. The given `offset` value (default 0) is added to the line
    number for each result.

    For example:

        >>> s ='''\\
        ... 'hi'
        ... 
        ... x = 'string'
        ... 
        ... def f():
        ...     'doc'
        ...     return 'result'
        ... '''
        >>> extractLiteralStrings(s)
        [('hi', 1), ('string', 3), ('doc', 6), ('result', 7)]
        >>> extractLiteralStrings(s, 10)
        [('hi', 11), ('string', 13), ('doc', 16), ('result', 17)]
    """
    # Parse a string into an AST if necessary
    if isinstance(src, str):
        src = ast.parse(src)

    result = []
    for node in ast.walk(src):
        if isinstance(node, ast.Constant) and type(node.value) == str:
            result.append((node.value, node.lineno + offset))

    return result


class NotCached:
    """
    Unique object used to identify situations where a value which could
    be `None` is not cached.
    """
    pass


class DocChecks(Trial):
    """
    Represents one or more checks performed against code docstrings
    (including doctest examples). Like a `TestCase`, it can have
    outcomes (one for each check performed) and is tracked globally.
    """
    def __init__(self, manager: 'TestManager') -> None:
        """
        A manager must be specified, but that's it.
        """
        super().__init__(manager)

        # How to describe this trial
        self.description = f"docstring checks for {self.manager.tag}"

        # Used to cache doctest extractions
        self._tests: Optional[List[doctest.DocTest]] = None

        # Used to cache docstring
        self._docstring: Union[str, Type[NotCached], None] = NotCached

    def trialDetails(self) -> TrialDetails:
        """
        The base details describe what kind of code was run; the full
        details include the number of doctest examples found.
        """
        baseDetails = self.manager.checkDetails()

        # Get count of doctest examples
        if self._tests is not None:
            exCount = sum(len(test.examples) for test in self._tests)
            return (baseDetails, f"Docstrings included {exCount} examples.")
            # TODO: More detail for these full details?
        else:
            return (baseDetails, "No doctest examples were found.")
        # TODO: Account for different types of tests we can perform
        # besides doctest checks?

    def getDocstring(self) -> Optional[str]:
        """
        Retrieves the docstring for the code associated with this
        trial's manager, which is either the `__doc__` attribute of this
        manager's target if it is a function, or any initial string
        literal in this manager's code. If it's not a function, the
        initial AST note must be an `ast.Expr` that has an
        `ast.Constant` as its value which in turn has a string value.
        The result gets cached.
        """
        if self._docstring is not NotCached:  # use cache if available
            return cast(Optional[str], self._docstring)

        # Is it a function? then use __doc__
        if isinstance(self.manager.target, FunctionType):
            self._docstring = self.manager.target.__doc__
            return self._docstring
        else:
            # Otherwise get the code and extract any initial constant
            # AST node's string value.
            if self.manager.code is None:
                self._docstring = None
                return self._docstring
            else:
                self._docstring = None
                tree = ast.parse(self.manager.code)
                if not isinstance(tree, ast.Module) or len(tree.body) == 0:
                    # Did we even parse a Module obj? Did it have a body?
                    return self._docstring  # None
                first = tree.body[0]
                if not isinstance(first, ast.Expr):
                    # Is the first thing in the body an expression?
                    return self._docstring  # None
                const = first.value
                if not isinstance(const, ast.Constant):
                    # Is the expression's value a constant?
                    return self._docstring  # None
                result = const.value
                if not isinstance(result, str):
                    # Is it a string constant?
                    return self._docstring  # None

                # An actual docstring
                self._docstring = result
                return self._docstring

    def checkHasDocstring(self) -> Optional[bool]:
        """
        Performs a check for whether the target of this trial has a
        non-empty docstring or not. Returns `True` if there is any
        non-whitespace character in the docstring for the
        file/code-block/function this trial is associated with, or
        `False` if not. Returns `None` if the check is skipped.
        """
        if self._should_skip():
            self._print_skip_message(self.tag, "prior test failed")
            return None
        else:
            # Get tag for this check
            tag = tag_for(get_my_location())

            # Get docstring
            ourDoc = self.getDocstring()

            # Must be a string & not empty when stripped
            passed = ourDoc is not None and ourDoc.strip() != ''

            # Base message for result
            if passed:
                base_msg = "Docstring is present and not empty."
            else:
                base_msg = "Docstring was absent or empty."

            # Extra message reports on whether docstring was
            # present/absent
            if ourDoc is None:
                extra_msg = "No docstring was present."
            elif len(ourDoc) > 0 and ourDoc.strip() == '':
                extra_msg = "Found a docstring but it was empty."
            else:
                if "'''" in ourDoc:
                    quote = '"""'
                else:
                    quote = "'''"
                extra_msg = f"Found docstring:\n{quote}\n{ourDoc}\n{quote}"

            # Create success/failure message
            msg_cat: MessageCategory
            if passed:
                msg = self._create_success_message(tag, base_msg, extra_msg)
                msg_cat = "succeeded"
            else:
                msg = self._create_failure_message(tag, base_msg, extra_msg)
                msg_cat = "failed"

            # Print our message
            print_message(msg, color=msg_color(msg_cat))

            # Record outcome
            self._register_outcome(passed, tag, msg)

            return passed

    def getDocTests(self) -> List[doctest.DocTest]:
        """
        Returns a list of `doctest.DocTest` objects for any doctest
        defined in a literal string by the code that this trial's
        manager tests.

        - Returns all doctests defined in any string literal anywhere
            within the code associated with this trial's manager. This
            is both broader and narrower than how the `doctest` module
            finds doctests: It's broader because non-docstring strings
            can have doctests in them, and it's narrower because
            doctests in dynamically-established docstrings won't be
            considered.
        - Must run the code in order to extract doctests except for
            `FunctionManager`s, because it needs to set them up to run
            in an environment where the code's functions/variables have
            been defined.
            * For `FunctionManager`s, there's no automatic way to run
                the code without knowing which arguments to use, but in
                any case, tests just need to run in the context of the
                function's module, which is available via the
                `__module__` attribute of the function. For functions
                defined dynamically (e.g., via `exec` within a custom
                scope) `__module__` will be `None`, in which case we
                don't have access to the scope within which they were
                defined. We run these in a custom scope which only
                includes a definition for the function being tested.
            * In all cases, we use `buildScope` to create the scope
                which creates a `deepish_copy` of the scope so that we
                can prevent global effects leakage from tests as much as
                possible. However, things like edits to global variables
                will still leak, because functions bind to their original
                context when determining things like which global
                variable value to edit.
        - Creates a trial that is used to run the block of code. This
            trial does not hold any outcomes and is not used later on.
        - Only runs the given block of code one time, and caches
            extracted tests, so if you call it again it will just return
            the same values. Create a fresh manager if the underlying
            code changes.
        """
        if self._tests is not None:  # caches the results
            return self._tests 

        # Create a parser to extract doc tests from docstrings
        parser = doctest.DocTestParser()

        # Figure out name for the tests
        target = self.manager.target
        testsName: str
        filename: str
        if isinstance(target, (types.FunctionType, types.MethodType)):
            # Tests name is just the function name
            testsName = target.__name__
            # Use code's filename if we can
            if hasattr(target, '__code__'):
                filename = target.__code__.co_filename
            else:
                # Otherwise just use function's name
                filename = f"function filename.__name__"
        else:
            testsName = target
            filename = target

        # Get a scope to run tests in
        testsScope = self.manager.buildScope()

        # Get AST or code source to extract strings from
        extract_from: Union[str, ast.AST, None] = self.manager.syntax_tree
        if extract_from is None:
            extract_from = self.manager.code
            if extract_from is None:
                raise RuntimeError(
                    "Cannot get doctests from a manager that does not"
                    f" have any associated code."
                )

        offset = 0
        if (
            isinstance(self.manager, FunctionManager)
        and hasattr(self.manager.target, "__code__")
        ):
                offset = self.manager.target.__code__.co_firstlineno

        # Extract *ALL* strings from the source code
        strings = extractLiteralStrings(extract_from, offset)

        # Create blank list for tests & populate w/ parse results from
        # each string we found.
        self._tests = []
        for string, line in strings:
            self._tests.append(
                parser.get_doctest(
                    string,
                    testsScope,  # globals = testing scope
                    testsName,  # name
                    filename,  # filename
                    line  # lineno
                )
            )

        return self._tests

    def checkDocTestsPass(self) -> Optional[bool]:
        """
        Gets doc tests using `getDocTests` and runs each discovered test
        block, reporting success/failure messages and registering one
        outcome from each test block.

        Returns `True` if all examples in all tested blocks succeeded,
        and there was at least one example. Returns `False` if any
        example in any tested block failed, or if there were no examples
        to test (use `checkDocTestCount` for establishing more granular
        restrictions on how many examples there are). Returns `None` if
        all of the checks were skipped (e.g., due to a prior failure on
        this manager).

        Note that this may change values that are part of the cached code
        results and/or the scope within which a tested function was
        defined, for example if the doctests call a function that changes
        a global variable (see `getDocTests`).

        This re-runs the tests each time you run it.
        """
        tag = tag_for(get_my_location())

        # Single skip message for all examples if we should skip
        if self._should_skip():
            self._print_skip_message(tag, "prior test failed")
            return None

        tests = self.getDocTests()

        # Special message for no tests
        if len(tests) == 0 or len(tests) == 1 and len(tests[0].examples) == 0:
            msg = self._create_failure_message(
                tag,
                "No doctests were found."
            )
            print_message(msg, color=msg_color("failed"))
            self._register_outcome(False, tag, msg)
            return False

        result = None
        for test in tests:  # Each example has an outcome
            # Skip individual examples (e.g. if one fails)
            if self._should_skip():
                self._print_skip_message(tag, "prior test failed")
                continue
            # Create runner & run tests
            runner = DocTestIntercepter(self, tag)
            # This prints & registers outcomes
            failed, attempted = runner.run(test)
            if failed > 0:
                result = False
            elif result is None and attempted > 0:
                result = True

        return result

    def checkDocTestCount(
        self,
        minimum: int = 1,
        include: Optional[List[Union[str, 'ASTRequirement']]] = None,
        exclude: Optional[List[Union[str, 'ASTRequirement']]] = None
    ) -> Optional[bool]:
        """
        Check that docstrings define at least the specified minimum
        number of *distinct* examples (default 1). Returns `True` if they
        do, `False` if they don't, or `None` if the check was skipped.

        Note that each '>>>' line in a doctest is an 'example' even if
        it's just part of a larger conceptual 'test'. For example,
        calling a function and then checking the length & first element
        of its return value would count as 3 tests. Also, duplicates are
        filtered based on the AST dump of the line concatenated with the
        expectation, so if the same code is used repeatedly with the same
        result, we only count it once.

        `include` and/or `exclude` lists of `ASTRequirement` objects
        and/or strings can be provided (strings are converted to
        `ASTRequirement`s):

        - If `include` is not `None` (the default), then only
            `doctest.Example`s whose code contains *all* of the
            specified structures will count towards the requirement (but
            if the minimum requirement is not met, the full example
            count will also be reported). You can use a `MatchAny` as
            part of the list to allow alternatives.
        - If `exclude` is not `None`, then any `doctest.Example` whose
            code matches *any* of the listed requirements will not count
            towards the minimum.
        """
        tag = tag_for(get_my_location())

        # Skip if required
        if self._should_skip():
            self._print_skip_message(tag, "prior check failed")
            return None

        # Normalize include/exclude
        if include is None:
            include = []
        mustHave: List[ASTRequirement] = [
            x if isinstance(x, ASTRequirement) else ExactMatch(x)
            for x in include
        ]
        if exclude is None:
            exclude = []
        mustAvoid: List[ASTRequirement] = [
            x if isinstance(x, ASTRequirement) else ExactMatch(x)
            for x in exclude
        ]

        # Get our tests
        tests = self.getDocTests()
        # Set of unique ast dumps we've seen so far
        seen: Set[str] = set()
        # Number of duplicates observed
        dupes = 0
        for test in tests:
            for ex in test.examples:
                # Parse the example & dump it for a canonical repr
                tree = ast.parse(ex.source)
                dump = ast.dump(tree)
                key = dump + '|' + ex.want
                counts = True

                if key in seen:  # duplicates one we've seen before
                    dupes += 1
                    continue  # this one doesn't count; skip to next

                # Check all inclusion criteria
                for mustMatch in mustHave:
                    if not mustMatch.allMatches(tree).isFull:
                        counts = False
                        break

                # If those passed, check all exclusion criteria
                if counts:
                    for mustNot in mustAvoid:
                        if mustNot.allMatches(tree).isFull:
                            counts = False
                            break
                if counts:
                    seen.add(key)

        # Check whether we met the requirement
        total = len(seen)
        success = total >= minimum

        # Create base + extra messages about the outcome
        only = ""
        if not success:
            only = "only "

        matching = ""
        if include or exclude:
            matching = " matching"

        # Message fragment about dupes
        dupeMsg = ''
        if dupes > 0:
            dupeMsg = f"; ignored {dupes} duplicates"

        # Base message reports total & minimum
        base_msg = (
            f"Found {only}{total}{matching} distinct doctest example(s)"
            f" (required {minimum}{dupeMsg})."
        )

        # Extra message explains include/exclude filters
        if not include and not exclude:
            extra_msg = "Counted all examples."
        else:
            extra_msg = "Counted only examples..."
            if include:
                extra_msg += '\n...which contained:' + '\nAND\n'.join(
                    incl.fullStructure() for incl in mustHave
                )
            if exclude:
                extra_msg += '\n...which did NOT contain:' + '\nOR\n'.join(
                    excl.fullStructure() for excl in mustAvoid
                )

        # Set up result message & category
        msg_cat: MessageCategory
        if success:
            msg = self._create_success_message(tag, base_msg, extra_msg)
            msg_cat = "succeeded"
        else:
            msg = self._create_failure_message(tag, base_msg, extra_msg)
            msg_cat = "failed"

        # Print our message
        print_message(msg, color=msg_color(msg_cat))

        # Record outcome
        self._register_outcome(success, tag, msg)

        return success


class DocTestIntercepter(doctest.DocTestRunner):
    """
    Inherits from `DocTestRunner` in the `doctest` module and overrides
    report functions so it can use the associated `Trial` (basically
    always a `DocCheck`) to report success/failure of doctests in the
    optimism style and also register them as outcomes.
    """
    def __init__(
        self,
        trial: Trial,
        tag: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        in addition to a `Trial` and a code location tag to be used when
        reporting success/failure, takes the same arguments as
        `doctest.DocTestRunner.__init__()` and passes them through. All
        results of tests using this runner will be reported as outcomes
        for the given trial.
        """
        # TODO: HERE
        # TODO: Turn IGNORE_EXCEPTION_DETAIL on by default
        # TODO: Document that!
        if len(args) < 3 and 'optionflags' not in kwargs:
            kwargs['optionflags'] = doctest.IGNORE_EXCEPTION_DETAIL
        super().__init__(*args, **kwargs)
        self.trial = trial
        self.tag = tag

    def reportOutcome(
        self,
        test: doctest.DocTest,
        example: doctest.Example,
        succeeded: bool,
        got: str
    ) -> None:
        """
        Common outcome-reporting function for success or failure. Prints
        a success or failure message for the given test/example built
        using the given expected/got strings.
        """
        # reports that the example's expectation

        # Figure out line number where doctest was defined
        if test.lineno is None:
            line = None
        else:
            line = test.lineno + example.lineno + 1

        # Figure out filename where doctest was defined & build 'at'
        # string describing where the test is
        if test.filename:
            at = "At " + tag_for({"file": test.filename, "line": line})
        else:
            at = f"In a doctest from {self.trial.manager.target}"

        msg_cat: MessageCategory
        if succeeded:
            info = f"""\
{at}, output matched what the test expected:
{indent(example.want, 2)}"""
            # TODO: add extra message w/ 'got' included if they don't
            # match 1:1?
            message = self.trial._create_success_message(self.tag, info)
            msg_cat = "succeeded"
        else:
            info = f"""\
{at}, output didn't match what the test expected. Expected:
{indent(example.want, 2)}
Got:
{indent(got, 2)}"""
            message = self.trial._create_failure_message(self.tag, info)
            msg_cat = "failed"

        # Print the message in the appropriate color
        print_message(message, color=msg_color(msg_cat))

        # registers an outcome triple with the trial
        self.trial._register_outcome(succeeded, self.tag, message)

    def report_success(
        self,
        out: Callable[[str], object],
        test: doctest.DocTest,
        example: doctest.Example,
        got: str
    ) -> None:
        """
        Callback for the doctest running system to use when an example
        succeeds. Reports that the given example ran successfully and
        registers the outcome our trial.
        """
        self.reportOutcome(test, example, True, got)

    def report_failure(
        self,
        out: Callable[[str], object],
        test: doctest.DocTest,
        example: doctest.Example,
        got: str
    ) -> None:
        """
        Like `report_success` but for failed examples.
        """
        self.reportOutcome(test, example, False, got)

    def report_unexpected_exception(
        self,
        out: Callable[[str], object],
        test: doctest.DocTest,
        example: doctest.Example,
        exc_info: Any
    ) -> None:  #TODO: figure out type
        """
        Callback for unexpected exceptions. Includes traceback info in
        its message.
        """
        exc_type, exc_val, exc_tb = exc_info
        tb = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
        message = f"Unexpected exception:\n{indent(tb,2)}"

        self.reportOutcome(test, example, False, message)


#----------------------#
# Test Manager Classes #
#----------------------#

CT = TypeVar('CT', bound=TestCase)
"""
A 'case-type' type variable for the `TestManager` superclass. Types used
must be subclasses of `TestCase`.
"""


class TestManager(Generic[CT]):
    """
    Abstract base class for managing tests for a certain function, file,
    or block of code. Create these using the `testFunction`, `testFile`,
    and/or `testBlock` factory functions. The `TestManager.case`
    function can be used to derive `TestCase` objects which can then be
    used to set up checks.

    It can also be used to directly check structural properties of the
    function, file, or block it manages tests for TODO
    """
    case_type: Type[CT]
    """
    The case type determines what kind of test case will be constructed
    when calling the `TestManager.case` method. Subclasses override
    this.
    """

    target: Union[str, FunctionType]
    """
    A string description of what we're testing, for use in outcome
    messages, or if we're testing a function, the function object that
    we're testing.
    """

    code: Optional[str]
    """
    The source code for the thing we're testing, if available.
    """

    syntax_tree: Optional[ast.AST]
    """
    Where source code is available, the parsed abstract syntax tree of
    that code.
    """

    any_failed: bool
    """
    Whether or not any of the `Trial`s associated with this manager has
    failed.
    """

    tag: str
    """
    The filename-colon-line-number string indicating where this manager
    was created.
    """

    code_checks: Optional[CodeChecks]
    """
    The singular `CodeChecks` `Trial` that we attach every code check
    to, since all code checks have the same context. Will remain `None`
    until a code check is performed.
    """

    doc_checks: Optional[DocChecks]
    """
    The singular `DocChecks` `Trial` that we attach every docstring
    check to, since they all have the same context. Note that this is
    not the trial used to run the code when harvesting docstrings that
    establishes the scope within which we'll run them.
    """

    def __init__(
        self,
        target: Union[str, FunctionType],
        code: Optional[str]
    ) -> None:
        """
        A testing target (a filename string, function object, code
        string, or test label string) must be provided. The relevant
        code text must also be provided, although this can be set to
        None in cases where it isn't available.
        """
        self.target = target

        self.code = code

        if code is not None:
            self.syntax_tree = ast.parse(code, filename=self.codeFilename())
        else:
            self.syntax_tree = None

        # Keeps track of whether any cases derived from this manager have
        # failed so far
        self.any_failed = False

        self.tag = tag_for(get_my_location())

        self.code_checks = None

        self.doc_checks = None

    def codeFilename(self):
        """
        Returns the filename to be used when parsing the code for this
        test case.
        """
        return f"code specified at {self.tag}"

    def checkDetails(self) -> str:
        """
        Returns base details string describing what code was checked for
        a `checkCodeContains` check.
        """
        return "checked unknown code"

    def case(self) -> CT:
        """
        Returns a `TestCase` object that will test the target
        file/function/block. Some manager types allow arguments to this
        function.
        """
        return self.case_type(self)

    def checkCodeContains(self, checkFor: 'ASTRequirement') -> Optional[bool]:
        """
        Given an `ASTRequirement` object, ensures that some part of the
        code that this manager would run during a test case contains the
        structure specified by that check object. Immediately performs
        the check and prints a pass/fail message. The check's result will
        be added to the `CodeChecks` outcomes for this manager; a new
        `CodeChecks` trial will be created and registered if one hasn't
        been already.

        Returns `True` if the check succeeds and `False` if it fails
        (including cases where there's a partial match). Returns `None`
        if the check was skipped.
        """
        # Create a code checks trial if we haven't already
        if self.code_checks is None:
            self.code_checks = CodeChecks(self)
        trial = self.code_checks

        return trial.performCheck(checkFor)

    def buildScope(self) -> Dict[str, Any]:
        """
        Runs the associated code in order to build a scope within which
        doctests can execute properly. If the manager is a function
        manager, just copies that function's module's scope, or creates
        a scope containing just that function, without actually running
        the function. Actually runs the code for file and block
        managers.

        Creates a deepish copy of the resulting scope, to try to avoid
        altering it when tests are run, but mutable custom objects that
        aren't deep-copyable could potentially be changed by code in a
        doctest, and when functions use global variables, these will
        remain bound back into the original scope.
        """
        case = self.case_type(self)
        # Note: 'scope' from fetchResults is already a deepish copy of
        # the env used to 
        return case.fetchResults()['scope']

    def validateTrace(self) -> Optional[bool]:
        """
        Not implemented yet.
        """
        raise NotImplementedError(
            "validateTrace is a planned feature, but has not been"
            " implemented yet."
        )

    def getDocstring(self) -> Optional[str]:
        """
        Gets the docstring for the code associated with this manager if
        there is one. Looks for a string constant that's the first
        thing in the body of the code. See `DocChecks.getDocstring`.
        """
        if self.doc_checks is None:
           self.doc_checks = DocChecks(self)

        return self.doc_checks.getDocstring()

    def getDocTests(self) -> List[doctest.DocTest]:
        """
        Gets doctests for the associated code. See
        `DocChecks.getDocTests`.
        """
        if self.doc_checks is None:
           self.doc_checks = DocChecks(self)

        return self.doc_checks.getDocTests()

    def checkHasDocstring(self) -> Optional[bool]:
        """
        See `DocChecks.checkHasDocstring`.
        """
        if self.doc_checks is None:
           self.doc_checks = DocChecks(self)

        return self.doc_checks.checkHasDocstring()

    def checkDocTestsPass(self) -> Optional[bool]:
        """
        See `DocChecks.checkDocTestsPass`.
        """
        if self.doc_checks is None:
           self.doc_checks = DocChecks(self)

        return self.doc_checks.checkDocTestsPass()

    def checkDocTestCount(
        self,
        minimum: int = 1,
        include: Optional[List[Union[str, 'ASTRequirement']]] = None,
        exclude: Optional[List[Union[str, 'ASTRequirement']]] = None
    ) -> Optional[bool]:
        """
        See `DocChecks.checkDocTestCount`.
        """
        if self.doc_checks is None:
           self.doc_checks = DocChecks(self)

        return self.doc_checks.checkDocTestCount(minimum, include, exclude)


class FileManager(TestManager[FileCase]):
    """
    Manages test cases for running an entire file. Unlike other
    managers, cases for a file cannot have parameters. Calling
    `TestCase.provideInputs` on a case to provide inputs still means
    that having multiple cases can be useful, however.
    """
    case_type = FileCase
    target: str  # target value is a filename string

    def __init__(self, filename: str) -> None:
        """
        A FileManager needs a filename string that specifies which file
        we'll run when we run a test case.
        """
        if not isinstance(filename, str):
            raise TypeError(
                f"For a file test manager, the target must be a file"
                f" name string. (You provided a/an {type(filename)}.)"
            )

        with open(filename, 'r') as inputFile:
            code = inputFile.read()

        super().__init__(filename, code)

    def codeFilename(self) -> str:
        return self.target

    def checkDetails(self) -> str:
        return f"checked code in file '{self.target}'"

    # case is inherited as-is


class FunctionManager(TestManager):
    """
    Manages test cases for running a specific function. Arguments to the
    `TestManager.case` function are passed to the function being tested
    for that case.
    """
    case_type = FunctionCase
    target: FunctionType

    def __init__(self, function: FunctionType) -> None:
        """
        A FunctionManager needs a function object as the target. Each
        case will call that function with arguments provided when the
        case is created.
        """
        if not isinstance(function, FunctionType):
            raise TypeError(
                f"For a function test manager, the target must be a"
                f" function. (You provided a/an {type(function)}.)"
            )

        # We need to track down the source code for this function;
        # luckily the inspect module makes that easy :)
        try:
            sourceCode = inspect.getsource(function)
        except OSError:
            # In some cases code might not be available, for example
            # when testing a function that was defined using exec.
            sourceCode = None

        super().__init__(function, sourceCode)

    def codeFilename(self) -> str:
        return f"function {self.target.__name__}"

    def checkDetails(self) -> str:
        return f"checked code of function '{self.target.__name__}'"

    def case(self, *args: Any, **kwargs: Any) -> FunctionCase:
        """
        Arguments supplied here are used when calling the function which
        is what happens when the case is run. Returns a `FunctionCase`
        object.
        """
        return self.case_type(self, args, kwargs)

    def buildScope(self) -> Dict[str, Any]:
        """
        Copies the target function's module's scope, or copies the
        target function's __globals__ dict, or creates a scope
        containing just the target function. Does not actually run the
        function.

        The copies are deepish copies, so some un-deep-copyable mutable
        stuff may still be shared.
        """
        # What module does it come from? (might be None)
        targetMod = self.target.__module__
        if targetMod in sys.modules:  # is that module listed?
            # Okay return a copy of that module's dict
            return deepish_copy(sys.modules[targetMod].__dict__)
        elif hasattr(self.target, '__globals__'):
            # Maybe it has a __globals__ dict directly?
            return deepish_copy(self.target.__globals__)
        else:
            # No module available, so just return scope with the
            # function by itself
            return {self.target.__name__: self.target}


class BlockManager(TestManager[BlockCase]):
    """
    Manages test cases for running a block of code (from a string).
    Keyword arguments to the `TestManager.case` function are defined as
    variables before the block is executed in that case.
    """
    case_type = BlockCase
    target: str  # A string description of where the block was defined
    code: str  # code is non-optional here

    def __init__(self, code: str, includeGlobals: bool = False) -> None:
        """
        A BlockManager needs a code string as the target (the actual
        target value will be set to a string describing where
        `testBlock` was called or the `BlockTest` was create).
        Optionally, the `use_globals` argument (default `False`) can be
        set to `True` to make globals defined at case-creation time
        accessible to the code in the case.
        """
        if not isinstance(code, str):
            raise TypeError(
                f"For a 'block' test manager, the target must be a"
                f" string. (You provided a/an {type(code)}.)"
            )

        # TODO: This check is good, but avoiding multiple parsing passes
        # might be nice for larger code blocks...
        try:
            ast.parse(code)
        except Exception:
            raise ValueError(
                "The code block you provided could not be parsed as Python"
                " code."
            )

        self.includeGlobals = bool(includeGlobals)

        super().__init__("a code block", code)
        # Now that we have a tag, update our target
        self.target = f"code block from {self.tag}"

    def codeFilename(self) -> str:
        return self.target

    def checkDetails(self) -> str:
        return f"checked code from block at {self.tag}"

    def case(self, **assignments: Dict[str, Any]) -> BlockCase:
        """
        Keyword argument supplied here will be defined as variables
        in the environment used to run the code block, and will override
        any global variable values (which are only included if
        `includeGlobals` was set to true when the manager was created).
        Returns a `BlockCase` object.
        """
        if self.includeGlobals:
            provide = copy.copy(get_external_calling_frame().f_globals)
            provide.update(assignments)
        else:
            provide = assignments

        return self.case_type(self, provide)


class SkipManager(TestManager[SkipCase]):
    """
    Manages fake test cases for a file, function, or code block that
    needs to be skipped (perhaps for a function that doesn't yet exist,
    for example). Cases derived are `SkipCase` objects which just print
    skip messages for any checks requested.
    """
    case_type = SkipCase

    def __init__(self, label: str) -> None:
        """
        Needs a label string to identify which tests are being skipped.
        """
        if not isinstance(label, str):
            raise TypeError(
                f"For a skip test manager, the target must be a string."
                f" (You provided a/an {type(label)}.)"
            )
        super().__init__(label, None)

    def codeFilename(self) -> str:
        return "no code (cases skipped)"

    def checkDetails(self) -> str:
        return "skipped check (no code available)"

    def case(self, *_: Any, **__: Any) -> SkipCase:
        """
        Accepts (and ignores) any extra arguments.
        """
        return super().case()

    def buildScope(self) -> Dict[str, Any]:
        """
        Returns an empty dictionary since we're skipping checks here.
        """
        return {}

    def checkCodeContains(self, checkFor: 'ASTRequirement') -> None:
        """
        Skips checking the AST of the target; see
        `TestManager.checkCodeContains`.
        """
        tag = tag_for(get_my_location())
        # Detail level controls initial message
        if DETAIL_LEVEL < 1:
            msg = f"~ {tag} (skipped)"
        else:
            msg = (
                f"~ code check at {tag} skipped"
            )
        print_message(msg, color=msg_color("skipped"))
        return None

    def checkHasDocstring(self) -> None:
        """
        Skips checking for a docstring; returns `None`.
        """
        tag = tag_for(get_my_location())
        # Detail level controls initial message
        if DETAIL_LEVEL < 1:
            msg = f"~ {tag} (skipped)"
        else:
            msg = (
                f"~ docstring check at {tag} skipped"
            )
        print_message(msg, color=msg_color("skipped"))
        return None

    def checkDocTestsPass(self) -> None:
        """
        Skips checking doctests; returns `None`.
        """
        tag = tag_for(get_my_location())
        # Detail level controls initial message
        if DETAIL_LEVEL < 1:
            msg = f"~ {tag} (skipped)"
        else:
            msg = (
                f"~ doctests check at {tag} skipped"
            )
        print_message(msg, color=msg_color("skipped"))
        return None

    def checkDocTestCount(self, *_: Any, **__: Any) -> None:
        """
        Skips checking doctest count; returns `None`.
        """
        tag = tag_for(get_my_location())
        # Detail level controls initial message
        if DETAIL_LEVEL < 1:
            msg = f"~ {tag} (skipped)"
        else:
            msg = (
                f"~ doctests count check at {tag} skipped"
            )
        print_message(msg, color=msg_color("skipped"))
        return None


class QuietSkipManager(TestManager[SilentCase]):
    """
    Manages fake test cases that should be skipped silently, without any
    notifications. Cases derived are `SilentCase` objects which don't
    print anything.
    """
    case_type = SilentCase

    def __init__(self) -> None:
        """
        No arguments needed.
        """
        super().__init__("ignored", None)

    def codeFilename(self) -> str:
        return "no code (cases skipped)"

    def checkDetails(self) -> str:
        return "skipped check (no code available)"

    def case(self, *_: Any, **__: Any) -> SilentCase:
        """
        Accepts (and ignores) any extra arguments.
        """
        return super().case()

    def buildScope(self) -> Dict[str, Any]:
        """
        Returns an empty dictionary since we're skipping checks here.
        """
        return {}

    def checkCodeContains(self, checkFor: 'ASTRequirement') -> None:
        """
        Skips checking the AST; returns `None`.
        """
        return None

    def checkHasDocstring(self) -> None:
        """
        Skips checking for a docstring; returns `None`.
        """
        return None

    def checkDocTestsPass(self) -> None:
        """
        Skips checking doctests; returns `None`.
        """
        return None

    def checkDocTestCount(self, *_: Any, **__: Any) -> None:
        """
        Skips checking doctest count; returns `None`.
        """
        return None


#----------------#
# Test factories #
#----------------#

def testFunction(fn: FunctionType) -> FunctionManager:
    """
    Creates a test-manager for the given function.
    """
    if not isinstance(fn, FunctionType):
        raise TypeError(
            "Test target must be a function (use testFile or testBlock"
            " instead to test a file or block of code)."
        )

    return FunctionManager(fn)


def testFunctionMaybe(
    module: ModuleType,
    fname: str
) -> Union[SkipManager, FunctionManager]:
    """
    This function creates a test-manager for a named function from a
    specific module, but displays an alternate message and returns a
    dummy manager if that module doesn't define any variable with the
    target name. Useful for defining tests for functions that will be
    skipped if the functions aren't done yet.
    """
    # Message if we can't find the function
    if not hasattr(module, fname):
        print_message(
            f"Did not find '{fname}' in module '{module.__name__}'...",
            color=msg_color("skipped")
        )
        return SkipManager(f"{module.__name__}.{fname}")
    else:
        target = getattr(module, fname)
        if not isinstance(target, FunctionType):
            print_message(
                (
                    f"'{fname}' in module '{module.__name__}' is not a"
                    f" function..."
                ),
                color=msg_color("skipped")
            )
            return SkipManager(f"{module.__name__}.{fname}")
        else:
            return FunctionManager(target)


def testFile(filename: str) -> FileManager:
    """
    Creates a test-manager for running the named file.
    """
    if not isinstance(filename, str):
        raise TypeError(
            "Test target must be a file name (use testFunction instead"
            " to test a function)."
        )

    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"We cannot create a test for running '{filename}' because"
            f" that file does not exist."
        )

    return FileManager(filename)


def testBlock(code: str, includeGlobals: bool = False) -> BlockManager:
    """
    Creates a test-manager for running a block of code (provided as a
    string). If `includeGlobals` is set to true, global variables which
    are defined at the time a case is created from the manager will be
    available to the code in that test case; if not (the default) no
    variables defined outside of the test block are available to the code
    in the block, except for explicit definitions supplied when creating
    a test case (see `BlockManager.case`).
    """
    if not isinstance(code, str):
        raise TypeError(
            "Test target must be a code string (use testFunction instead"
            " to test a function)."
        )

    return BlockManager(code, includeGlobals)


SKIP_NOTEBOOK_CELL_CHECKS: bool = False
"""
If set to true, notebook cell checks will be skipped silently. This is
used to avoid recursive checking problems.
"""

_SKIP_NOTEBOOK_CELL_CHECKS: bool = True
"""
The value for `SKIP_NOTEBOOK_CELL_CHECKS` to restore to when
`endSkippingNotebookCellChecks` is called.
"""


def beginSkippingNotebookCellChecks() -> None:
    """
    Sets `SKIP_NOTEBOOK_CELL_CHECKS` to True, and saves the old value in
    `_SKIP_NOTEBOOK_CELL_CHECKS`.
    """
    global SKIP_NOTEBOOK_CELL_CHECKS, _SKIP_NOTEBOOK_CELL_CHECKS
    _SKIP_NOTEBOOK_CELL_CHECKS = SKIP_NOTEBOOK_CELL_CHECKS
    SKIP_NOTEBOOK_CELL_CHECKS = True


def endSkippingNotebookCellChecks() -> None:
    """
    Sets `SKIP_NOTEBOOK_CELL_CHECKS` back to whatever value was stored
    when `beginSkippingNotebookCellChecks` was called (might not actually
    end skipping, because of that).
    """
    global SKIP_NOTEBOOK_CELL_CHECKS, _SKIP_NOTEBOOK_CELL_CHECKS
    SKIP_NOTEBOOK_CELL_CHECKS = _SKIP_NOTEBOOK_CELL_CHECKS


def testThisNotebookCell(
    includeGlobals: bool = True
) -> Union[QuietSkipManager, BlockManager]:
    """
    Creates a test manager for running code in an IPython (and by
    implication also Jupyter) notebook cell (without any
    other cells being run). The current cell that is executing when the
    function is called is captured as a string and a `BlockManager` is
    created for that string, with `includeGlobals` set to `True` (you
    can override that by providing `False` as an argument to this
    function).

    This function will raise an error if it is called outside of an
    IPython context, although this will not happen if
    `SKIP_NOTEBOOK_CELL_CHECKS` is set (see below).

    If the `SKIP_NOTEBOOK_CELL_CHECKS` global variable is `True`, the
    result will be a special silent `QuietSkipManager` instead of a
    `BlockManager`. The code block captured from the notebook cell is
    augmented to set that variable to True at the beginning and back to
    its original value at the end, to avoid infinite recursion.
    """
    if SKIP_NOTEBOOK_CELL_CHECKS:
        return QuietSkipManager()

    try:
        # get_ipython will be defined as a global in any IPython context
        # This try/except checks for that, which is why we just assume
        # it's available.
        getIP = get_ipython  # type: ignore
        hist = getIP().history_manager  # noqa F821
    except Exception:
        raise RuntimeError(
            "Failed to get IPython context; testThisNotebookCell will"
            " only work when run from within a notebook."
        )

    sessionID = hist.get_last_session_id()
    thisCellCode = next(hist.get_range(sessionID, start=-1, stop=None))[2]
    return BlockManager(
        (
            "import optimism\n"
          + "optimism.beginSkippingNotebookCellChecks()\n"
          + "try:\n"
          + indent(thisCellCode, 4)
          + "\nfinally:\n"
          + "    optimism.endSkippingNotebookCellChecks()\n"
        ),
        includeGlobals
    )


def mark(name: str) -> None:
    """
    Collects the code of the file or notebook cell within which the
    function call occurs, and caches it for later testing using
    `testMarkedCode`. Note that all code in a file or notebook cell is
    collected: if you use `mark` multiple times in the same file each
    `testMarkedCode` call will still test the entire file.

    Also, if this function is called during the run of another test and a
    code block is not available but an old code block was under the same
    name, that old code block will not be modified.
    """
    global _MARKED_CODE_BLOCKS
    block_filename = get_filename(get_external_calling_frame())
    if block_filename is None:
        contents = None
    else:
        contents = ''.join(linecache.getlines(block_filename))
    if contents or not _RUNNING_TEST_CODE:
        _MARKED_CODE_BLOCKS[name] = contents or None


def getMarkedCode(markName: str) -> Optional[str]:
    """
    Gets the block of code (e.g., Python file; notebook cell; etc.)
    within which `mark` was called with the specified name. Returns
    `None` if that information isn't available. Reasons it isn't
    available include that `mark` was never called with that name, and
    that `mark` was called, but we weren't able to extract the source
    code of the block it was called in (e.g., because it was called in
    an interactive interpreter session).
    """
    return _MARKED_CODE_BLOCKS.get(markName)


def testMarkedCode(
    markName: str,
    includeGlobals: bool = True
) -> Union[SkipManager, BlockManager]:
    """
    Creates a test manager for running the code block (e.g., Python file;
    notebook cell; etc.) within which `mark` was called using the given
    mark name. `mark` must have already been called with the specified
    name, and changes to the code around it may or may not be picked up
    if they were made since the call happened. A `BlockManager` is
    created for that code, with `includeGlobals` set based on the value
    provided here (default `True`).

    If no code is available, a `SkipManager` will be returned.
    """
    code = getMarkedCode(markName)
    if code is None:
        print(
            (
                f"Warning: unable to find code for test suite"
                f" '{markName}'. Have you called 'mark' already with"
                f" that name?"
            ),
            file=PRINT_TO
        )
        return SkipManager("Code around mark '{markName}'")
    else:
        return BlockManager(code, includeGlobals)


#----------------#
# Output capture #
#----------------#

class CapturingStream(io.StringIO):
    """
    An output capture object which is an `io.StringIO` underneath, but
    which has an option to also write incoming text to normal
    `sys.stdout`. Call the install function to begin capture.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Passes arguments through to `io.StringIO`'s constructor.
        """
        self.original_stdout: Optional[TextIO] = None
        self.tee = False
        super().__init__(*args, **kwargs)

    def echo(self, doit: bool = True) -> None:
        """
        Turn on echoing to stdout along with capture, or turn it off if
        False is given.
        """
        self.tee = doit

    def install(self) -> None:
        """
        Replaces `sys.stdout` to begin capturing printed output.
        Remembers the old `sys.stdout` value so that `uninstall` can
        work. Note that if someone else changes `sys.stdout` after this
        is installed, uninstall will set `sys.stdout` back to what it was
        when `install` was called, which could cause issues. For example,
        if we have two capturing streams A and B, and we call:

        ```py
        A.install()
        B.install()
        A.uninstall()
        B.uninstall()
        ```

        The original `sys.stdout` will not be restored. In general, you
        must uninstall capturing streams in the reverse order that you
        installed them.
        """
        self.original_stdout = sys.stdout
        sys.stdout = self

    def uninstall(self) -> None:
        """
        Returns `sys.stdout` to what it was before `install` was called,
        or does nothing if `install` was never called.
        """
        if self.original_stdout is not None:
            sys.stdout = self.original_stdout

    def reset(self) -> None:
        """
        Resets the captured output.
        """
        self.seek(0)
        self.truncate(0)

    # Note: we use type: ignore here because mypy CANNOT recognize any
    # possible type declaration here as matching the superclass since in
    # the inheritance chain there are two superclasses that have
    # different types for the first argument (Iterable[Buffer] and
    # Iterable[str]) and these violate the Liskov substitution principle.
    def writelines(self, lines: Iterable[str]):  # type: ignore
        """
        Override writelines to work through write.
        """
        for line in lines:
            self.write(line)

    def write(self, stuff: str) -> int:
        """
        Accepts a string and writes to our capture buffer (and to
        original stdout if `echo` has been called). Returns the number
        of characters written.
        """
        if self.tee and self.original_stdout is not None:
            self.original_stdout.write(stuff)
        return super().write(stuff)


def showPrintedLines(show: bool = True) -> None:
    """
    Changes the testing mechanisms so that printed output produced during
    tests is shown as normal in addition to being captured. Call it with
    False as an argument to disable this.
    """
    global _SHOW_OUTPUT
    _SHOW_OUTPUT = show


#---------------------#
# Debugging functions #
#---------------------#

def differencesAreSubtle(val: str, ref: str) -> bool:
    """
    Judges whether differences between two strings are 'subtle' in which
    case the first difference details will be displayed. Returns true if
    either value is longer than a typical floating-point number, or if
    the representations are the same once all whitespace is stripped
    out.
    """
    # If either has non-trivial length, we'll include the first
    # difference report. 18 is the length of a floating-point number
    # with two digits before the decimal point and max digits afterwards
    if len(val) > 18 or len(ref) > 18:
        return True

    valNoWS = re.sub(r'\s', '', val)
    refNoWS = re.sub(r'\s', '', ref)
    # If they're the same modulo whitespace, then it's probably useful
    # to report first difference, otherwise we won't
    return valNoWS == refNoWS


def expect(expr: Any, value: Any) -> Optional[bool]:
    """
    Establishes an immediate expectation that the values of the two
    arguments should be equivalent. The expression provided will be
    picked out of the source code of the module calling `expect` (see
    `get_my_context`). The expression and sub-values will be displayed
    if the expectation is not met, and either way a message indicating
    success or failure will be printed. Use `detailLevel` to control how
    detailed the messages are.

    For `expect` to work properly, the following rules must be followed:

    1. When multiple calls to `expect` appear on a single line of the
        source code (something you should probably avoid anyway), none of
        the calls should execute more times than another when that line
        is executed (it's difficult to violate this, but examples
        include the use of `expect` multiple times on one line within
        generator or if/else expressions)
    2. None of the following components of the expression passed to
        `expect` should have side effects when evaluated:
        - Attribute accesses
        - Subscripts (including expressions inside brackets)
        - Variable lookups
        (Note that those things don't normally have side effects!)

    This function returns True if the expectation is met and False
    otherwise. It returns None if the check is skipped, which will
    happen when `SKIP_ON_FAILURE` is `'all'` and a previous check failed.
    If the values are not equivalent, this will count as a failed check
    and other checks may be skipped.

    If not skipped, this function registers an outcome in `ALL_OUTCOMES`.
    """
    global CHECK_FAILED
    context = get_my_context(cast(FunctionType, expect))
    tag = tag_for(context)

    # Skip this expectation if necessary
    if SKIP_ON_FAILURE == 'all' and CHECK_FAILED:
        if DETAIL_LEVEL < 1:
            msg = f"~ {tag} (skipped)"
        else:
            msg = (
                f"~ direct expectation at {tag} for skipped because a"
                f" prior check failed"
            )
            print_message(msg, color=msg_color("skipped"))
            return None

    # Figure out if we want to suppress any failure message
    suppress = SUPPRESS_ON_FAILURE == 'all' and CHECK_FAILED

    short_result = ellipsis(repr(expr), 78)
    short_expected = ellipsis(repr(value), 78)
    full_result = repr(expr)
    full_expected = repr(value)

    firstDiff = findFirstDifference(expr, value)
    msg_cat: MessageCategory
    if firstDiff is None:
        message = f"✓ {tag}"
        equivalent = "equivalent to"
        msg_cat = "succeeded"
        same = True
    else:
        message = f"✗ {tag}"
        equivalent = "NOT equivalent to"
        msg_cat = "failed"
        same = False

    # At higher detail for success or any detail for unsuppressed
    # failure:
    if DETAIL_LEVEL >= 1 or (not same and not suppress):
        message += f"""
  Result:
{indent(short_result, 4)}
  was {equivalent} the expected value:
{indent(short_expected, 4)}"""

    if (
        not same
    and not suppress
    and differencesAreSubtle(short_result, short_expected)
    ):
        assert firstDiff is not None
        message += f"\n  First difference was:\n{indent(firstDiff, 4)}"

    # Report full values if detail level is turned up and the short
    # values were abbreviations
    if DETAIL_LEVEL >= 1:
        if short_result != full_result:
            message += f"\n  Full result:\n{indent(full_result, 4)}"
        if short_expected != full_expected:
            message += (
                f"\n  Full expected value:\n{indent(full_expected, 4)}"
            )

    # Report info about the test expression
    if 'expr' not in context:
        raise RuntimeError(
            f"Error acquiring expectation context. Got:\n{context!r}"
        ) 
    context = cast(ContextDict, context)
    # TODO :What if the context here was just a CodeLocation ?
    base, extra = expr_details(context)
    if (
           (same and DETAIL_LEVEL >= 1)
        or (not same and not suppress and DETAIL_LEVEL >= 0)
    ):
        message += '\n' + indent(base, 2)

    if DETAIL_LEVEL >= 1 and extra:
        message += '\n' + indent(extra, 2)

    # Register a check failure if the expectation was not met
    if not same:
        CHECK_FAILED = True

    # Print our message
    print_message(message, color=msg_color(msg_cat))

    # Register our outcome
    _register_outcome(same, tag, message)

    # Return our result
    return same


def expectType(expr: Any, typ: type) -> Optional[bool]:
    """
    Works like `expect`, but establishes an expectation for the type of
    the result of the expression, not for the exact value. The same
    rules must be followed as for `expect` for this to work properly.

    If the type of the expression's result is an instance of the target
    type, the expectation counts as met.

    If not skipped, this function registers an outcome in `ALL_OUTCOMES`.
    """
    global CHECK_FAILED
    context = get_my_context(cast(FunctionType, expectType))
    tag = tag_for(context)

    # Skip this expectation if necessary
    if SKIP_ON_FAILURE == 'all' and CHECK_FAILED:
        if DETAIL_LEVEL < 1:
            msg = f"~ {tag} (skipped)"
        else:
            msg = (
                f"~ direct expectation at {tag} for skipped because a"
                f" prior check failed"
            )
            print_message(msg, color=msg_color("skipped"))
            return None

    suppress = SUPPRESS_ON_FAILURE == 'all' and CHECK_FAILED

    msg_cat: MessageCategory
    if type(expr) == typ:
        message = f"✓ {tag}"
        desc = "the expected type"
        msg_cat = "succeeded"
        same = True
    elif isinstance(expr, typ):
        message = f"✓ {tag}"
        desc = f"a kind of {typ}"
        msg_cat = "succeeded"
        same = True
    else:
        message = f"✗ {tag}"
        desc = f"NOT a kind of {typ}"
        msg_cat = "failed"
        same = False

    # Note failed check
    if not same:
        CHECK_FAILED = True

    # Report on the type if the detail level warrants it, and also about
    # the test expression
    assert 'expr' in context
    context = cast(ContextDict, context)
    # TODO :What if the context here was just a CodeLocation ?
    base, extra = expr_details(context)
    if (
           (same and DETAIL_LEVEL >= 1)
        or (not same and not suppress and DETAIL_LEVEL >= 0)
    ):
        message += f"\n  The result type ({type(expr)}) was {desc}."
        message += '\n' + indent(base, 2)

    if DETAIL_LEVEL >= 1 and extra:
        message += '\n' + indent(extra, 2)

    # Print our message
    print_message(message, color=msg_color(msg_cat))

    # Register our outcome
    _register_outcome(same, tag, message)

    # Return our result
    return same


#--------------#
# AST Checking #
#--------------#

AST_LOC_FIELDS = [
    "lineno", "col_offset", "end_lineno", "end_col_offset"
]
"""
AST node fields which denote the location of the node, rather than
anything about its structure. These are ignored by `nodeAsDict`.
"""


def astMatchExact(
    a: Any,
    b: Any,
    matching: Optional[Set[Tuple[int, int]]] = None
) -> bool:
    """
    Returns true if the two AST trees (or lists, tuples, sets, or
    dictionaries containing AST tress) contain exactly the same
    arrangement of nodes, ignoring things like line numbers. Note that
    for two dictionaries if any keys are AST nodes, it will only work if
    the insertion order of items matches up (for other dictionaries
    insertion order doesn't matter).

    The `matching` set is used during recursion to prevent infinite
    recursion.

    Borrowed from: https://stackoverflow.com/questions/3312989/elegant-way-to-test-python-asts-for-equality-not-reference-or-object-identity

    For example:

        >>> astMatchExact(ast.parse('x = 5'), ast.parse('x = 5'))
        True
        >>> astMatchExact(ast.parse('x = 5'), ast.parse('x = 5  # hi'))
        True
        >>> astMatchExact(ast.parse('x = 5'), ast.parse('x = 6'))
        False
        >>> astMatchExact(ast.parse('x = 5'), ast.parse('x: int = 5'))
        False
        >>> astMatchExact(
        ...     ast.parse('x = 5\\ny = 6'),
        ...     ast.parse('x = 5\\ny = 6')
        ... )
        True
        >>> astMatchExact(
        ...     ast.parse('y = 6\\nx = 5'),
        ...     ast.parse('x = 5\\ny = 6')
        ... )
        False
        >>> t = ast.parse('x = 5\\ny = x')
        >>> x1 = t.body[0].targets[0]  # store context
        >>> x2 = t.body[1].value  # load context
        >>> astMatchExact(x1, x2)  # load/store context must match
        False
    """
    # Establish base matched dict if none given
    if matching is None:
        matching = set()

    # Key used to prevent infinite recursion
    matchKey = (id(a), id(b))

    # If we're already trying to match this pair, return `True` without
    # comparing them, so that the outer comparison can succeed if they
    # have identical recursive structures or fail if there's a
    # difference somewhere.
    if matchKey in matching:
        return True

    # Now add our match key as we start to compare
    matching.add(matchKey)

    # Not equal if types are different
    if type(a) != type(b):
        return False

    # If both are AST nodes, compare their attributes
    if isinstance(a, ast.AST):
        # Not equal if any vars differ
        if set(vars(a)) != set(vars(b)):
            return False
        # Can compare each attribute...
        for attr in vars(a):
            # Exclude location fields
            if attr in AST_LOC_FIELDS:
                continue
            if not astMatchExact(getattr(a, attr), getattr(b, attr), matching):
                return False
        # True if all fields matched
        return True

    # Lists or tuples need to be same length & match at each position
    elif isinstance(a, (list, tuple)):
        return (
            len(a) == len(b)
        and all(astMatchExact(a[i], b[i], matching) for i in range(len(a)))
        )

    # Note: as far as I'm aware, there are no AST fields which contain
    # sets or dictionaries whose keys or values are sub-AST-nodes, but
    # just in case, we'll handle those:
    elif isinstance(a, set):
        return astMatchExact(sorted(a), sorted(b), matching)

    elif isinstance(a, dict):
        if any(isinstance(k, ast.AST) for k in a):
            # Note: this requires same insertion order, but since an AST
            # node can be a dict key, it's prohibitive to try to match up
            # keys elsehow.
            return astMatchExact(list(a.items()), list(b.items()), matching)
        else:
            if set(a) != set(b):  # Make sure keys are the same
                # Note: an ast.AST in b only would trigger this
                return False
            for k in a:
                if not astMatchExact(a[k], b[k], matching):
                    return False

            # Value matched for each key
            return True

    # Anything else uses normal ==
    else:
        return a == b


class ASTMatch:
    """
    Represents a full, partial, or missing (i.e., non-) match of an
    `ASTRequirement` against an abstract syntax tree, ignoring
    sub-checks. The `isFull` and `isPartial` fields specify whether the
    match is a full match (values `True`, `False`), a partial match
    (`False`, `True`) or not a match at all (`False`, `False`).
    """
    isFull: bool
    isPartial: bool

    def __init__(
        self,
        node: Optional[ast.AST],
        isPartial: bool = False
    ) -> None:
        """
        The matching AST node is required; use None for a non-match. If
        a node is given, `isPartial` will be stored to determine whether
        it's a partial or full match (when node is set to `None`,
        `isPartial` is ignored).
        """
        self.node = node
        if node is None:
            self.isFull = False
            self.isPartial = False
        else:
            self.isFull = not isPartial
            self.isPartial = isPartial

    def __str__(self) -> str:
        """
        Represents the match using the name of the type of node matched,
        plus the line number of that node if available.
        """
        error = False
        if self.node is None or (not self.isFull and not self.isPartial):
            return "No match found"
        elif self.isFull:
            result = "Full match: "
        elif self.isPartial:
            result = "Partial match: "
        else:
            error = True

        name = type(self.node).__name__
        if hasattr(self.node, "lineno") and self.node.lineno is not None:
            what = f"{name} on line {self.node.lineno}"
            result += what
        else:
            what = f"{name} (unknown location)"
            result += what

        if error:
            raise RuntimeError(
                f"Neither full nor partial match, but a node is"
                f" given:\n{what}\n  which is:\n{self.node}"
            )

        return result


class RuleMatches:
    """
    Represents how an `ASTRequirement` matches against a syntax tree,
    including sub-checks. It can be a full, partial, or non-match, as
    dictated by the `isFull` and `isPartial` variables (`True`/`False` →
    full match, `False`/`True` → partial match, and `False`/`False` →
    non-match).

    Stores a list of tuples each containing an `ASTMatch` object for the
    check itself, plus a list of `RuleMatches` objects for each
    sub-check.

    The number of these tuples compared to the min/max match
    requirements of the check this `RuleMatches` was derived from
    determine if it's a full, partial, or non-match.
    """
    check: 'ASTRequirement'
    """
    The check from which this match is derived.
    """

    nFull: int
    """
    The number of fully-matching AST nodes for this rule.
    """

    matchPoints: List[Tuple[ASTMatch, Sequence["RuleMatches"]]]
    """
    Points at which we have matches. Each point is a tuple containing an
    AST node, followed by a sequence of sub-`RuleMatches` objects
    representing sub-matches for dependent rules.
    """

    final: bool
    """
    Whether this matches object has been finalized yet.
    """

    isFull: bool
    """
    Whether or not this is a full match.
    """

    isPartial: bool
    """
    Whether or not this is a partial match. Will never have the same
    value as `isFull`, although both can be false in the case of a
    non-match.
    """

    def __init__(self, check: 'ASTRequirement') -> None:
        """
        The `ASTRequirement` that we're deriving this `RuleMatches` from
        is required. An empty structure (set up as a non-match unless
        the check's maxMatches or minMatches is 0 in which case it's set
        up as a full match) will be created which can be populated using
        the `addMatch` method.
        """
        self.check = check
        self.nFull = 0
        self.matchPoints = []
        self.final = False

        if self.check.minMatches == 0 or self.check.maxMatches == 0:
            self.isFull = True
            self.isPartial = False
        else:
            self.isFull = False
            self.isPartial = False

    def __str__(self) -> str:
        """
        Represents the matches by listing them out over multiple lines,
        prefaced with a description of whether the whole rule is a
        full/partial/non- match.
        """
        if self.isFull:
            category = "fully"
        elif self.isPartial:
            category = "partially"
        else:
            category = "not"

        # Separate full & partial matches (attending to sub-matches which
        # the match objects themselves don't)
        full = []
        partial = []
        for (match, subMatches) in self.matchPoints:
            if match.isFull and all(sub.isFull for sub in subMatches):
                full.append(str(match).split(':')[-1].strip())
            elif match.isFull or match.isPartial:
                partial.append(str(match).split(':')[-1].strip())

        return (
            (
                f"Requirement {category} satisfied via {self.nFull} full"
                f" and {len(self.matchPoints) - self.nFull} partial"
                f" match(es):\n"
            )
          + '\n'.join(
                indent("Full match: " + matchStr, 2)
                for matchStr in full
            )
          + '\n'.join(
                indent("Partial match: " + matchStr, 2)
                for matchStr in partial
            )
        )

    def addMatch(
        self,
        nodeMatch: ASTMatch,
        subMatches: Sequence["RuleMatches"]
    ) -> None:
        """
        Adds a single matching AST node to this matches suite. The node
        at which the match occurs is required (as an `ASTMatch` object),
        along with a list of sub-`RuleMatches` objects for each sub-check
        of the check. This list is not required if the `nodeMatch` is a
        non-match, but in that case the entry will be ignored.

        This object's partial/full status will be updated according to
        whether or not the count of full matches falls within the
        min/max match range after adding the specified match point. Note
        that a match point only counts as a full match if the
        `nodeMatch` is a full match and each of the `subMatches` are
        full matches; if the `nodeMatch` is a non-match, then it doesn't
        count at all, and otherwise it's a partial match.

        Note that each of the sub-matches provided will be marked as
        final, and any attempts to add new matches to them will fail
        with a `ValueError`.
        """
        if self.final:
            raise ValueError(
                "Attempted to add to a RuleMatches suite after it was"
                " used as a sub-suite for another RuleMatches suite"
                " (you may not call addMatch after using a RuleMatches"
                " as a sub-suite)."
            )

        # Mark each sub-match as final now that it's being used to
        # substantiate a super-match.
        for sub in subMatches:
            sub.final = True

        # IF this isn't actually a match at all, ignore it
        if not nodeMatch.isFull and not nodeMatch.isPartial:
            return

        if len(subMatches) != len(self.check.subChecks):
            raise ValueError(
                f"One sub-matches object must be supplied for each"
                f" sub-check of the rule ({len(self.check.subChecks)}"
                f" were required but you supplied {len(subMatches)})."
            )

        # Add to our list of match points, which includes all full and
        # partial matches.
        self.matchPoints.append((nodeMatch, subMatches))

        # Check if the new match is a full match
        if nodeMatch.isFull and all(sub.isFull for sub in subMatches):
            self.nFull += 1

        # Update our full/partial status depending on the new number
        # of full matches
        if (
            (
                self.check.minMatches is None
             or self.check.minMatches <= self.nFull
            )
        and (
                self.check.maxMatches is None
             or self.check.maxMatches >= self.nFull
            )
        ):
            self.isFull = True
            self.isPartial = False
        else:
            self.isFull = False
            self.isPartial = True

    def explanation(self) -> str:
        """
        Produces a text explanation of whether or not the associated
        check succeeded, and if not, why.
        """
        if self.isFull:
            return "check succeeded"
        elif self.isPartial:
            return "check failed (partial match(es) found)"
        else:
            return "check failed (no matches)"


class DefaultMin:
    """
    Represents the default min value (to distinguish from an explicit
    value that's the same as the default).
    """
    pass


class NumArgs(TypedDict, total=False):
    """
    The keyword arguments used to specify the min/max/specific number of
    required matches to an `ASTRequirement`. This is defined so that
    types which inherit from `ASTRequirement` can use it as the type of
    their **kwargs. All slots are optional.
    """
    min: Union[type[DefaultMin], None, int]
    max: Optional[int]
    n: Optional[int]


class ASTRequirement:
    """
    Represents a specific abstract syntax tree structure to check for
    within a file, function, or code block (see
    `TestManager.checkCodeContains`). This base class is abstract, the
    concrete subclasses each check for specific things.
    """
    subChecks: List['ASTRequirement']
    """
    The list of sub-rules attached to this rule. Sub-rules must match
    within the AST node of the original match (including its
    descendants).
    """

    minMatches: Optional[int]
    """
    The minimum number of distinct AST nodes that need to match for this
    requirement to be satisfied.
    """

    maxMatches: Optional[int]
    """
    The maximum number of distinct AST nodes that can match while still
    considering this requirement satisfied. Can be set to 0 to indicate
    we DON'T want to allow a certain structure.
    """

    def __init__(
        self,
        *,
        min: Union[type[DefaultMin], None, int] = DefaultMin,
        max: Optional[int] = None,
        n: Optional[int] = None
    ):
        """
        Creates basic common data structures. The `min`, `max`, and `n`
        keyword arguments can be used to specify the number of matches
        required: if `n` is set, it overrides both `min` and `max`;
        either of those can be set to `None` to eschew an upper/lower
        limit. Note that a lower limit of `None` or 0 will mean that the
        check isn't required to match, and an upper limit of 0 will mean
        that the check will only succeed if the specified structure is
        NOT present. If `min` is greater than `max`, the check will never
        succeed; a warning will be issued in that case.
        """
        # Run-time type checking for our arguments here
        if (
            min is not DefaultMin
        and min is not None
        and not isinstance(min, int)
        ):
            raise TypeError(
                f"min argument must be an integer or None (got: '{min}'"
                f" which is a/an: {type(min)}."
            )

        if max is not None and not isinstance(max, int):
            raise TypeError(
                f"max argument must be an integer or None (got: '{max}'"
                f" which is a/an: {type(max)}."
            )

        if n is not None and not isinstance(n, int):
            raise TypeError(
                f"n argument must be an integer or None (got: '{n}'"
                f" which is a/an: {type(n)}."
            )

        # Set up empty sub-checks list
        self.subChecks = []

        # Figure out actual minimum value
        if min is DefaultMin:
            if max == 0:
                self.minMatches = 0
            else:
                self.minMatches = 1
        else:
            assert isinstance(min, (int, NoneType))
            self.minMatches = min

        self.maxMatches = max
        if n is not None:
            self.minMatches = n
            self.maxMatches = n

        if (
            self.minMatches is not None
        and self.maxMatches is not None
        and self.minMatches > self.maxMatches
        ):
            warnings.warn(
                "Min matches is larger than max matches for"
                " ASTRequirement; it will always fail."
            )

    def structureString(self) -> str:
        """
        Returns a string expressing the structure that this check is
        looking for.
        """
        raise NotImplementedError(
            "ASTRequirement base class is abstract."
        )

    def howMany(self) -> str:
        """
        Returns a string describing how many are required based on min +
        max match values.
        """
        # Figure out numeric descriptor from min/max
        if self.maxMatches is None:
            if self.minMatches is None:
                return "any number of"
            else:
                return f"at least {self.minMatches}"
        else:
            if self.maxMatches == 0:
                return "no"
            elif self.minMatches is None:
                return f"at most {self.maxMatches}"
            elif self.minMatches == self.maxMatches:
                return str(self.minMatches)
            else:
                return f"{self.minMatches}-{self.maxMatches}"

    def fullStructure(self) -> str:
        """
        The structure string (see `structureString`) plus a list of what
        sub-checks are used to constrain contents of those matches, and
        text describing how many matches are required.
        """
        result = f"{self.howMany()} {self.structureString()}"
        if len(self.subChecks) > 0:
            result += " that also contain(s):\n" + '\n'.join(
                indent(sub.fullStructure(), 2)
                for sub in self.subChecks
            )

        return result

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        """
        Given a syntax tree, yields each node from that tree that should
        be checked for subrule matches. These are yielded in tuples
        where the second element is True for a full match at that node
        and False for a partial match. This is used by `allMatches`.
        """
        raise NotImplementedError(
            "ASTRequirement base class is abstract."
        )

    def allMatches(self, syntax_tree: ast.AST) -> RuleMatches:
        """
        Returns a `RuleMatches` object representing all full and partial
        matches of this check within the given syntax tree.

        Only matches which happen at distinct AST nodes are considered;
        this does NOT list out all of the ways a match could happen (per
        sub-rule possibilities) for each node that might match.

        This object will be finalized and may be used for a sub-result in
        another check.
        """
        result = RuleMatches(self)
        for (node, isFull) in self._nodesToCheck(syntax_tree):
            subMatchSuites = self._subRuleMatches(node)
            result.addMatch(ASTMatch(node, not isFull), subMatchSuites)

        return result

    def _walkNodesOfType(
        self,
        root: ast.AST,
        nodeTypes: ClassInfo
    ):
        """
        A generator that yields all nodes within the given AST (including
        the root node) which match the given node type (or one of the
        types in the given node type tuple). The nodes are yielded in
        (an approximation of) execution order (see `walk_ast_in_order`).
        """
        for node in walk_ast_in_order(root):
            if isinstance(node, nodeTypes):
                yield node

    def _subRuleMatches(self, withinNode: ast.AST) -> List[RuleMatches]:
        """
        Returns a list of one `RuleMatches` object for each sub-check of
        this check. These will be finalized and can safely be added as
        sub-rule-matches for a entry in a `RuleMatches` suite for this
        node.
        """
        return [
            check.allMatches(withinNode)
            for check in self.subChecks
        ]

    def contains(self, *subChecks: "ASTRequirement") -> "ASTRequirement":
        """
        Enhances this check with one or more sub-check(s) which must
        match (anywhere) within the contents of a basic match for the
        whole check to have a full match.

        Returns self for chaining.

        For example:

        >>> import optimism
        >>> optimism.messagesAsErrors(False)
        >>> optimism.colors(False)
        >>> manager = optimism.testBlock('''\\
        ... def f():
        ...     for i in range(3):
        ...         print('A' * i)
        ... ''')
        >>> manager.checkCodeContains(
        ...     optimism.Def().contains(
        ...         optimism.Loop().contains(
        ...             optimism.Call('print')
        ...         )
        ...     )
        ... ) # doctest: +ELLIPSIS
        ✓ ...
        True
        >>> manager.checkCodeContains(
        ...     optimism.Def().contains(
        ...         optimism.Call('print')
        ...     )
        ... ) # doctest: +ELLIPSIS
        ✓ ...
        True
        >>> manager.checkCodeContains(
        ...     optimism.Loop().contains(
        ...         optimism.Def()
        ...     )
        ... ) # doctest: +ELLIPSIS
        ✗ ...
          Code does not contain the expected structure:
            at least 1 loop(s) or generator expression(s) that also contain(s):
              at least 1 function definition(s)
          Although it does partially satisfy the requirement:
            Requirement partially satisfied via 0 full and 1 partial match(es):
              Partial match: For on line 2
          checked code from block at ...
        False
        """
        self.subChecks.extend(subChecks)
        return self


class MatchAny(ASTRequirement):
    """
    A special kind of `ASTRequirement` which matches when at least one of
    several other checks matches. Allows testing for one of several
    different acceptable code structures. For example, the following code
    shows how to check that either `with` was used with `open`, or
    `try/finally` was used with `open` in the try part and `close` in the
    finally part (and that either way, `read` was used):

    >>> import optimism
    >>> optimism.messagesAsErrors(False)
    >>> optimism.colors(False)
    >>> manager1 = optimism.testBlock('''\\
    ... with open('f') as fileInput:
    ...     print(f.read())''')
    ...
    >>> manager2 = optimism.testBlock('''\\
    ... fileInput = None
    ... try:
    ...     fileInput = open('f')
    ...     print(f.read())
    ... finally:
    ...     close(fileInput)''')
    ...
    >>> check = optimism.MatchAny(
    ...     optimism.With().contains(optimism.Call('open')),
    ...     optimism.Try()
    ...         .contains(optimism.Call('open'))
    ...         .contains(optimism.Call('close'))
    ...     # TODO: Implement these
    ...     #    .tryContains(optimism.Call('open'))
    ...     #    .finallyContains(optimism.call('close'))
    ... ).contains(optimism.Call('read', isMethod=True))
    ...
    >>> manager1.checkCodeContains(check) # doctest: +ELLIPSIS
    ✓ ...
    True
    >>> manager2.checkCodeContains(check) # doctest: +ELLIPSIS
    ✓ ...
    True
    """
    def __init__(
        self,
        *checkers: ASTRequirement,
        min: Optional[int] = 1,
        max: Optional[int] = None,
        n: Optional[int] = None
    ):
        """
        Any number of sub-checks may be supplied. Note that `contains`
        will be broadcast to each of these sub-checks if called on the
        `MatchAny` object. `min`, `max`, and/or `n` may be specified as
        integers to place limits on the number of matches we look for;
        the default is 1 minimum and no maximum. The min and max
        arguments are ignored if a specific number of required matches
        is provided.
        """
        super().__init__(min=min, max=max, n=n)

        if len(checkers) == 0:
            warnings.warn(
                "A MatchAny check without any sub-checks will always"
                " fail (or will always succeed if there is no minimum)."
            )
        self.subChecks = list(checkers)

    def structureString(self) -> str:
        "Lists the full structures of each alternative."
        if len(self.subChecks) == 0:
            return "zero alternatives"

        return "the following:\n" + (
            '\n...or...\n'.join(
              indent(check.fullStructure(), 2)
              for check in self.subChecks
          )
        )

    def fullStructure(self) -> str:
        "Lists the alternatives."
        if len(self.subChecks) == 0:
            return "A MatchAny with no alternatives (always fails)"

        # Special case 'no' -> 'none of'
        n = self.howMany()
        if n == "no":
            n = "none of"

        return f"{n} {self.structureString()}"

    def allMatches(self, syntax_tree: ast.AST) -> RuleMatches:
        """
        Runs each sub-check and returns a `RuleMatches` with just one
        `ASTMatch` entry that targets the root of the syntax tree. The
        `RuleMatches` sub-entires for this single match point are full
        `RuleMatches` for each alternative listed in this `MatchAny`,
        which might contain match points on nodes also matched by other
        `RuleMatches` of different alternatives.

        However, the overall `isFull`/`isPartial` status of the resulting
        `RuleMatches` is overridden to be based on the count of distinct
        node positions covered by full matches of any of the
        alternatives. So if you set min/max on the base `MatchAny`
        object, it will apply to the number of node points at which any
        sub-rule matches. For example:

        >>> import optimism
        >>> optimism.messagesAsErrors(False)
        >>> optimism.colors(False)
        >>> manager = optimism.testBlock('''\\
        ... def f(x):
        ...     x = max(x, 0)
        ...     if x > 5:
        ...         print('big')
        ...     elif x > 1:
        ...         print('medium')
        ...     else:
        ...         print('small')
        ...     return x
        ... ''')
        ...
        >>> check = optimism.MatchAny(
        ...    optimism.IfElse(),
        ...    optimism.Call('print'),
        ...    n=5 # 2 matches for if/else, 3 for call to print
        ... )
        ...
        >>> manager.checkCodeContains(check) # doctest: +ELLIPSIS
        ✓ ...
        True
        >>> check = optimism.MatchAny(
        ...    optimism.Call(),
        ...    optimism.Call('print'),
        ...    n=4 # 4 nodes that match, 3 of which overlap
        ... )
        ...
        >>> manager.checkCodeContains(check) # doctest: +ELLIPSIS
        ✓ ...
        True
        """
        result = RuleMatches(self)

        if len(self.subChecks) == 0:
            return result  # a failure, since minMatches >= 1

        # Create a mapping from AST nodes to True/False/None for a
        # full/partial/no match at that node from ANY sub-check, since we
        # don't want to count multiple match points on the same node. At
        # the same time, build a list of sub-matches for each sub-check.
        nodeMap: Dict[ast.AST, Optional[bool]] = {}
        subMatchList = []
        for i, check in enumerate(self.subChecks):
            # Find sub-matches for this alternative
            subMatches = check.allMatches(syntax_tree)

            # Record in list + note first full/partial indices
            subMatchList.append(subMatches)

            # Note per-node best matches
            for (match, subSubMatches) in subMatches.matchPoints:
                if match.node is None:  # not a real match; shouldn't happen
                    continue
                fullPos = (
                    match.isFull
                and all(subSub.isFull for subSub in subSubMatches)
                )
                prev = nodeMap.get(match.node, None)
                if prev is None or fullPos and prev is False:
                    nodeMap[match.node] = fullPos

        # We have only a single result, containing the full sub-matches
        # for each alternative:
        result.addMatch(ASTMatch(syntax_tree), subMatchList)

        # Set 'final' on the result so nobody adds more to it
        result.final = True

        # But we override the counting logic: we don't want to count the
        # # of places where a match occurred (there's only ever 1); and
        # we don't want to count the # of sub-rules that matched (that
        # caps out at the # of subrules, even if they match multiple
        # nodes). Instead we want to count the # of distinct nodes
        # where full matches were found across all sub-rules.
        result.nFull = len([k for k in nodeMap if nodeMap[k]])

        # Override isFull/isPartial on result based on new nFull
        if (
            (
                result.check.minMatches is None
             or result.check.minMatches <= result.nFull
            )
        and (
                result.check.maxMatches is None
             or result.check.maxMatches >= result.nFull
            )
        ):
            result.isFull = True
            result.isPartial = False
        else:
            result.isFull = False
            if (
                result.nFull == 0
            and (
                    result.check.maxMatches is None
                 or result.check.maxMatches > 0
                )
            ):
                # In this case we consider it to be not a match at all,
                # since we found 0 match points for any alternatives and
                # the requirement was a positive one where max was > 0.
                result.isPartial = False
            else:
                result.isPartial = True

        # And we're done
        return result

    def contains(self, *subChecks: "ASTRequirement") -> "ASTRequirement":
        """
        Broadcasts the call to each sub-check. Note that this can create
        a sharing situation where the same `ASTRequirement` object is a
        sub-check of multiple other checks.

        This function returns the `MatchAny` object for chaining.
        """
        for check in self.subChecks:
            check.contains(*subChecks)

        return self


class Import(ASTRequirement):
    """
    Checks for an `import` statement, possibly with a specific module
    name.
    """
    def __init__(
        self,
        moduleName: Optional[str] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        The argument specifies the required module name; leave it as
        `None` (the default) to match any `import` statement.
        """
        super().__init__(**kwargs)
        self.name = moduleName

    def structureString(self) -> str:
        if self.name is not None:
            return f"import(s) of {self.name}"
        else:
            return "import statement(s)"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Note that every import statement is a partial match
        for node in self._walkNodesOfType(
            syntax_tree,
            (ast.Import, ast.ImportFrom)
        ):
            if self.name is None:
                yield (node, True)
            else:
                if isinstance(node, ast.Import):
                    if any(
                        alias.name == self.name
                        for alias in node.names
                    ):
                        yield (node, True)
                    else:
                        yield (node, False)
                else:  # must be ImportFrom
                    if node.module == self.name:
                        yield (node, True)
                    else:
                        yield (node, False)


class Def(ASTRequirement):
    """
    Matches a function definition, possibly with a specific name and/or
    number of arguments.
    """
    def __init__(
        self,
        name: Optional[str] = None,
        minArgs: Optional[int] = 0,
        maxArgs: Optional[int] = None,
        nArgs: Optional[int] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        The first argument specifies the function name. Leave it as
        `None` (the default) to allow any function definition to match.

        The `minArgs`, `maxArgs`, and `nArgs` arguments specify the
        number of arguments the function must accept. Min and max are
        ignored if `nArgs` is specified; min or max can be None to eschew
        an upper or lower limit. Default is any number of arguments.

        A warning is issued if `minArgs` > `maxArgs`.
        """
        super().__init__(**kwargs)
        self.name = name
        self.minArgs = minArgs
        self.maxArgs = maxArgs
        if nArgs is not None:
            self.minArgs = nArgs
            self.maxArgs = nArgs

        if (
            self.minArgs is not None
        and self.maxArgs is not None
        and self.minArgs > self.maxArgs
        ):
            warnings.warn(
                "A def node with minArgs > maxArgs cannot match."
            )

    def structureString(self) -> str:
        if self.name is not None:
            result = f"definition(s) of {self.name}"
        else:
            result = "function definition(s)"
        if self.minArgs is not None and self.minArgs > 0:
            if self.maxArgs is None:
                result += f" (with at least {self.minArgs} arguments)"
            elif self.maxArgs == self.minArgs:
                result += f" (with {self.minArgs} arguments)"
            else:
                result += f" (with {self.minArgs}-{self.maxArgs} arguments)"
        elif self.maxArgs is not None:
            result += " (with at most {self.maxArgs} arguments)"
        # otherwise no parenthetical is necessary
        return result

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Note that every def is considered a partial match, but
        # definitions whose name matches and whose arguments don't are
        # yielded before those whose names don't match.
        later = []
        for node in self._walkNodesOfType(
            syntax_tree,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            nameMatch = self.name is None or node.name == self.name
            nArgs = (
                (
                    len(node.args.posonlyargs)
                    if hasattr(node.args, "posonlyargs")
                    else 0
                )
              + len(node.args.args)
              + len(node.args.kwonlyargs)
              + (1 if node.args.vararg is not None else 0)
              + (1 if node.args.kwarg is not None else 0)
            )
            argsMatch = (
                (self.minArgs is None or self.minArgs <= nArgs)
            and (self.maxArgs is None or self.maxArgs >= nArgs)
            )
            if nameMatch and argsMatch:
                yield (node, True)
            elif nameMatch:
                yield (node, False)
            else:
                # Order non-name-matched nodes last
                later.append(node)

        for node in later:
            yield (node, False)


class Call(ASTRequirement):
    """
    Matches a function call, possibly with a specific name, and possibly
    restricted to only method calls or only non-method calls.
    """
    def __init__(
        self,
        name: Optional[str] = None,
        isMethod: Optional[bool] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        The first argument specifies the function name. Leave it as
        `None` (the default) to allow any function call to match.

        The second argument `isMethod` specifies whether the call must be
        a method call, not a method call, or may be either. Note that any
        call to an attribute of an object is counted as a "method" call,
        including calls that use explicit module names, since it's not
        possible to know without running the code whether the attribute's
        object is a class or something else. Set this to `True` to
        match only method calls, `False` to match only non-method calls,
        and any other value (like the default `None`) to match either.

        TODO: Support restrictions on arguments used?
        """
        super().__init__(**kwargs)
        self.name = name
        self.isMethod = isMethod

    def structureString(self) -> str:
        if self.name is not None:
            if self.isMethod is True:
                result = f"call(s) to ?.{self.name}"
            else:
                result = f"call(s) to {self.name}"
        else:
            if self.isMethod is True:
                result = "method call(s)"
            elif self.isMethod is False:
                result = "non-method function call(s)"
            else:
                result = "function call(s)"

        return result

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Note that are calls whose name doesn't match are not considered
        # matches at all, while calls which are/aren't methods are still
        # considered partial matches even when isMethod indicates they
        # should be the opposite. Also note that only calls whose
        # function expression is either a Name or an Attribute will match
        # if isMethod is specified (one way or the other) or name is not
        # None. Things like lambdas, if/else expression results, or
        # subscripts won't match because they don't really have a name,
        # and they're not really specifically methods or not methods.

        # If no specific requirements are present, then we can simply
        # yield all of the Call nodes
        if (
            self.isMethod is not True
        and self.isMethod is not False
        and self.name is None
        ):
            for node in self._walkNodesOfType(syntax_tree, ast.Call):
                yield (node, True)
        else:
            # Otherwise only call nodes w/ Name or Attribute expressions
            # can match
            for node in self._walkNodesOfType(syntax_tree, ast.Call):
                # Figure out the name and/or method status of the thing being
                # called:
                funcExpr = node.func

                # Unwrap any := assignments to get at the actual function
                # object being used
                if HAS_WALRUS:
                    while isinstance(funcExpr, ast.NamedExpr):
                        funcExpr = funcExpr.value

                # Handle name vs. attr nodes
                if isinstance(funcExpr, ast.Name):
                    name = funcExpr.id
                    method = False
                elif isinstance(funcExpr, ast.Attribute):
                    name = funcExpr.attr
                    method = True
                else:
                    # Only Name and Attribute nodes can actually be checked
                    # for details, so other matches are ignored
                    continue

                if self.name is None or self.name == name:
                    # "is not not" is actually correct here...
                    yield (node, self.isMethod is not (not method))


def anyNameMatches(nameToMatch: str, targetsList: Sequence[ast.AST]) -> bool:
    """
    Recursive function for matching assigned names within target
    tuple/list AST structures.
    """
    for target in targetsList:
        if isinstance(target, ast.Name) and target.id == nameToMatch:
            return True
        elif isinstance(target, (ast.List, ast.Tuple)):
            if anyNameMatches(nameToMatch, target.elts):
                return True
        # Any other kind of node is ignored

    return False


class Assign(ASTRequirement):
    """
    Matches an assignment, possibly to a variable with a specific name.
    By default augmented assignments and assignments via named
    expressions are allowed, but these may be disallowed or required.
    Assignments of disallowed types are still counted as partial matches
    if their name matches or if no name was specified.

    Assignments to things other than variables (like list slots) will not
    match when a variable name is specified.

    Note that the entire assignment node is matched, so you can use
    `contains` to specify checks to apply to the expression (plus the
    target, but usually that's fine).

    In cases where a tuple assignment is made, if any of the assigned
    names matches the required name, the entire tuple assignment is
    considered a match, since it may not be possible to pick apart the
    right-hand side to find a syntactic node that was assigned to just
    that variable. This can lead to some weird matches, for example,

    >>> import optimism
    >>> optimism.messagesAsErrors(False)
    >>> optimism.colors(False)
    >>> tester = optimism.testBlock("x, (y, z) = 1, (3, 5)")
    >>> tester.checkCodeContains(
    ...     optimism.Assign('x').contains(optimism.Constant(5))
    ... ) # doctest: +ELLIPSIS
    ✓ ...
    True
    """
    def __init__(
        self,
        name: Optional[str] = None,
        isAugmented: Optional[bool] = None,
        isNamedExpr: Optional[bool] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        The first argument specifies the variable name. Leave it as
        `None` (the default) to allow any assignment to match.

        `isAugmented` specifies whether augmented assignments (e.g., +=)
        are considered matches or not; `False` disallows them, `True`
        will only match them, and any other value (like the default
        `None`) will allow them and other assignment types.

        `isNamedExpr` works the same way for controlling whether named
        expressions (:=) are permitted. A `ValueError` will be raised if
        both `isAugmented` and `isNamedExpr` are set to true, since named
        expressions can't be augmented.

        TODO: Allow checking for assignment to fields?
        """
        if isAugmented is True and isNamedExpr is True:
            raise ValueError(
                "Both isAugmented and isNamedExpr cannot be set to True"
                " at once, since no assignments would match in that"
                " case."
            )

        super().__init__(**kwargs)
        self.name = name
        self.isAugmented = isAugmented
        self.isNamedExpr = isNamedExpr

    def structureString(self) -> str:
        if self.name is None:
            if self.isAugmented is True:
                result = "augmented assignment statement(s)"
            elif self.isNamedExpr is True:
                result = "assignment(s) via named expression(s)"
            else:
                result = "assignment(s)"
        else:
            if self.isAugmented is True:
                result = f"augmented assignment(s) to {self.name}"
            elif self.isNamedExpr is True:
                result = f"named assignment(s) to {self.name}"
            else:
                result = f"assignment(s) to {self.name}"

        if self.isAugmented is False:
            result += " (not augmented)"

        if self.isNamedExpr is False:
            result += " (not via named expression(s))"

        return result

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Consider all Assign, AugAssign, AnnAssign, and NamedExpr nodes
        matchTypes: Tuple[type, ...] = (
            ast.Assign,
            ast.AugAssign,
            ast.AnnAssign
        )
        # Also consider `NamedExpr` nodes if walrus operator is in play
        if HAS_WALRUS:
            matchTypes += (ast.NamedExpr,)

        # Look for real matches
        for node in self._walkNodesOfType(
            syntax_tree,
            matchTypes
        ):
            # Figure out the name and/or method status of the thing being
            # called:
            if self.name is None:
                nameMatch = True
            else:
                if isinstance(node, ast.Assign):
                    nameMatch = anyNameMatches(self.name, node.targets)
                else:
                    nameExpr = node.target
                    nameMatch = (
                        isinstance(nameExpr, ast.Name)
                    and nameExpr.id == self.name
                    )

            augmented = isinstance(node, ast.AugAssign)
            namedExpr = HAS_WALRUS and isinstance(node, ast.NamedExpr)

            if (
                nameMatch
            and self.isAugmented is not (not augmented)
            and self.isNamedExpr is not (not namedExpr)
            ):
                yield (node, True)
            elif nameMatch:
                yield (node, False)


class Reference(ASTRequirement):
    """
    Matches a variable reference, possibly to a variable with a specific
    name. By default attribute accesses with the given name will also be
    matched (e.g., both 'pi' and 'math.pi' will match for the name 'pi').
    You may specify that only attributes should match or that attributes
    should not match; matches that violate that specification will still
    be partial matches.

    >>> import optimism
    >>> optimism.messagesAsErrors(False)
    >>> optimism.colors(False)
    >>> tester = optimism.testBlock("x = 5\\ny = x * math.pi")
    >>> tester.checkCodeContains(
    ...     optimism.Reference('x')
    ... ) # doctest: +ELLIPSIS
    ✓ ...
    True
    >>> tester.checkCodeContains(
    ...     optimism.Reference('y')
    ... ) # doctest: +ELLIPSIS
    ✗ ...
    False
    >>> tester.checkCodeContains(
    ...     optimism.Reference('pi')
    ... ) # doctest: +ELLIPSIS
    ✓ ...
    True
    >>> tester.checkCodeContains(
    ...     optimism.Reference('x', attribute=True)
    ... ) # doctest: +ELLIPSIS
    ✗ ...
    False
    >>> tester.checkCodeContains(
    ...     optimism.Reference('pi', attribute=True)
    ... ) # doctest: +ELLIPSIS
    ✓ ...
    True
    >>> tester.checkCodeContains(
    ...     optimism.Reference('pi', attribute=False)
    ... ) # doctest: +ELLIPSIS
    ✗ ...
    False
    """
    def __init__(
        self,
        name: Optional[str] = None,
        attribute: Optional[bool] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        The first argument specifies the variable name. Leave it as
        `None` (the default) to allow any assignment to match.

        The second argument specifies whether the reference must be to
        an attribute with that name (if `True`), or to a regular
        variable with that name (if `False`). Leave it as the default
        `None` to allow matches for either.
        """
        super().__init__(**kwargs)
        self.name = name
        self.attribute = attribute

    def structureString(self) -> str:
        if self.name is None:
            if self.attribute is True:
                result = "attribute reference(s)"
            elif self.attribute is False:
                result = "non-attribute variable reference(s)"
            else:
                result = "variable reference(s)"
        else:
            if self.attribute is True:
                result = f"reference(s) to .{self.name}"
            else:
                result = f"reference(s) to {self.name}"

        return result

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Consider all Name and Attribute nodes
        for node in self._walkNodesOfType(
            syntax_tree,
            (ast.Name, ast.Attribute)
        ):
            # Only match references being loaded (use `Assign` for
            # variables being assigned).
            if not isinstance(node.ctx, ast.Load):
                continue

            # Figure out whether the name matches:
            if self.name is None:
                nameMatch = True
            else:
                if isinstance(node, ast.Name):
                    nameMatch = node.id == self.name
                else:  # must be en Attribute
                    nameMatch = node.attr == self.name

            if self.attribute is None:
                typeMatch = True
            else:
                if self.attribute is True:
                    typeMatch = isinstance(node, ast.Attribute)
                elif self.attribute is False:
                    typeMatch = isinstance(node, ast.Name)

            if nameMatch and typeMatch:
                yield (node, True)
            elif nameMatch:
                yield (node, False)


class Class(ASTRequirement):
    """
    Matches a class definition, possibly with a specific name.
    """
    def __init__(
        self,
        name: Optional[str] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        A name my be specified; `None` (the default) will match any class
        definition.
        """
        super().__init__(**kwargs)
        self.name = name

    def structureString(self) -> str:
        if self.name is not None:
            return f"class definition(s) for {self.name}"
        else:
            return "class definition(s)"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Consider just ClassDef nodes; all such nodes are considered as
        # least partial matches.
        for node in self._walkNodesOfType(syntax_tree, ast.ClassDef):
            yield (node, self.name is None or node.name == self.name)


class IfElse(ASTRequirement):
    """
    Matches a single if or elif, possibly with an else attached. In an
    if/elif/else construction, it will match on the initial if plus on
    each elif, since Python treats them as nested if/else nodes. Also
    matches if/else expression nodes, although this can be disabled or
    required.
    """
    def __init__(
        self,
        onlyExpr: Optional[bool] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        Set `onlyExpr` to `False` to avoid matching if/else expression
        nodes; set it to `True` to only match those nodes; set it to
        anything else to match both normal and expression if/else.
        """
        super().__init__(**kwargs)
        self.onlyExpr = onlyExpr

    def structureString(self) -> str:
        if self.onlyExpr is True:
            return "if/else expression(s)"
        elif self.onlyExpr is False:
            return "if/else statement(s)"
        else:
            return "if/else statement(s) or expression(s)"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Consider If and IfExp nodes
        for node in self._walkNodesOfType(syntax_tree, (ast.If, ast.IfExp)):
            if self.onlyExpr is False:
                full = isinstance(node, ast.If)
            elif self.onlyExpr is True:
                full = isinstance(node, ast.IfExp)
            else:
                full = True

            yield (node, full)


LoopType: TypeAlias = LiteralType[
    "for",
    "async for",
    "while",
    "generator",
    "list comp",
    "dict comp",
    "set comp"
]
"""
The different varieties of loop we can check for. They are:

- "for" - for loops
- "async for" - asynchronous for loops
- "while" - while loops
- "generator" - generator expressions (NOT in comprehensions)
- "list comp" - list comprehensions
- "dict comp" - dictionary comprehensions
- "set comp" - set comprehensions
"""


ExtendedLoopType: TypeAlias = Union[
    LoopType,
    LiteralType[
        "any generator",
        "non-generator",
        "non-async"
    ]
]
"""
A `LoopType` string, or one of the following strings denoting the union
over one of several loop types:

- "any generator"- generator or list/dict/set comp.
- "non-generator" - any non-generator non-comprehension
- "non-async" - any kind except async for
"""


class Loop(ASTRequirement):
    """
    Matches for and while loops, asynchronous versions of those loops,
    and also generator expressions and list/dict/set comprehensions. Can
    be restricted to match only some of those things, although all of
    them are always considered at least partial matches.
    """
    def __init__(
        self,
        only: Optional[Iterable[ExtendedLoopType]] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        The `only` argument can be used to narrow what is matched, it
        should be a single string, or a set (or some other iterable) of
        strings from the `ExtendedLoopType` options.

        A `ValueError` will be raised if an empty `only` set is provided;
        leave it as `None` (the default) to allow any kind of looping
        construct to match. A `ValueError` will also be raised if the
        `only` set contains any strings not listed above.
        """
        super().__init__(**kwargs)

        if only is not None:
            if isinstance(only, str):
                only = { only }
            else:
                only = set(only)

            if "any generator" in only:
                only.add("generator")
                only.add("list comp")
                only.add("dict comp")
                only.add("set comp")
                only.remove("any generator")

            if "non-generator" in only:
                only.add("for")
                only.add("async for")
                only.add("while")
                only.remove("non-generator")

            if "non-async" in only:
                only.add("for")
                only.add("while")
                only.add("generator")
                only.add("list comp")
                only.add("dict comp")
                only.add("set comp")
                only.remove("non-async")

        self.only = cast(Optional[Set[LoopType]], only)

        if only is not None:
            invalid = only - {
                "for", "async for", "while", "generator", "list comp",
                "dict comp", "set comp"
            }
            if len(invalid) > 0:
                raise ValueError(
                    f"One or more invalid loop types was specified for"
                    f" 'only': {invalid}"
                )

            if len(only) == 0:
                raise ValueError(
                    "At least one type of loop must be specified when"
                    " 'only' is used (leave it as None to allow all loop"
                    " types."
                )

    def structureString(self) -> str:
        if self.only is None:
            return "loop(s) or generator expression(s)"
        elif self.only == {"for"} or self.only == {"for", "async for"}:
            return "for loop(s)"
        elif self.only == {"async for"}:
            return "async for loop(s)"
        elif self.only == {"while"}:
            return "while loop(s)"
        elif self.only == {"generator"}:
            return "generator expression(s)"
        elif self.only == {"list comp"}:
            return "list comprehension(s)"
        elif self.only == {"dict comp"}:
            return "dictionary comprehension(s)"
        elif self.only == {"set comp"}:
            return "set comprehension(s)"
        elif len(
            self.only - {"for", "async for", "while"}
        ) == 0:
            return "generator expression(s) or comprehension(s)"
        elif len(
            self.only - {"generator", "list comp", "dict comp", "set comp"}
        ) == 0:
            return (
                "for or while loop(s) (not generator expression(s) or"
                " comprehension(s))"
            )
        elif len(self.only) == 1:
            return f"{list(self.only)[0]} statement(s)"
        else:
            listed = list(self.only)
            firsts = ', '.join(listed[:-1])
            return f"{firsts}, or {listed[-1]} statement(s)"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        allIterationTypes = (
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.GeneratorExp,
            ast.ListComp,
            ast.DictComp,
            ast.SetComp
        )
        if self.only is not None:
            allowed = tuple([
                {
                    "for": ast.For,
                    "async for": ast.AsyncFor,
                    "while": ast.While,
                    "generator": ast.GeneratorExp,
                    "list comp": ast.ListComp,
                    "dict comp": ast.DictComp,
                    "set comp": ast.SetComp,
                }[item]
                for item in self.only
            ])

        for node in self._walkNodesOfType(syntax_tree, allIterationTypes):
            if self.only is None or isinstance(node, allowed):
                yield (node, True)
            else:
                # If only some types are required, other types still
                # count as partial matches
                yield (node, False)


class Return(ASTRequirement):
    """
    Matches a return statement. An expression may be required or
    forbidden, but by default returns with or without expressions count.
    """
    def __init__(
        self,
        requireExpr: Optional[bool] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        `requireExpr` controls whether a return expression is
        allowed/required. Set to `True` to require one, or `False` to
        forbid one, and any other value (such as the default `None`) to
        match returns with or without an expression.
        """
        super().__init__(**kwargs)
        self.requireExpr = requireExpr

    def structureString(self) -> str:
        if self.requireExpr is False:
            return "return statement(s) (without expression(s))"
        else:
            return "return statement(s)"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        for node in self._walkNodesOfType(syntax_tree, ast.Return):
            if self.requireExpr is True:
                full = node.value is not None
            elif self.requireExpr is False:
                full = node.value is None
            else:
                full = True

            yield (node, full)


class Try(ASTRequirement):
    """
    Matches try/except/finally nodes. The presence of except, finally,
    and/or else clauses may be required or forbidden, although all
    try/except/finally nodes are counted as at least partial matches.
    """
    def __init__(
        self,
        requireExcept: Optional[bool] = None,
        requireFinally: Optional[bool] = None,
        requireElse: Optional[bool] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        `requireExcept`, `requireFinally`, and `requireElse` are used to
        specify whether those blocks must be present, must not be
        present, or are neither required nor forbidden. Use `False` for
        to forbid matches with that block and `True` to only match
        constructs with that block. Any other value (like the default
        `None` will ignore the presence or absence of that block. A
        `ValueError` will be raised if both `requireExcept` and
        `requireFinally` are set to `False`, as a `try` block must have
        at least one or the other to be syntactically valid. Similarly,
        if `requireElse` is set to `True`, `requireExcept` must not be
        `False` (and syntactically, `else` can only be used when `except`
        is present).
        """
        super().__init__(**kwargs)
        if requireExcept is False and requireFinally is False:
            raise ValueError(
                "Cannot require that neither 'except' nor 'finally' is"
                " present on a 'try' statement, as one or the other will"
                " always be present."
            )

        if requireElse is True and requireExcept is False:
            raise ValueError(
                "Cannot require that 'else' be present on a 'try'"
                " statement while also requiring that 'except' not be"
                " present, since 'else' cannot be used without 'except'."
            )

        self.requireExcept = requireExcept
        self.requireFinally = requireFinally
        self.requireElse = requireElse

    def structureString(self) -> str:
        result = "try statement(s)"
        if self.requireExcept is not False:
            result += " (with except block(s))"
        if self.requireElse is True:
            result += " (with else block(s))"
        if self.requireFinally is True:
            result += " (with finally block(s))"
        return result

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # All try/except/finally statements count as matches, but ones
        # missing required clauses or which have forbidden clauses count
        # as partial matches.
        for node in self._walkNodesOfType(syntax_tree, ast.Try):
            full = True
            if self.requireExcept is True and len(node.handlers) == 0:
                full = False
            if self.requireExcept is False and len(node.handlers) > 0:
                full = False
            if self.requireElse is True and len(node.orelse) == 0:
                full = False
            if self.requireElse is False and len(node.orelse) > 0:
                full = False
            if self.requireFinally is True and len(node.finalbody) == 0:
                full = False
            if self.requireFinally is False and len(node.finalbody) > 0:
                full = False

            yield (node, full)


class With(ASTRequirement):
    """
    Matches a `with` or `async with` block. Async may be required or
    forbidden, although either form will always be considered at least a
    partial match.
    """
    def __init__(
        self,
        onlyAsync: Optional[bool] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        `onlyAsync` should be set to `False` to disallow `async with`
        blocks, `True` to match only async blocks, and any other value
        (like the default `None`) to match both normal and async blocks.
        """
        super().__init__(**kwargs)
        self.onlyAsync = onlyAsync

    def structureString(self) -> str:
        if self.onlyAsync is True:
            return "async with statement(s)"
        else:
            return "with statement(s)"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        for node in self._walkNodesOfType(
            syntax_tree,
            (ast.With, ast.AsyncWith)
        ):
            yield (
                node,
                self.onlyAsync is not (not isinstance(node, ast.AsyncWith))
                # 'not not' is intentional here
            )


class AnyValue:
    """
    Represents the situation where any value can be accepted for a
    node in a `Constant` or `Literal` `ASTRequirement`. Also used to
    represent a `getLiteralValue` where we don't know the value.
    """
    pass


class AnyType:
    """
    Represents the situation where any type can be accepted for a
    node in a `Constant` or `Literal` `ASTRequirement`.
    """


class Constant(ASTRequirement):
    """
    A check for a constant, possibly with a specific value and/or of a
    specific type. All constants are considered partial matches.

    Note that this cannot match literal tuples, lists, sets,
    dictionaries, etc.; only simple constants. Use `Literal` instead for
    literal lists, tuples, sets, or dictionaries.
    """
    def __init__(
        self,
        value: Any = AnyValue,
        types: Union[type, Tuple[type, ...], type[AnyType]] = AnyType,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        A specific value may be supplied (including `None`) or else any
        value will be accepted if the `AnyValue` class (not an instance
        of it) is used as the argument (this is the default).

        If the value is `AnyValue`, `types` may be specified, and only
        constants with that type will match. `type` may be a tuple (but
        not list) of types or a single type, as with `isinstance`.

        Even if a specific value is specified, the type check is still
        applied, since it's possible to create a value that checks equal
        to values from more than one type. For example, specifying
        `Constant(6)` will match both 6 and 6.0 but `Constant(6, float)`
        will only match the latter.
        """
        super().__init__(**kwargs)
        self.value = value
        self.types = types

        # Allowed types for constants (ignoring doc which claims tuples
        # or frozensets can be Constant values)
        allowed = (int, float, complex, bool, NoneType, str, bytes)

        # value-type and type-type checking
        if value is not AnyValue and type(value) not in allowed:
            raise TypeError(
                f"Value {value!r} has type {type(value)} which is not a"
                f" type that a Constant can be (did you mean to use a"
                f" Literal instead?)."
            )

        if self.types is not AnyType:
            if isinstance(self.types, tuple):
                for typ in self.types:
                    if typ not in allowed:
                        raise TypeError(
                            f"Type {typ} has is not a type that a"
                            f" Constant can be (did you mean to use a"
                            f" Literal instead?)."
                        )
            else:
                if self.types not in allowed:
                    raise TypeError(
                        f"Type {self.types} has is not a type that a"
                        f" Constant can be (did you mean to use a"
                        f" Literal instead?)."
                    )

    def structureString(self) -> str:
        if self.value == AnyValue:
            if self.types == AnyType:
                return "constant(s)"
            else:
                if isinstance(self.types, tuple):
                    types = (
                        ', '.join(t.__name__ for t in self.types[:-1])
                      + ' or ' + self.types[-1].__name__
                    )
                    return f"{types} constant(s)"
                else:
                    return f"{self.types.__name__} constant(s)"
        else:
            return f"constant {repr(self.value)}"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # ALL Constants w/ values/types other than what was expected are
        # considered partial matches.
        if SPLIT_CONSTANTS:
            for node in self._walkNodesOfType(
                syntax_tree,
                (ast.Num, ast.Str, ast.Bytes, ast.NameConstant, ast.Constant)
            ):
                val: Union[int, float, complex, bool, None, str, bytes]
                if isinstance(node, ast.Num):
                    val = node.n
                elif isinstance(node, (ast.Str, ast.Bytes)):
                    val = node.s
                elif isinstance(node, (ast.NameConstant, ast.Constant)):
                    val = node.value

                valMatch = (
                    self.value == AnyValue
                 or val == self.value
                )

                typeMatch = (
                    self.types == AnyType
                 or isinstance(val, self.types)
                )

                yield (node, valMatch and typeMatch)
        else:
            for node in self._walkNodesOfType(syntax_tree, ast.Constant):
                valMatch = (
                    self.value == AnyValue
                 or node.value == self.value
                )

                typeMatch = (
                    self.types == AnyType
                 or isinstance(node.value, self.types)
                )

                yield (node, valMatch and typeMatch)


LiterallyDeclarable: TypeAlias = Union[
    int,
    float,
    complex,
    bool,
    None,
    str,
    bytes,
    # Compound types still declarable as literals
    list,
    tuple,
    set,
    dict
]
"""
A union of the types which can be declared as literals.
"""


def getLiteralValue(astNode: ast.AST) -> Union[
    LiterallyDeclarable,
    type[AnyValue]
]:
    """
    For an AST node that's entirely made up of `Constant` and/or
    `Literal` nodes, extracts the value of that node from the AST. For
    nodes which have things like variable references in them whose
    values are not determined by the AST alone, returns `AnyValue` (the
    class itself, not an instance).

    Examples:

    >>> node = ast.parse('[1, 2, 3]').body[0].value
    >>> type(node).__name__
    'List'
    >>> getLiteralValue(node)
    [1, 2, 3]
    >>> node = ast.parse("('string', 4, {5: (6, 7)})").body[0].value
    >>> getLiteralValue(node)
    ('string', 4, {5: (6, 7)})
    >>> node = ast.parse("(variable, 4, {5: (6, 7)})").body[0].value
    >>> getLiteralValue(node) # can't determine value from AST
    <class 'optimism.AnyValue'>
    >>> node = ast.parse("[x for x in range(3)]").body[0].value
    >>> getLiteralValue(node) # not a literal or constant
    <class 'optimism.AnyValue'>
    >>> node = ast.parse("[1, 2, 3][0]").body[0].value
    >>> getLiteralValue(node) # not a literal or constant
    <class 'optimism.AnyValue'>
    >>> getLiteralValue(node.value) # the value part is though
    [1, 2, 3]
    """
    # Handle constant node types depending on SPLIT_CONSTANTS
    if SPLIT_CONSTANTS:
        if isinstance(astNode, ast.Num):
            return astNode.n
        elif isinstance(astNode, (ast.Str, ast.Bytes)):
            return astNode.s
        elif isinstance(astNode, (ast.NameConstant, ast.Constant)):
            return astNode.value
        # Else check literal types below
    else:
        if isinstance(astNode, ast.Constant):
            return astNode.value
        # Else check literal types below

    result: Union[list, tuple, set, dict]

    if isinstance(astNode, (ast.List, ast.Tuple, ast.Set)):
        result = []
        for elem in astNode.elts:
            subValue = getLiteralValue(elem)
            if subValue is AnyValue:
                return AnyValue
            result.append(subValue)
        return {
            ast.List: list,
            ast.Tuple: tuple,
            ast.Set: set
        }[type(astNode)](result)

    elif isinstance(astNode, ast.Dict):
        result = {}
        for index in range(len(astNode.keys)):
            thisKey = astNode.keys[index]
            if thisKey is None:
                raise RuntimeError(
                    f"AST literal dict node with None key at index"
                    f" {index!r}:\n{astNode!r}"
                )
            kv = getLiteralValue(thisKey)
            vv = getLiteralValue(astNode.values[index])
            if kv is AnyValue or vv is AnyValue:
                return AnyValue
            result[kv] = vv
        return result

    else:
        return AnyValue


class Literal(ASTRequirement):
    """
    A check for a complex literal possibly with a specific value and/or
    of a specific type. All literals of the appropriate type(s) are
    considered partial matches even when a specific value is supplied,
    and list/tuple literals are both considered together for these
    partial matches.

    Note that this cannot match string, number, or other constants, use
    `Constant` for that.
    """
    def __init__(
        self,
        value: Any = AnyValue,
        types: Union[type, Tuple[type, ...], type[AnyType]] = AnyType,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        A specific value may be supplied (it must be a list, tuple, set,
        or dictionary) or else any value will be accepted if the
        `AnyValue` class (not an instance of it) is used as the argument
        (that is the default).

        If the value is `AnyValue`, one or more `types` may be
        specified, and only literals with that type will match. `types`
        may be a tuple (but not list) of types or a single type, as with
        `isinstance`. Matched nodes will always have a value which is one
        of the following types: `list`, `tuple`, `set`, or `dict`.

        If both a specific value and a type or tuple of types is
        specified, any collection whose members match the members of the
        specific value supplied and whose type is one of the listed types
        will match. For example, `Literal([1, 2], types=(list, tuple,
        set))` will match any of `[1, 2]`, `(1, 2)`, or `{2, 1}` but will
        NOT match `[2, 1]`, `(2, 1)`, or any dictionary.

        Specifically, the value is converted to match the type of the
        node being considered and then a match is checked, so for
        example, `Literal([1, 2, 2], types=set)` will match the set `{1,
        2}` and the equivalent sets `{2, 1}` and `{1, 1, 2}`.

        If a node has elements which aren't constants or literals, it
        will never match when a value is provided because we don't
        evaluate code during matching. It might still match if only
        type(s) are provided, of course.
        """
        super().__init__(**kwargs)
        self.value = value
        self.types = types

        # Allowed types for literals
        allowed = (list, tuple, set, dict)

        # value-type and type-type checking
        if value is not AnyValue and type(value) not in allowed:
            raise TypeError(
                f"Value {value!r} has type {type(value)} which is not a"
                f" type that a Literal can be (did you mean to use a"
                f" Constant instead?)."
            )

        if self.types is not AnyType:
            if isinstance(self.types, tuple):
                for typ in self.types:
                    if typ not in allowed:
                        raise TypeError(
                            f"Type {typ} has is not a type that a"
                            f" Literal can be (did you mean to use a"
                            f" Constant instead?)."
                        )
            else:
                if self.types not in allowed:
                    raise TypeError(
                        f"Type {self.types} has is not a type that a"
                        f" Literal can be (did you mean to use a"
                        f" Constant instead?)."
                    )

    def structureString(self) -> str:
        if self.value == AnyValue:
            if self.types == AnyType:
                return "literal(s)"
            else:
                if isinstance(self.types, tuple):
                    types = (
                        ', '.join(t.__name__ for t in self.types[:-1])
                      + ' or ' + self.types[-1].__name__
                    )
                    return f"{types} literal(s)"
                else:
                    return f"{self.types.__name__} literal(s)"
        else:
            return f"literal {repr(self.value)}"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        # Some literals might be considered partial matches
        for node in self._walkNodesOfType(
            syntax_tree,
            (ast.List, ast.Tuple, ast.Set, ast.Dict)
        ):
            # First, get the value of the node. This will be None if
            # it's not computable from the AST alone.
            value = getLiteralValue(node)

            valType: type
            if value in (AnyValue, None):
                valType = {
                    ast.List: list,
                    ast.Tuple: tuple,
                    ast.Set: set,
                    ast.Dict: dict,
                }[type(node)]
            else:
                valType = type(value)

            # Next, determine whether we have something that counts as a
            # partial match, and if we don't, continue to the next
            # potential match.
            partial = False
            partialTypes = self.types
            if partialTypes is AnyType:
                if self.value is not AnyValue:
                    partialTypes = (type(self.value),)
                else:
                    partial = True

            # Only keep checking if we aren't already sure it's a
            # partial match
            if not partial:
                if not isinstance(partialTypes, tuple):
                    partialTypes = (partialTypes,)

                # List and tuple imply each other for partials
                if list in partialTypes and tuple not in partialTypes:
                    partialTypes = partialTypes + (tuple,)
                if tuple in partialTypes and list not in partialTypes:
                    partialTypes = partialTypes + (list,)

                partial = issubclass(valType, partialTypes)

            # Skip this match entirely if it doesn't qualify as at least
            # a partial match.
            if not partial:
                continue

            # Now check for a value match
            if self.value is AnyValue:
                valMatch = True
            elif value is None:
                valMatch = False
            elif self.types is AnyType:
                valMatch = value == self.value
            else:
                check = self.types
                if not isinstance(check, tuple):
                    check = (check,)

                # Coerce type of our own value to type of the value provided
                valType = cast(
                    Union[type[set], type[list], type[tuple], type[dict]],
                    valType
                )
                checkAgainst = valType(self.value)
                # Type checker is mad about this, but it's correct
                # the type checker doesn't know (but we do) that
                # type(value) will be one of list, set, dict, tuple
                # (i.e., values writeable as literals). These can all
                # accept an argument to coerce. TODO: Some kinda cast
                # here?

                # Actually check type & value
                valMatch = (
                    isinstance(value, check)
                and checkAgainst == value
                )

            typeMatch = (
                self.types == AnyType
             or issubclass(valType, self.types)
            )

            # Won't get here unless it's a partial match
            yield (node, valMatch and typeMatch)


OpStr: TypeAlias = LiteralType[
    'u+',
    'u-',
    'not',
    '~',
    '+',
    '-',
    '*',
    '/',
    '//',
    '%',
    '**',
    '<<',
    '>>',
    '|',
    '^',
    '&',
    '@',
    'and',
    'or',
    '==',
    '!=',
    '<',
    '<=',
    '>',
    '>=',
    'is',
    'is not',
    'in',
    'not in'
]
"""
Strings used to specify an operator type to match in an `Operator` check.
In most cases the operator specified is the operator that would be
performed if you wrote the string in Python code. The exceptions are:

- 'u+' and 'u-' for unary forms of + and -, with '+' and '-' specifying
    the binary forms.
- 'in' and 'not in' both match any usage of the 'in' operator
- 'is' and 'is not' both match any usage of the 'is' operator
"""


AT = TypeVar('AT', bound=ast.AST)
"""
A type variable for types that are ast.AST subtypes.
"""

OpMapEntry: TypeAlias = Tuple[
    Tuple[type[ast.AST], ...],
    Tuple[type[ast.AST], ...]
]
"""
The generic type for entries in our `OP_MAP` operator mapping
dictionary: each value is a tuple of full-match and partial-match AST
node types.
"""

OP_MAP: Dict[str, OpMapEntry] = {
    'u+': ((ast.UAdd,), ()),
    'u-': ((ast.USub,), ()),
    'not': ((ast.Not,), ()),
    '~': ((ast.Invert,), ()),
    '+': ((ast.Add,), (ast.Sub,)),
    '-': ((ast.Sub,), (ast.Add,)),
    '*': ((ast.Mult,), (ast.Div,)),
    '/': ((ast.Div,), (ast.Mult,)),
    '//': ((ast.FloorDiv,), (ast.Mod, ast.Div,)),
    '%': ((ast.Mod,), (ast.Div, ast.FloorDiv,)),
    '**': ((ast.Pow,), (ast.Mult,)),
    '<<': ((ast.LShift,), (ast.RShift,)),
    '>>': ((ast.RShift,), (ast.LShift,)),
    '|': ((ast.BitOr,), (ast.BitXor, ast.BitAnd)),
    '^': ((ast.BitXor,), (ast.BitOr, ast.BitAnd)),
    '&': ((ast.BitAnd,), (ast.BitXor, ast.BitOr)),
    '@': ((ast.MatMult,), (ast.Mult,)),
    'and': ((ast.And,), (ast.Or,)),
    'or': ((ast.Or,), (ast.And,)),
    '==': ((ast.Eq,), (ast.NotEq, ast.Is, ast.IsNot)),
    '!=': ((ast.NotEq,), (ast.Eq, ast.Is, ast.IsNot)),
    '<': ((ast.Lt,), (ast.LtE, ast.Gt, ast.GtE)),
    '<=': ((ast.LtE,), (ast.Lt, ast.Gt, ast.GtE)),
    '>': ((ast.Gt,), (ast.Lt, ast.LtE, ast.GtE)),
    '>=': ((ast.GtE,), (ast.Lt, ast.LtE, ast.Gt)),
    'is': ((ast.Is, ast.IsNot), (ast.Eq, ast.NotEq)),
    'is not': ((ast.IsNot, ast.Is), (ast.Eq, ast.NotEq)),
    'in': ((ast.In, ast.NotIn), ()),
    'not in': ((ast.NotIn, ast.In), ()),
}
"""
The mapping from operator strings to pairs containing the tuple of
full-match-type AST node types followed by the tuple of
partial-match-type AST node types.
"""


class Operator(ASTRequirement):
    """
    A check for a unary operator, binary operator, boolean operator, or
    comparator. 'Similar' operations will count as partial matches. Note
    that 'is' and 'is not' are categorized as the same operator, as are
    'in' and 'not in'.
    """
    opTypes: Tuple[type, ...]
    partialTypes: Tuple[type, ...]

    def __init__(
        self,
        op: str = '+',
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        A specific operator must be specified as an `OpStr`. Use the text
        you'd write in Python to perform that operation (e.g., '//',
        '<=', or 'and'). The two ambiguous cases are + and - which have
        both binary and unary forms. Add a 'u' beforehand to get their
        unary forms. Note that 'not in' and 'is not' are both allowed,
        but they are treated the same as 'in' and 'is'.
        """
        super().__init__(**kwargs)
        self.op = op
        # Determine correct + similar types
        typesToMatch: Optional[OpMapEntry] = OP_MAP.get(op)

        if typesToMatch is None:
            raise ValueError(f"Unrecognized operator '{op}'.")

        self.opTypes, self.partialTypes = typesToMatch

    def structureString(self) -> str:
        return f"operator '{self.op}'"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        for node in self._walkNodesOfType(
            syntax_tree,
            (ast.UnaryOp, ast.BinOp, ast.BoolOp, ast.Compare)
        ):
            # Determine not/partial/full status of match...
            match: LiteralType[True, "partial", False] = False
            if isinstance(node, ast.Compare):
                if any(
                    isinstance(op, self.opTypes)
                    for op in node.ops
                ):
                    match = True
                elif match is False and any(
                    isinstance(op, self.partialTypes)
                    for op in node.ops
                ):
                    match = "partial"
            else:
                if isinstance(node.op, self.opTypes):
                    match = True
                elif (
                    match is False
                and isinstance(node.op, self.partialTypes)
                ):
                    match = "partial"

            # Yield node if it's a partial or full match
            if match:
                yield (node, match is True)


class SpecificNode(ASTRequirement, Generic[AT]):
    """
    A flexible check where you can simply specify the AST node class(es)
    that you're looking for, plus a filter function to determine which
    matches are full/partial/non-matches. This does not perform any
    complicated sub-checks and doesn't have the cleanest structure
    string, so other `ASTRequirement` sub-classes are preferable if one
    of them can match what you want.
    """
    nodeTypes: Tuple[type[AT], ...]
    """
    The tuple of allowed `ast.AST` node types
    """

    def __init__(
        self,
        nodeTypes: Union[type[AT], Sequence[type[AT]]],
        filterFunction: Optional[Callable[[ast.AST], bool]] = None,
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        Either a single AST node class (from the `ast` module, for
        example `ast.Break`) or a sequence of such classes is required to
        specify what counts as a match. If a sequence is provided, any of
        those node types will match; a `ValueError` will be raised if an
        empty sequence is provided.

        If a filter function is provided, it will be called with an AST
        node as the sole argument for each node that has one of the
        specified types. If it returns exactly `True`, that node will be
        counted as a full match, if it returns exactly `False` that node
        will be counted as a partial match, and if it returns any other
        value (e.g., `None`) then that node will not be counted as a
        match at all.
        """
        super().__init__(**kwargs)
        if isinstance(nodeTypes, type) and issubclass(nodeTypes, ast.AST):
            nodeTypes = (nodeTypes,)
        else:
            nodeTypes = tuple(nodeTypes)
            if len(nodeTypes) == 0:
                raise ValueError(
                    "Cannot specify an empty sequence of node types."
                )
            wrongTypes = tuple(
                [nt for nt in nodeTypes if not issubclass(nt, ast.AST)]
            )
            if len(wrongTypes) > 0:
                raise TypeError(
                    (
                        "All specified node types must be ast.AST"
                        " subclasses, but you provided some node types"
                        " that weren't:\n  "
                    ) + '\n  '.join(repr(nt) for nt in wrongTypes)
                )

        self.nodeTypes = nodeTypes
        self.filterFunction = filterFunction

    def structureString(self) -> str:
        if len(self.nodeTypes) == 1:
            result = f"{self.nodeTypes[0].__name__} node(s)"
        elif len(self.nodeTypes) == 2:
            result = (
                f"either {self.nodeTypes[0].__name__} or"
                f" {self.nodeTypes[1].__name__} node(s)"
            )
        elif len(self.nodeTypes) > 2:
            result = (
                "node(s) that is/are:"
              + ', '.join(nt.__name__ for nt in self.nodeTypes[:-1])
              + ', or ' + self.nodeTypes[-1].__name__
            )

        if self.filterFunction is not None:
            result += " (with additional criteria)"

        return result

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        for node in self._walkNodesOfType(syntax_tree, self.nodeTypes):
            if self.filterFunction is None:
                yield (node, True)
            else:
                matchStatus = self.filterFunction(node)
                if matchStatus in (True, False):
                    yield (node, matchStatus)
                # Otherwise (e.g., None) it's a non-match


class ExactMatch(ASTRequirement):
    """
    A check based on a string which checks for an AST structure that
    exactly matches the structure of the string provided. The string
    must be a single expression or statement, this cannot match multiple
    adjacent statements. All AST nodes that match the node type of the
    outer 

    Examples:

        >>> f = ExactMatch('def f():\\n  return 3')
        >>> m = f.allMatches(ast.parse('def f():\\n  return 3'))
        >>> m.isFull
        True
        >>> m.nFull
        1
        >>> m = f.allMatches(ast.parse('def f():\\n  return 4'))
        >>> m.nFull
        0
        >>> len(m.matchPoints)
        1
        >>> m = f.allMatches(ast.parse('def f():\\n  pass\\n  return 3'))
        >>> m.nFull  # match must be complete & exact
        0
        >>> len(m.matchPoints)
        1
        >>> m = f.allMatches(ast.parse('x = 5\\ndef f():\\n  return 3'))
        >>> m.nFull
        1
        >>> m.isFull
        True
    """
    required: str
    """
    The requirement string.
    """

    tree: ast.AST
    """
    The parsed syntax tree for our requirement.
    """

    def __init__(
        self,
        required: Union[str, ast.AST],
        **kwargs: Unpack[NumArgs]
    ) -> None:
        """
        A string is required to specify what we're looking for, or an
        ast.AST tree can be specified directly. If given a string, it
        will be parsed as an AST and must contain a single expression or
        statement.
        """
        super().__init__(**kwargs)
        if isinstance(required, str):
            self.required = required
            parsed = ast.parse(required)
            if not isinstance(parsed, ast.Module) or len(parsed.body) != 1:
                raise ValueError(
                    f"Provided code string is not a single statement or"
                    f" expression. Got:\n{required!r}"
                )
            self.tree = parsed.body[0]
        elif isinstance(required, ast.AST):
            try:
                self.required = ast.unparse(required)
            except RecursionError:
                self.required = ast.dump(required)  # awkward backup
            self.tree = required

    def structureString(self) -> str:
        return f"node(s) matching {self.required!r}"

    def _nodesToCheck(
        self,
        syntax_tree: ast.AST
    ) -> Iterator[Tuple[ast.AST, bool]]:
        for node in self._walkNodesOfType(syntax_tree, type(self.tree)):
            if astMatchExact(node, self.tree):
                yield (node, True)
            else:
                yield (node, False)


# TODO: custom classes could be set up for:
# ast.Assert, ast.Delete, ast.Match, ast.Raise, ast.Global, ast.Nonlocal,
# ast.Pass, ast.Break, ast.Continue, ast.JoinedStr/ast.FormattedValue


#----------------#
# Memory Reports #
#----------------#

@functools.total_ordering
class MemReference:
    """
    A class used for representing object references in memory maps and
    diagrams. A reference is usually just an integer but it might also be
    a string for named references.
    """
    def __init__(self, tag: Union[int, str]) -> None:
        """
        Needs to know what number/name we're assigned.
        """
        if not isinstance(tag, (int, str)):
            raise TypeError(
                f"MemReference tag must be either an integer or a string."
                f" (got: {tag} which is a {type(tag)})"
            )
        self.tag = tag

    def __hash__(self) -> int:
        """
        Hash function based on the tag.
        """
        return 1928928 + hash(self.tag)

    def __eq__(self, other: Any) -> bool:
        """
        Comparison for references (two refs with the same tag are the
        same).
        """
        return isinstance(other, MemReference) and self.tag == other.tag

    def __lt__(self, other: Any) -> bool:
        """
        Ordering for references. All numeric references come after all
        string references; within both categories we use the natural
        ordering of their tags.
        """
        if not isinstance(other, MemReference):
            return NotImplemented
        if (
            isinstance(self.tag, type(other.tag))
         or isinstance(other.tag, type(self.tag))
        ):
            return self.tag < other.tag  # type: ignore
        elif isinstance(self.tag, int):  # other must be str
            return True
        else:
            return False

    def __repr__(self) -> str:
        """
        The representation is an @ sign followed by the tag.
        """
        return "@{}".format(self.tag)


MemoryMap: TypeAlias = Dict[int, Tuple[MemReference, Any]]
"""
Maps integer IDs to tuples containing first a `MemReference` object
assigned to an original object and then a shallow version of that object
which has slots that used to contain complex sub-objects replaced with
`MemReference` objects. See `memoryMap`.
"""


SmallType: TypeAlias = Union[
    int,
    float,
    complex,
    bool,
    NoneType  # type: ignore
]
"""
The object types which are small enough to fit into a single field
without using a pointer in theory, which we thus represent without using
a `MemReference` in a memory report.
"""
# Note that NoneType is used over None here because we use get_args and
# isinstance later so it cannot just be None. If we only wanted to
# support Python 3.10+, we could use the union directly in isinstance.


def memoryMap(
    obj: Any,
    assigned: MemoryMap,
    count_from: int = 0,
    name: Optional[str] = None
) -> Tuple[Optional[int], Union[SmallType, str, MemReference]]:
    """
    Modifies the given `MemoryMap` assignment dictionary to include an
    assignment between the given object's ID and a tuple containing a
    `MemReference` assigned to the object, and a shallow object based on
    the given object, where any complex sub-objects replaced by
    `MemReferences` which will also appear in the assignment map. If a
    `name` is provided, the reference for the given object will use that
    name. The assignment map provided to start from must be a
    dictionary, but it may be empty.

    For example, if the original value were the list [[1, 2], 3, [1, 2]]
    where both [1, 2] sublists are the same list we would have the
    following behavior:

    >>> top = [[1, 2], 3]
    >>> top.append(top[0])  # build using append to share refs
    >>> assignments = {}
    >>> memoryMap(top, assignments)
    (1, @0)
    >>> len(assignments)
    2
    >>> assignments[id(top)]  # note @ comes from `MemReference.__repr__`
    (@0, [@1, 3, @1])
    >>> assignments[id(top[0])]
    (@1, [1, 2])
    >>> assignments == {
    ...   id(top): (MemReference(0), [ MemReference(1), 3, MemReference(1) ]),
    ...   id(top[0]): (MemReference(1), [1, 2])
    ... }
    True

    This function returns a tuple containing the highest numerical
    MemReference ID it assigned within the assignments, and the provided
    object if it's small, or a `MemReference` instance if it's large.
    Only tuples, lists, sets, and dicts have their contents replaced;
    custom objects don't. Strings are shown inline, unless
    `INLINE_STRINGS_IN_MEMORY_REPORTS` is set to `False`, in which case
    they are treated as references (but of course not altered). Any
    custom objects are treated as references.

    The first part of the return value will be `None` if no new numerical
    IDs were assigned.

    TODO: More tests for this!
    TODO: How to handle renaming a ref when name= is passed after the
        same object has already been assigned an anonymous reference?!?
    """
    if id(obj) in assigned:
        return None, assigned[id(obj)][0]

    if name is not None:
        my_ref = MemReference(name)
    else:
        my_ref = MemReference(count_from)
        count_from += 1

    shallow: Union[tuple, list, set, dict]
    if (
        isinstance(obj, get_args(SmallType))
     or (INLINE_STRINGS_IN_MEMORY_REPORTS and isinstance(obj, str))
    ):
        # Simple values are used as-is:
        return None, obj
    elif isinstance(obj, (tuple, list, set)):
        # Structures are made shallow and referenced
        # Must happen before recursion:
        assigned[id(obj)] = (my_ref, None)  # placeholder
        parts = []
        for sub in obj:
            highest_id, repl = memoryMap(sub, assigned, count_from)
            parts.append(repl)
            if highest_id is not None:
                count_from = highest_id + 1
            # else don't change count_from; we didn't assign any new IDs
        shallow = type(obj)(parts)
        assigned[id(obj)] = (my_ref, shallow)
        if count_from > 0:
            return count_from - 1, my_ref
        else:
            return None, my_ref
    elif isinstance(obj, dict):
        # Dictionaries use references for both keys and values
        shallow = {}
        # Must happen before recursion
        assigned[id(obj)] = (my_ref, shallow)
        for key in obj:
            highest_id, krepl = memoryMap(key, assigned, count_from)
            if highest_id is not None:
                count_from = highest_id + 1
            # else don't change count_from; we didn't assign any new IDs
            highest_id, vrepl = memoryMap(obj[key], assigned, count_from)
            if highest_id is not None:
                count_from = highest_id + 1
            # else don't change count_from; we didn't assign any new IDs

            # Insert key/value pair
            shallow[krepl] = vrepl

        if count_from > 0:
            return count_from - 1, my_ref
        else:
            return None, my_ref
    else:
        # All other values including strings when
        # INLINE_STRINGS_IN_MEMORY_REPORTS is False are referenced but
        # not made shallow
        assigned[id(obj)] = (my_ref, obj)
        if count_from > 0:
            return count_from, my_ref
        else:
            return None, my_ref


def memoryReport(*objs: Any, **named: Any) -> str:
    """
    Returns a memory report, which is like an exploded repr of one or
    more objects where 'large' values like strings and lists get assigned
    an ID and are reported on a separate line.

    Each of the given objects is processed in sequence, with increasing
    IDs for later objects, and if any keyword arguments are given, those
    keywords are shown first in the memory report as having the
    associated objects as their values.

    Example:

    >>> p = [1, 2]
    >>> g = [p, 3, p, 4]
    >>> print(memoryReport(g), end='')
    @0: [@1, 3, @1, 4]
    @1: [1, 2]
    >>> print(memoryReport(g, p), end='')
    @0: [@1, 3, @1, 4]
    @1: [1, 2]
    >>> print(memoryReport(p, g), end='')
    @0: [1, 2]
    @1: [@0, 3, @0, 4]
    >>> print(memoryReport(p=p, g=g), end='')
    p: @0
    g: @1
    @0: [1, 2]
    @1: [@0, 3, @0, 4]
    >>> print(memoryReport(p=p, g=g, h=[1, 2]), end='')
    p: @0
    g: @1
    h: @2
    @0: [1, 2]
    @1: [@0, 3, @0, 4]
    @2: [1, 2]
    >>> inlineStringsInMemoryReports(True)
    >>> print(memoryReport(p=p, g=g, h='hi'), end='')
    p: @0
    g: @1
    h: 'hi'
    @0: [1, 2]
    @1: [@0, 3, @0, 4]
    >>> print(memoryReport(p), end='')
    @0: [1, 2]
    >>> r = ['hi']
    >>> r.append(r)
    >>> inlineStringsInMemoryReports(False)
    >>> print(memoryReport(r), end='')
    @0: [@1, @0]
    @1: 'hi'
    >>> print(memoryReport(r=r, h='hi'), end='')
    r: @0
    h: @1
    @0: [@1, @0]
    @1: 'hi'
    >>> inlineStringsInMemoryReports()
    >>> print(memoryReport(r), end='')
    @0: ['hi', @0]
    >>> print(memoryReport(r=r, h='hi'), end='')
    r: @0
    h: 'hi'
    @0: ['hi', @0]
    >>> print(memoryReport(x=5, y=12.0), end='')
    x: 5
    y: 12.0
    """
    refs: MemoryMap = {}
    top = -1
    for obj in objs:
        (new_top, ref) = memoryMap(obj, refs, top + 1)
        if new_top is not None:
            top = new_top

    name_rows = []
    for vname, obj in named.items():
        (new_top, ref) = memoryMap(obj, refs, top + 1)
        if new_top is not None:
            top = new_top
        name_rows.append((vname, ref))

    # Order by named values (in order given) and then numeric values (by
    # number assigned)

    result = ''
    handled = set()
    for vname, ref_to in name_rows:
        result += "{}: {}\n".format(vname, repr(ref_to))
    for obj in named.values():
        handled.add(id(obj))
        ref, shallow = refs.get(id(obj), (None, None))
        if ref is not None:
            result += '{}: {}\n'.format(repr(ref), repr(shallow))
    for ident, (ref, shallow) in sorted(refs.items(), key=lambda x: x[1]):
        if ident in handled:
            continue
        result += '{}: {}\n'.format(repr(ref), repr(shallow))

    return result


class Unreconstructable:
    """
    Represents an object that could not be reconstructed when parsing a
    memory report. Since memory reports use `repr` for unrecognized
    object types, sometimes we might get something like:

        <Foo object at 0x7fec3481a9d1>

    We can't reconstruct that object, but to represent it, we use this
    instances of class, with the raw repr as the stored representation.

    This object regurgitates that representation when `repr` is called
    on it.

    Two `Unreconstructable` objects are considered equal if they have
    the same representation (which is often NOT true of the actual
    objects they were derived from). They are NOT considered equal to
    any other kinds of objects, so they won't be equal to the object
    whose repr they were derived from (unless it was an
    `Unreconstructable` already).
    """
    def __init__(self, representation: str) -> None:
        self.representation = representation

    def __hash___(self) -> int:
        return 37 + 17*hash(self.representation)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Unreconstructable)
        and self.representation == other.representation
        )

    def __repr__(self) -> str:
        return self.representation


DELIMITERS: Dict[str, str] = {
    '[': ']',
    '(': ')',
    '{': '}',
}
"""
Python delimiters that can lead to line continuation...
"""


def parseMemoryReport(report: str) -> Any:
    """
    Parses a memory report to create a partially-reconstructed object.

    NOTE: This function evaluates the report as Python code, and should
    NOT be used with untrusted code.

    TODO: Use ast.listeral_eval instead? Would have to shoehorn our
    function calls into other forms... ?

    The result is a dictionary with strings (for variables) and
    `MemReference`s (for numbered references) as keys and the
    corresponding objects for values. To the extent possible, the
    objects are reconstructed from the string contents of the memory
    report, but `Unreconstructable` instances are used when contents are
    encountered that can't be backed out from their string
    representations.

    Examples:

    >>> r = "var: @1\\n@1: [1, 2]"
    >>> re.sub(r"^([a-zA-Z0-9_]+):", r"'\\1':", r, re.MULTILINE)
    "'var': @1\\n@1: [1, 2]"
    >>> parseMemoryReport("var: @1\\n@1: [1, 2]")
    {'var': @1, @1: [1, 2]}
    >>> parseMemoryReport('''\\
    ... var: @1
    ... @1: [1, @2, 'hi']
    ... @2: {
    ...     'key': @3,
    ...     'k2': 4.5,
    ... }
    ... @3: { 1, 2 }
    ... ''') # note that MemReferences are shown as their reprs
    {'var': @1, @1: [1, @2, 'hi'], @2: {'key': @3, 'k2': 4.5}, @3: {1, 2}}
    """
    # Add quotes to variable names at the start of lines...
    report = re.sub(
        r"^([a-zA-Z0-9_]+):",
        r"'\1':",
        report,
        flags=re.MULTILINE
    )
    # Use token-replacement to change '@' outside of strings into calls
    # to `MemReference`
    buff = io.StringIO(report)
    munged: List[Union[Tuple[int, str], tokenize.TokenInfo]] = []
    expecting_id = False
    unreconstructable: Optional[List[tokenize.TokenInfo]] = None
    delimStack: List[str] = []
    for tok in tokenize.generate_tokens(buff.readline):
        # Handle delimeter-zone recognition
        if len(delimStack) > 0:
            if tok.type == token.OP and tok.string == delimStack[-1]:
                delimStack.pop()
            # Appended below
        elif (
            unreconstructable is None
        and tok.type == token.OP
        and tok.string in DELIMITERS
        ):
            delimStack.append(DELIMITERS[tok.string])
            # Appended below

        # Handle ID replacement, unreconstructables, and comma-insertion
        if expecting_id:
            # Just saw an '@' so we must see a NUMBER next
            if tok.type != token.NUMBER:
                raise SyntaxError(
                    f"'@' not followed by a number at column"
                    f" {tok.start[1]} on line {tok.start[0]}."
                )
            else:
                # Turn this into a `MemReference` construction call
                munged.extend([
                    (token.NAME, 'MemReference'),
                    (token.OP, '('),
                    tok,
                    (token.OP, ')'),
                ])
                # No longer expecting an ID
                expecting_id = False

        elif unreconstructable is not None:
            # Compiling unreconstructable stuff between '<' and '>'
            if tok.type == token.OP and tok.exact_type == token.GREATER:
                # End of the stuff; wrap it in an `Unreconstructable`
                # call so we preserve it as a string
                munged.extend([
                    (token.NAME, 'Unreconstructable'),
                    (token.OP, '('),
                    (
                        token.STRING,
                        repr(
                            '<'
                          + tokenize.untokenize(unreconstructable)
                          + '>'
                        )
                    ),
                    (token.OP, ')'),
                ])
                unreconstructable = None
            else:
                # Not the end yet; gather more
                unreconstructable.append(tok)

        elif tok.type == token.OP and tok.exact_type == token.LESS:
            # Start of unreconstructable stuff ('<' operator cannot
            # appear naturally in a memory report)
            unreconstructable = []

        elif tok.type == token.OP and tok.exact_type == token.AT:
            # '@' sign so we must see a number next
            if expecting_id:
                raise SyntaxError(
                    f"Double '@' at column {tok.start[1]} on line"
                    f" {tok.start[0]}."
                )
            expecting_id = True

        elif tok.type == token.NEWLINE and len(delimStack) == 0:
            # Inject commas before un-delimited newlines
            munged.append((token.COMMA, ','))
            munged.append(tok)

        else:
            munged.append(tok)

    # Create our dictionary
    # TODO: Use ast.literal_eval instead, by turning MemReference and
    # Unreconstructable objects into specially-prefixed string tokens
    # instead of function call tokens...
    return eval('{' + tokenize.untokenize(munged) + '}')


def yieldMemoryReportDifferences(
    attempt: Union[str, Any],
    correct: Union[str, Any],
    targets: Optional[
        Tuple[Union[str, MemReference], Union[str, MemReference]]
    ] = None,
    env: Optional[Dict[MemReference, MemReference]] = None
) -> Iterator[str]:
    """
    Yields strings describing the differences between two memory
    reports, ignoring object ID mismatches and re-orderings of included
    objects/variables. The second memory report is treated as the
    correct one when referenced in the strings returned. If either report
    given is not a string, it will be treated as a reconstructed object
    to be compared directly.

    The memory reports may be given as strings, or instead as
    dictionaries mapping variable name strings and/or ID `MemReference`
    objects to flat objects that contain `MemReference` where they
    refer to each other (i.e., the result of `parseMemoryReport`). This
    function has the same limitations as `parseMemoryReport` in terms of
    reconstructing objects from their representations, but two
    `Unreconstructable` objects with the same string will be considered
    equivalent (even though that is often in fact NOT the case).

    If `targets` is given, it should be a pair of strings or
    `MemReference` objects naming variables or referenced IDs from each
    memory report, `attempt` first and then `correct`. When `targets` is
    given, the two targets are assumed to represent the same object and
    just the differences within that object are reported. Yields nothing
    and raises `StopIteration` if it can't find any differences.

    If `env` is given (it should not normally be by users of this code)
    it must be a dictionary mapping `MemReference` objects found in the
    `attempt` map to `MemReference` objects found in the `correct` map.
    This is used during recursion to establish bindings.

    Examples:

    >>> list(yieldMemoryReportDifferences('@0: [0]', '@0: [0]'))
    []
    >>> list(yieldMemoryReportDifferences('@100: [0]', '@0: [0]'))
    []
    >>> list(yieldMemoryReportDifferences('''\\
    ... @100: [0, @200]
    ... @200: [1, 1]
    ... ''', '''\\
    ... @0: [0, @1]
    ... @1: [1, 1]
    ... '''))
    []
    >>> # TODO: Make this recognize more of the similarities?
    >>> d = list(yieldMemoryReportDifferences('''\\
    ... @100: [0, @200]
    ... @200: [1, 2]
    ... ''', '''\\
    ... @0: [0, @1]
    ... @1: [1, 1]
    ... '''))
    >>> len(d)
    4
    >>> d[0]
    'reference @100 did not match any expected object'
    >>> d[1]
    'reference @200 did not match any expected object'
    >>> d[2]
    'did not find a match for list @0'
    >>> d[3]
    'did not find a match for list @1'
    >>> env = {}
    >>> dl = list(yieldMemoryReportDifferences('''\\
    ... x: @100
    ... @100: [0, @200]
    ... @200: [1, 2]
    ... ''', '''\\
    ... x: @0
    ... @0: [0, @1]
    ... @1: [1, 1]
    ... ''',
    ... None,
    ... env))
    >>> env
    {@100: @0, @200: @1}
    >>> dl
    ['list @200 slot 1: value 2 differs from expected value 1']
    >>> list(yieldMemoryReportDifferences('''\\
    ... x: 5
    ... y: @1
    ... @1: [3, @1]
    ... ''', '''\\
    ... x: 5
    ... y: @1
    ... @1: [3, 1]
    ... '''))
    ['list @1 slot 1: reference @1 differs from expected value 1']
    >>> d = list(yieldMemoryReportDifferences('x: 5\\ny: 6', 'x: 6\\ny: 7'))
    >>> len(d)
    2
    >>> d[0]
    "variable 'x': value 5 differs from expected value 6"
    >>> d[1]
    "variable 'y': value 6 differs from expected value 7"
    >>> list(yieldMemoryReportDifferences(
    ...     'x: 5\\ny: 6',
    ...     'x: 6\\ny: 7',
    ...     ('x', 'x')
    ... ))
    ["variable 'x': value 5 differs from expected value 6"]
    >>> list(yieldMemoryReportDifferences(
    ...     'x: 5\\ny: 6',
    ...     'x: 6\\ny: 7',
    ...     ('x', 'y')
    ... ))
    ["variable 'x': value 5 differs from expected value 7"]
    >>> list(yieldMemoryReportDifferences(
    ...     'x: 5\\ny: 6',
    ...     'x: 6\\ny: 7',
    ...     ('y', 'x')
    ... ))
    []
    >>> list(yieldMemoryReportDifferences(
    ...     'x: 5\\ny: 6',
    ...     'x: 6\\ny: 7',
    ...     ('y', 'y')
    ... ))
    ["variable 'y': value 6 differs from expected value 7"]
    >>> list(yieldMemoryReportDifferences(
    ...     'x: @1\\n@1: [3, 4]',
    ...     'x: @4\\n@4: [3, 4]'
    ... ))
    []
    >>> d = list(yieldMemoryReportDifferences(
    ...     'x: @1\\n@1: [3, 4]',
    ...     'y: @4\\n@4: [3, 4]'
    ... ))
    >>> len(d)
    2
    >>> d[0]
    "expected variable 'y' was not defined"
    >>> d[1]
    "variable 'x' should not be defined"
    >>> d = list(yieldMemoryReportDifferences(
    ...     'x: @1\\ny: "hi"\\n@1: [3, 4]',
    ...     'y: @4\\n@4: [3, 4]'
    ... ))
    >>> len(d)
    2
    >>> d[0]
    "variable 'x' should not be defined"
    >>> d[1]
    "variable 'y': value should have been a reference"
    >>> list(yieldMemoryReportDifferences(
    ...     'x: @1\\n@1: [3, 4]',
    ...     'y: @4\\n@4: [3, 4]',
    ...     (MemReference(1), MemReference(4))
    ... ))
    []
    >>> list(yieldMemoryReportDifferences(
    ...     '@1: [3, 4]\\n@2: [4, 5]',
    ...     '@1: [3, 4]\\n@2: [4, 5]',
    ... ))
    []
    >>> list(yieldMemoryReportDifferences(
    ...     '@1: [4, 5]\\n@2: [3, 4]',
    ...     '@1: [3, 4]\\n@2: [4, 5]',
    ... ))
    []
    >>> d = list(yieldMemoryReportDifferences(
    ...     '@1: [3, 4]\\n@2: [4, 5]',
    ...     '@1: [3, 4]\\n@2: [4, 5]',
    ...     env={MemReference(1): MemReference(2)}
    ... ))
    >>> len(d)
    2
    >>> for diff in d:
    ...     print(diff)
    reference @2 did not match any expected object
    did not find a match for list @1
    """
    if env is None:
        env = {}

    if isinstance(attempt, str):
        attempt = parseMemoryReport(attempt)

    if isinstance(correct, str):
        correct = parseMemoryReport(correct)

    if targets is None:
        # Scan first for missing variables, then for extra variables
        avars = { key for key in attempt if isinstance(key, str) }
        cvars = { key for key in correct if isinstance(key, str) }
        missing = cvars - avars
        for var in missing:
            yield f"expected variable '{var}' was not defined"
        extra = avars - cvars
        for var in extra:
            yield f"variable '{var}' should not be defined"
        both = avars & cvars
        # Now yield differences in every matching variable, in the order
        # they appear in the attempt
        for var in attempt:
            if isinstance(var, str) and var in both:
                yield from yieldMemoryReportDifferences(
                    attempt,
                    correct,
                    (var, var),
                    env
                )

        # Finally, report unmatched references
        for key in attempt:
            if isinstance(key, MemReference) and key not in env:
                greedy = greedyUntakenMatch(attempt, correct, key, env)
                if greedy is None:
                    yield (
                        f"reference {repr(key)} did not match any expected"
                        f" object"
                    )
                else:
                    env[key] = greedy
            # if not a `MemReference` we handled it above, and if in the
            # env, it's already been matched

        # Report unassigned `MemReference`s
        assigned = set(env.values())
        for key in correct:
            if key not in assigned and isinstance(key, MemReference):
                yield (
                    f"did not find a match for"
                    f" {type(correct[key]).__name__} {repr(key)}"
                )
    else:
        # Look only for differences in these specific targets
        aTarget, cTarget = targets
        if aTarget not in attempt:
            raise RuntimeError(
                f"Target '{aTarget}' not found in attempt report:\n{attempt}"
            )
        if cTarget not in correct:
            raise RuntimeError(
                f"Target '{cTarget}' not found in correct report:\n{correct}"
            )

        # Get objects to compare
        aObj = attempt[aTarget]
        cObj = correct[cTarget]

        # generate prefix for locating differences
        if isinstance(aTarget, str):
            prefix = f"variable '{aTarget}'"
        else:
            prefix = f"{type(aObj).__name__} {aTarget}"

        yield from reportObjDiffs(attempt, correct, aObj, cObj, prefix, env)


def reportObjDiffs(
    attempt: Any,
    correct: Any,
    aObj: Union[MemReference, Any],
    cObj: Union[MemReference, Any],
    prefix: str = "",
    env: Optional[Dict[MemReference, MemReference]] = None
):
    """
    Yields strings describing differences between two specific objects
    (which could be `MemReference`s) in the given `attempt` and
    `correct` parsed memory maps (i.e., arbitrary objects). The reports
    include the provided prefix. `env` is used to supply a
    reference-to-reference binding dictionary, but should normally be
    left as `None`.
    """
    if env is None:
        env = {}

    if isinstance(cObj, MemReference):
        if not isinstance(aObj, MemReference):
            yield f"{prefix}: value should have been a reference"
        else:
            if aObj in env:
                if env[aObj] != cObj:
                    # Mismatch: you're using an alias when the
                    # correct value is a clone (or a different
                    # object entirely)
                    yield (
                        f"{prefix}: reference {repr(aObj)} cannot"
                        f" match {repr(cObj)} because {repr(aObj)}"
                        f" is already assigned to match"
                        f" {repr(env[aObj])}. This means you have"
                        f" used two references to the same object"
                        f" where the correct solution used"
                        f" references to different objects."
                    )
                # else differences in these objects have been
                # enumerated elsewhere
            elif cObj in env.values():
                # Mismatch: you're using a new reference where an
                # alias is needed
                # reverse lookup of the key
                rev = [key for key in env if env[key] == cObj][0]
                yield (
                    f"{prefix}: reference {repr(aObj)} cannot match"
                    f" {repr(cObj)} because {repr({cObj})} is already"
                    f" assigned as the match for {repr(rev)}. This"
                    f" means you have used two references to"
                    f" different objects where the correct solution"
                    f" used two references to the same object."
                )
            else:
                # Assign them to each other
                env[aObj] = cObj
                # They're both references; so explore them
                yield from yieldMemoryReportDifferences(
                    attempt,
                    correct,
                    (aObj, cObj),
                    env
                )
                # new prefixes will be established...
    elif isinstance(aObj, MemReference):
        yield (
            f"{prefix}: reference {repr(aObj)} differs from expected"
            f" value {repr(cObj)}"
        )
    else:
        # Neither is a reference
        if type(aObj) != type(cObj):
            yield (
                f"{prefix}: value has wrong type {type(aObj)}"
                f" (expected {type(cObj)})"
            )

        elif isinstance(aObj, (list, tuple)):
            longer = len(aObj) - len(cObj)
            typ = type(aObj).__name__
            if longer > 0:
                yield f"{prefix}: {typ} has {longer} extra item(s)"
            elif longer < 0:
                yield f"{prefix}: {typ} has {-longer} missing item(s)"
            for index in range(min(len(aObj), len(cObj))):
                aSub = aObj[index]
                cSub = cObj[index]
                yield from reportObjDiffs(
                    attempt,
                    correct,
                    aSub,
                    cSub,
                    prefix + f" slot {index}",
                    env
                )

        elif isinstance(aObj, dict):
            aKeys = set(aObj)
            cKeys = set(cObj)
            # Greedily explore possible key/key matches for
            # MemReference keys...
            aRefs = [k for k in aKeys if isinstance(k, MemReference)]
            cRefs = [k for k in cKeys if isinstance(k, MemReference)]
            aNot = aKeys - set(aRefs)
            cNot = cKeys - set(cRefs)
            # Starting values that include non-reference items
            missing = list(cNot - aNot)
            extra = list(aNot - cNot)
            both = list(aNot & cNot)
            for mk in missing:
                yield f"{prefix} is missing key {repr(mk)}"
            for ek in extra:
                yield f"{prefix} should not have key {repr(ek)}"
            for bk in both:
                aVal = aObj[bk]
                cVal = cObj[bk]
                yield from reportObjDiffs(
                    attempt,
                    correct,
                    aVal,
                    cVal,
                    prefix + " slot " + repr(bk),
                    env
                )

            for ak in aRefs:
                if ak in env:
                    matched = env[ak]
                    if matched not in cRefs:
                        yield (
                            f"{prefix} should not have key"
                            f" {repr(ak)} (it matches"
                            f" {repr(env[ak])} which should not"
                            f" be one of the keys of {prefix}"
                        )
                    else:
                        aVal = aObj[ak]
                        cVal = cObj[matched]
                        yield from reportObjDiffs(
                            attempt,
                            correct,
                            aVal,
                            cVal,
                            prefix + " slot " + repr(ak),
                            env
                        )
                else:
                    greedy = greedyUntakenMatch(
                        attempt,
                        correct,
                        ak,
                        env,
                        cRefs
                    )
                    if greedy is None:
                        yield (
                            f"{prefix} should not have key {repr(ak)}"
                            f" (it can't match any relevant keys in the"
                            f" correct report)"
                        )
                    # No diffs if greedy is not None

            # handle leftover refs
            for ck in cRefs:
                if ck not in env.values():
                    yield (
                        f"{prefix} is missing a key that matches"
                        f" reference {repr(ck)} which has structure"
                        f" {repr(correct[ck])}"
                    )

        elif isinstance(aObj, set):
            # Split into MemReference and non-MemReference pools
            aNonRefs = set()
            aSetRefs = set()
            cNonRefs = set()
            cSetRefs = set()
            for item in aObj:
                if isinstance(item, MemReference):
                    aSetRefs.add(item)
                else:
                    aNonRefs.add(item)
            for item in cObj:
                if isinstance(item, MemReference):
                    cSetRefs.add(item)
                else:
                    cNonRefs.add(item)

            extraNon = aNonRefs - cNonRefs
            missingNon = cNonRefs - aNonRefs
            # non-reference items in both sets aren't differences

            # Report missing/extra non-reference keys
            for mi in missingNon:
                yield f"{prefix} is missing item {repr(mi)}"
            for ei in extraNon:
                yield f"{prefix} should not have item {repr(ei)}"

            for aRef in aSetRefs:
                greedy = greedyUntakenMatch(
                    attempt,
                    correct,
                    aRef,
                    env,
                    cSetRefs
                )
                if greedy is None:
                    yield (
                        f"{prefix} should not include item {repr(aRef)}"
                        f" (it can't match any relevant items in the"
                        f" correct report)"
                    )
                # No diffs if greedy is not None

            # Report unmatched refs in correct report
            for cRef in cSetRefs:
                if cRef not in env.values():
                    yield (
                        f"{prefix} had no match for reference"
                        f" {repr(cRef)} with structure"
                        f" {repr(correct[cRef])}"
                    )

        else:
            if aObj != cObj:
                yield (
                    f"{prefix}: value {repr(aObj)} differs from"
                    f" expected value {repr(cObj)}"
                )


def greedyUntakenMatch(
    attempt: Any,
    correct: Any,
    key: MemReference,
    env: Optional[Dict[MemReference, MemReference]] = None,
    targets: Optional[Collection[MemReference]] = None
) -> Optional[MemReference]:
    """
    Finds the first memory key in the `correct` memory map which maps to
    a perfect match for the object from the specified `key` of the
    `attempt`, updating `env` along the way with any object
    correspondences discovered. Will not match a key that's already
    assigned a match in the provided `env`. If `targets` is given it
    should be a collection of `MemReference`s, and matches will only be
    attempted against members of that collection.

    For example:

    >>> env = {}
    >>> greedyUntakenMatch(
    ...     {MemReference(1): [1, 2]},
    ...     {MemReference(23): [1, 2]},
    ...     MemReference(1),
    ...     env
    ... )
    @23
    >>> env
    {@1: @23}
    >>> env = {}
    >>> greedyUntakenMatch(
    ...     {MemReference(1): [1, 2], MemReference(2): [3, 4]},
    ...     {MemReference(23): [1, 2], MemReference(24): [3, 4]},
    ...     MemReference(2),
    ...     env
    ... )
    @24
    >>> env
    {@2: @24}
    >>> env = {}
    >>> greedyUntakenMatch(
    ...     {MemReference(1): [1, 2], MemReference(2): [3, 4]},
    ...     {MemReference(23): [1, 3], MemReference(24): [2, 4]},
    ...     MemReference(1),
    ...     env
    ... ) is None
    True
    >>> env
    {}
    >>> env = {}
    >>> greedyUntakenMatch(
    ...     {MemReference(1): [1, 2], MemReference(2): [3, 4]},
    ...     {MemReference(23): [1, 2], MemReference(24): [3, 4]},
    ...     MemReference(1),
    ...     env,
    ...     { MemReference(24) }
    ... ) is None
    True
    >>> env
    {}
    >>> env = {}
    >>> greedyUntakenMatch(
    ...     {MemReference(1): [1, 2], MemReference(2): [3, 4]},
    ...     {MemReference(23): [1, 2], MemReference(24): [3, 4]},
    ...     MemReference(1),
    ...     env,
    ...     set()
    ... ) is None
    True
    >>> env
    {}
    >>> env = {}
    >>> greedyUntakenMatch(
    ...     {MemReference(1): [1, 2], MemReference(2): [1, 2]},
    ...     {MemReference(23): [1, 2]},
    ...     MemReference(1),
    ...     env
    ... )
    @23
    >>> env
    {@1: @23}
    >>> # Can't match because reference is taken
    >>> greedyUntakenMatch(
    ...     {MemReference(1): [1, 2], MemReference(2): [1, 2]},
    ...     {MemReference(23): [1, 2]},
    ...     MemReference(2),
    ...     env
    ... ) is None
    True
    >>> env
    {@1: @23}
    """
    if env is None:
        env = {}

    if targets is None:
        targets = correct.keys()

    taken = set(env.values())
    for target in targets:
        if target in taken:
            continue
        probe = {}
        probe.update(env)
        probe[key] = target
        try:
            next(
                yieldMemoryReportDifferences(
                    attempt,
                    correct,
                    (key, target),
                    probe
                )
            )
        except StopIteration:
            # No differences, so apply probe env & return
            env.update(probe)
            return target

    # No untaken targets found which did not have any differences...
    return None


#------------------#
# Message Handling #
#------------------#

def indent(msg: str, level: int = 2) -> str:
    """
    Indents every line of the given message (a string).
    """
    indent = ' ' * level
    return indent + ('\n' + indent).join(msg.splitlines())


def ellipsis(string: str, maxlen: int = 40) -> str:
    """
    Returns the provided string as-is, or if it's longer than the given
    maximum length, returns the string, truncated, with '...' at the
    end, which will, including the ellipsis, be exactly the given
    maximum length. The maximum length must be 4 or more.
    """
    if len(string) > maxlen:
        return string[:maxlen - 3] + "..."
    else:
        return string


def dual_string_repr(string: str) -> Tuple[str, str]:
    """
    Returns a pair containing full and truncated representations of the
    given string. The formatting of even the full representation depends
    on whether it's a multi-line string or not and how long it is.
    """
    lines = string.split('\n')
    if len(repr(string)) < 80 and len(lines) == 1:
        full = repr(string)
        short = repr(string)
    else:
        full = '"""\\\n' + string.replace('\r', '\\r') + '"""'
        if len(string) < 240 and len(lines) <= 7:
            short = full
        elif len(lines) > 7:
            head = '\n'.join(lines[:7])
            short = (
                '"""\\\n' + ellipsis(head.replace('\r', '\\r'), 240) + '"""'
            )
        else:
            short = (
                '"""\\\n' + ellipsis(string.replace('\r', '\\r'), 240) + '"""'
            )

    return (full, short)


def limited_repr(string: str) -> str:
    """
    Given a string that might include multiple lines and/or lots of
    characters (regardless of lines), returns version cut off by
    ellipses either after 5 or so lines, or after 240 characters.
    Returns the full string if it's both less than 240 characters and
    less than 5 lines.
    """
    # Split by lines
    lines = string.split('\n')

    # Already short enough
    if len(string) < 240 and len(lines) < 5:
        return string

    # Try up to 5 lines, cutting them off until we've got a
    # short-enough head string
    for n in range(min(5, len(lines)), 0, -1):
        head = '\n'.join(lines[:n])
        if n < len(lines):
            head += '\n...'
        if len(head) < 240:
            break
    else:
        # If we didn't break, just use first 240 characters
        # of the string
        head = string[:240] + '...'

    # If we cut things too short (e.g., because of initial
    # empty lines) use first 240 characters of the string
    if len(head) < 12:
        head = string[:240] + '...'

    return head


def msg_color(category: MessageCategory) -> Optional[str]:
    """
    Returns an ANSI color code for the given category of message (one of
    the `MessageCategory` strings), or returns None if COLORS is
    disabled or an invalid category is provided.
    """
    if not COLORS:
        return None
    else:
        return MSG_COLORS.get(category)


def print_message(msg: str, color: Optional[str] = None) -> None:
    """
    Prints a test result message to `PRINT_TO`, but also flushes stdout,
    stderr, and the `PRINT_TO` file beforehand and afterwards to improve
    message ordering.

    If a color is given, it should be an ANSI terminal color code string
    (just the digits, for example '34' for blue or '1;31' for bright red).
    """
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        PRINT_TO.flush()
    except Exception:
        pass

    # Make the whole message colored
    if color:
        print(f"\x1b[{color}m", end="", file=PRINT_TO)
        suffix = "\x1b[0m"
    else:
        suffix = ""

    print(msg + suffix, file=PRINT_TO)

    sys.stdout.flush()
    sys.stderr.flush()
    try:
        PRINT_TO.flush()
    except Exception:
        pass


def expr_details(context: 'ContextDict') -> Tuple[str, str]:
    """
    Returns a pair of strings containing base and extra details for an
    expression as represented by a dictionary returned from
    `get_my_context`. The extra message may be an empty string if the
    base message contains all relevant information.
    """
    # Expression that was evaluated
    expr = context.get("expr_src", "???")
    short_expr = ellipsis(expr, 78)
    # Results
    msg = ""
    extra_msg = ""

    # Base message
    msg += f"Test expression was:\n{indent(short_expr, 2)}"

    # Figure out values to display
    vdict = context.get("values", {})
    if context.get("relevant") is not None:
        show = sorted(
            context["relevant"],
            key=lambda fragment: (expr.index(fragment), len(fragment))
        )
    else:
        show = sorted(
            vdict.keys(),
            key=lambda fragment: (expr.index(fragment), len(fragment))
        )

    if len(show) > 0:
        msg += "\nValues were:"

    longs = []
    for key in show:
        if key in vdict:
            val = repr(vdict[key])
        else:
            val = "???"

        entry = f"  {key} = {val}"
        fits = ellipsis(entry)
        msg += '\n' + fits
        if fits != entry:
            longs.append(entry)

    # Extra message
    if short_expr != expr:
        if extra_msg != "" and not extra_msg.endswith('\n'):
            extra_msg += '\n'
        extra_msg += f"Full expression:\n{indent(expr, 2)}"
    extra_values = sorted(
        [
            key
            for key in vdict.keys()
            if key not in context.get("relevant", [])
        ],
        key=lambda fragment: (expr.index(fragment), len(fragment))
    )
    if context.get("relevant") is not None and extra_values:
        if extra_msg != "" and not extra_msg.endswith('\n'):
            extra_msg += '\n'
        extra_msg += "Extra values:"
        for ev in extra_values:
            if ev in vdict:
                val = repr(vdict[ev])
            else:
                val = "???"

            entry = f"  {ev} = {val}"
            fits = ellipsis(entry, 78)
            extra_msg += '\n' + fits
            if fits != entry:
                longs.append(entry)

    if longs:
        if extra_msg != "" and not extra_msg.endswith('\n'):
            extra_msg += '\n'
        extra_msg += "Full values:"
        for entry in longs:
            extra_msg += '\n' + entry

    return msg, extra_msg


#------------#
# Comparison #
#------------#

def findFirstDifference(
    val: Any,
    ref: Any,
    comparing: Optional[Set[Tuple[int, int]]] = None
) -> Optional[str]:
    """
    Returns a string describing the first point of difference between
    `val` and `ref`, or None if the two values are equivalent. If
    IGNORE_TRAILING_WHITESPACE is True, trailing whitespace will be
    trimmed from each string before looking for differences.

    A small amount of difference is ignored between floating point
    numbers, including those found in complex structures.

    Works for recursive data structures; the `comparing` argument serves
    as a memo to avoid infinite recursion, and the `within` argument
    indicates where in a complex structure we are; both should normally
    be left as their defaults.
    """
    if comparing is None:
        comparing = set()

    cmpkey = (id(val), id(ref))
    if cmpkey in comparing:
        # Either they differ somewhere else, or they're functionally
        # identical
        # TODO: Does this really ward off all infinite recursion on
        # finite structures?
        return None

    comparing.add(cmpkey)

    try:
        simple = val == ref
    except RecursionError:
        simple = False

    if simple:
        return None

    else:  # let's hunt for differences
        if (
            isinstance(val, (int, float, complex))
        and isinstance(ref, (int, float, complex))
        ):  # what if they're both numbers?
            if cmath.isclose(
                val,
                ref,
                rel_tol=FLOAT_REL_TOLERANCE,
                abs_tol=FLOAT_ABS_TOLERANCE
            ):
                return None
            else:
                if isinstance(val, complex) and isinstance(ref, complex):
                    return f"complex numbers {val} and {ref} are different"
                elif isinstance(val, complex) or isinstance(ref, complex):
                    return f"numbers {val} and {ref} are different"
                elif val > 0 and ref < 0:
                    return f"numbers {val} and {ref} have different signs"
                else:
                    return f"numbers {val} and {ref} are different"

        elif type(val) != type(ref):  # different types; not both numbers
            svr = ellipsis(repr(val), 8)
            srr = ellipsis(repr(ref), 8)
            return (
                f"values {svr} and {srr} have different types"
                f" ({type(val)} and {type(ref)})"
            )

        elif isinstance(val, str):  # both strings
            if '\n' in val or '\n' in ref:
                # multi-line strings; look for first different line
                # Note: we *don't* use splitlines here because it will
                # give multiple line breaks in a \r\r\n situation like
                # those caused by csv.DictWriter on windows when opening
                # a file without newlines=''. We'd like to instead ignore
                # '\r' as a line break (we're not going to work on early
                # Macs) and strip it if IGNORE_TRAILING_WHITESPACE is on.
                valLines = val.split('\n')
                refLines = ref.split('\n')

                # First line # where they differ (1-indexed)
                firstDiff = None

                # Compute point of first difference
                i = None
                for i in range(min(len(valLines), len(refLines))):
                    valLine = valLines[i]
                    refLine = refLines[i]
                    if IGNORE_TRAILING_WHITESPACE:
                        valLine = valLine.rstrip()
                        refLine = refLine.rstrip()

                    if valLine != refLine:
                        firstDiff = i + 1
                        break
                else:
                    if i is not None:
                        # if one has more lines
                        if len(valLines) != len(refLines):
                            # In this case, one of the two is longer...
                            # If IGNORE_TRAILING_WHITESPACE is on, and
                            # the longer one just has a blank extra line
                            # (possibly with some whitespace on it), then
                            # the difference is just in the presence or
                            # absence of a final newline, which we also
                            # count as a "trailing whitespace" difference
                            # and ignore. Note that multiple final '\n'
                            # characters will be counted as a difference,
                            # since they result in multiple final
                            # lines...
                            if (
                                IGNORE_TRAILING_WHITESPACE
                            and (
                                    (
                                        len(valLines) == len(refLines) + 1
                                    and valLines[i + 1].strip() == ''
                                    )
                                 or (
                                        len(valLines) + 1 == len(refLines)
                                    and refLines[i + 1].strip() == ''
                                    )
                                )
                            ):
                                return None
                            else:
                                # If we're attending trailing whitespace,
                                # or if there are multiple extra lines or
                                # the single extra line is not blank,
                                # then that's where our first difference
                                # is.
                                firstDiff = i + 2
                        else:
                            # There is no difference once we trim
                            # trailing whitespace...
                            return None
                    else:
                        # Note: this is a line number, NOT a line index
                        firstDiff = 1

                got = "nothing (string had fewer lines than expected)"
                expected = "nothing (string had more lines than expected)"
                i = firstDiff - 1
                if i < len(valLines):
                    got = repr(valLines[i])
                if i < len(refLines):
                    expected = repr(refLines[i])

                limit = 60
                shortGot = ellipsis(got, limit)
                shortExpected = ellipsis(expected, limit)
                while (
                    shortGot == shortExpected
                and limit < len(got) or limit < len(expected)
                and limit < 200
                ):
                    limit += 10
                    shortGot = ellipsis(got, limit)
                    shortExpected = ellipsis(expected, limit)

                return (
                    f"strings differ on line {firstDiff} where we got:"
                    f"\n  {shortGot}\nbut we expected:"
                    f"\n  {shortExpected}"
                )
            else:
                # Single-line strings: find character pos of difference
                if IGNORE_TRAILING_WHITESPACE:
                    val = val.rstrip()
                    ref = ref.rstrip()
                    if val == ref:
                        return None

                # Find character position of first difference
                pos = None
                i = None
                for i in range(min(len(val), len(ref))):
                    if val[i] != ref[i]:
                        pos = i
                        break
                else:
                    if i is not None:
                        pos = i + 1
                    else:
                        pos = 0  # one string is empty

                vchar = None
                rchar = None
                if pos < len(val):
                    vchar = val[pos]
                if pos < len(ref):
                    rchar = ref[pos]

                if vchar is None:
                    missing = ellipsis(repr(ref[pos:]), 20)
                    return (
                        f"expected text missing from end of string:"
                        f" {missing}"
                    )
                elif rchar is None:
                    extra = ellipsis(repr(val[pos:]), 20)
                    return (
                        f"extra text at end of string:"
                        f" {extra}"
                    )
                else:
                    if pos > 6:
                        got = ellipsis(repr(val[pos:]), 14)
                        expected = ellipsis(repr(ref[pos:]), 14)
                        return (
                            f"strings differ from position {pos}: got {got}"
                            f" but expected {expected}"
                        )
                    else:
                        got = ellipsis(repr(val), 14)
                        expected = ellipsis(repr(ref), 14)
                        return (
                            f"strings are different: got {got}"
                            f" but expected {expected}"
                        )

        elif isinstance(val, (list, tuple)):  # both lists and tuples
            svr = ellipsis(repr(val), 10)
            srr = ellipsis(repr(ref), 10)
            typ = type(val).__name__
            if len(val) != len(ref):
                return (
                    f"{typ}s {svr} and {srr} have different lengths"
                    f" ({len(val)} and {len(ref)})"
                )
            else:
                for i in range(len(val)):
                    diff = findFirstDifference(val[i], ref[i], comparing)
                    if diff is not None:
                        return f"in slot {i} of {typ}, " + diff
                return None  # no differences in any slot

        elif isinstance(val, (set)):  # both sets
            svr = ellipsis(repr(val), 10)
            srr = ellipsis(repr(ref), 10)
            onlyVal = (val - ref)
            onlyRef = (ref - val)
            # Sort so we can match up different-but-equivalent
            # floating-point items...
            try:
                sonlyVal = sorted(onlyVal)
                sonlyRef = sorted(onlyRef)
                diff = findFirstDifference(
                    sonlyVal,
                    sonlyRef,
                    comparing
                )
            except TypeError:
                # not sortable, so not just floating-point diffs
                diff = "some"

            if diff is None:
                return None
            else:
                nMissing = len(onlyRef)
                nExtra = len(onlyVal)
                if nExtra == 0:
                    firstMissing = ellipsis(repr(list(onlyRef)[0]), 12)
                    result = f"in a set, missing element {firstMissing}"
                    if nMissing > 1:
                        result += f" ({nMissing} missing elements in total)"
                    return result
                elif nMissing == 0:
                    firstExtra = ellipsis(repr(list(onlyVal)[0]), 12)
                    result = f"in a set, extra element {firstExtra}"
                    if nExtra > 1:
                        result += f" ({nExtra} extra elements in total)"
                    return result
                else:
                    firstMissing = ellipsis(repr(list(onlyRef)[0]), 8)
                    firstExtra = ellipsis(repr(list(onlyVal)[0]), 8)
                    result = (
                        "in a set, elements are different (extra"
                        f" element {firstExtra} and missing element"
                        f" {firstMissing}"
                    )
                    if nMissing > 1 and nExtra > 1:
                        result += (
                            f" ({nExtra} total extra elements and"
                            f" {nMissing} total missing elements"
                        )
                    elif nMissing == 1:
                        if nExtra > 1:
                            result += (
                                f" (1 missing and {nExtra} total extra"
                                f" elements)"
                            )
                    else:  # nExtra must be 1
                        if nMissing > 1:
                            result += (
                                f" (1 extra and {nExtra} total missing"
                                f" elements)"
                            )
                    return result

        elif isinstance(val, dict):  # both dicts
            svr = ellipsis(repr(val), 14)
            srr = ellipsis(repr(ref), 14)

            if len(val) != len(ref):
                if len(val) < len(ref):
                    ldiff = len(ref) - len(val)
                    firstMissing = ellipsis(
                        repr(list(set(ref.keys()) - set(val.keys()))[0]),
                        30
                    )
                    return (
                        f"dictionary is missing key {firstMissing} (has"
                        f" {ldiff} fewer key{'s' if ldiff > 1 else ''}"
                        f" than expected)"
                    )
                else:
                    ldiff = len(val) - len(ref)
                    firstExtra = ellipsis(
                        repr(list(set(val.keys()) - set(ref.keys()))[0]),
                        30
                    )
                    return (
                        f"dictionary has extra key {firstExtra} (has"
                        f" {ldiff} more key{'s' if ldiff > 1 else ''}"
                        f" than expected)"
                    )
                return (
                    f"dictionaries {svr} and {srr} have different sizes"
                    f" ({len(val)} and {len(ref)})"
                )

            vkeys = set(val.keys())
            rkeys = set(ref.keys())
            keyCorrespondence: Optional[dict]
            try:
                onlyVal = sorted(vkeys - rkeys)
                onlyRef = sorted(rkeys - vkeys)
                keyCorrespondence = {}
            except TypeError:  # unsortable...
                keyCorrespondence = None

            # Check for floating-point equivalence of keys if sets are
            # sortable...
            if keyCorrespondence is not None:
                if findFirstDifference(onlyVal, onlyRef, comparing) is None:
                    keyCorrespondence = {
                        onlyVal[i]: onlyRef[i]
                        for i in range(len(onlyVal))
                    }
                    # Add pass-through mappings for matching keys
                    for k in vkeys & rkeys:
                        keyCorrespondence[k] = k
                else:
                    # No actual mapping is available...
                    keyCorrespondence = None

            # We couldn't find a correspondence between keys, so we
            # return a key-based difference
            if keyCorrespondence is None:
                onlyVal = vkeys - rkeys
                onlyRef = rkeys - vkeys
                nExtra = len(onlyVal)
                nMissing = len(onlyRef)
                if nExtra == 0:
                    firstMissing = ellipsis(repr(list(onlyRef)[0]), 10)
                    result = f"dictionary is missing key {firstMissing}"
                    if nMissing > 1:
                        result += f" ({nMissing} missing keys in total)"
                    return result
                elif nMissing == 0:
                    firstExtra = ellipsis(repr(list(onlyVal)[0]), 10)
                    result = f"dictionary has extra key {firstExtra}"
                    if nExtra > 1:
                        result += f" ({nExtra} extra keys in total)"
                    return result
                else:  # neither is 0
                    firstMissing = ellipsis(repr(list(onlyRef)[0]), 10)
                    firstExtra = ellipsis(repr(list(onlyVal)[0]), 10)
                    result = (
                        f"dictionary is missing key {firstMissing} and"
                        f" has extra key {firstExtra}"
                    )
                    if nMissing > 1 and nExtra > 1:
                        result += (
                            f" ({nMissing} missing and {nExtra} extra"
                            f" keys in total)"
                        )
                    elif nMissing == 1:
                        if nExtra > 1:
                            result += (
                                f" (1 missing and {nExtra} extra keys"
                                f" in total)"
                            )
                    else:  # nExtra must be 1
                        if nMissing > 1:
                            result += (
                                f" (1 extra and {nMissing} missing keys"
                                f" in total)"
                            )
                    return result

            # if we reach here, keyCorrespondence maps val keys to
            # equivalent (but not necessarily identical) ref keys

            for vk in keyCorrespondence:
                rk = keyCorrespondence[vk]
                vdiff = findFirstDifference(val[vk], ref[rk], comparing)
                if vdiff is not None:
                    krep = ellipsis(repr(vk), 14)
                    return f"in dictionary slot {krep}, " + vdiff

            return None

        else:  # not sure what kind of thing this is...
            if val == ref:
                return None
            else:
                limit = 15
                vr = repr(val)
                rr = repr(ref)
                svr = ellipsis(vr, limit)
                srr = ellipsis(rr, limit)
                while (
                    svr == srr
                and (limit < len(vr) or limit < len(rr))
                and limit < 100
                ):
                    limit += 10
                    svr = ellipsis(vr, limit)
                    srr = ellipsis(rr, limit)
                return f" objects {svr} and {srr} are different"


def checkContainment(val1: Any, val2: Any) -> bool:
    """
    Returns True if val1 is 'contained in' to val2, and False otherwise.
    This is equivalent to the `in` operator (specifically, `val1 in
    val2`) unless the global variable `IGNORE_TRAILING_WHITESPACE` is
    True, in which case trailing whitespace is trimmed from both strings
    before `in` is applied.

    For example:

    >>> checkContainment(1, [1, 2, 3])
    True
    >>> checkContainment([1, 2], [1, 2, 3])  # no subsequence matching
    False
    >>> checkContainment('12', '123')  # does match since they're strings
    True
    >>> save = IGNORE_TRAILING_WHITESPACE
    >>> attendTrailingWhitespace(False)
    >>> checkContainment('1 ', '123')
    True
    >>> checkContainment('3 ', '123 ')
    True
    >>> attendTrailingWhitespace()
    >>> checkContainment('1 ', '123')
    False
    >>> checkContainment('3 ', '123')
    False
    >>> checkContainment('3 ', '123 ')
    True
    >>> attendTrailingWhitespace(not save)
    """
    if (not isinstance(val1, str)) or (not isinstance(val2, str)):
        return val1 in val2  # use regular containment test
    # For two strings, pay attention to IGNORE_TRAILING_WHITESPACE
    elif IGNORE_TRAILING_WHITESPACE:
        # remove trailing whitespace from both strings (on all lines)
        return trimWhitespace(val1) in trimWhitespace(val2)
    else:
        return val1 in val2  # use regular containment test


def trimWhitespace(st: str, requireNewline: bool = False) -> str:
    """
    Uses .rstrip() to remove trailing whitespace from each line of the
    given string. This has the side effect of replacing complex newlines
    with just '\\n'. If `requireNewline` is set to true, only whitespace
    that comes before a newline will be trimmed, and whitespace which
    occurs at the end of the string on the last line will be retained if
    there is no final newline.
    """
    if requireNewline:
        return re.sub('[ \t\r]*([\r\n])', r'\1', st)
    else:
        result = '\n'.join(line.rstrip() for line in st.split('\n'))
        return result


def compare(val: Any, ref: Any) -> bool:
    """
    Comparison function returning a boolean which uses
    `findFirstDifference` under the hood.
    """
    return findFirstDifference(val, ref) is None


def test_compare() -> None:
    "Tests the compare function."
    # TODO: test findFirstDifference instead & confirm correct
    # messages!!!
    # Integers
    assert compare(1, 1)
    assert compare(1, 2) is False
    assert compare(2, 1 + 1)

    # Floating point numbers
    assert compare(1.1, 1.1)
    assert compare(1.1, 1.2) is False
    assert compare(1.1, 1.1000000001)
    assert compare(1.1, 1.1001) is False

    # Complex numbers
    assert compare(1.1 + 2.3j, 1.1 + 2.3j)
    assert compare(1.1 + 2.3j, 1.1 + 2.4j) is False

    # Strings
    assert compare('abc', 1.1001) is False
    assert compare('abc', 'abc')
    assert compare('abc', 'def') is False

    # Lists
    assert compare([1, 2, 3], [1, 2, 3])
    assert compare([1, 2, 3], [1, 2, 4]) is False
    assert compare([1, 2, 3], [1, 2, 3.0000000001])

    # Tuples
    assert compare((1, 2, 3), (1, 2, 3))
    assert compare((1, 2, 3), (1, 2, 4)) is False
    assert compare((1, 2, 3), (1, 2, 3.0000000001))

    # Nested lists + tuples
    assert compare(
        ['a', 'b', 'cdefg', [1, 2, [3]], (4, 5)],
        ['a', 'b', 'cdefg', [1, 2, [3]], (4, 5)]
    )
    assert compare(
        ['a', 'b', 'cdefg', [1, 2, [3]], (4, 5)],
        ['a', 'b', 'cdefg', [1, 2, [3]], (4, '5')]
    ) is False
    assert compare(
        ['a', 'b', 'cdefg', [1, 2, [3]], (4, 5)],
        ['a', 'b', 'cdefg', [1, 2, [3]], [4, 5]]
    ) is False

    # Sets
    assert compare({1, 2}, {1, 2})
    assert compare({1, 2}, {1}) is False
    assert compare({1}, {1, 2}) is False
    assert compare({1, 2}, {'1', 2}) is False
    assert compare({'a', 'b', 'c'}, {'a', 'b', 'c'})
    assert compare({'a', 'b', 'c'}, {'a', 'b', 'C'}) is False
    # Two tricky cases
    assert compare({1, 2}, {1.00000001, 2})
    assert compare({(1, 2), 3}, {(1.00000001, 2), 3})

    # Dictionaries
    assert compare({1: 2, 3: 4}, {1: 2, 3: 4})
    assert compare({1: 2, 3: 4}, {1: 2, 3.00000000001: 4})
    assert compare({1: 2, 3: 4}, {1: 2, 3: 4.00000000001})
    assert compare({1: 2, 3: 4}, {1: 2, 3.1: 4}) is False
    assert compare({1: 2, 3: 4}, {1: 2, 3: 4.1}) is False

    # Nested dictionaries & lists
    assert compare(
        {1: {1.1: 2.2}, 2: [2.2, 3.3]},
        {1: {1.1: 2.2}, 2: [2.2, 3.3]}
    )
    assert compare(
        {1: {1.1: 2.2}, 2: [2.2, 3.3]},
        {1: {1.2: 2.2}, 2: [2.2, 3.3]}
    ) is False
    assert compare(
        {1: {1.1: 2.2}, 2: [2.2, 3.3]},
        {1: {1.1: 2.3}, 2: [2.2, 3.3]}
    ) is False
    assert compare(
        {1: {1.1: 2.2}, 2: [2.2, 3.3]},
        {1: {1.1: 2.2}, 2: [2.2, 3.4]}
    ) is False
    assert compare(
        {1: {1.1: 2.2}, 2: [2.2, 3.3]},
        {1: {1.1: 2.2}, 2: 2.2}
    ) is False
    assert compare(
        {1: {1.1: 2.2}, 2: [2.2, 3.3]},
        {1: {1.1: 2.2}, 2: (2.2, 3.3)}
    ) is False

    # Equivalent infinitely recursive list structures
    a: list = [1, 2, 3]
    a.append(a)
    a2: list = [1, 2, 3]
    a2.append(a2)
    b: list = [1, 2, 3, [1, 2, 3]]
    b[3].append(b)
    c: list = [1, 2, 3, [1, 2, 3, [1, 2, 3]]]
    c[3][3].append(c[3])
    d: list = [1, 2, 3]
    d.insert(2, d)

    assert compare(a, a)
    assert compare(a, a2)
    assert compare(a2, a)
    assert compare(a, b)
    assert compare(a, c)
    assert compare(a2, b)
    assert compare(b, a)
    assert compare(b, a2)
    assert compare(c, a)
    assert compare(b, c)
    assert compare(a, d) is False
    assert compare(b, d) is False
    assert compare(c, d) is False
    assert compare(d, a) is False
    assert compare(d, b) is False
    assert compare(d, c) is False

    # Equivalent infinitely recursive dicitonaries
    e: dict = {1: 2}
    e[2] = e
    e2: dict = {1: 2}
    e2[2] = e2
    f: dict = {1: 2}
    f2: dict = {1: 2}
    f[2] = f2
    f2[2] = f
    g: dict = {1: 2, 2: {1: 2.0000000001}}
    g[2][2] = g
    h: dict = {1: 2, 2: {1: 3}}
    h[2][2] = h

    assert compare(e, e2)
    assert compare(e2, e)
    assert compare(f, f2)
    assert compare(f2, f)
    assert compare(e, f)
    assert compare(f, e)
    assert compare(e, g)
    assert compare(f, g)
    assert compare(g, e)
    assert compare(g, f)
    assert compare(e, h) is False
    assert compare(f, h) is False
    assert compare(g, h) is False
    assert compare(h, e) is False
    assert compare(h, f) is False
    assert compare(h, g) is False

    # Custom types + objects
    class T:
        pass

    assert compare(T, T)
    assert compare(T, 1) is False
    assert compare(T(), T()) is False

    # Custom type w/ a custom __eq__
    class E:
        def __eq__(self, other):
            return isinstance(other, E) or other == 1

    assert compare(E, E)
    assert compare(E, 1) is False
    assert compare(E(), 1)
    assert compare(E(), 2) is False
    assert compare(E(), E())

    # Custom type w/ custom __hash__ and __eq__
    class A:
        def __init__(self, val):
            self.val = val

        def __hash__(self):
            return 3  # hashes collide

        def __eq__(self, other):
            return isinstance(other, A) and self.val == other.val

    assert compare({A(1), A(2)}, {A(1), A(2)})
    assert compare({A(1), A(2)}, {A(1), A(3)}) is False


#-----------------------#
# Configuration control #
#-----------------------#

def detailLevel(level: LevelOfDetail) -> None:
    """
    Sets the level of detail for printed messages.
    The detail levels are:

    * -1: Super-minimal output, with no details beyond success/failure.
    * 0: Succinct messages indicating success/failure, with minimal
        details when failure occurs.
    * 1: More verbose success/failure messages, with details about
        successes and more details about failures.
    """
    global DETAIL_LEVEL
    DETAIL_LEVEL = level


def attendTrailingWhitespace(on: bool = True) -> None:
    """
    Call this function to force `optimism` to pay attention to
    whitespace at the end of lines when checking expectations. By
    default, such whitespace is removed both from expected
    values/output fragments and from captured outputs/results before
    checking expectations. To turn that functionality on again, you
    can call this function with False as the argument.
    """
    global IGNORE_TRAILING_WHITESPACE
    IGNORE_TRAILING_WHITESPACE = not on


def inlineStringsInMemoryReports(on: bool = True) -> None:
    """
    Call this function to force `optimism` to write strings inline in
    memory reports instead of giving them separate addresses. Call it
    with `False` to force the opposite behavior. The
    `INLINE_STRINGS_IN_MEMORY_REPORTS` variable stores the value used
    here and controls the behavior.
    """
    global INLINE_STRINGS_IN_MEMORY_REPORTS
    INLINE_STRINGS_IN_MEMORY_REPORTS = on


def skipChecksAfterFail(mode: SkipMode = "all") -> None:
    """
    The argument should be either 'case' (the default), 'manager', or
    None. In 'manager' mode, when one check fails, any other checks of
    cases derived from that manager, including the case where the check
    failed, will be skipped. In 'case' mode, once a check fails any
    further checks of the same case will be skipped, but checks of other
    cases derived from the same manager will not be. In None mode (or if
    any other value is provided) no checks will be skipped because of
    failed checks (but they might be skipped for other reasons).
    """
    global SKIP_ON_FAILURE
    SKIP_ON_FAILURE = mode


def suppressErrorDetailsAfterFail(mode: SkipMode = "all") -> None:
    """
    The argument should be one of the following values:

    - `'case'`: Causes error details to be omitted for failed checks
      after the first failed check on each particular test case.
    - `'manager'`: Causes error details to be omitted for failed checks
      after the first failed check on any test case for a particular
      manager.
    - `'all'`: Causes error details to be omitted for all failed checks
      after any check fails. Reset this with `clearFailure`.
    - None (or any other value not listed above): Means that full error
      details will always be reported.

    The default value is `'all`' if you call this function; see
    `SUPPRESS_ON_FAILURE` for the default value when `optimism` is
    imported.

    Note that detail suppression has no effect if the detail level is set
    above 0.
    """
    global SUPPRESS_ON_FAILURE
    SUPPRESS_ON_FAILURE = mode


def clearFailure() -> None:
    """
    Resets the failure status so that checks will resume when
    `SKIP_ON_FAILURE` is set to `'all'`.
    """
    global CHECK_FAILED
    CHECK_FAILED = False


#----------------------------------#
# Summarization and Trial Tracking #
#----------------------------------#

def _register_outcome(passed: bool, tag: str, message: str) -> None:
    """
    Given a passed/failed boolean, a tag string indicating the file name
    + line number where a check was requested, and a message for that
    outcome, registers that outcome triple in the `ALL_OUTCOMES`
    dictionary under the current test suite name.
    """
    ALL_OUTCOMES.setdefault(_CURRENT_SUITE_NAME, []).append(
        (passed, tag, message)
    )


def showSummary(suiteName: Optional[str] = None) -> None:
    """
    Shows a summary of the number of checks in the current test suite
    (see `currentTestSuite`) that have been met or not. You can also
    give an argument to specify the name of the test suite to summarize.
    Prints output to `sys.stderr`.

    Note that the results of `expect` checks are not included in the
    summary, because they aren't trials.
    """
    if suiteName is None:
        suiteName = currentTestSuite()

    # Flush stdout, stderr, and PRINT_TO to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        PRINT_TO.flush()
    except Exception:
        pass

    # Build lists of met and unmet expectations
    met = []
    unmet = []
    for passed, tag, msg in listOutcomesInSuite(suiteName):
        if passed:
            met.append(tag)
        else:
            unmet.append(tag)

    print(f'-- Summary for suite {suiteName!r} --', file=PRINT_TO)

    if len(unmet) == 0:
        if len(met) == 0:
            print("No expectations were established.", file=PRINT_TO)
        else:
            print(
                f"All {len(met)} expectation(s) were met.",
                file=PRINT_TO
            )
    else:
        if len(met) == 0:
            print(
                f"None of the {len(unmet)} expectation(s) were met!",
                file=PRINT_TO
            )
        else:
            print(
                (
                    f"{len(unmet)} of the {len(met) + len(unmet)}"
                    f" expectation(s) were NOT met:"
                ),
                file=PRINT_TO
            )
        if COLORS:  # bright red
            print("\x1b[1;31m", end="", file=PRINT_TO)
        for tag in unmet:
            print(f"  ✗ {tag}", file=PRINT_TO)
        if COLORS:  # reset
            print("\x1b[0m", end="", file=PRINT_TO)
    print('----', file=PRINT_TO)

    # Flush stdout & stderr to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        PRINT_TO.flush()
    except Exception:
        pass


def showOverview() -> None:
    """
    Prints an overview of ALL outcomes recorded so far, including a
    warning line when there are any failures.
    """
    overallPassed = 0
    fullTotal = 0
    print_message('---')
    for suiteName in ALL_OUTCOMES:
        passed = 0
        total = 0
        for outcome in ALL_OUTCOMES[suiteName]:
            if outcome[0]:
                passed += 1
                overallPassed += 1
            total += 1
            fullTotal += 1

        if passed == total:
            mark = "✓"
            color = msg_color("succeeded")
        else:
            mark = "✗"
            color = msg_color("failed")
        print_message(f"{mark} {passed}/{total} {suiteName}", color)

    if overallPassed == fullTotal:
        mark = "✓"
        color = msg_color("succeeded")
    else:
        mark = "✗"
        color = msg_color("failed")
    print_message('---')
    print_message(f"{mark} {overallPassed}/{fullTotal} TOTAL", color)
    print_message('---')


def currentTestSuite() -> str:
    """
    Returns the name of the current test suite (a string).
    """
    return _CURRENT_SUITE_NAME


def testSuite(name: str) -> None:
    """
    Starts a new test suite with the given name, or resumes an old one.
    Any cases created subsequently will be registered to that suite.
    """
    global _CURRENT_SUITE_NAME
    if not isinstance(name, str):
        raise TypeError(
            f"The test suite name must be a string (got: '{repr(name)}'"
            f" which is a {type(name)})."
        )
    _CURRENT_SUITE_NAME = name


def resetTestSuite(suiteName: Optional[str] = None) -> None:
    """
    Resets the cases and outcomes recorded in the current test suite (or
    the named test suite if an argument is provided).
    """
    if suiteName is None:
        suiteName = currentTestSuite()

    ALL_TRIALS[suiteName] = []
    ALL_OUTCOMES[suiteName] = []


def freshTestSuite(name: str) -> None:
    """
    Works like `testSuite`, but calls `resetTestSuite` for that suite
    name first, ensuring no old test suite contents will be included.
    """
    resetTestSuite(name)
    testSuite(name)


def deleteAllTestSuites() -> None:
    """
    Deletes all test suites, removing all recorded test cases and
    outcomes, and setting the current test suite name back to "default".
    """
    global ALL_TRIALS, ALL_OUTCOMES, _CURRENT_SUITE_NAME
    _CURRENT_SUITE_NAME = "default"
    ALL_TRIALS = {}
    ALL_OUTCOMES = {}


def listTrialsInSuite(suiteName: Optional[str] = None) -> List[Trial]:
    """
    Returns a list of trials (`Trial` objects) in the current test suite
    (or the named suite if an argument is provided).
    """
    if suiteName is None:
        suiteName = currentTestSuite()

    if suiteName not in ALL_TRIALS:
        raise ValueError(f"Test suite '{suiteName}' does not exist.")

    return ALL_TRIALS[suiteName][:]


def listOutcomesInSuite(
    suiteName: Optional[str] = None
) -> List[Tuple[bool, str, str]]:
    """
    Returns a list of all individual expectation outcomes attached to
    trials in the given test suite (default: the current test suite).
    Includes `expect` and `expectType` outcomes even though those aren't
    attached to trials.
    """
    if suiteName is None:
        suiteName = currentTestSuite()

    if suiteName not in ALL_OUTCOMES:
        raise ValueError(f"Test suite '{suiteName}' does not exit.")

    return ALL_OUTCOMES[suiteName][:]


def listAllTrials() -> List[Trial]:
    """
    Returns a list of all registered trials (`Trial` objects) in any
    known test suite. Note that if `deleteAllTestSuites` has been called,
    this will not include any `Trial` objects created before that point.
    """
    result = []
    for suiteName in ALL_TRIALS:
        result.extend(ALL_TRIALS[suiteName])

    return result


#---------------#
# Color control #
#---------------#

def colors(enable: bool = False) -> None:
    """
    Enables or disables colors in printed output. If your output does not
    support ANSI color codes, the color output will show up as garbage
    and you can disable this.
    """
    global COLORS
    COLORS = enable


#---------#
# Tracing #
#---------#

def trace(expr: T) -> T:
    """
    Given an expression (actually, of course, just a value), returns the
    value it was given. But also prints a trace message indicating what
    the expression was, what value it had, and the line number of that
    line of code.

    The file name and overlength results are printed only when the
    `detailLevel` is set to 1 or higher.
    """
    # Flush stdout & stderr to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        PRINT_TO.flush()
    except Exception:
        pass

    ctx = get_my_context(cast(FunctionType, trace))
    rep = repr(expr)
    short = ellipsis(repr(expr))
    tag = "{line}".format(**ctx)
    if DETAIL_LEVEL >= 1:
        tag = "{file}:{line}".format(**ctx)
    print(
        f"{tag} {ctx.get('expr_src', '???')} ⇒ {short}",
        file=PRINT_TO
    )
    if DETAIL_LEVEL >= 1 and short != rep:
        print("  Full result is:\n    " + rep, file=PRINT_TO)

    # Flush stdout & stderr to improve ordering
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        PRINT_TO.flush()
    except Exception:
        pass

    return expr


#------------------------------#
# Reverse evaluation machinery #
#------------------------------#

class HasLocation(TypedDict, total=False):
    """
    Spec for dictionaries which at least have 'file' and 'line' slots
    indicating a filename and code line. Both will be `None` for
    instances where a filename & line number cannot be determined.
    """
    file: Optional[str]
    line: Optional[int]


class CodeLocation(HasLocation, total=True):
    """
    A dictionary with just the 'file' and 'line' keys that `HasLocation`
    requires.
    """


class ContextDict(TypedDict):
    """
    Represents the code context in which a function call is made. Has
    the following entries:

    - file: The filename of the calling module
    - line: The line number on which the call to the function occurred
    - src: The source code string of the calling module
    - expr: An AST node storing the expression passed as the first
        argument to the function
    - expr_src: The source code string of the expression passed as the
        first argument to the function
    - values: A dictionary mapping source code fragments to their
        values, for each variable reference in the test expression. These
        are deepish copies of the values encountered.
    - relevant: A set of source code fragments which appear in the
        values dictionary which are judged to be most-relevant to the
        result of the test.
    """
    file: str
    line: int
    src: str
    expr: ast.AST
    expr_src: str
    values: Dict[str, Any]
    relevant: Set[str]


def get_src_index(src: str, lineno: int, col_offset: int) -> int:
    """
    Turns a line number and column offset into an absolute index into
    the given source string, assuming length-1 newlines.
    """
    lines = src.splitlines()
    above = lines[:lineno - 1]
    return sum(len(line) for line in above) + len(above) + col_offset


def test_gsr() -> None:
    """Tests for get_src_index."""
    s = 'a\nb\nc'
    assert get_src_index(s, 1, 0) == 0
    assert get_src_index(s, 2, 0) == 2
    assert get_src_index(s, 3, 0) == 4
    assert s[get_src_index(s, 1, 0)] == 'a'
    assert s[get_src_index(s, 2, 0)] == 'b'
    assert s[get_src_index(s, 3, 0)] == 'c'


def find_identifier_end(code: str, start_index: int) -> int:
    """
    Given a code string and an index in that string which is the start
    of an identifier, returns the index of the end of that identifier.
    """
    at = start_index + 1
    while at < len(code):
        ch = code[at]
        if not ch.isalpha() and not ch.isdigit() and ch != '_':
            break
        at += 1
    return at - 1


def test_find_identifier_end() -> None:
    """Tests for find_identifier_end."""
    assert find_identifier_end("abc.xyz", 0) == 2
    assert find_identifier_end("abc.xyz", 1) == 2
    assert find_identifier_end("abc.xyz", 2) == 2
    assert find_identifier_end("abc.xyz", 4) == 6
    assert find_identifier_end("abc.xyz", 5) == 6
    assert find_identifier_end("abc.xyz", 6) == 6
    assert find_identifier_end("abc_xyz123", 0) == 9
    assert find_identifier_end("abc xyz123", 0) == 2
    assert find_identifier_end("abc xyz123", 4) == 9
    assert find_identifier_end("x", 0) == 0
    assert find_identifier_end("  x", 2) == 2
    assert find_identifier_end("  xyz1", 2) == 5
    s = "def abc(def):\n  print(xyz)\n"
    assert find_identifier_end(s, 0) == 2
    assert find_identifier_end(s, 4) == 6
    assert find_identifier_end(s, 8) == 10
    assert find_identifier_end(s, 16) == 20
    assert find_identifier_end(s, 22) == 24


def unquoted_enumerate(
    src: str,
    start_index: int
) -> Iterator[Tuple[int, str]]:
    """
    A generator that yields index, character pairs from the given code
    string, skipping quotation marks and the strings that they delimit,
    including triple-quotes and respecting backslash-escapes within
    strings.
    """
    quote = None
    at = start_index

    while at < len(src):
        char = src[at]

        # skip escaped characters in quoted strings
        if quote and char == '\\':
            # (thank goodness I don't have to worry about r-strings)
            at += 2
            continue

        # handle quoted strings
        elif char == '"' or char == "'":
            if quote == char:
                quote = None  # single end quote
                at += 1
                continue
            elif src[at:at + 3] in ('"""', "'''"):
                tq = src[at:at + 3]
                at += 3  # going to skip these no matter what
                if tq == quote or tq[0] == quote:
                    # Ending triple-quote, or matching triple-quote at
                    # end of single-quoted string = ending quote +
                    # empty string
                    quote = None
                    continue
                else:
                    if quote:
                        # triple quote of other kind inside single or
                        # triple quoted string
                        continue
                    else:
                        quote = tq
                        continue
            elif quote is None:
                # opening single quote
                quote = char
                at += 1
                continue
            else:
                # single quote inside other quotes
                at += 1
                continue

        # Non-quote characters in quoted strings
        elif quote:
            at += 1
            continue

        else:
            yield (at, char)
            at += 1
            continue


def test_unquoted_enumerate() -> None:
    """Tests for unquoted_enumerate."""
    uqe = unquoted_enumerate
    assert list(uqe("abc'123'", 0)) == list(zip(range(3), "abc"))
    assert list(uqe("'abc'123", 0)) == list(zip(range(5, 8), "123"))
    assert list(uqe("'abc'123''", 0)) == list(zip(range(5, 8), "123"))
    assert list(uqe("'abc'123''", 1)) == [(1, 'a'), (2, 'b'), (3, 'c')]
    mls = "'''\na\nb\nc'''\ndef"
    assert list(uqe(mls, 0)) == list(zip(range(12, 16), "\ndef"))
    tqs = '"""\'\'\'ab\'\'\'\'""" cd'
    assert list(uqe(tqs, 0)) == [(15, ' '), (16, 'c'), (17, 'd')]
    rqs = "a'b'''c\"\"\"'''\"d\"''''\"\"\"e'''\"\"\"f\"\"\"'''"
    assert list(uqe(rqs, 0)) == [(0, 'a'), (6, 'c'), (23, 'e')]
    assert list(uqe(rqs, 6)) == [(6, 'c'), (23, 'e')]
    bss = "a'\\'b\\''c"
    assert list(uqe(bss, 0)) == [(0, 'a'), (8, 'c')]
    mqs = "'\"a'b\""
    assert list(uqe(mqs, 0)) == [(4, 'b')]


def find_nth_attribute_period(
    code: str,
    start_index: int,
    n: int
) -> Optional[int]:
    """
    Given a string of Python code and a start index within that string,
    finds the nth period character (counting from first = zero) after
    that start point, but only considers periods which are used for
    attribute access, i.e., periods outside of quoted strings and which
    are not part of ellipses. Returns the index within the string of the
    period that it found. A period at the start index (if there is one)
    will be counted. Returns None if there are not enough periods in the
    code. If the start index is inside a quoted string, things will get
    weird, and the results will probably be wrong.
    """
    for (at, char) in unquoted_enumerate(code, start_index):
        if char == '.':
            if code[at - 1:at] == '.' or code[at + 1:at + 2] == '.':
                # part of an ellipsis, so ignore it
                continue
            else:
                n -= 1
                if n < 0:
                    break

    # Did we hit the end of the string before counting below 0?
    if n < 0:
        return at
    else:
        return None


def test_find_nth_attribute_period() -> None:
    """Tests for find_nth_attribute_period."""
    assert find_nth_attribute_period("a.b", 0, 0) == 1
    assert find_nth_attribute_period("a.b", 0, 1) is None
    assert find_nth_attribute_period("a.b", 0, 100) is None
    assert find_nth_attribute_period("a.b.c", 0, 1) == 3
    assert find_nth_attribute_period("a.b.cde.f", 0, 1) == 3
    assert find_nth_attribute_period("a.b.cde.f", 0, 2) == 7
    s = "a.b, c.d, 'e.f', g.h"
    assert find_nth_attribute_period(s, 0, 0) == 1
    assert find_nth_attribute_period(s, 0, 1) == 6
    assert find_nth_attribute_period(s, 0, 2) == 18
    assert find_nth_attribute_period(s, 0, 3) is None
    assert find_nth_attribute_period(s, 0, 3) is None
    assert find_nth_attribute_period(s, 1, 0) == 1
    assert find_nth_attribute_period(s, 2, 0) == 6
    assert find_nth_attribute_period(s, 6, 0) == 6
    assert find_nth_attribute_period(s, 7, 0) == 18
    assert find_nth_attribute_period(s, 15, 0) == 18


def find_closing_item(
    code: str,
    start_index: int,
    openclose: str = '()'
) -> Optional[int]:
    """
    Given a string of Python code, a starting index where there's an
    open paren, bracket, etc., and a 2-character string containing the
    opening and closing delimiters of interest (parentheses by default),
    returns the index of the matching closing delimiter, or None if the
    opening delimiter is unclosed. Note that the given code must not
    contain syntax errors, or the behavior will be undefined.

    Does NOT work with quotation marks (single or double).
    """
    level = 1
    open_delim = openclose[0]
    close_delim = openclose[1]
    for at, char in unquoted_enumerate(code, start_index + 1):
        # Non-quoted open delimiters
        if char == open_delim:
            level += 1

        # Non-quoted close delimiters
        elif char == close_delim:
            level -= 1
            if level < 1:
                break

        # Everything else: ignore it

    if level == 0:
        return at
    else:
        return None


def test_find_closing_item() -> None:
    """Tests for find_closing_item."""
    assert find_closing_item('()', 0, '()') == 1
    assert find_closing_item('()', 0) == 1
    assert find_closing_item('(())', 0, '()') == 3
    assert find_closing_item('(())', 1, '()') == 2
    assert find_closing_item('((word))', 0, '()') == 7
    assert find_closing_item('((word))', 1, '()') == 6
    assert find_closing_item('(("(("))', 0, '()') == 7
    assert find_closing_item('(("(("))', 1, '()') == 6
    assert find_closing_item('(("))"))', 0, '()') == 7
    assert find_closing_item('(("))"))', 1, '()') == 6
    assert find_closing_item('(()())', 0, '()') == 5
    assert find_closing_item('(()())', 1, '()') == 2
    assert find_closing_item('(()())', 3, '()') == 4
    assert find_closing_item('(""")(\n""")', 0, '()') == 10
    assert find_closing_item("\"abc(\" + ('''def''')", 9, '()') == 19
    assert find_closing_item("\"abc(\" + ('''def''')", 0, '()') is None
    assert find_closing_item("\"abc(\" + ('''def''')", 4, '()') is None
    assert find_closing_item("(()", 0, '()') is None
    assert find_closing_item("(()", 1, '()') == 2
    assert find_closing_item("()(", 0, '()') == 1
    assert find_closing_item("()(", 2, '()') is None
    assert find_closing_item("[]", 0, '[]') == 1
    assert find_closing_item("[]", 0) is None
    assert find_closing_item("{}", 0, '{}') == 1
    assert find_closing_item("aabb", 0, 'ab') == 3


def find_unbracketed_comma(code: str, start_index: int) -> Optional[int]:
    """
    Given a string of Python code and a starting index, finds the next
    comma at or after that index which isn't surrounded by brackets of
    any kind that start at or after that index and which isn't in a
    quoted string. Returns the index of the matching comma, or None if
    there is none. Stops and returns None if it finds an unmatched
    closing bracket. Note that the given code must not contain syntax
    errors, or the behavior will be undefined.
    """
    seeking = []
    delims = {
        '(': ')',
        '[': ']',
        '{': '}'
    }
    closing = delims.values()
    for at, char in unquoted_enumerate(code, start_index):
        # Non-quoted open delimiter
        if char in delims:
            seeking.append(delims[char])

        # Non-quoted matching close delimiter
        elif len(seeking) > 0 and char == seeking[-1]:
            seeking.pop()

        # Non-quoted non-matching close delimiter
        elif char in closing:
            return None

        # A non-quoted comma
        elif char == ',' and len(seeking) == 0:
            return at

        # Everything else: ignore it

    # Got to the end
    return None


def test_find_unbracketed_comma() -> None:
    """Tests for find_unbracketed_comma."""
    assert find_unbracketed_comma('()', 0) is None
    assert find_unbracketed_comma('(),', 0) == 2
    assert find_unbracketed_comma('((,),)', 0) is None
    assert find_unbracketed_comma('((,),),', 0) == 6
    assert find_unbracketed_comma('((,),),', 1) == 4
    assert find_unbracketed_comma(',,,', 1) == 1
    assert find_unbracketed_comma('",,",","', 0) == 4
    assert find_unbracketed_comma('"""\n,,\n""","""\n,,\n"""', 0) == 10
    assert find_unbracketed_comma('"""\n,,\n""","""\n,,\n"""', 4) == 4
    assert find_unbracketed_comma('"""\n,,\n"""+"""\n,,\n"""', 0) is None
    assert find_unbracketed_comma('\n\n,\n', 0) == 2


def get_expr_src(src: str, call_node: ast.Call) -> str:
    """
    Gets the string containing the source code for the expression passed
    as the first argument to a function call, given the string source of
    the file that defines the function and the AST node for the function
    call.
    """
    # Find the child node for the first (and only) argument
    arg_expr = call_node.args[0]

    # If get_source_segment is available, use that
    if hasattr(ast, "get_source_segment"):
        attempt = ast.get_source_segment(src, arg_expr)
        if attempt is not None:
            return textwrap.dedent(attempt).strip()
        # else fall out and try without get_source_segment
    # implicit else

    # We're going to have to do this ourself: find the start of the
    # expression and state-machine to find a matching paren
    start = get_src_index(src, call_node.lineno, call_node.col_offset)
    open_paren = src.index('(', start)
    end = find_closing_item(src, open_paren, '()')
    # Note: can't be None because that would have been a SyntaxError
    assert end is not None
    first_comma = find_unbracketed_comma(src, open_paren + 1)
    # Could be None if it's a 1-argument function
    if first_comma is not None:
        end = min(end, first_comma)
    return textwrap.dedent(src[open_paren + 1:end]).strip()


def get_ref_src(src: str, node: ast.AST) -> str:
    """
    Gets the string containing the source code for a variable reference,
    attribute, or subscript.
    """
    # Use get_source_segment if it's available
    if hasattr(ast, "get_source_segment"):
        attempt = ast.get_source_segment(src, node)
        if attempt is not None:
            return attempt
    # implicit else

    # We're going to have to do this ourself: find the start of the
    # expression and state-machine to find its end
    start = get_src_index(src, node.lineno, node.col_offset)

    # Figure out the end point
    if isinstance(node, ast.Attribute):
        # Find sub-attributes so we can count syntactic periods to
        # figure out where the name part begins to get the span
        inner_period_count = 0
        for node in ast.walk(node):
            if isinstance(node, ast.Attribute):
                inner_period_count += 1
        inner_period_count -= 1  # for the node itself
        dot = find_nth_attribute_period(src, start, inner_period_count)
        assert dot is not None
        end = find_identifier_end(src, dot + 1)

    elif isinstance(node, ast.Name):
        # It's just an identifier so we can find the end
        end = find_identifier_end(src, start)

    elif isinstance(node, ast.Subscript):
        # Find start of sub-expression so we can find opening brace
        # and then match it to find the end
        inner = node.slice
        if isinstance(inner, ast.Slice):
            pass
        elif hasattr(ast, "Index") and isinstance(inner, ast.Index):
            # 3.7 Index has a "value" (it's deprecated now, sorry mypy)
            inner = inner.value  # type: ignore
        elif hasattr(ast, "ExtSlice") and isinstance(inner, ast.ExtSlice):
            # 3.7 ExtSlice has "dims" (it's deprecated now, sorry mypy)
            inner = inner.dims[0]  # type: ignore
        else:
            raise TypeError(
                f"Unexpected subscript slice type {type(inner)} for"
                f" node:\n{ast.dump(node)}"
            )
        sub_start = get_src_index(src, inner.lineno, inner.col_offset)
        match = find_closing_item(src, sub_start - 1, "[]")
        assert match is not None
        end = match

    return src[start:end + 1]


def deepish_copy(obj: T, memo: Optional[dict] = None) -> T:
    """
    Returns the deepest possible copy of the given object, using
    copy.deepcopy wherever possible and making shallower copies
    elsewhere. Basically a middle-ground between copy.deepcopy and
    copy.copy.
    """
    if memo is None:
        memo = {}
    if id(obj) in memo:
        return memo[id(obj)]

    result: T
    try:
        result = copy.deepcopy(obj)
        # not sure about memo dict compatibility
        memo[id(obj)] = result
        return result

    except Exception:
        constructor = type(obj)
        if isinstance(obj, list):
            result = constructor()
            memo[id(obj)] = result
            # TODO: How to tell mypy that 'T' is '<list' in this block?
            cast(list, result).extend(
                deepish_copy(item, memo)
                for item in obj
            )
            return result
        elif isinstance(obj, tuple):
            # Note: no way to pre-populate the memo, but also no way to
            # construct an infinitely-recursive tuple without having
            # some mutable structure at some layer...
            # TODO: How to tell mypy that 'T' is '<tuple' in this block?
            result = cast(
                T,
                type(obj)(deepish_copy(item, memo) for item in obj)
            )
            memo[id(obj)] = result
            return result
        elif isinstance(obj, dict):
            result = constructor()
            memo[id(obj)] = result
            cast(dict, result).update(
                {
                    deepish_copy(key, memo): deepish_copy(value, memo)
                    for key, value in obj.items()
                }
            )
            return result
        elif isinstance(obj, set):
            result = constructor()
            memo[id(obj)] = result
            # TODO: How to tell mypy that 'T' is '<set' in this block?
            itsASet = cast(set, result)
            itsASet |= set(
                deepish_copy(item, memo)
                for item in obj
            )
            return result
        else:
            # Can't go deeper I guess
            try:
                result = copy.copy(obj)
                memo[id(obj)] = result
                return result
            except Exception:
                # Can't even copy (e.g., a module)
                result = obj
                memo[id(obj)] = result
                return result


def get_external_calling_frame() -> FrameType:
    """
    Uses the inspect module to get a reference to the stack frame which
    called into the `optimism` module. Returns None if it can't find an
    appropriate call frame in the current stack.

    In the special case where the result would be a frame for a function
    named '__run' in the 'doctest' module and the lower frame comes from
    the file where this is called (usually optimism.py, this file) then
    we assume we're in a doctest and use the frame below (which is not
    external) as the 'external' frame.

    Remember to del the result after you're done with it, so that
    garbage doesn't pile up.
    """
    myname = __name__
    cf = inspect.currentframe()
    assert cf is not None  # TODO: What to do if it is?!?
    prev: Optional[FrameType] = None
    while (
        hasattr(cf, "f_back")
    and cf.f_back is not None
    and cf.f_globals.get("__name__") == myname
    ):
        prev = cf
        cf = cf.f_back

    # If the external calling frame is doctest's __run function this
    # implies that we're in a doctest and might actually be from this
    # module, so we go down a frame. The resulting frame will
    # technically be internal, not external.
    if (
        prev is not None
    and prev.f_globals.get("__name__") == myname
    and cf.f_globals.get("__name__") == "doctest"
    and cf.f_code.co_name == "__run"
    ):
        # TODO: modify line number here based on test obj from doctest frame?
        return prev

    return cf


def get_module(stack_frame: FrameType) -> Optional[ModuleType]:
    """
    Given a stack frame, returns a reference to the module where the
    code from that frame was defined.

    Returns None if it can't figure that out.
    """
    other_name = stack_frame.f_globals.get("__name__", None)
    return sys.modules.get(other_name)


def get_filename(
    stack_frame: FrameType,
    speculate_filename: bool = True
) -> Optional[str]:
    """
    Given a stack frame, returns the filename of the file in which the
    code which created that stack frame was defined. Returns None if
    that information isn't available via a __file__ global, or if
    speculate_filename is True (the default), uses the value of the
    frame's f_code.co_filename, which may not always be a real file on
    disk, or which is weird circumstances could be the name of a file on
    disk which is *not* where the code came from.
    """
    filename = stack_frame.f_globals.get("__file__")
    if filename is None and speculate_filename:
        filename = stack_frame.f_code.co_filename
    return filename


def get_code_line(stack_frame: FrameType) -> int:
    """
    Given a stack frame, returns the line number of the code where that
    stack frame originated.
    """
    return stack_frame.f_lineno


def evaluate_in_context(node: ast.expr, stack_frame: FrameType) -> Any:
    """
    Given an AST node which is an expression, returns the value of that
    expression as evaluated in the context of the given stack frame.

    Shallow copies of the stack frame's locals and globals are made in
    an attempt to prevent the code being evaluated from having any
    impact on the stack frame's values, but of course there's still some
    possibility of side effects...
    """
    expr = ast.Expression(node)
    code = compile(
        expr,
        stack_frame.f_globals.get("__file__", "__unknown__"),
        'eval'
    )
    return eval(
        code,
        copy.copy(stack_frame.f_globals),
        copy.copy(stack_frame.f_locals)
    )


def walk_ast_in_order(
    node: Union[None, ast.AST, Iterable[Union[None, ast.AST]]]
) -> Iterator[ast.AST]:
    """
    Yields all of the descendants of the given node (or list of nodes)
    in execution order. Note that this has its limits, for example, if
    we run it on the code:

    ```py
    x = [A for y in C if D]
    ```

    It will yield the nodes for C, then y, then D, then A, and finally
    x, but in actual execution the nodes for D and A may be executed
    multiple times before x is assigned.
    """
    if node is None:
        pass  # empty iterator
    elif isinstance(node, ast.AST):  # must be an ast.something
        # Note: the node itself will be yielded LAST
        if isinstance(node, (ast.Module, ast.Interactive, ast.Expression)):
            yield from walk_ast_in_order(node.body)
        elif (
            hasattr(ast, "FunctionType")
        and isinstance(node, ast.FunctionType)
        ):
            yield from walk_ast_in_order(node.argtypes)
            yield from walk_ast_in_order(node.returns)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.returns)
            yield from walk_ast_in_order(reversed(node.decorator_list))
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.ClassDef):
            yield from walk_ast_in_order(node.bases)
            yield from walk_ast_in_order(node.keywords)
            yield from walk_ast_in_order(reversed(node.decorator_list))
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.Return):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.Delete):
            yield from walk_ast_in_order(node.targets)
        elif isinstance(node, ast.Assign):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.targets)
        elif isinstance(node, ast.AugAssign):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.target)
        elif isinstance(node, ast.AnnAssign):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.annotation)
            yield from walk_ast_in_order(node.target)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            yield from walk_ast_in_order(node.iter)
            yield from walk_ast_in_order(node.target)
            yield from walk_ast_in_order(node.body)
            yield from walk_ast_in_order(node.orelse)
        elif isinstance(node, (ast.While, ast.If, ast.IfExp)):
            yield from walk_ast_in_order(node.test)
            yield from walk_ast_in_order(node.body)
            yield from walk_ast_in_order(node.orelse)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            yield from walk_ast_in_order(node.items)
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.Raise):
            yield from walk_ast_in_order(node.cause)
            yield from walk_ast_in_order(node.exc)
        elif isinstance(node, ast.Try):
            yield from walk_ast_in_order(node.body)
            yield from walk_ast_in_order(node.handlers)
            yield from walk_ast_in_order(node.orelse)
            yield from walk_ast_in_order(node.finalbody)
        elif isinstance(node, ast.Assert):
            yield from walk_ast_in_order(node.test)
            yield from walk_ast_in_order(node.msg)
        elif isinstance(node, ast.Expr):
            yield from walk_ast_in_order(node.value)
        # Import, ImportFrom, Global, Nonlocal, Pass, Break, and
        # Continue each have no executable content, so we'll yield them
        # but not any children

        elif isinstance(node, ast.BoolOp):
            yield from walk_ast_in_order(node.values)
        elif HAS_WALRUS and isinstance(node, ast.NamedExpr):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.target)
        elif isinstance(node, ast.BinOp):
            yield from walk_ast_in_order(node.left)
            yield from walk_ast_in_order(node.right)
        elif isinstance(node, ast.UnaryOp):
            yield from walk_ast_in_order(node.operand)
        elif isinstance(node, ast.Lambda):
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.Dict):
            for i in range(len(node.keys)):
                yield from walk_ast_in_order(node.keys[i])
                yield from walk_ast_in_order(node.values[i])
        elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            yield from walk_ast_in_order(node.elts)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            yield from walk_ast_in_order(node.generators)
            yield from walk_ast_in_order(node.elt)
        elif isinstance(node, ast.DictComp):
            yield from walk_ast_in_order(node.generators)
            yield from walk_ast_in_order(node.key)
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, (ast.Await, ast.Yield, ast.YieldFrom)):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.Compare):
            yield from walk_ast_in_order(node.left)
            yield from walk_ast_in_order(node.comparators)
        elif isinstance(node, ast.Call):
            yield from walk_ast_in_order(node.func)
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.keywords)
        elif isinstance(node, ast.FormattedValue):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.format_spec)
        elif isinstance(node, ast.JoinedStr):
            yield from walk_ast_in_order(node.values)
        elif isinstance(node, (ast.Attribute, ast.Starred)):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.Subscript):
            yield from walk_ast_in_order(node.value)
            yield from walk_ast_in_order(node.slice)
        elif isinstance(node, ast.Slice):
            yield from walk_ast_in_order(node.lower)
            yield from walk_ast_in_order(node.upper)
            yield from walk_ast_in_order(node.step)
        # Constant and Name nodes don't have executable contents

        elif isinstance(node, ast.comprehension):
            yield from walk_ast_in_order(node.iter)
            yield from walk_ast_in_order(node.ifs)
            yield from walk_ast_in_order(node.target)
        elif isinstance(node, ast.ExceptHandler):
            yield from walk_ast_in_order(node.type)
            yield from walk_ast_in_order(node.body)
        elif isinstance(node, ast.arguments):
            yield from walk_ast_in_order(node.defaults)
            yield from walk_ast_in_order(node.kw_defaults)
            if hasattr(node, "posonlyargs"):
                yield from walk_ast_in_order(node.posonlyargs)
            yield from walk_ast_in_order(node.args)
            yield from walk_ast_in_order(node.vararg)
            yield from walk_ast_in_order(node.kwonlyargs)
            yield from walk_ast_in_order(node.kwarg)
        elif isinstance(node, ast.arg):
            yield from walk_ast_in_order(node.annotation)
        elif isinstance(node, ast.keyword):
            yield from walk_ast_in_order(node.value)
        elif isinstance(node, ast.withitem):
            yield from walk_ast_in_order(node.context_expr)
            yield from walk_ast_in_order(node.optional_vars)
        # alias and typeignore have no executable members

        # Finally, yield this node itself
        yield node

    else:  # we assume it's iterable and try to iterate...
        for child in node:
            yield from walk_ast_in_order(child)


def find_call_nodes_on_line(
    node: ast.AST,
    frame: FrameType,
    function: Union[FunctionType, str],
    lineno: int
) -> List[ast.Call]:
    """
    Given an AST node, a stack frame, a function object, and a line
    number, looks for all function calls which occur on the given line
    number and which are calls to the given function (as evaluated in
    the given stack frame).

    Note that calls to functions defined as part of the given AST cannot
    be found in this manner, because the objects being called are newly
    created and one could not possibly pass a reference to one of them
    into this function. For that reason, if the function argument is a
    string, any function call whose call part matches the given string
    will be matched. Normally only Name nodes can match this way, but if
    ast.unparse is available, the string will also attempt to match
    (exactly) against the unparsed call expression.

    Calls that start on the given line number will match, but if there
    are no such calls, then a call on a preceding line whose expression
    includes the target line will be looked for and may match.

    The return value will be a list of ast.Call nodes, and they will be
    ordered in the same order that those nodes would be executed when
    the line of code is executed.
    """
    def call_matches(call_node):
        """
        Locally-defined matching predicate.
        """
        nonlocal function
        call_expr = call_node.func
        return (
            (
                isinstance(function, str)
            and (
                    (
                        isinstance(call_expr, ast.Name)
                    and call_expr.id == function
                    )
                 or (
                        isinstance(call_expr, ast.Attribute)
                    and call_expr.attr == function
                    )
                 or (
                        hasattr(ast, "unparse")
                    and ast.unparse(call_expr) == function
                    )
                )
            )
         or (
                not isinstance(function, str)
            and evaluate_in_context(call_expr, frame) is function
            )
        )

    result = []
    all_on_line = []
    for child in walk_ast_in_order(node):
        # only consider call nodes on the target line
        if (
            hasattr(child, "lineno")
        and child.lineno == lineno
        ):
            all_on_line.append(child)
            if isinstance(child, ast.Call) and call_matches(child):
                result.append(child)

    # If we didn't find any candidates, look outwards from ast nodes on
    # the target line to find a Call that encompasses them...
    if len(result) == 0:
        for on_line in all_on_line:
            here = getattr(on_line, "parent", None)
            while (
                here is not None
            and not isinstance(
                    here,
                    # Call (what we're looking for) plus most nodes that
                    # indicate there couldn't be a call grandparent:
                    (
                        ast.Call,
                        ast.Module, ast.Interactive, ast.Expression,
                        ast.FunctionDef, ast.AsyncFunctionDef,
                        ast.ClassDef,
                        ast.Return,
                        ast.Delete,
                        ast.Assign, ast.AugAssign, ast.AnnAssign,
                        ast.For, ast.AsyncFor,
                        ast.While,
                        ast.If,
                        ast.With, ast.AsyncWith,
                        ast.Raise,
                        ast.Try,
                        ast.Assert,
                        ast.Assert,
                        ast.Assert,
                        ast.Assert,
                        ast.Assert,
                        ast.Assert,
                        ast.Assert,
                        ast.Assert,
                    )
                )
            ):
                here = getattr(here, "parent", None)

            # If we found a Call that includes the target line as one
            # of its children...
            if isinstance(here, ast.Call) and call_matches(here):
                result.append(here)

    return result


def assign_parents(root: ast.AST) -> None:
    """
    Given an AST node, assigns "parent" attributes to each sub-node
    indicating their parent AST node. Assigns None as the value of the
    parent attribute of the root node.
    """
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore
            # TODO: Is there a better way to say I'm monkey-patching?

    root.parent = None  # type: ignore


def is_inside_call_func(node: ast.AST) -> bool:
    """
    Given an AST node which has a parent attribute, traverses parents to
    see if this node is part of the func attribute of a Call node.
    """
    if not hasattr(node, "parent") or node.parent is None:
        return False
    if isinstance(node.parent, ast.Call) and node.parent.func is node:
        return True
    else:
        return is_inside_call_func(node.parent)


def tag_for(located: Union[HasLocation, ContextDict]) -> str:
    """
    Given a dictionary which has 'file' and 'line' slots, returns a
    string to be used as the tag for a test with 'filename:line' as the
    format. Unless the `DETAIL_LEVEL` is 2 or higher, the filename will
    be shown without the full path.
    """
    filename = located.get('file') or '???'
    if DETAIL_LEVEL < 2:
        filename = os.path.basename(filename)
    line = located.get('line', '?')
    return f"{filename}:{line}"


def get_my_location(speculate_filename: bool = True) -> CodeLocation:
    """
    Fetches the filename and line number of the external module whose
    call into this module ended up invoking this function. Returns a
    dictionary with "file" and "line" keys.

    If speculate_filename is False, then the filename will be set to
    None in cases where a __file__ global cannot be found, instead of
    using f_code.co_filename as a backup. In some cases, this is useful
    because f_code.co_filename may not be a valid file.
    """
    frame = get_external_calling_frame()
    try:
        filename = get_filename(frame, speculate_filename)
        lineno = get_code_line(frame)
    finally:
        del frame

    return { "file": filename, "line": lineno }


def get_my_context(
    function_or_name: Union[FunctionType, str]
) -> Union[ContextDict, CodeLocation]:
    """
    Returns a `ContextDict` dictionary indicating the context of a
    function call, assuming that this function is called from within a
    function with the given name (or from within the given function),
    and that that function is being called from within a different
    module.

    Currently, the relevant list just lists any fragments which aren't
    found in the func slot of Call nodes, under the assumption that we
    don't care as much about the values of the functions we're calling.

    Prints a warning and returns a dictionary with just "file" and
    "line" entries if the other context info is unavailable.
    """
    function_name: str
    if isinstance(function_or_name, FunctionType):
        function_name = function_or_name.__name__
    else:
        function_name = function_or_name

    frame = get_external_calling_frame()
    try:
        filename = get_filename(frame)
        lineno = get_code_line(frame)
        if filename is None:
            src = None
        else:
            try:
                with open(filename, 'r') as fin:
                    src = fin.read()
            except Exception:
                # Try to get contents from the linecache as a backup...
                try:
                    src = ''.join(linecache.getlines(filename))
                except Exception:
                    # We'll assume here that the source is something like
                    # an interactive shell so we won't warn unless the
                    # detail level is turned up.
                    if DETAIL_LEVEL >= 2:
                        print(
                            "Warning: unable to get calling code's source.",
                            file=PRINT_TO
                        )
                        print(
                            (
                                "Call is on line {} of module {} from file"
                                " '{}'"
                            ).format(
                                lineno,
                                frame.f_globals.get("__name__"),
                                filename
                            ),
                            file=PRINT_TO
                        )
                    src = None

        if src is None:
            return {
                "file": filename,
                "line": lineno
            }

        assert filename is not None  # src would have been None

        src_node = ast.parse(src, filename=filename, mode='exec')
        assign_parents(src_node)
        candidates = find_call_nodes_on_line(
            src_node,
            frame,
            function_or_name,
            lineno
        )

        # What if there are zero candidates?
        if len(candidates) == 0:
            print(
                f"Warning: unable to find call node for {function_name}"
                f" on line {lineno} of file {filename}.",
                file=PRINT_TO
            )
            return {
                "file": filename,
                "line": lineno
            }

        # Figure out how many calls to get_my_context have happened
        # referencing this line before, so that we know which call on
        # this line we might be
        prev_this_line = COMPLETED_PER_LINE\
            .setdefault(function_name, {})\
            .setdefault((filename, lineno), 0)
        match = candidates[prev_this_line % len(candidates)]

        # Record this call so the next one will grab the subsequent
        # candidate
        COMPLETED_PER_LINE[function_name][(filename, lineno)] += 1

        arg_expr = match.args[0]

        # Add .parent attributes
        assign_parents(arg_expr)

        # Source code for the expression
        expr_src = get_expr_src(src, match)

        # Prepare our result dictionary
        result: ContextDict = {
            "file": filename,
            "line": lineno,
            "src": src,
            "expr": arg_expr,
            "expr_src": expr_src,
            "values": {},
            "relevant": set()
        }

        # Walk expression to find values for each variable
        for node in ast.walk(arg_expr):
            # If it's potentially a reference to a variable...
            if isinstance(
                node,
                (ast.Attribute, ast.Subscript, ast.Name)
            ):
                key = get_ref_src(src, node)
                if key not in result["values"]:
                    # Don't re-evaluate multiply-reference expressions
                    # Note: we assume they won't take on multiple
                    # values; if they did, even our first evaluation
                    # would probably be inaccurate.
                    val = deepish_copy(evaluate_in_context(node, frame))
                    result["values"][key] = val
                    if not is_inside_call_func(node):
                        result["relevant"].add(key)

        return result

    finally:
        del frame


#----------------#
# Output control #
#----------------#

def messagesAsErrors(activate: bool = True) -> None:
    """
    Sets `PRINT_TO` to `sys.stderr` so that messages from optimism will
    appear as error messages, rather than as normal printed output. This
    is the default behavior, but you can pass `False` as the argument to
    set it to `sys.stdout` instead, causing messages to appear as normal
    output.
    """
    global PRINT_TO
    if activate:
        PRINT_TO = sys.stderr
    else:
        PRINT_TO = sys.stdout
