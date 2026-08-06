---
title: "How to build a function that helps prove a theorem"
layout: docs
kicker: Fourier function engineering
description: "A story-led introduction to designing proof functions by choosing waves, cancellation, concentration, filtering, and independently checkable certificates."
---

## The room with the hidden shape

The reader sits near the window while I carry a blank sheet to the board.

“I need a magical shape,” I say.

Ana looks at the empty sheet.

“What shape?”

“A shape that helps prove a theorem. Perhaps it should detect something, count something, make unwanted things cancel, smooth a rough signal, or keep an error small.”

I try to draw the finished shape directly.

The chalk curls, stops, and curls again.

“That is hard,” says Malik.

“Exactly. So I will use a different door.”

I write:

~~~text
🎯 proof goal
      ↓
🎵 choose the notes
      ↓
🎚️ choose their strengths and phases
      ↓
🔄 combine the notes
      ↓
🌊 a helper shape appears
      ↓
📜 check its properties, then use them in the proof
~~~

“This,” I say, “is Fourier function engineering.”

The central idea is:

> **Design the frequencies first. Transform them into a function. Use the function as a carefully checked proof tool.**

The function is not magic evidence. A program or mathematician still has to verify the properties that make the final argument work.

<figure class="fp-figure">
  <p class="fp-figure-title">Build the helper from its notes</p>
  {% include diagrams/fourier-function-engineering.svg %}
  <figcaption class="fp-figure-caption">A difficult shape can be designed indirectly. The proof begins with a goal, not with a famous formula.</figcaption>
</figure>

## The small rulebook for this lesson

The class writes four promises on the side of the board.

~~~text
finite clocks       use positions 0, 1, ..., q−1
periodic waves      repeat after 2π
infinite heat       use x on the real line and t > 0
proof language      state what is exact, bounded, or approximate
computer search     distinguish a candidate from its certificate
~~~

When a statement involves an infinite sum, an integral, or a limit, the domain and convergence rule matter. The finite wave calculations below are exact. The approximation theorem is stated for continuous periodic functions. The heat example uses sufficiently decaying initial data on the real line.

Those assumptions are part of the theorem. They are not decoration.

## A function is a little machine

A function is a machine with an input and an output:

~~~text
input x
   ↓
┌─────────────┐
│  function f │
└─────────────┘
   ↓
output f(x)
~~~

For example:

$$
f(x)=x^2.
$$

Read it as:

> “The output of <code>f</code> at <code>x</code> is <code>x</code> times <code>x</code>.”

So:

$$
f(3)=9.
$$

The same function can also be drawn as a landscape:

~~~text
height
  ▲
  │       /\
  │      /  \
  │_____/____\________▶ position
~~~

At each position <code>x</code>, the function gives a height <code>f(x)</code>.

Fourier analysis gives us another way to describe the same machine. Instead of describing every height directly, we describe the machine’s repeating waves.

## A function can be an orchestra

The simplest repeating waves are:

~~~text
constant note     1
slow wave         cos(x)
faster wave       cos(2x)
sideways wave     sin(x)
~~~

The number <code>k</code> is the frequency. It says how many complete wiggles occur during one trip around the circle.

~~~text
k = 1       one wiggle
k = 2       two wiggles
k = 5       five wiggles
~~~

A finite Fourier sum is a finite orchestra:

$$
F(x)
=
a_0+
\sum_{k=1}^{N}
\bigl(a_k\cos(kx)+b_k\sin(kx)\bigr).
$$

The dictionary is:

~~~text
k        which note
aₖ,bₖ    how loudly and in which direction it plays
Σ        combine the notes
F(x)     the finished shape
~~~

The complex notation compresses the two real waves into one rotating arrow:

$$
e^{ikx}=\cos(kx)+i\sin(kx),
\qquad i^2=-1.
$$

Here <code>i</code> is a symbol whose square is <code>-1</code>. The arrow rotates as <code>x</code> changes.

On the real line, one common Fourier-transform convention is:

$$
\widehat f(\xi)
=
\int_{-\infty}^{\infty}
f(x)e^{-i\xi x}\,dx.
$$

Under suitable regularity and decay assumptions, the inverse transform rebuilds the shape:

$$
f(x)
=
\frac{1}{2\pi}
\int_{-\infty}^{\infty}
\widehat f(\xi)e^{i\xi x}\,d\xi.
$$

Child translation:

~~~text
Fourier transform          listen for the notes
inverse Fourier transform  put the notes back together
~~~

For a periodic function, the integral becomes a list of discrete notes. For a finite sum, the reconstruction is an exact identity. For an infinite series or an integral transform, an inversion theorem with stated hypotheses must be supplied. The displayed formulas are not valid for every imaginable function without qualification.

## The first proof tool is a detector

The teacher draws a lamp.

“Suppose we want to find objects with property <code>P</code>. We can build a detector.”

$$
\mathbf{1}_{P}(x)
=
\begin{cases}
1,&\text{if }x\text{ has property }P,\\
0,&\text{if }x\text{ does not have property }P.
\end{cases}
$$

The symbol <code>1_P</code> means “the indicator of <code>P</code>.” It is a mathematical light switch:

~~~text
property true   → 1 → light on
property false  → 0 → light off
~~~

Once the detector exists, counting becomes addition:

$$
\#\{x:P(x)\}
=
\sum_x\mathbf{1}_{P}(x).
$$

Every success contributes <code>1</code>. Every failure contributes <code>0</code>.

The difficulty is that a detector can look jagged and unpleasant. Fourier analysis lets us build it from waves that agree on the wanted inputs and cancel on the unwanted inputs.

## The even-number lamp

