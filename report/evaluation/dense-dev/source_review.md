# Source review — dense-dev

Codex (AI), source-based offline review; not human certification

Answer grade uses all final context: 0 unsupported/wrong, 1 partially grounded, 2 complete. Citation support is strict for the claim attached to a citation or adjacent citation group; each group member must contribute evidence and the group must cover the claim. ID presence alone is insufficient. Context 0 no requested evidence, 1 partial evidence, 2 sufficient evidence and source. Errors remain separate. No labels are sent to the answering agent.

Human verification: not performed. These are AI-authored labels, not human certification.

## q01 (answered)

What does an interpreter do?

Reference: It reads another program and executes it.

Actual answer: An interpreter is a program that reads another program and executes it [588a2586f952d92e2134a52f]. It processes instructions line by line, allowing immediate execution and feedback, and can operate in interactive mode (where users type code at a prompt) or script mode (where it reads and runs code from a file) [e10ecac6a58a9974976be680].

Error: None

Answer grade: 1; context grade: 2. Definition is supported on PDF28. PDF36 supports interactive/script modes, but not the added line-by-line and immediate-feedback claim.

- [588a2586f952d92e2134a52f]: support=True. PDF28 directly defines interpreter.
- [e10ecac6a58a9974976be680]: support=False. PDF36 mode definitions do not establish all added execution claims.

Final context actually supplied to the model:

````text
[588a2586f952d92e2134a52f | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 28]
interpreter:A program that reads another program and executes it
prompt:Characters displayed by the interpreter to indicate that it is ready to take input
       from the user.

program:A set of instructions that specifies a computation.

[c40950ea17a520f2e201651d | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 29]
1.9. Exercises                                                                                                                                     7

print statement:An instruction that causes the Python interpreter to display a value on
       the screen.

operator:A special symbol that represents a simple computation like addition, multipli-
       cation, or string concatenation.

value:One of the basic units of data, like a number or string, that a program manipulates.

[e10ecac6a58a9974976be680 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 36]
interactive mode:A way of using the Python interpreter by typing code at the prompt.

script mode:A way of using the Python interpreter to read code from a script and run it.

script:A program stored in a file.

order of operations:Rules governing the order in which expressions involving multiple
       operators and operands are evaluated.

concatenate:To join two operands end-to-end.
````

## q02 (answered)

How are formal languages designed to differ from natural languages in ambiguity?

Reference: Formal languages aim to be nearly or completely unambiguous, giving each statement one meaning regardless of context.

Actual answer: Formal languages are designed to be nearly or completely unambiguous, meaning any statement has exactly one meaning regardless of context, unlike natural languages, which are full of ambiguity and rely on contextual clues to interpret meaning [8b450acd31f27b77b9302f2e]. Natural languages use redundancy to reduce misunderstandings and are often verbose, while formal languages are less redundant and more concise [064a156c6558e1b0678c1da1].

Error: None

Answer grade: 2; context grade: 2. PDF27 explicitly supports unambiguous formal language and redundancy contrast.

- [8b450acd31f27b77b9302f2e]: support=True. Ambiguity paragraph supports the first claim.
- [064a156c6558e1b0678c1da1]: support=True. Redundancy paragraph supports the second claim.

Final context actually supplied to the model:

````text
[8b450acd31f27b77b9302f2e | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 27]
ambiguity:Natural languages are full of ambiguity, which people deal with by using con-
       textual clues and other information.  Formal languages are designed to be nearly or
       completely unambiguous, which means that any statement has exactly one meaning,
       regardless of context.

[1f9ce86281020887a1ba4493 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 27]
Because we all grow up speaking natural languages, it is sometimes hard to adjust to for-
mal languages.  The difference between formal and natural language is like the difference
between poetry and prose, but more so:

Poetry:Words are used for their sounds as well as for their meaning, and the whole poem
       together creates an effect or emotional response. Ambiguity is not only common but
       often deliberate.

[064a156c6558e1b0678c1da1 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 27]
redundancy:In order to make up for ambiguity and reduce misunderstandings, natural
       languages employ lots of redundancy.  As a result, they are often verbose.  Formal
       languages are less redundant and more concise.
````

## q03 (answered)

What does the Python interpreter's prompt tell the user?

Reference: The interpreter is ready for the user to enter code or input.

