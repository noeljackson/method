# Coding Defaults

Software defaults for the Kernel's smallest cohesive deliverable, nearest
guard, and reported limitations. They specialize existing rules, add no hard
requirement, and yield to the request and canonical project instructions.
Adapted from the MIT-licensed Ponytail skill.

## Read, then choose the smallest sufficient change

Read the task and trace the code it touches before choosing. Then stop at the
first option that holds:

1. The change is unnecessary for the present need; say so in one line.
2. Code already in the project covers it; reuse it.
3. The language's standard library covers it.
4. A native platform feature covers it, such as a form control, stylesheet
   rule, or database constraint.
5. An installed dependency covers it. Add a dependency only when a few lines
   cannot do the job.
6. Otherwise, write the minimum code that works.

Prefer deletion to addition and boring code to clever code. Add no interface
with one implementation, factory with one product, configuration for a value
that never changes, or scaffolding for a future need. When two options are the
same size, take the one that is correct on edge cases.

## Never simplify away

Keep requested behavior, validation at trust boundaries, error handling that
prevents data loss, security measures, and accessibility basics. When the
requester insists on the fuller version, build it.

## Repair the shared cause

A report names one symptom. Before editing, find every caller of the code
you will change. Fix the shared path once, then check its other callers rather
than guarding only the reported one.

## Leave one check

Nontrivial new logic, such as a branch, loop, parser, or money or security
path, leaves the smallest runnable check that fails if it breaks. Trivial
one-line changes need none.

## Name deliberate shortcuts

Mark a deliberate simplification with a known ceiling, such as a global lock
or quadratic scan, with a short comment naming the ceiling and its upgrade
path. Report it with the limitations.

## Keep the report short

Lead with the change. Then state, in a few lines, what was skipped and when to
add it. Requested explanations remain complete.