I ask the class:

> “Can we build a lamp that turns on for even numbers and off for odd numbers?”

The first wave never changes:

$$
C(n)=1.
$$

The second wave flips sign at every step:

$$
A(n)=(-1)^n.
$$

The two patterns are:

~~~text
n:       0   1   2   3   4   5

C(n):    1   1   1   1   1   1

A(n):    1  −1   1  −1   1  −1
~~~

Now average them:

$$
E(n)=\frac{1+(-1)^n}{2}.
$$

For an even number, the two waves agree:

$$
E(4)=\frac{1+1}{2}=1.
$$

For an odd number, they cancel:

$$
E(5)=\frac{1-1}{2}=0.
$$

The whole lamp is:

~~~text
n:       0   1   2   3   4   5

E(n):    1   0   1   0   1   0
~~~

<figure class="fp-figure">
  <p class="fp-figure-title">Agreement becomes a detector</p>
  {% include diagrams/fourier-detector.svg %}
  <figcaption class="fp-figure-caption">The constant note and the alternating note agree on even inputs and cancel on odd inputs.</figcaption>
</figure>

The first Fourier lesson is:

> **Make waves agree where the helper should be large. Make waves cancel where the helper should vanish.**

## The lamp proves a counting theorem

Claim:

> Among the numbers <code>0, 1, 2, …, 2m−1</code>, exactly <code>m</code> are even.

Use the detector:

$$
\sum_{n=0}^{2m-1}E(n)
=
\sum_{n=0}^{2m-1}
\frac{1+(-1)^n}{2}.
$$

Separate the two parts:

$$
\sum_{n=0}^{2m-1}E(n)
=
\frac{1}{2}\sum_{n=0}^{2m-1}1
+
\frac{1}{2}\sum_{n=0}^{2m-1}(-1)^n.
$$

The first sum contains <code>2m</code> ones:

$$
\frac{1}{2}(2m)=m.
$$

The second sum cancels in pairs:

$$
1-1+1-1+\cdots+1-1=0.
$$

Therefore:

$$
\sum_{n=0}^{2m-1}E(n)=m.
$$

The detector did not merely illustrate the answer. It converted the counting problem into a cancellation proof.

## The clock with <code>q</code> seats

The class replaces the even-odd line with a clock:

~~~text
0 → 1 → 2 → ... → q−1 → 0
~~~

Now the question is:

> “Did <code>n</code> make a whole number of laps?”

That means:

$$
n\equiv0\pmod q.
$$

To build the detector, place one arrow-step around a circle:

$$
\omega=e^{2\pi i/q}.
$$

The powers

$$
1,\omega,\omega^2,\ldots,\omega^{q-1}
$$

are evenly spaced around the unit circle.

Define:

$$
\delta_q(n)
=
\frac{1}{q}
\sum_{r=0}^{q-1}\omega^{rn}.
$$

Child reading:

> “Spin the <code>q</code> test arrows according to <code>n</code>, add them, and divide by <code>q</code>.”

## Why the clock detector works

### Whole laps

If <code>q divides n</code>, then <code>ω^n=1</code>. Every term is <code>1</code>:

$$
\sum_{r=0}^{q-1}\omega^{rn}
=
\sum_{r=0}^{q-1}1
=q.
$$

So:

$$
\delta_q(n)=1.
$$

### A partial lap

If <code>q does not divide n</code>, set <code>z=ω^n</code>. Then <code>z≠1</code>, but <code>z^q=1</code>. The geometric-sum identity gives:

$$
\sum_{r=0}^{q-1}z^r
=
\frac{1-z^q}{1-z}
=0.
$$

So:

$$
\delta_q(n)=0.
$$

We have proved:

$$
\delta_q(n)
=
\begin{cases}
1,&q\mid n,\\
0,&q\nmid n.
\end{cases}
$$

The arrows explain the same result visually:

~~~text
whole lap       → → → → →     line up
partial lap     ↗ ← ↙ → ↘     cancel
~~~

The formal proof is the finite geometric sum. The picture is a memory aid.

## Count solutions by inserting the detector

Suppose we want to count pairs <code>(x,y)</code> with:

$$
x+y\equiv0\pmod q,
\qquad
0\le x,y<q.
$$

The detector turns the condition into a number:

$$
N
=
\sum_{x=0}^{q-1}
\sum_{y=0}^{q-1}
\delta_q(x+y).
$$

Substitute the Fourier detector:

$$
N
=
\frac{1}{q}
\sum_{r=0}^{q-1}
\sum_x\sum_y
\omega^{r(x+y)}.
$$

The exponent splits:

$$
\omega^{r(x+y)}
=
\omega^{rx}\omega^{ry}.
$$

So the two sums separate:

$$
N
=
\frac{1}{q}
\sum_{r=0}^{q-1}
\left(\sum_x\omega^{rx}\right)
\left(\sum_y\omega^{ry}\right).
$$

When <code>r=0</code>, each inner sum equals <code>q</code>.

When <code>r≠0</code>, the arrows complete a nontrivial circle and cancel, so each inner sum is <code>0</code>.

Only one frequency survives:

$$
N
=
\frac{1}{q}(q)(q)
=q.
$$

There are exactly <code>q</code> solutions.

The teacher circles the proof:

~~~text
logical condition
      ↓ detector
sum of waves
      ↓ cancellation
exact count
~~~

## A probe can listen for one note

Fourier functions can also act as listening devices.

Suppose a finite wave mixture is:

$$
F(x)
=
a_0+
\sum_{k=1}^{N}
\bigl(a_k\cos(kx)+b_k\sin(kx)\bigr).
$$