Actual answer: The Python interpreter's prompt tells the user that the interpreter is ready to accept input from them. It indicates that the user can enter a line of code, which the interpreter will then read and execute [588a2586f952d92e2134a52f].

Error: None

Answer grade: 2; context grade: 2. PDF28 defines prompt as readiness for input and interpreter as reading/executing programs; PDF24 also explicitly explains entering code.

- [588a2586f952d92e2134a52f]: support=True. Prompt and interpreter definitions jointly support the answer.

Final context actually supplied to the model:

````text
[45c4d9c37356d7623e4b2eb6 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 24]
The last line is apromptthat indicates that the interpreter is ready for you to enter code. If
you type a line of code and hit Enter, the interpreter displays the result:
>>>  1  +  1
2
Now you’re ready to get started.  From here on, I assume that you know how to start the
Python interpreter and run code.

[e90d3f8ff995b006a5683f9c | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 24]
The  Pythoninterpreteris  a  program  that  reads  and  executes  Python  code.   Depending
on your environment, you might start the interpreter by clicking on an icon, or by typing
pythonon a command line. When it starts, you should see output like this:
Python  3.4.0  (default,  Jun  19  2015,  14:20:21)
[GCC  4.8.2]  on  linux
Type  "help",  "copyright",  "credits"  or  "license"  for  more  information.

[588a2586f952d92e2134a52f | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 28]
interpreter:A program that reads another program and executes it
prompt:Characters displayed by the interpreter to indicate that it is ready to take input
       from the user.

program:A set of instructions that specifies a computation.
````

## q04 (answered)

Which Python operator raises a number to a power?

Reference: The ** operator performs exponentiation.

Actual answer: The Python operator that raises a number to a power is the double asterisk (`**`). [09829ead7af7fc053d174bf7]

Error: None

Answer grade: 2; context grade: 2. PDF25 explicitly identifies ** as exponentiation.

- [09829ead7af7fc053d174bf7]: support=True. Operator and meaning appear together in cited chunk.

Final context actually supplied to the model:

````text
[09829ead7af7fc053d174bf7 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 25]
Finally, the operator**performs exponentiation; that is, it raises a number to a power:
>>>  6**2  +  6
42
In some other languages,^is used for exponentiation, but in Python it is a bitwise operator
called XOR. If you are not familiar with bitwise operators, the result will surprise you:
>>>  6  ^  2
4
I won’t cover bitwise operators in this book, but you can read about them athttp://wiki.
python.org/moin/BitwiseOperators.

[9c3a9eaca91d8365771a5d0b | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 25]
After “Hello, World”, the next step is arithmetic.  Python providesoperators, which are
special symbols that represent computations like addition and multiplication.

The operators+,-, and*perform addition, subtraction, and multiplication, as in the fol-
lowing examples:
>>>  40  +  2
42
>>>  43  -  1
42
>>>  6  *  7
42
The operator/performs division:
>>>  84  /  2
42.0
You might wonder why the result is42.0instead of42. I’ll explain in the next section.

[c40950ea17a520f2e201651d | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 29]
1.9. Exercises                                                                                                                                     7

print statement:An instruction that causes the Python interpreter to display a value on
       the screen.

operator:A special symbol that represents a simple computation like addition, multipli-
       cation, or string concatenation.

value:One of the basic units of data, like a number or string, that a program manipulates.
````

## q05 (answered)

How does the book define a variable?

Reference: A variable is a name that refers to a value.

Actual answer: A variable is a name that refers to a value [2cde73c27461559f77e0ede7][1b6352ef4f45c016e1de3651].

Error: None

Answer grade: 2; context grade: 2. Both PDF36 glossary and PDF31 introduction define variable as a name referring to a value.

- [2cde73c27461559f77e0ede7]: support=True. Direct definition on PDF36.
- [1b6352ef4f45c016e1de3651]: support=True. Direct definition on PDF31.

Final context actually supplied to the model:

````text
[2cde73c27461559f77e0ede7 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 36]
14                                                                  Chapter 2. Variables, expressions and statements
2.9    Glossary

variable:A name that refers to a value.

assignment:A statement that assigns a value to a variable.

state diagram:A graphical representation of a set of variables and the values they refer to.

keyword:A reserved word that is used to parse a program; you cannot use keywords like
       if,def, andwhileas variable names.

