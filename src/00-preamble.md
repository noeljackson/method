# Noel Method

The Noel Method is a compact methodology for delegated work: work in which
direction, evaluation, research, and execution may be performed by different
actors, or by one actor wearing explicitly different hats.

It applies wherever a result must be trusted rather than merely produced.

## Normative language

**MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe
requirements.

- `C1` through `C8` are the non-waivable hard core.
- A profile may tighten the core or specialize behavior the core leaves open.
  Weakening a core rule creates a labeled nonconforming fork.
- An authorized direction-setter may change a work contract. Record the
  decision, reason, and affected evidence before relying on it.

## Loading the method

Load `BASE.md` and the accepted ProjectProfile for every task. Merge
`program`, `experiment`, and `secrets` context flags from the caller, accepted
profile, and model by boolean OR, then load the enabled protocol modules. A
model may enable a flag but cannot clear one supplied by the caller or profile.
Flags select context; they do not grant authority.

If the profile is missing, draft, invalid, or cannot be independently
verified, load the ProjectProfile bootstrap and remain read-only.

Use the least ceremony that preserves trust. A bounded, reversible direct task
may use its prompt as a contract. Substantive or consequential work uses the
public contracts in this method.

## Everyday use

For a direct task, state only the outcome, relevant constraints, evidence or
source of truth, and next action. Do not create a formal WorkContract unless
the work is substantive: it changes external or irreversible state, handles
sensitive material, crosses meaningful handoff or authority boundaries, or has
material uncertainty about success.

An accepted ProjectProfile is workspace setup for its stated scope and exact
revision, not paperwork recreated for each task. Reaccept it only when that
scope, revision, or its independent authority changes.