How can we recover the coefficient <code>a_m</code>?

Use the probe:

$$
g_m(x)=\cos(mx).
$$

Over a complete period, different notes cancel:

$$
\int_0^{2\pi}\cos(nx)\cos(mx)\,dx
=0
\qquad
(n\ne m).
$$

The matching note survives:

$$
\int_0^{2\pi}\cos^2(mx)\,dx=\pi.
$$

Therefore:

$$
a_m
=
\frac{1}{\pi}
\int_0^{2\pi}F(x)\cos(mx)\,dx.
$$

The sine probe recovers <code>b_m</code>. The constant probe recovers <code>a_0</code>.

This proves uniqueness of the coefficients: two finite wave descriptions of the same function must have the same coefficients.

Child translation:

~~~text
complicated song
      ↓ play one matching note
only that note answers
~~~

This is the same design pattern as the detector. Choose a function that is orthogonal to everything the proof should ignore.

## Build a spotlight, not a switch

A detector is sharp. Sometimes a proof needs a soft spotlight:

~~~text
bright near the target
dim far away
never negative
total brightness known
~~~

Start with a wave bundle:

$$
G_N(x)
=
1+e^{ix}+e^{2ix}+\cdots+e^{i(N-1)x}.
$$

At <code>x=0</code>, every wave equals <code>1</code>, so all arrows align:

$$
G_N(0)=N.
$$

Away from <code>0</code>, the arrows point in different directions and begin to cancel.

Now square the size:

$$
K_N(x)
=
\frac{1}{N}\lvert G_N(x)\rvert^2.
$$

This is the Fejér kernel.

Because it is a squared magnitude:

$$
K_N(x)\ge0.
$$

The total mass is one. To see why, expand:

$$
K_N(x)
=
\frac{1}{N}
\sum_{j=0}^{N-1}
\sum_{\ell=0}^{N-1}
e^{i(j-\ell)x}.
$$

Collect terms having the same difference <code>k=j−ℓ</code>. Exactly <code>N−|k|</code> pairs have difference <code>k</code>, so:

$$
K_N(x)
=
\sum_{k=-(N-1)}^{N-1}
\left(1-\frac{|k|}{N}\right)e^{ikx}.
$$

This formula exposes the spectral cost of the square. The bundle <code>G_N</code> uses frequencies <code>0,...,N−1</code>, while <code>|G_N|²</code> uses every difference frequency from <code>−(N−1)</code> through <code>N−1</code>.

Average over one period. Every term with <code>j≠ℓ</code> cancels. The <code>N</code> terms with <code>j=ℓ</code> each contribute <code>1</code>:

$$
\frac{1}{2\pi}
\int_{-\pi}^{\pi}K_N(x)\,dx
=
\frac{1}{N}N
=1.
$$

<figure class="fp-figure">
  <p class="fp-figure-title">A spotlight made from aligned waves</p>
  {% include diagrams/fourier-spotlight.svg %}
  <figcaption class="fp-figure-caption">Squaring the wave bundle guarantees nonnegativity. Adding frequencies makes the main peak narrower.</figcaption>
</figure>

As <code>N</code> grows, the kernel keeps total mass one but concentrates more of that mass near <code>x=0</code>.

That gives us a soft version of a detector:

~~~text
exact detector     1 here, 0 there
spotlight          mostly here, very little there
~~~

## The spotlight proves an approximation theorem

Let <code>f</code> be a continuous <code>2π</code>-periodic function. Define:

$$
\sigma_Nf(x)
=
\frac{1}{2\pi}
\int_{-\pi}^{\pi}
f(x-y)K_N(y)\,dy.
$$

This is a weighted average of nearby values of <code>f</code>.

The Fejér approximation theorem says:

$$
\sup_{x\in\mathbb{R}}
\lvert \sigma_Nf(x)-f(x)\rvert
\longrightarrow0.
$$

In words:

> The finite Fourier averages <code>σ_N f</code> approach <code>f</code> uniformly.

The proof has two rooms.

### Near the target

If <code>|y|<δ</code>, continuity makes:

$$
\lvert f(x-y)-f(x)\rvert
$$

small.

### Far from the target

If <code>|y|≥δ</code>, the difference may not be small. But the spotlight places less and less total mass there as <code>N</code> grows.

So:

~~~text
near region   small change × lots of weight = small
far region    possible change × tiny weight = small
~~~

The total error is small.

The formal proof begins with:

$$
\sigma_Nf(x)-f(x)
=
\frac{1}{2\pi}
\int_{-\pi}^{\pi}
\bigl(f(x-y)-f(x)\bigr)K_N(y)\,dy.
$$

Then split the integral into <code>|y|<δ</code> and <code>|y|≥δ</code>, and use continuity plus concentration.

This is a powerful proof-engineering lesson:

> **If the theorem needs a local average, construct a nonnegative, normalized, increasingly concentrated kernel.**

### When is the square trick complete?

For one-variable trigonometric polynomials, the square construction is more than a convenient sufficient condition. The Fejér–Riesz factorization theorem says that if:

$$
T(x)=\sum_{k=-N}^{N}c_ke^{ikx}
$$

is real-valued and nonnegative for every real <code>x</code>, then there is an ordinary polynomial:

$$
P(z)=a_0+a_1z+\cdots+a_Nz^N
$$

such that:

$$
T(x)=\left|P(e^{ix})\right|^2.
$$

So, in this one-dimensional finite-band setting, searching over squared magnitudes can represent every nonnegative trigonometric polynomial. This statement does not automatically extend to several variables as one squared magnitude. The domain is part of the theorem.

## The heat room: filtering frequencies

The class now brings in a rough temperature profile:

~~~text
🔥░🔥░░🔥░🔥░░░🔥
~~~

“Heat should smooth this,” says Noor.

The heat equation is:

$$
\frac{\partial u}{\partial t}
=
\frac{\partial^2u}{\partial x^2}.
$$

Here <code>u(x,t)</code> is temperature, <code>x</code> is position, and <code>t</code> is time.

For this example, assume <code>x∈ℝ</code>, <code>t>0</code>, and the initial temperature decays enough at infinity for the integrations by parts below to have no boundary terms.

Use the Fourier transform:

$$
\widehat u(\xi,t)
=
\int_{-\infty}^{\infty}
u(x,t)e^{-i\xi x}\,dx.
$$

Fourier analysis turns a second derivative into multiplication:

$$
\widehat{\frac{\partial^2u}{\partial x^2}}
=
-\xi^2\widehat u.
$$

So the heat equation becomes:

$$
\frac{\partial\widehat u}{\partial t}
=
-\xi^2\widehat u.
$$

For each frequency <code>ξ</code>, this is a simple decay equation:

$$
\widehat u(\xi,t)
=
e^{-t\xi^2}\widehat u_0(\xi).
$$

The multiplier is a frequency volume knob:

~~~text
slow frequency   ξ small   → mostly kept
fast frequency   ξ large   → strongly weakened
~~~

<figure class="fp-figure">
  <p class="fp-figure-title">Heat keeps slow notes and removes fast wiggles</p>
  {% include diagrams/fourier-heat-filter.svg %}
  <figcaption class="fp-figure-caption">The differential equation becomes one decay rule for each frequency.</figcaption>
</figure>

The inverse transform gives the Gaussian heat kernel:

$$
G_t(x)
=
\frac{1}{\sqrt{4\pi t}}
e^{-x^2/(4t)}.
$$

The temperature is:

$$
u(x,t)
=
\int_{-\infty}^{\infty}
G_t(y)u_0(x-y)\,dy.
$$

This integral is called convolution. In child language, slide the Gaussian across the starting temperature and take a weighted average at each position.

The Gaussian has three proof-friendly properties:

$$
G_t(x)\ge0,
$$

$$
\int_{-\infty}^{\infty}G_t(x)\,dx=1,
$$

and:

$$
G_t\text{ is smooth for }t>0.
$$

Therefore the later temperature is an average of nearby starting temperatures. It does not create a new value larger than the largest starting value:

$$
\lvert u(x,t)\rvert
\le
\sup_y\lvert u_0(y)\rvert.
$$

The frequency design explains the smoothing. The kernel shape makes the averaging properties visible.

There is also a time-composition law:

$$
G_t\text{ followed by }G_s
=
G_{t+s}.
$$

In frequency space the proof is one line:

$$
e^{-t\xi^2}e^{-s\xi^2}
=
e^{-(t+s)\xi^2}.
$$

The teacher underlines the pattern:

~~~text
hard spatial equation
      ↓ Fourier transform
one small equation per frequency
      ↓ solve
frequency multiplier
      ↓ inverse transform
proof-friendly spatial kernel
~~~

## Can a program automate this?

The class writes a program card:

~~~text
🧠 human states the proof goal
🧮 program chooses a search space
🎚️ program searches for coefficients
🔄 program reconstructs a candidate function
🔍 checker verifies the certificate
📜 human connects the properties to the theorem
~~~

The honest answer is:

> **Yes, function engineering can be automated inside a declared family. The program can search for a candidate. A separate checker must still verify the mathematical obligations.**

### The bounded synthesis version

Suppose the program is allowed to use only these waves:

$$
1,\cos(x),\sin(x),\ldots,\cos(Nx),\sin(Nx).
$$

The unknowns are the coefficients:

$$
a_0,a_1,b_1,\ldots,a_N,b_N.
$$

The proof goal becomes constraints on those numbers:

~~~text
detector:
  value = 1 at the target
  value = 0 at the forbidden inputs

spotlight:
  value ≥ 0
  total mass = 1
  mass outside the target region is small

filter:
  low frequencies survive
  high frequencies shrink
~~~

The program can then use:

~~~text
linear algebra          exact linear constraints
linear programming      inequalities on coefficients
symbolic algebra        identities and simplification
sum-of-squares methods  some positivity searches
interval arithmetic     certified numerical bounds
~~~

The solver proposes coefficients. The checker expands the resulting function and verifies each promised property.

If positivity is encoded by writing <code>K=|G|²</code>, the search must also account for the enlarged difference-frequency support of <code>K</code>. Positivity is gained, but bandwidth is spent.

<figure class="fp-figure">
  <p class="fp-figure-title">A bounded Fourier synthesis loop</p>
  {% include diagrams/fourier-automation.svg %}
  <figcaption class="fp-figure-caption">Automation can search a declared family, but a numerical sample is not the same as a proof over every real input.</figcaption>
</figure>

### A small numerical experiment

This program evaluates the modular detector with floating-point complex numbers:

~~~python
from cmath import exp, pi


def fourier_detector(n, q):
    omega = exp(2j * pi / q)
    return sum(omega ** (r * n) for r in range(q)) / q


for q in range(2, 9):
    for n in range(2 * q):
        expected = 1 if n % q == 0 else 0
        value = fourier_detector(n, q)
        assert abs(value - expected) < 1e-10
~~~

This is useful evidence. It checks a finite collection of examples.

It is not, by itself, a proof for every integer <code>n</code> and every <code>q</code>. The proof is the geometric-sum identity, which handles the unbounded claim symbolically.

### A proof-carrying automation loop

A safer program returns more than a picture:

~~~text
candidate coefficients
      +
domain and assumptions
      +
exact identities
      +
error or positivity bounds
      ↓
finite proof certificate
      ↓
independent checker
~~~

The checker should be able to reject:

~~~text
wrong domain
missing normalization
unverified continuous claim
floating-point error mistaken for zero
frequency family too small for the requested shape
~~~

This separates four jobs:

~~~text
finding a candidate  = search
showing a picture    = explanation
deriving properties  = proof
replaying the steps   = checking
~~~

### What automation cannot promise automatically

A solver does not become an oracle merely because it uses Fourier coefficients.

It may find a function that works on sampled points but fails between them.

It may find a positive value at many points without proving positivity on the whole interval.

It may solve a finite optimization problem while the theorem asks about an infinite family.

It may return a floating-point number that is close to zero but not exactly zero.

The safe claim is conditional:

> If the search space is specified and the checker verifies the required analytic properties, automation can produce a proof-carrying helper function for that problem.

## The backward-design worksheet

The teacher gives each child a card.

### The proof goal

What must the helper function do?

~~~text
detect
count
cancel
concentrate
smooth
bound
solve a differential equation
~~~

### The spatial promises

~~~text
nonnegative?
localized?
integral one?
specific zeros?
bounded?
symmetric?
smooth?
~~~

### The frequency promises

~~~text
which frequencies exist?
how loud is each one?
which phases make them align?
which frequencies must disappear?
how quickly should high frequencies decay?
~~~

### The construction move

~~~text
positivity        → square the magnitude, then count the new frequencies
mass one          → normalize
concentration     → align many frequencies
exact cancellation → use a complete cycle
smoothing         → suppress high frequencies
probe one note    → use an orthogonal wave
~~~

### The verification move

~~~text
check the formula
check the domain
check normalization
check convergence or error
check the final theorem bridge
~~~

The helper function is not complete until every promise has a proof.

## Three common traps

### A positive spectrum is not automatically a positive shape

The fact that <code>f̂(ξ)≥0</code> does not, by itself, guarantee <code>f(x)≥0</code>.

If spatial positivity is needed, a safer design is often:

$$
K(x)=\lvert G(x)\rvert^2.
$$

Squaring the magnitude gives a direct reason for <code>K(x)≥0</code>.

In one variable and with finite frequency support, Fejér–Riesz factorization explains why this search form is complete for nonnegative trigonometric polynomials. Outside that setting, it is only a justified construction family, not a universal promise.

### Finite tests are not continuous proofs

Checking a function at one thousand points does not prove a statement about every real input. A continuous proof needs a bound between sample points, a symbolic identity, or another certificate that covers the entire domain.

### The domain changes the Fourier tool

~~~text
finite clock      finite Fourier sums
periodic circle   Fourier series
real line         Fourier transform
heat flow         frequency multiplier plus inverse transform
~~~

The notation may look similar while the theorem changes. Always name the world before using the formula.

## The pocket map

The class compresses the lesson:

~~~text
🎯 proof job
      ↓
🎵 frequency design
      ↓
🔄 Fourier synthesis
      ↓
🌊 helper function
      ↓
🔍 verified properties
      ↓
📜 theorem
~~~

The three central constructions are:

~~~text
exact detector
  waves align on the target
  waves cancel away from it

soft spotlight
  square a wave bundle
  normalize its total mass
  add frequencies to concentrate it

heat filter
  keep slow frequencies
  suppress fast frequencies
  transform back into a smoothing kernel
~~~

The deepest sentence is:

> **Fourier proof design means building a mathematical tool from waves: make the waves agree where strength is wanted, cancel where zero is wanted, weaken the frequencies that must disappear, and verify the resulting function before using it.**

The program can help search.

The picture can help explain.

The certificate can help check.

The theorem still depends on the verified bridge between the helper function and the claim.

## Part II: fewer knobs, smaller search

The next afternoon, the teacher brings a machine with many knobs.

“A Fourier function may have many adjustable coefficients,” I say. “A computer can search them, but it helps to remove choices that the proof does not need.”

Malik asks, “Is removing choices the same as proving?”

“No. Removing choices can make a search smaller. It is safe only when we know that a solution has not been removed.”

That is the second lesson:

> **Reduce the search space, but prove that the reduction is allowed.**

<figure class="fp-figure">
  <p class="fp-figure-title">Fewer knobs, smaller search</p>
  {% include diagrams/fourier-knob-reduction.svg %}
  <figcaption class="fp-figure-caption">Finite frequencies and justified symmetry can turn a huge function search into a small, checkable coefficient problem.</figcaption>
</figure>

### A degree of freedom is a choice

A degree of freedom is one independent choice.

Think of a machine with three knobs:

~~~text
🎛️ knob a
🎛️ knob b
🎛️ knob c
~~~

Start with:

$$
f(x)=a+bx+cx^2.
$$

The knobs control:

~~~text
a   height
b   tilt
c   curve
~~~

Before adding any rules, <code>a</code>, <code>b</code>, and <code>c</code> can be chosen independently. There are three degrees of freedom.

Now require:

$$
f(0)=0.
$$

Since <code>f(0)=a</code>, the rule forces:

$$
a=0.
$$

One knob is locked:

~~~text
before:   🎛️a   🎛️b   🎛️c

after:    🔒a=0  🎛️b   🎛️c
~~~

Add a second rule:

$$
f(1)=1.
$$

Then:

$$
b+c=1.
$$

The two knobs <code>b</code> and <code>c</code> are no longer independent. Choose <code>b</code>, and <code>c=1-b</code> is forced.

The search has changed:

~~~text
3 free choices
      ↓ f(0)=0
2 free choices
      ↓ f(1)=1
1 free choice
~~~

The equations have not yet selected one function. They have made the remaining search smaller.

### Fourier coefficients are knobs

A periodic function may be written formally as:

$$
f(x)=\sum_{k=-\infty}^{\infty}a_ke^{ikx}.
$$

Each <code>a_k</code> controls one frequency.

~~~text
a₋₂   frequency −2
a₋₁   frequency −1
a₀    constant note
a₁    frequency 1
a₂    frequency 2
~~~

An unrestricted Fourier description has infinitely many knobs. A program cannot simply try every real sequence of coefficients.

So begin with a declared finite family:

$$
f_N(x)
=
\sum_{k=-N}^{N}a_ke^{ikx}.
$$

For <code>N=2</code>, this is a five-coefficient search:

$$
f_2(x)
=
a_{-2}e^{-2ix}
a_{-1}e^{-ix}
a_0
a_1e^{ix}
a_2e^{2ix}.
$$

This is called band-limited in this finite sense. The family uses only a limited band of notes.

The reduction is useful, but it has a boundary:

> If the real helper needs frequency <code>7</code>, a search restricted to frequencies <code>0,1,2</code> will not find it.

Failure inside a small family proves only:

~~~text
no candidate was found in this box
~~~

It does not prove:

~~~text
no candidate exists anywhere
~~~

### Real-valued functions pair their notes

The complex Fourier coefficients of a real-valued function obey:

$$
a_{-k}=\overline{a_k}.
$$

The bar means complex conjugation, which reflects a rotating arrow across the real axis.

This pairing removes duplicate choices. The same real function can be written using cosines and sines:

$$
f(x)
=
a_0+
\sum_{k=1}^{N}
\bigl(b_k\cos(kx)+c_k\sin(kx)\bigr).
$$

Now the knobs are real coefficients <code>a_0,b_k,c_k</code>.

### Symmetry removes more knobs

Suppose the desired helper is even:

$$
f(-x)=f(x).
$$

It has mirror symmetry around zero:

~~~text
             /\
          __/  \__
_________/        \_________
       −x          x
~~~

Sine is odd:

$$
\sin(-x)=-\sin(x).
$$

Therefore an even Fourier sum has no sine terms:

$$
f(x)
=
a_0+\sum_{k=1}^{N}b_k\cos(kx).
$$

The reduction ladder is:

~~~text
all functions
      ↓ choose a finite band
finite Fourier sums
      ↓ require real values
sine and cosine sums
      ↓ require even symmetry
cosine sums only
~~~

Fewer knobs mean a smaller search. The reduction is safe only if the theorem’s helper can be replaced by an even helper without losing the required properties.

### Averaging can make symmetry safely

Suppose <code>f</code> is a candidate. Build its mirror-average:

$$
f_{\mathrm{even}}(x)
=
\frac{f(x)+f(-x)}{2}.
$$

Then:

$$
f_{\mathrm{even}}(-x)=f_{\mathrm{even}}(x).
$$

The averaging operation has forced even symmetry.

But a proof obligation remains:

> Do the properties needed by the theorem survive this averaging?

For example, linear equalities often survive averaging. A nonlinear condition may not. A positivity condition does survive if both <code>f(x)</code> and <code>f(-x)</code> are nonnegative, because an average of nonnegative numbers is nonnegative.

This is the difference between:

~~~text
safe reduction:
  prove a solution can be symmetrized

unsafe reduction:
  search symmetric functions because they look convenient
~~~

## A tiny three-knob spotlight

The teacher asks for a function with:

~~~text
✅ height 1 at x = 0
✅ height 0 at x = π
✅ no negative values
✅ only a few frequencies
~~~

Start with:

$$
K(x)=a+b\cos(x)+c\cos(2x).
$$

There are three knobs:

~~~text
🎛️ a
🎛️ b
🎛️ c
~~~

The first condition gives:

$$
K(0)=a+b+c=1.
$$

The second gives:

$$
K(\pi)=a-b+c=0.
$$

Subtract the second equation from the first:

$$
2b=1,
\qquad
b=\frac12.
$$

Then:

$$
a+c=\frac12.
$$

Two equations have reduced three knobs to one free choice. They have not yet proved positivity.

To see the entire remaining family, write:

$$
y=\cos(x),
\qquad -1\le y\le1,
$$

and use <code>cos(2x)=2y²−1</code>. Since <code>b=1/2</code> and <code>a=1/2−c</code>:

$$
K_c(y)
=
(y+1)
\left(\frac12+2c(y-1)\right).
$$

The first factor is nonnegative on <code>[-1,1]</code>. The second factor is affine, so its minimum occurs at an endpoint. Exact endpoint checking gives:

$$
K_c(x)\ge0\text{ for every real }x
\quad\Longleftrightarrow\quad
c\le\frac18.
$$

This exposes an important point: the original conditions do not select a unique spotlight. They select a whole half-line of valid coefficients.

For a falsifier, choose <code>c=1/7</code> and <code>y=−7/8</code>. Then:

$$
K_{1/7}(-7/8)=-\frac{1}{224}<0.
$$

So a candidate just beyond the boundary really does fail between the two required endpoints.

The boundary choice <code>c=1/8</code> has an extra property. It makes <code>K''(π)=0</code>, producing the flattest zero at <code>π</code> within this family. Equivalently, it maximizes <code>c</code> subject to nonnegativity. That additional design rule selects the square:

$$
K(x)
=
\left(\frac{1+\cos(x)}{2}\right)^2.
$$

This immediately gives:

$$
K(x)\ge0.
$$