[1b6352ef4f45c016e1de3651 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 31]
Chapter 2

Variables, expressions and
statements

One of the most powerful features of a programming language is the ability to manipulate
variables. A variable is a name that refers to a value.

2.1    Assignment statements

[a2029d4ac1548e1751da0292 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 32]
10                                                                  Chapter 2. Variables, expressions and statements

Variable names can be as long as you like. They can contain both letters and numbers, but
they can’t begin with a number. It is legal to use uppercase letters, but it is conventional to
use only lower case for variables names.
````

## q06 (answered)

Why is class not allowed as a variable name?

Reference: class is a Python keyword. Keywords identify program structure and cannot be used as variable names.

Actual answer: class is one of Python’s keywords, and keywords are reserved for parsing the structure of the program. Because the interpreter uses keywords to recognize the syntax of the language, they cannot be used as variable names. Using class as a variable name would conflict with its role as a keyword, making it illegal [4b016dd00049b7575d402120].

Error: None

Answer grade: 2; context grade: 2. PDF32 names class as a reserved keyword used for program structure, not a variable name.

- [4b016dd00049b7575d402120]: support=True. Cited paragraph supplies both keyword status and restriction.

Final context actually supplied to the model:

````text
[4b016dd00049b7575d402120 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 32]
It turns out thatclassis one of Python’skeywords.   The interpreter uses keywords to
recognize the structure of the program, and they cannot be used as variable names.
Python 3 has these keywords:
False            class            finally        is                  return
None              continue      for                lambda          try
True              def                from              nonlocal      while
and                del                global          not                with
as

[32162818c8fb7d655b7cd9a5 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 32]
illegal character,@. But what’s wrong withclass?

[2cde73c27461559f77e0ede7 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 36]
14                                                                  Chapter 2. Variables, expressions and statements
2.9    Glossary

variable:A name that refers to a value.

assignment:A statement that assigns a value to a variable.

state diagram:A graphical representation of a set of variables and the values they refer to.

keyword:A reserved word that is used to parse a program; you cannot use keywords like
       if,def, andwhileas variable names.
````

## q07 (answered)

Why does a standalone expression in a Python script not display its result, and how can you display it?

Reference: In script mode Python evaluates the expression but does not display the result. Use a print statement to display it.

Actual answer: A standalone expression in a Python script does not display its result because, in script mode, Python evaluates the expression but does not automatically print the output. To display the result, a `print` statement must be used. For example, instead of just writing `miles * 1.61`, you need to write `print(miles * 1.61)` to see the result on the screen [30778f61bef932f3ed9263c7].

Error: None

Answer grade: 2; context grade: 2. Both required fragments from PDF33 are in final context; cited continuation explains evaluate-without-display and print with matching example.

- [30778f61bef932f3ed9263c7]: support=True. Cited paragraph supplies evaluation, display restriction and print example; preceding context establishes script mode.

Final context actually supplied to the model:

````text
[2d6429c9b0799d98c9fc0906 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 33]
For example, if you are using Python as a calculator, you might type
>>>  miles  =  26.2
>>>  miles  *  1.61
42.182
The first line assigns a value tomiles, but it has no visible effect. The second line is an ex-
pression, so the interpreter evaluates it and displays the result. It turns out that a marathon
is about 42 kilometers.
But if you type the same code into a script and run it, you get no output at all.  In script
mode an expression, all by itself, has no visible effect.

[30778f61bef932f3ed9263c7 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 33]
Python evaluates the expression, but
it doesn’t display the result. To display the result, you need aprintstatement like this:
miles  =  26.2
print(miles  *  1.61)
This behavior can be confusing at first.  To check your understanding, type the following
statements in the Python interpreter and see what they do:
5
x  =  5
x  +  1
Now put the same statements in a script and run it. What is the output? Modify the script
by transforming each expression into a print statement and then run it again.

[c40950ea17a520f2e201651d | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 29]
1.9. Exercises                                                                                                                                     7

print statement:An instruction that causes the Python interpreter to display a value on
       the screen.

operator:A special symbol that represents a simple computation like addition, multipli-
       cation, or string concatenation.

value:One of the basic units of data, like a number or string, that a program manipulates.
````

## q08 (answered)

In chapter 2, when one operand of * is a string, what does the operation do and what type must the other operand have?

Reference: It repeats the string, and the other operand must be an integer.

