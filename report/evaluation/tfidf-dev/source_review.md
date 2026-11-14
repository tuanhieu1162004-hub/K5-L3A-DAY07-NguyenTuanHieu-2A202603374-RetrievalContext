# Source review — tfidf-dev

Codex (AI), source-based offline review; not human certification

Answer grade uses all final context: 0 unsupported/wrong, 1 partially grounded, 2 complete. Citation support is strict for the claim attached to a citation or adjacent citation group; each group member must contribute evidence and the group must cover the claim. ID presence alone is insufficient. Context 0 no requested evidence, 1 partial evidence, 2 sufficient evidence and source. Errors remain separate. No labels are sent to the answering agent.

Human verification: not performed. These are AI-authored labels, not human certification.

## q01 (answered)

What does an interpreter do?

Reference: It reads another program and executes it.

Actual answer: An interpreter executes code line by line, translating each instruction into machine language and immediately executing it, without compiling the entire program beforehand. This allows for immediate feedback and easier debugging, but can be slower than compiled programs [45c4d9c37356d7623e4b2eb6].

Error: None

Answer grade: 0; context grade: 1. PDF24 demonstrates interactive code input, but does not ground line-by-line translation into machine code, no compilation, debugging or relative performance. Main explanatory answer is unsupported.

- [45c4d9c37356d7623e4b2eb6]: support=False. Prompt example does not establish the claimed interpreter implementation or performance.

Final context actually supplied to the model:

````text
[5109861fb586dcfa1620c979 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 35]
If  there  is  a  semantic  error  in  your  program,  it  will  run  without  generating  error
       messages, but it will not do the right thing.  It will do something else.  Specifically, it
       will do what you told it to do.
       Identifying semantic errors can be tricky because it requires you to work backward
       by looking at the output of the program and trying to figure out what it is doing.

[c37387c05351462db0f300d9 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 58]
36                                                                                    Chapter 4. Case study: interface design

It is terse, but it contains the essential information someone would need to use this func-
tion.  It explains concisely what the function does (without getting into the details of how
it does it).  It explains what effect each parameter has on the behavior of the function and
what type each parameter should be (if it is not obvious).

[45c4d9c37356d7623e4b2eb6 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 24]
The last line is apromptthat indicates that the interpreter is ready for you to enter code. If
you type a line of code and hit Enter, the interpreter displays the result:
>>>  1  +  1
2
Now you’re ready to get started.  From here on, I assume that you know how to start the
Python interpreter and run code.
````

## q02 (answered)

How are formal languages designed to differ from natural languages in ambiguity?

Reference: Formal languages aim to be nearly or completely unambiguous, giving each statement one meaning regardless of context.

Actual answer: Formal languages are designed to be nearly or completely unambiguous, meaning any statement has exactly one meaning regardless of context, unlike natural languages, which are full of ambiguity and rely on contextual clues to interpret meaning [8b450acd31f27b77b9302f2e]. Additionally, natural languages use redundancy to reduce misunderstandings, while formal languages are less redundant and more concise [064a156c6558e1b0678c1da1].

Error: None

Answer grade: 2; context grade: 2. PDF27 supports both ambiguity contrast and redundancy contrast.

- [8b450acd31f27b77b9302f2e]: support=True. Direct ambiguity paragraph.
- [064a156c6558e1b0678c1da1]: support=True. Direct redundancy paragraph.

Final context actually supplied to the model:

````text
[8b450acd31f27b77b9302f2e | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 27]
ambiguity:Natural languages are full of ambiguity, which people deal with by using con-
       textual clues and other information.  Formal languages are designed to be nearly or
       completely unambiguous, which means that any statement has exactly one meaning,
       regardless of context.

[399ecac7135bf11c1c774577 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 26]
Formal languagesare languages that are designed by people for specific applications. For
example,  the  notation  that  mathematicians  use  is  a  formal language  that  is  particularly
good at denoting relationships among numbers and symbols.  Chemists use a formal lan-
guage to represent the chemical structure of molecules. And most importantly:

       Programming  languages  are  formal  languages  that  have  been  designed  to
       express computations.

[064a156c6558e1b0678c1da1 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 27]
redundancy:In order to make up for ambiguity and reduce misunderstandings, natural
       languages employ lots of redundancy.  As a result, they are often verbose.  Formal
       languages are less redundant and more concise.
````

## q03 (answered)

What does the Python interpreter's prompt tell the user?

Reference: The interpreter is ready for the user to enter code or input.