It also gives:

$$
K(0)=1,
\qquad
K(\pi)=0.
$$

Expand the square:

$$
K(x)
=
\frac{(1+\cos(x))^2}{4}.
$$

Using:

$$
\cos^2(x)=\frac{1+\cos(2x)}{2},
$$

we obtain:

$$
K(x)
=
\frac38+\frac12\cos(x)+\frac18\cos(2x).
$$

So the exact coefficients are:

$$
a=\frac38,
\qquad
b=\frac12,
\qquad
c=\frac18.
$$

The square was more than a pretty formula. It carried positivity inside the construction. The new extremal condition explains why this square was selected from the other valid choices.

## How much did the search shrink?

Imagine each coefficient can take ten trial values.

With six independent coefficients:

$$
10^6=1,000,000
$$

candidates exist.

If symmetry removes three degrees of freedom, only three remain:

$$
10^3=1,000
$$

candidates remain.

~~~text
6 knobs   → 1,000,000 trial combinations
3 knobs   →       1,000 trial combinations
~~~

The search is one thousand times smaller.

This is not a proof that the reduced family contains the answer. It is a proof-engineering benefit conditional on the reduction being sound.

## What programs do

Fourier proof work uses programs at several levels:

~~~text
human:
  chooses the theorem and the meaning

program:
  computes transforms
  searches coefficients
  solves equations
  plots candidates
  estimates or certifies bounds

checker:
  replays exact identities
  accepts or rejects the certificate
~~~

### The Fast Fourier Transform

Suppose a program receives sampled values:

~~~text
[3, 4, 6, 4, 3, 1, 0, 1]
~~~

The Fast Fourier Transform, or FFT, quickly converts those samples into frequency data:

~~~text
sampled shape
      ↓ FFT
frequency strengths
~~~

The FFT is an efficient calculation. It does not by itself prove a theorem about every real input.

### Coefficient search

For a family such as:

$$
K(x)=a_0+a_1\cos(x)+\cdots+a_N\cos(Nx),
$$

a program can search for coefficients satisfying:

~~~text
K(0)=1
K(π)=0
K(x) ≥ 0
small mass away from zero
~~~

Different constraints suggest different tools:

~~~text
linear equations        exact linear algebra
linear inequalities     linear programming
polynomial positivity   symbolic or sum-of-squares methods
continuous bounds       interval arithmetic
large numerical search  optimization
~~~

The solver proposes a candidate. The checker must then verify every property used by the theorem.

### Numerical search is discovery, not automatic proof

A program may report:

~~~text
minimum value ≈ 0.0000003
~~~

That does not automatically prove:

$$
K(x)\ge0
\qquad\text{for every real }x.
$$

The graph may have missed a dip between sample points. Floating-point rounding may have hidden a small negative value. The optimizer may have stopped at a local solution.

The four levels of computer help are:

~~~text
1. exploration
   plots and examples

2. numerical search
   candidate coefficients

3. rigorous numerical certification
   intervals and error bounds

4. formal proof checking
   exact replay of a certificate
~~~

The level must be named. “The computer found it” is not a proof category.

### Interval arithmetic

Ordinary arithmetic may say:

~~~text
the answer is approximately 0.37
~~~

Interval arithmetic says:

$$
x\in[0.369,0.371].
$$

The interval is guaranteed to contain the true value.

To certify <code>K(x)≥0</code> on a whole interval:

~~~text
split the domain
      ↓
bound K on every small piece
      ↓
every lower bound is ≥ 0
      ↓
K is ≥ 0 everywhere
~~~

The certificate is a collection of boxes and verified bounds.

### Exact algebra after numerical discovery

A numerical search may return:

~~~text
a ≈ 0.3750000001
b ≈ 0.4999999998
c ≈ 0.1250000000
~~~

A person may recognize:

$$
a=\frac38,
\qquad
b=\frac12,
\qquad
c=\frac18.
$$

The final proof should use the exact fractions and prove the identity. A decimal guess is a clue, not the certificate.

## The three-seat detector, redesigned by a program

Suppose the program must detect multiples of <code>3</code>. The three residues are:

~~~text
0 → 1
1 → 0
2 → 0
~~~

Let:

$$
\omega=e^{2\pi i/3}.
$$

Search for:

$$
D(n)=a+b\omega^n+c\omega^{2n}.
$$

The desired outputs create the equations:

$$
a+b+c=1,
$$

$$
a+b\omega+c\omega^2=0,
$$

$$
a+b\omega^2+c\omega=0.
$$

The exact solution is:

$$
a=b=c=\frac13.
$$

Therefore:

$$
D(n)
=
\frac13\bigl(1+\omega^n+\omega^{2n}\bigr).
$$

The program solved the coefficient system. Fourier cancellation explains why the solution works for every integer <code>n</code>.

The degree count is:

~~~text
3 coefficient knobs
− 3 independent output conditions
= 0 free knobs
~~~

Enough correct conditions can force a unique helper.

## A program-assisted proof pipeline

The class draws the complete machine:

~~~text
🎯 theorem
      ↓
🧠 semantic design
What kind of helper would force it?
      ↓
✂️ justified reduction
symmetry, finite band, normalization
      ↓
💻 computer search
find promising coefficients
      ↓
🔢 exact recovery
turn decimal patterns into exact values
      ↓
📜 proof
show the helper has the required properties
      ↓
🤖 certification
replay the finite certificate
      ↓
✅ theorem
~~~

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">The boundary of automation</p>
  <p>A program can search a declared family and certify declared obligations. It does not automatically choose the right theorem, justify an unsafe reduction, or turn finite samples into a statement about every real input.</p>