Actual answer: When one operand of * is a string, the operation performs repetition. The other operand must be an integer. [dfd307858f548598142b0ab2]

Error: None

Answer grade: 2; context grade: 2. PDF34 supports string repetition and integer requirement.

- [dfd307858f548598142b0ab2]: support=True. Both required conditions are explicit in cited chunk.

Final context actually supplied to the model:

````text
[dfd307858f548598142b0ab2 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 34]
The+operator performsstring concatenation, which means it joins the strings by linking
them end-to-end. For example:
>>>  first  ='throat'
>>>  second  ='warbler'
>>>  first  +  second
throatwarbler
The*operator also works on strings;  it performs repetition.   For example,'Spam'*3is
'SpamSpamSpam'. If one of the values is a string, the other has to be an integer.

[f33741a2dda8eef7aa05c3c0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 34]
This use of+and*makes sense by analogy with addition and multiplication.  Just as4*3
is equivalent to4+4+4, we expect'Spam'*3to be the same as'Spam'+'Spam', and'+'Spam
it is. On the other hand, there is a significant way in which string concatenation and repe-
tition are different from integer addition and multiplication.  Can you think of a property
that addition has that string concatenation does not?

2.7    Comments

[10a5eb21f23b8d6343d53552 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 34]
•  Operators with the same precedence are evaluated from left to right (except exponen-
       tiation).  So in the expressiondegrees  /  2  *  pi, the division happens first and the
       result is multiplied bypi. To divide by 2π, you can use parentheses or writedegrees
       /  2  /  pi.

I don’t work very hard to remember the precedence of operators.  If I can’t tell by looking
at the expression, I use parentheses to make it obvious.

2.6    String operations
````

## q09 (answered)

Does int round a floating-point value to the nearest integer when converting it?

Reference: No. It removes the fractional part rather than rounding to the nearest integer.

Actual answer: No, the `int` function does not round a floating-point value to the nearest integer; it chops off the fraction part. For example, `int(3.99999)` returns `3` and `int(-2.3)` returns `-2` [9d18da86eebbf287b14ae350].

Error: None

Answer grade: 2; context grade: 2. PDF39 explicitly says no rounding, chops fraction, and contains both examples.

- [9d18da86eebbf287b14ae350]: support=True. Definition and examples match cited text.

Final context actually supplied to the model:

````text
[9d18da86eebbf287b14ae350 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 39]
Theintfunction
takes any value and converts it to an integer, if it can, or complains otherwise:
>>>  int('32')
32
>>>  int('Hello')
ValueError:  invalid  literal  for  int():  Hello
intcan convert floating-point values to integers, but it doesn’t round off; it chops off the
fraction part:
>>>  int(3.99999)
3
>>>  int(-2.3)
-2
floatconverts integers and strings to floating-point numbers:
>>>  float(32)
32.0
>>>  float('3.14159')
3.14159

[2b98dde0b6b256da468eacad | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 61]
Thefloor divisionoperator,//, divides two numbers and rounds down to an integer. For
example, suppose the run time of a movie is 105 minutes.  You might want to know how
long that is in hours. Conventional division returns a floating-point number:
>>>  minutes  =  105
>>>  minutes  /  60
1.75
But we don’t normally write hours with decimal points.

[6e9df293a19d32ab6775442d | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 62]
If you are using Python 2, division works differently.  The division operator,/, performs
floor division if both operands are integers, and floating-point division if either operand is
afloat.

5.2    Boolean expressions
````

## q10 (answered)

Does executing a function definition immediately run the statements inside the function?

Reference: No. The statements inside run only when the function is called; the definition itself generates no output.

Actual answer: No, executing a function definition does not immediately run the statements inside the function. The statements inside a function are only executed when the function is called. [396ee1406052125e0fad32af]

Error: None

Answer grade: 2; context grade: 2. PDF43 says statements do not run until called; this answers the question about defining versus calling.

- [396ee1406052125e0fad32af]: support=True. Cited flow-of-execution paragraph explicitly supports the claim.

Final context actually supplied to the model:

````text
[396ee1406052125e0fad32af | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 43]
3.6    Flow of execution

To ensure that a function is defined before its first use, you have to know the order state-
ments run in, which is called theflow of execution.
Execution always begins at the first statement of the program. Statements are run one at a
time, in order from top to bottom.

