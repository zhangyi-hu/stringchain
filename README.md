# stringchain

When you are programming on the client side, preparing a delimited string
to specify a request to the server can be tedious and error prone.
Suppose the case that request "foo.barr" is supported, but "foo.bar" is not.

Such kind of errors can only be noticed at runtime, and debugging them is
not a meaningful work at all. The purpose of Tool is largely to save us from
non-creative job so that humans can focus on the real work.

stringchain is such a tool.

With stringchain, you can download all the supported request strings
documented on the server, feed it to stringchain, and it will generate
a python modules that contains all the valid delimited string combinations.

Being grammartized, when you type those strings, your IDE will help you
with autocomplete and scream red, wavy underlines if it is invalid.
Silly typos won't even reach the interpreter.


Dependency:

    python >= 3.7

Install:

    conda install -c zhangyi-hu stringchain

Usage:

<img src="demo/demo.gif" width="600">