</div>

This is the same separation used in formal methods:

~~~text
search        proposes a candidate
explanation   shows the picture
proof         derives the required facts
checker       replays the public steps
~~~

## A majorant can build an inequality proof

Sometimes the helper should sit above a difficult function.

If:

$$
F(x)\le K(x)
$$

and:

$$
K(x)\le B,
$$

then:

$$
F(x)\le K(x)\le B.
$$

The function <code>K</code> is a majorant, an easy roof over <code>F</code>. A function below <code>F</code> is a minorant.

The computer can search for a Fourier-built roof:

~~~text
hard function F
       ↓ below
easy Fourier roof K
       ↓ below
constant ceiling B
~~~

If the goal asks for the best possible ceiling, the search becomes an extremal problem:

~~~text
valid helper functions
      ↓ optimize
best helper
      ↓
sharp bound
~~~

Finding a good helper is only half of an optimality proof. The proof must also show that no valid helper can do better.

## Convex and nonconvex searches

Some coefficient searches form a convex problem. Child picture:

~~~text
convex bowl:

        \        /
         \      /
          \____/
~~~

In a convex problem, a locally optimal point is globally optimal under the stated assumptions. This can make certification easier.

Other searches have many valleys:

~~~text
\__/\/\____/\__/
~~~

A numerical optimizer may stop in one valley without finding the best one.

So a rigorous report should say:

~~~text
what family was searched
what constraints were enforced
what objective was optimized
whether the solver found a global or local result
how the final candidate was certified
~~~

## Four small exercises

### Build the odd-number lamp

Construct a function that returns <code>1</code> for odd <code>n</code> and <code>0</code> for even <code>n</code>.

Hint:

$$
O(n)=1-E(n)
=
\frac{1-(-1)^n}{2}.
$$

Ask:

~~~text
Why do the waves agree on odd numbers?
Why do they cancel on even numbers?
~~~

### Remove a sine family

Start with a candidate <code>f</code>. Build:

$$
f_{\mathrm{even}}(x)
=
\frac{f(x)+f(-x)}{2}.
$$

Prove that <code>f_even</code> is even. Then list one theorem property that survives averaging and one nonlinear property that might not.

### Classify the three-note spotlights

Start with:

$$
K(x)=a+b\cos(x)+c\cos(2x).
$$

Require:

$$
K(0)=1,
\qquad
K(\pi)=0.
$$

Find the remaining one-parameter family. Prove that it is nonnegative exactly when <code>c≤1/8</code>. Then show that requiring <code>K''(π)=0</code> selects:

$$
K(x)
=
\left(\frac{1+\cos(x)}{2}\right)^2.
$$

Expand it and verify nonnegativity.

### Separate search from proof

Write one sentence for each:

~~~text
What did the program search?
What exact statement did the checker verify?
What theorem bridge still needed a human proof?
~~~

## Part II in one picture

~~~text
huge function space
          ↓ justified constraints
small Fourier family
          ↓ computer search
promising coefficients
          ↓ exact pattern recovery
mathematical candidate
          ↓ independent checker
proof certificate
          ↓ theorem bridge
proved conclusion
~~~

The teacher closes the knob machine.

“Reducing degrees of freedom makes a search smaller,” I say. “It does not make an unjustified assumption true.”

Ana points to the Fourier detector.

“So the safest order is?”

The class answers:

~~~text
name the theorem
choose what the helper must do
reduce only with a reason
search the remaining knobs
recover exact mathematics
check every promise
connect the helper to the theorem
~~~

The final sentence is:

> **A small search can discover a proof function, but only a justified reduction and an independent certificate can turn the discovery into a theorem.**

## Part III: a tiny proof-carrying lab

The class now gives the three-note problem to a small deterministic checker.

The checker does not sample a graph. It receives a rational value of <code>c</code> and verifies four finite obligations:

~~~text
1. substitute b = 1/2 and a = 1/2 − c
2. expand the claimed factorization exactly
3. check K(1) = 1 and K(−1) = 0 in the y-coordinate
4. minimize the remaining affine factor by checking the correct endpoint
~~~

The source is:

~~~text
examples/fourier_function_engineering/verify_three_note_spotlight.py
~~~

Run:

~~~bash
python3 examples/fourier_function_engineering/verify_three_note_spotlight.py
~~~

The self-test includes:

~~~text
c = 1/8    accepted, extremal square
c = 0      accepted, proving nonuniqueness
c = −2     accepted, another valid member
c = 1/7    rejected with the exact witness y = −7/8
~~~

This is a narrow checker, not a general theorem prover. Its authority is deliberately small:

~~~text
search or human proposes c
          ↓
exact checker verifies this declared family
          ↓
the tutorial proves why the finite checks cover every x
~~~

The key bridge is the substitution <code>y=cos(x)</code>. It turns an infinite trigonometric claim into a polynomial claim on the compact interval <code>[-1,1]</code>. The factorization then reduces positivity to one affine endpoint check.

That is Fourier function engineering in miniature:

~~~text
shape requirement
      ↓
frequency family
      ↓
algebraic reparameterization
      ↓
small exact certificate
      ↓
independently checked claim
~~~

The lab does not prove that this spotlight is best for every theorem. It proves exactly which members of this declared three-note family satisfy the stated constraints, and why.

## Further reading

- [On a Fejér–Riesz factorization of generalized trigonometric polynomials](https://arxiv.org/abs/2005.11920) states the classical one-variable factorization and develops a generalized version.
- [Factorization of multivariate positive Laurent polynomials](https://arxiv.org/abs/math/0503133) explains why several variables require a more careful sum-of-squared-magnitudes theory.