Function definitions do not alter the flow of execution of the program, but remember that
statements inside the function don’t run until the function is called.

[5debe41951c8ff512dd453ee | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 43]
A function call is like a detour in the flow of execution.  Instead of going to the next state-
ment, the flow jumps to the body of the function, runs the statements there, and then comes
back to pick up where it left off.

[d05faa0b8be81490e134c8f0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
26                                                                                                                     Chapter 3. Functions

body:The sequence of statements inside a function definition.

parameter:A name used inside a function to refer to the value passed as an argument.

function call:A statement that runs a function.  It consists of the function name followed
       by an argument list in parentheses.
````

## q11 (answered)

In chapter 3, what does it mean for a variable created inside a function to be local?

Reference: It exists only inside that function.

Actual answer: A variable created inside a function is local, which means it only exists and can only be used within that function. [29439b00e0581d30f1842a9b]

Error: None

Answer grade: 2; context grade: 2. PDF44 explicitly says local means exists only inside the function.

- [29439b00e0581d30f1842a9b]: support=True. Local-variable paragraph supports scope restriction.

Final context actually supplied to the model:

````text
[dd1bf77ddb19877772dc93ab | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
argument:A value provided to a function when the function is called.  This value is as-
       signed to the corresponding parameter in the function.

local variable:A  variable  defined  inside  a  function.   A  local  variable  can  only  be  used
       inside its function.

return value:The result of a function. If a function call is used as an expression, the return
       value is the value of the expression.

fruitful function:A function that returns a value.

[29439b00e0581d30f1842a9b | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 44]
When you create a variable inside a function, it islocal, which means that it only exists
inside the function. For example:
def  cat_twice(part1,  part2):
     cat  =  part1  +  part2
     print_twice(cat)
This function takes two arguments, concatenates them, and prints the result twice. Here is
an example that uses it:
>>>  line1  ='Bing  tiddle'
>>>  line2  ='tiddle  bang.'
>>>  cat_twice(line1,  line2)
Bing  tiddle  tiddle  bang.
Bing  tiddle  tiddle  bang.

[3de30b32bff0185e7b7a5e0b | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 44]
You can also use a variable as an argument:
>>>  michael  ='Eric,  the  half  a  bee.'
>>>  print_twice(michael)
Eric,  the  half  a  bee.
Eric,  the  half  a  bee.
The name of the variable we pass as an argument (michael) has nothing to do with the
name of the parameter (bruce). It doesn’t matter what the value was called back home (in
the caller); here inprint_twice, we call everybodybruce.

3.8    Variables and parameters are local
````

## q12 (answered)

What distinguishes a fruitful function from a void function in the book's terminology?

Reference: A fruitful function returns a result; a void function performs an action without returning a useful value.

Actual answer: A fruitful function is distinguished from a void function by returning a value, whereas a void function always returns None and does not have a return value [dd1bf77ddb19877772dc93ab].

Error: None

Answer grade: 2; context grade: 2. Final context supports fruitful-return and void-None distinction, but the one citation only defines fruitful functions, not void functions. Correct contextual answer with incomplete citation attachment.

- [dd1bf77ddb19877772dc93ab]: support=False. dd1bf chunk lacks void/None definition; that is in other available chunks c683 and cfe91.

Final context actually supplied to the model:

````text
[c68331d5eaad34e17367e9cc | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
void function:A function that always returnsNone.

None: A special value returned by void functions.

module:A file that contains a collection of related functions and other definitions.

import statement:A statement that reads a module file and creates a module object.

module object:A value created by animportstatement that provides access to the values
       defined in a module.

[cfe91b7a78bcfd78b85c571a | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 46]
Void functions might display something on the screen or have some other effect, but they
don’t have a return value.  If you assign the result to a variable, you get a special value
calledNone.
>>>  result  =  print_twice('Bing')
Bing
Bing
>>>  print(result)
None
The valueNoneis not the same as the string'None'.  It is a special value that has its own
type:
>>>  type(None)
<class'>'NoneType
The functions we have written so far are all void.

[dd1bf77ddb19877772dc93ab | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
argument:A value provided to a function when the function is called.  This value is as-
       signed to the corresponding parameter in the function.

local variable:A  variable  defined  inside  a  function.   A  local  variable  can  only  be  used
       inside its function.

return value:The result of a function. If a function call is used as an expression, the return
       value is the value of the expression.

fruitful function:A function that returns a value.
````

## q13 (answered)

When is an expression supplied as a function argument evaluated relative to the function call?

Reference: The argument expression is evaluated before the function is called.

Actual answer: An expression supplied as a function argument is evaluated at the time of the function call. This means the expression is computed before the function is executed, and its result is then passed as an argument to the function [dd1bf77ddb19877772dc93ab].

Error: None

Answer grade: 0; context grade: 0. No final-context passage establishes evaluation before calling. PDF48 argument definition and PDF41 composition example cannot ground the timing claim; required PDF44 passage is absent.

- [dd1bf77ddb19877772dc93ab]: support=False. Cited glossary describes value-to-parameter assignment, not evaluation order.

Final context actually supplied to the model:

````text
[dd1bf77ddb19877772dc93ab | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
argument:A value provided to a function when the function is called.  This value is as-
       signed to the corresponding parameter in the function.

local variable:A  variable  defined  inside  a  function.   A  local  variable  can  only  be  used
       inside its function.

return value:The result of a function. If a function call is used as an expression, the return
       value is the value of the expression.

fruitful function:A function that returns a value.

[f784e8a1726df5b361a16a84 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 41]
For example, the argument of a function can be any
kind of expression, including arithmetic operators:
x  =  math.sin(degrees  /  360.0  *  2  *  math.pi)
And even function calls:
x  =  math.exp(math.log(x+1))
Almost anywhere you can put a value, you can put an arbitrary expression, with one ex-
ception:  the left side of an assignment statement has to be a variable name.   Any other
expression on the left side is a syntax error (we will see exceptions to this rule later).

[d05faa0b8be81490e134c8f0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
26                                                                                                                     Chapter 3. Functions

body:The sequence of statements inside a function definition.

parameter:A name used inside a function to refer to the value passed as an argument.

function call:A statement that runs a function.  It consists of the function name followed
       by an argument list in parentheses.
````

## q14 (answered)

What is the name of rearranging a program to improve interfaces and make code easier to reuse?

Reference: Refactoring.

Actual answer: The name of rearranging a program to improve interfaces and make code easier to reuse is refactoring [3bd0782d554b96a9c34d13c0].

Error: None

Answer grade: 2; context grade: 2. PDF57 explicitly names refactoring and the same purpose.

- [3bd0782d554b96a9c34d13c0]: support=True. Cited passage directly contains the requested definition.

Final context actually supplied to the model:

````text
[73fa8f9282d319c265d1416c | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 58]
interface:A description of how to use a function, including the name and descriptions of
       the arguments and return value.

refactoring:The process of modifying a working program to improve function interfaces
       and other qualities of the code.

development plan:A process for writing programs.

[3bd0782d554b96a9c34d13c0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 57]
4.8. A development plan                                                                                                               35

def  circle(t,  r):
     arc(t,  r,  360)
This process—rearranging a program to improve interfaces and facilitate code re-use—is
calledrefactoring. In this case, we noticed that there was similar code inarcandpolygon,
so we “factored it out” intopolyline.

[172a5fb0f9b121b6aac98b96 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 57]
If we had planned ahead, we might have writtenpolylinefirst and avoided refactoring,
but often you don’t know enough at the beginning of a project to design all the interfaces.
Once you start coding, you understand the problem better. Sometimes refactoring is a sign
that you have learned something.

4.8    A development plan

Adevelopment planis a process for writing programs.  The process we used in this case
study is “encapsulation and generalization”. The steps of this process are:
````

## q15 (answered)

Where is a docstring placed, and what does it explain?

Reference: It is a string at the beginning of a function that explains the function's interface.

Actual answer: A docstring is placed at the beginning of a function, class, or module in Python, and it explains the purpose, functionality, and usage of that code element [2ed8e23bdbcbb3742799992f]. By convention, all docstrings are triple-quoted strings, also known as multiline strings, because they allow the string to span more than one line [1f28fd86536dfc10a201af4c].

Error: None

Answer grade: 1; context grade: 2. Function placement and triple quoting are supported, but extending the definition to classes/modules is not supported by final context.

- [2ed8e23bdbcbb3742799992f]: support=False. PDF57 describes functions only, not classes/modules.
- [1f28fd86536dfc10a201af4c]: support=True. PDF57 continuation explicitly supports triple-quote convention.

Final context actually supplied to the model:

````text
[2ed8e23bdbcbb3742799992f | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 57]
Adocstringis a string at the beginning of a function that explains the interface (“doc” is
short for “documentation”). Here is an example:
def  polyline(t,  n,  length,  angle):
     """Draws  n  line  segments  with  the  given  length  and
     angle  (in  degrees)  between  them.    t  is  a  turtle.

[1f28fd86536dfc10a201af4c | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 57]
"""
     for  i  in  range(n):
           t.fd(length)
           t.lt(angle)
By  convention,  all  docstrings  are  triple-quoted  strings,  also  known  as  multiline  strings
because the triple quotes allow the string to span more than one line.

[54d631b4b196787fdc312528 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 59]
4.12. Exercises                                                                                                                                 37

                                            Figure 4.1: Turtle flowers.

                                              Figure 4.2: Turtle pies.

docstring:A string that appears at the top of a function definition to document the func-
       tion’s interface.
precondition:A requirement that should be satisfied by the caller before a function starts.
````

## dev-absent-01 (abstain)

What exact monthly subscription price does the indexed material state for PythonAnywhere?

Reference: Indexed chapters recommend PythonAnywhere and describe its Turtle limitation but give no monthly subscription price.

Actual answer: The retrieved passages do not provide enough evidence to answer.

Error: None

Answer grade: None; context grade: None. Explicit refusal with no price or speculation. Corpus audit finds PythonAnywhere recommendations but no subscription price.


Final context actually supplied to the model:

````text
[a5fdb6016e57440031dcce76 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 33]
Oth-
erwise I recommend using PythonAnywhere again. I have posted instructions for running
in script mode athttp://tinyurl.com/thinkpython2e.
Because Python provides both modes, you can test bits of code in interactive mode before
you put them in a script.  But there are differences between interactive mode and script
mode that can be confusing.

[5472054f25fd2f82efbe6ac9 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 24]
To avoid that problem, I recommend that you start out running Python in a browser. Later,
when you are comfortable with Python, I’ll make suggestions for installing Python on your
computer.

There are a number of web pages you can use to run Python.  If you already have a fa-
vorite, go ahead and use it. Otherwise I recommend PythonAnywhere. I provide detailed
instructions for getting started athttp://tinyurl.com/thinkpython2e.

[1cddd5a9ea6208145c978558 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 24]
One  of  the  challenges  of  getting  started  with  Python  is  that  you  might  have  to  install
Python and related software on your computer.  If you are familiar with your operating
system, and especially if you are comfortable with the command-line interface, you will
have no trouble installing Python.  But for beginners, it can be painful to learn about sys-
tem administration and programming at the same time.
````

## dev-absent-02 (abstain)

What minimum CPU clock speed in GHz does the indexed material require for running Turtle programs?

Reference: The Turtle setup describes installation and opening a window but specifies no CPU frequency requirement.

Actual answer: The retrieved passages do not provide enough evidence to answer.

Error: None

Answer grade: None; context grade: None. Explicit refusal with no GHz claim. Setup passages and full-corpus absence audit contain no CPU clock requirement.


Final context actually supplied to the model:

````text
[8fc9b0e57d98094b284e5387 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 59]
1.  Draw a stack diagram that shows the state of the program while executingcircle(bob,
       radius). You can do the arithmetic by hand or addprintstatements to the code.
   2.  The version ofarcin Section 4.7 is not very accurate because the linear approximation of the
       circle is always outside the true circle. As a result, the Turtle ends up a few pixels away from
       the correct destination.  My solution shows a way to reduce the effect of this error.

[2bc9b1453cc61559102cba7f | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 51]
To check whether you have theturtlemodule, open the Python interpreter and type
>>>  import  turtle
>>>  bob  =  turtle.Turtle()
When you run this code, it should create a new window with small arrow that represents
the turtle. Close the window.

[7da45d79f73c93b3bb1d68e0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 51]
Chapter 4

Case study: interface design

This chapter presents a case study that demonstrates a process for designing functions that
work together.

It introduces theturtlemodule, which allows you to create images using turtle graphics.
Theturtlemodule is included in most Python installations, but if you are running Python
using PythonAnywhere, you won’t be able to run the turtle examples (at least you couldn’t
when I wrote this).
````