Actual answer: The Python interpreter's prompt tells the user what input is expected. It serves as a guide for the user to type their response, and when the user presses Return or Enter, the program resumes and the input is returned as a string [d766b62febc4d2b37235e8dd].

Error: None

Answer grade: 0; context grade: 0. Wrong concept: context is input(prompt) on PDF67, not the interpreter prompt that indicates readiness for code.

- [d766b62febc4d2b37235e8dd]: support=False. Cited input-function example does not support the statement about interpreter prompt.

Final context actually supplied to the model:

````text
[9fdf55826322be97578e5b57 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 67]
That’s why the user’s input appears below the prompt.
If you expect the user to type an integer, you can try to convert the return value toint:
>>>  prompt  ='What...is  the  airspeed  velocity  of  an  unladen  swallow?\n'
>>>  speed  =  input(prompt)
What...is  the  airspeed  velocity  of  an  unladen  swallow?
42
>>>  int(speed)
42

[d766b62febc4d2b37235e8dd | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 67]
>>>  text
'What  are  you  waiting  for?'
Before getting input from the user, it is a good idea to print a prompt telling the user what
to type.inputcan take a prompt as an argument:
>>>  name  =  input('What...is  your  name?\n')
What...is  your  name?
Arthur,  King  of  the  Britons!
>>>  name
'Arthur,  King  of  the  Britons!'
The sequence\nat the end of the prompt represents anewline, which is a special character
that causes a line break.

[a1086c6d897fef1635c9db93 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 67]
The programs we have written so far accept no input from the user. They just do the same
thing every time.
Python provides a built-in function calledinputthat stops the program and waits for the
user to type something.  When the user pressesReturnorEnter, the program resumes and
inputreturns what the user typed as a string.   In Python 2,  the same function is called
raw_input.
>>>  text  =  input()
What  are  you  waiting  for?
````

## q04 (answered)

Which Python operator raises a number to a power?

Reference: The ** operator performs exponentiation.

Actual answer: The Python operator that raises a number to a power is the double asterisk (`**`). [09829ead7af7fc053d174bf7]

Error: None

Answer grade: 2; context grade: 2. PDF25 explicitly gives exponentiation operator **.

- [09829ead7af7fc053d174bf7]: support=True. Direct operator explanation.

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

[b682991e2f0b4f761994b81f | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 69]
5.13. Glossary                                                                                                                                  47
5.13    Glossary

floor division:An operator, denoted//, that divides two numbers and rounds down (to-
       ward negative infinity) to an integer.

modulus operator:An operator, denoted with a percent sign (%), that works on integers
       and returns the remainder when one number is divided by another.

[7bb7669831f51cc234f4b9ae | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 24]
There are two versions of Python, called Python 2 and Python 3. They are very similar, so
if you learn one, it is easy to switch to the other. In fact, there are only a few differences you
will encounter as a beginner.  This book is written for Python 3, but I include some notes
about Python 2.
````

## q05 (answered)

How does the book define a variable?

Reference: A variable is a name that refers to a value.

Actual answer: A variable is defined as "a name that refers to a value" [2cde73c27461559f77e0ede7].

Error: None

Answer grade: 2; context grade: 2. PDF36 directly defines variable as a name referring to a value.

- [2cde73c27461559f77e0ede7]: support=True. Exact definition in cited glossary.

Final context actually supplied to the model:

````text
[f87e205a74ed0628a0b5250b | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 39]
Chapter 3

Functions

In the context of programming, afunctionis a named sequence of statements that performs
a computation.  When you define a function, you specify the name and the sequence of
statements. Later, you can “call” the function by name.

3.1    Function calls

[2cde73c27461559f77e0ede7 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 36]
14                                                                  Chapter 2. Variables, expressions and statements
2.9    Glossary

variable:A name that refers to a value.

assignment:A statement that assigns a value to a variable.

state diagram:A graphical representation of a set of variables and the values they refer to.

keyword:A reserved word that is used to parse a program; you cannot use keywords like
       if,def, andwhileas variable names.

[c37387c05351462db0f300d9 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 58]
36                                                                                    Chapter 4. Case study: interface design

It is terse, but it contains the essential information someone would need to use this func-
tion.  It explains concisely what the function does (without getting into the details of how
it does it).  It explains what effect each parameter has on the behavior of the function and
what type each parameter should be (if it is not obvious).
````

## q06 (answered)

Why is class not allowed as a variable name?

Reference: class is a Python keyword. Keywords identify program structure and cannot be used as variable names.

