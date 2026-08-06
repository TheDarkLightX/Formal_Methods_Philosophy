# Fourier function engineering example

This directory contains the exact checker used by the Fourier function
engineering tutorial draft.

Run:

~~~bash
python3 examples/fourier_function_engineering/verify_three_note_spotlight.py
~~~

The checker classifies the rational coefficient c in:

~~~text
K(x) = a + (1/2) cos(x) + c cos(2x),
a = 1/2 - c.
~~~

It verifies the factorization in the coordinate y = cos(x) with exact
Fraction arithmetic. It accepts precisely when c <= 1/8. The bundled negative
case c = 1/7 produces the exact witness:

~~~text
y = -7/8
K(y) = -1/224
~~~

Scope: this is a deterministic checker for one declared family. It is not a
general Fourier, optimization, or theorem-proving engine.