Actual answer: The provided documents do not explain why "class" is not allowed as a variable name. While they mention the use of "class" in the context of types (e.g., `<class'int'>`), they do not address restrictions on variable names such as "class." [6736797ff94d11b6ea4c8c89]

Error: None

Answer grade: 0; context grade: 1. Semantic refusal despite answered status. Context discusses types and function-name keyword restrictions but does not identify class as a reserved keyword; original question remains unanswered.

- [6736797ff94d11b6ea4c8c89]: support=False. Type examples do not establish why class is forbidden or prove a corpus-wide absence.

Final context actually supplied to the model:

````text
[6736797ff94d11b6ea4c8c89 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 26]
If you are not sure what type a value has, the interpreter can tell you:
>>>  type(2)
<class'int'>
>>>  type(42.0)
<class'float'>
>>>  type('Hello,  World!')
<class'str'>
In these results, the word “class” is used in the sense of a category; a type is a category of
values.

Not surprisingly, integers belong to the typeint, strings belong tostrand floating-point
numbers belong tofloat.

[7d81695e517a29158b0e9de1 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 41]
The name of the function
isprint_lyrics. The rules for function names are the same as for variable names: letters,
numbers and underscore are legal, but the first character can’t be a number. You can’t use a
keyword as the name of a function, and you should avoid having a variable and a function
with the same name.

[a3c88b24065bb0fb71505923 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 46]
We will start writing fruitful functions in
a few chapters.

3.11    Why functions?

It may not be clear why it is worth the trouble to divide a program into functions.  There
are several reasons:
````

## q07 (answered)

Why does a standalone expression in a Python script not display its result, and how can you display it?

Reference: In script mode Python evaluates the expression but does not display the result. Use a print statement to display it.

Actual answer: A standalone expression in a Python script evaluates its result but does not display it. To display the result, a `print` statement must be used, such as `print(miles * 1.61)` [30778f61bef932f3ed9263c7]. In interactive mode, Python displays the result of a function call, but in a script, the return value is lost unless it is used or printed [89c8cf498ea77756b3aad3de].

Error: None

Answer grade: 2; context grade: 2. PDF33 continuation and PDF46 script example together explain no display and using print. Semantic context sufficient, although the frozen multi-fragment exact-gold metric lacks the first PDF33 fragment.

- [30778f61bef932f3ed9263c7]: support=True. PDF33 explicitly gives no display and print solution.
- [89c8cf498ea77756b3aad3de]: support=True. PDF46 supports interactive versus script return-value contrast.

Final context actually supplied to the model:

````text
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

[3390948daf2555a0df24953f | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 46]
math.sqrt(5)
This script computes the square root of 5, but since it doesn’t store or display the result, it
is not very useful.

[89c8cf498ea77756b3aad3de | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 46]
When you call a fruitful function, you almost always want to do something with the result;
for example, you might assign it to a variable or use it as part of an expression:
x  =  math.cos(radians)
golden  =  (math.sqrt(5)  +  1)  /  2
When you call a function in interactive mode, Python displays the result:
>>>  math.sqrt(5)
2.2360679774997898
But in a script, if you call a fruitful function all by itself, the return value is lost forever!
````

## q08 (error)

In chapter 2, when one operand of * is a string, what does the operation do and what type must the other operand have?

Reference: It repeats the string, and the other operand must be an integer.

Actual answer: (no valid final answer)

Error: Model call limit reached without a valid final decision

Execution error; no valid final answer to grade. Context grade: 0. Retrieved glossary/semantic-error passages do not explain string repetition or the integer requirement.


Final context actually supplied to the model:

````text
[5bd599a53107fa8bec0e02eb | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 36]
operand:One of the values on which an operator operates.

expression:A combination of variables, operators, and values that represents a single re-
       sult.

evaluate:To simplify an expression by performing the operations in order to yield a single
       value.

statement:A section of code that represents a command or action.  So far, the statements
       we have seen are assignments and print statements.

execute:To run a statement and do what it says.

[e29a9d771ac81bb2586ba2b8 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 36]
semantic error:An error in a program that makes it do something other than what the
       programmer intended.

2.10    Exercises

Exercise 2.1.Repeating my advice from the previous chapter, whenever you learn a new feature,
you should try it out in interactive mode and make errors on purpose to see what goes wrong.

   •We’ve seen thatn  =  42is legal. What about42  =  n?

[5109861fb586dcfa1620c979 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 35]
If  there  is  a  semantic  error  in  your  program,  it  will  run  without  generating  error
       messages, but it will not do the right thing.  It will do something else.  Specifically, it
       will do what you told it to do.
       Identifying semantic errors can be tricky because it requires you to work backward
       by looking at the output of the program and trying to figure out what it is doing.
````

## q09 (answered)

Does int round a floating-point value to the nearest integer when converting it?

Reference: No. It removes the fractional part rather than rounding to the nearest integer.

Actual answer: No, the `int` function does not round a floating-point value to the nearest integer; it chops off the fractional part. For example, `int(3.99999)` returns `3` and `int(-2.3)` returns `-2` [9d18da86eebbf287b14ae350].

Error: None

Answer grade: 2; context grade: 2. PDF39 explicitly supports truncation instead of rounding and both examples.

- [9d18da86eebbf287b14ae350]: support=True. Exact int behavior and example results.

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

[84fbf11d25a75404c5495fd8 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 55]
If you are using Python 2, the value ofanglemight be off because of integer division.  A
simple solution is to computeangle  =  360.0  /  n.  Because the numerator is a floating-
point number, the result is floating point.
When a function has more than a few numeric arguments, it is easy to forget what they are,
or what order they should be in.

[116dcc6a5aef142d6b82c926 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 29]
type:A category of values. The types we have seen so far are integers (typeint), floating-
       point numbers (typefloat), and strings (typestr).

integer:A type that represents whole numbers.

floating-point:A type that represents numbers with fractional parts.

string:A type that represents sequences of characters.

natural language:Any one of the languages that people speak that evolved naturally.
````

## q10 (error)

Does executing a function definition immediately run the statements inside the function?

Reference: No. The statements inside run only when the function is called; the definition itself generates no output.

Actual answer: (no valid final answer)

Error: Model call limit reached without a valid final decision

Execution error; no valid final answer to grade. Context grade: 2. PDF42 explicitly says the function body runs only when called; sufficient evidence was available despite final protocol failure.


Final context actually supplied to the model:

````text
[d05faa0b8be81490e134c8f0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
26                                                                                                                     Chapter 3. Functions

body:The sequence of statements inside a function definition.

parameter:A name used inside a function to refer to the value passed as an argument.

function call:A statement that runs a function.  It consists of the function name followed
       by an argument list in parentheses.

[8c83724f1c5f2e994b19c850 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 42]
repeat_lyrics()
This program contains two function definitions:print_lyricsandrepeat_lyrics. Func-
tion definitions get executed just like other statements, but the effect is to create function
objects.  The statements inside the function do not run until the function is called, and the
function definition generates no output.

[149c942b5ec82b8832bfb571 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 54]
square(bob)
The innermost statements,fdandltare indented twice to show that they are inside the
forloop, which is inside the function definition. The next line,square(bob), is flush with
the left margin, which indicates the end of both theforloop and the function definition.
````

## q11 (answered)

In chapter 3, what does it mean for a variable created inside a function to be local?

Reference: It exists only inside that function.

Actual answer: A variable created inside a function is local because it can only be used inside that function. This means the variable is not accessible outside the function's scope [dd1bf77ddb19877772dc93ab].

Error: None

Answer grade: 2; context grade: 2. PDF48 defines a local variable as usable only inside its function.

- [dd1bf77ddb19877772dc93ab]: support=True. Direct local-variable definition.

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

[d05faa0b8be81490e134c8f0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
26                                                                                                                     Chapter 3. Functions

body:The sequence of statements inside a function definition.

parameter:A name used inside a function to refer to the value passed as an argument.

function call:A statement that runs a function.  It consists of the function name followed
       by an argument list in parentheses.

[c2ce2cf7e3fe3ef8eae710ef | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 45]
To keep track of which variables can be used where, it is sometimes useful to draw astack
diagram.  Like state diagrams, stack diagrams show the value of each variable, but they
also show the function each variable belongs to.

Each function is represented by aframe.  A frame is a box with the name of a function
beside it and the parameters and variables of the function inside it. The stack diagram for
the previous example is shown in Figure 3.1.
````

## q12 (answered)

What distinguishes a fruitful function from a void function in the book's terminology?

Reference: A fruitful function returns a result; a void function performs an action without returning a useful value.

Actual answer: A fruitful function is distinguished from a void function by returning a value. A fruitful function returns a value, which can be used in expressions or assigned to variables, whereas a void function always returns `None` [dd1bf77ddb19877772dc93ab][c68331d5eaad34e17367e9cc].

Error: None

Answer grade: 2; context grade: 2. Adjacent citations jointly establish fruitful returns and void None; context PDF46 also supports using returned values.

- [dd1bf77ddb19877772dc93ab]: support=True. Contributes fruitful and return-value definitions to the citation group.
- [c68331d5eaad34e17367e9cc]: support=True. Contributes void and None definitions to the citation group.

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

[89c8cf498ea77756b3aad3de | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 46]
When you call a fruitful function, you almost always want to do something with the result;
for example, you might assign it to a variable or use it as part of an expression:
x  =  math.cos(radians)
golden  =  (math.sqrt(5)  +  1)  /  2
When you call a function in interactive mode, Python displays the result:
>>>  math.sqrt(5)
2.2360679774997898
But in a script, if you call a fruitful function all by itself, the return value is lost forever!

[c68331d5eaad34e17367e9cc | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
void function:A function that always returnsNone.

None: A special value returned by void functions.

module:A file that contains a collection of related functions and other definitions.

import statement:A statement that reads a module file and creates a module object.

module object:A value created by animportstatement that provides access to the values
       defined in a module.
````

## q13 (answered)

When is an expression supplied as a function argument evaluated relative to the function call?

Reference: The argument expression is evaluated before the function is called.

Actual answer: An expression supplied as a function argument is evaluated before the function call occurs. This is because the argument is processed as part of the function call, and its value is then assigned to the corresponding parameter within the function. [dd1bf77ddb19877772dc93ab]

Error: None

Answer grade: 0; context grade: 0. No context states evaluation order before the function call. Glossary value assignment and type example cannot ground the timing assertion.

- [dd1bf77ddb19877772dc93ab]: support=False. Argument glossary omits evaluation timing.

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

[d05faa0b8be81490e134c8f0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 48]
26                                                                                                                     Chapter 3. Functions

body:The sequence of statements inside a function definition.

parameter:A name used inside a function to refer to the value passed as an argument.

function call:A statement that runs a function.  It consists of the function name followed
       by an argument list in parentheses.

[bb21917efce6f7ead9e9f741 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 39]
We have already seen one example of afunction call:
>>>  type(42)
<class'int'>
The name of the function istype. The expression in parentheses is called theargumentof
the function. The result, for this function, is the type of the argument.
It is common to say that a function “takes” an argument and “returns” a result. The result
is also called thereturn value.
Python provides functions that convert values from one type to another.
````

## q14 (answered)

What is the name of rearranging a program to improve interfaces and make code easier to reuse?

Reference: Refactoring.

Actual answer: The process of rearranging a program to improve interfaces and make code easier to reuse is called refactoring [73fa8f9282d319c265d1416c].

Error: None

Answer grade: 2; context grade: 2. PDF57 explains reuse and PDF58 glossary identifies the same process as refactoring.

- [73fa8f9282d319c265d1416c]: support=True. Glossary identifies refactoring as improving interfaces and code qualities; context supplies exact reuse wording.

Final context actually supplied to the model:

````text
[3bd0782d554b96a9c34d13c0 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 57]
4.8. A development plan                                                                                                               35

def  circle(t,  r):
     arc(t,  r,  360)
This process—rearranging a program to improve interfaces and facilitate code re-use—is
calledrefactoring. In this case, we noticed that there was similar code inarcandpolygon,
so we “factored it out” intopolyline.

[73fa8f9282d319c265d1416c | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 58]
interface:A description of how to use a function, including the name and descriptions of
       the arguments and return value.

refactoring:The process of modifying a working program to improve function interfaces
       and other qualities of the code.

development plan:A process for writing programs.

[7875b3794b6f84e910384e5d | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 47]
3.12. Debugging                                                                                                                             25

   •  Creating a new function gives you an opportunity to name a group of statements,
      which makes your program easier to read and debug.

   •  Functions can make a program smaller by eliminating repetitive code.  Later, if you
      make a change, you only have to make it in one place.
````

## q15 (answered)

Where is a docstring placed, and what does it explain?

Reference: It is a string at the beginning of a function that explains the function's interface.

Actual answer: A docstring is placed at the beginning of a function, class, or module in Python, and it explains the purpose, functionality, and usage of that code element [c37387c05351462db0f300d9].

Error: None

Answer grade: 1; context grade: 1. Context supports function-use documentation but omits placement at the beginning and class/module generalization.

- [c37387c05351462db0f300d9]: support=False. PDF58 continuation describes function interface documentation, not placement or classes/modules.

Final context actually supplied to the model:

````text
[c37387c05351462db0f300d9 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 58]
36                                                                                    Chapter 4. Case study: interface design

It is terse, but it contains the essential information someone would need to use this func-
tion.  It explains concisely what the function does (without getting into the details of how
it does it).  It explains what effect each parameter has on the behavior of the function and
what type each parameter should be (if it is not obvious).

[acf35ef93e03adcab27738d5 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 70]
1.  What would happen if you called this function like this:recurse(-1,  0)?

   2.  Write a docstring that explains everything someone would need to know in order to use this
       function (and nothing else).

The following exercises use theturtlemodule, described in Chapter 4:
Exercise 5.5.Read the following function and see if you can figure out what it does (see the exam-
ples in Chapter 4). Then run it and see if you got it right.

[82440b27caf9e9c3d31f6443 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 43]
That sounds simple enough, until you remember that one function can call another. While
in the middle of one function, the program might have to run the statements in another
function.  Then, while running that new function, the program might have to run yet an-
other function!
Fortunately, Python is good at keeping track of where it is, so each time a function com-
pletes, the program picks up where it left off in the function that called it.
````

## dev-absent-01 (abstain)

What exact monthly subscription price does the indexed material state for PythonAnywhere?

Reference: Indexed chapters recommend PythonAnywhere and describe its Turtle limitation but give no monthly subscription price.

Actual answer: The retrieved passages do not provide enough evidence to answer.

Error: None

Answer grade: None; context grade: None. Explicit refusal without pricing guesses. Corpus audit establishes no PythonAnywhere monthly fee; retrieved book-price exercise is a different topic.


Final context actually supplied to the model:

````text
[72282302efda3b00daa2609e | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 31]
This kind of figure is called astate diagrambecause it shows what state each
of the variables is in (think of it as the variable’s state of mind). Figure 2.1 shows the result
of the previous example.

2.2    Variable names

Programmers generally choose names for their variables that are meaningful—they docu-
ment what the variable is used for.

                                     Figure 2.1: State diagram.

[c37387c05351462db0f300d9 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 58]
36                                                                                    Chapter 4. Case study: interface design

It is terse, but it contains the essential information someone would need to use this func-
tion.  It explains concisely what the function does (without getting into the details of how
it does it).  It explains what effect each parameter has on the behavior of the function and
what type each parameter should be (if it is not obvious).

[14beeef72811502d7b96ceec | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 37]
2.  Suppose the cover price of a book is $24.95, but bookstores get a 40% discount. Shipping costs
        $3 for the first copy and 75 cents for each additional copy. What is the total wholesale cost for
        60 copies?

    3.  If I leave my house at 6:52 am and run 1 mile at an easy pace (8:15 per mile), then 3 miles at
        tempo (7:12 per mile) and 1 mile at easy pace again, what time do I get home for breakfast?
````

## dev-absent-02 (abstain)

What minimum CPU clock speed in GHz does the indexed material require for running Turtle programs?

Reference: The Turtle setup describes installation and opening a window but specifies no CPU frequency requirement.

Actual answer: The retrieved passages do not provide enough evidence to answer.

Error: None

Answer grade: None; context grade: None. Explicit refusal without CPU frequency speculation; whole-corpus audit and Turtle setup contain no GHz requirement.


Final context actually supplied to the model:

````text
[b97dbc87c7e5f2131349fbe8 | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 51]
Create a file namedmypolygon.pyand type in the following code:
import  turtle
bob  =  turtle.Turtle()
print(bob)
turtle.mainloop()
Theturtlemodule (with a lowercase ’t’) provides a function calledTurtle(with an up-
percase ’T’) that creates a Turtle object, which we assign to a variable namedbob. Printing
bobdisplays something like:
<turtle.Turtle  object  at  0xb7bfbf4c>

[2bc9b1453cc61559102cba7f | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 51]
To check whether you have theturtlemodule, open the Python interpreter and type
>>>  import  turtle
>>>  bob  =  turtle.Turtle()
When you run this code, it should create a new window with small arrow that represents
the turtle. Close the window.

[8c513facb65b6e762670b25d | https://greenteapress.com/thinkpython2/thinkpython2.pdf | page 68]
46                                                                                      Chapter 5. Conditionals and recursion

But if the user types something other than a string of digits, you get an error:
>>>  speed  =  input(prompt)
What...is  the  airspeed  velocity  of  an  unladen  swallow?
What  do  you  mean,  an  African  or  a  European  swallow?
>>>  int(speed)
ValueError:  invalid  literal  for  int()  with  base  10
We will see how to handle this kind of error later.
````
