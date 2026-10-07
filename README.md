# BLUFF

**AI-adjudicated claims with decentralized consensus on GenLayer.**

BLUFF is a reusable Intelligent Contract for games and applications where a participant makes a subjective claim, another participant challenges it, and GenLayer validators determine whether the claim is valid under explicit scenario rules.

Instead of trusting a game server, administrator, or single AI model, BLUFF turns subjective rule enforcement into a consensus-backed state transition.

## Core Idea

Traditional smart contracts work well when correctness can be expressed deterministically.

But many games and applications contain questions such as:

> "Is this action actually possible under the rules?"

Those questions may require semantic reasoning rather than simple arithmetic or fixed conditions.

BLUFF provides the following lifecycle:

```text
Create Game
    ↓
Submit Claim
    ↓
Challenge Claim
    ↓
GenLayer AI Adjudication
    ↓
Validator Consensus
    ↓
VALID / INVALID
    ↓
Resolved State
```

The scenario and rules define the adjudication boundary. A claimant cannot simply invent capabilities, objects, permissions, or facts that do not exist in that environment.

## Why GenLayer?

BLUFF needs more than a conventional deterministic smart contract.

A claim may be grammatically different while expressing the same action, and determining whether that action is plausible can require contextual reasoning.

GenLayer allows BLUFF to use nondeterministic AI inference inside an Intelligent Contract while validators establish consensus over the result.

The contract therefore combines:

- deterministic game state
- explicit rules
- AI reasoning
- GenLayer validator consensus
- persistent consensus-backed outcomes

## Contract Lifecycle

A BLUFF game moves through four states:

```text
OPEN
  ↓
CLAIMED
  ↓
CHALLENGED
  ↓
RESOLVED
```

### 1. Create

A creator provides:

- unique game ID
- scenario
- explicit rules

The game enters `OPEN`.

### 2. Claim

A player submits an action or claim.

The game enters `CLAIMED`.

### 3. Challenge

Another address challenges the claim.

The claimant cannot challenge their own claim.

The game enters `CHALLENGED`.

### 4. Resolve

`resolve_game` asks GenLayer validators to adjudicate the claim against the scenario and rules.

The canonical consensus result is:

```text
VALID
```

or:

```text
INVALID
```

After consensus, the game enters `RESOLVED`.

## Adjudication Rules

A claim is considered `VALID` only when it:

1. obeys every explicit rule;
2. is reasonably possible within the scenario;
3. does not invent essential objects, powers, facts, permissions, or capabilities that are not provided by the scenario; and
4. plausibly achieves what the player claims.

Otherwise the claim is `INVALID`.

## Consensus Design

An important design principle in BLUFF is keeping the value used for validator equality small and canonical.

The AI adjudicator returns only:

```json
{
  "verdict": "VALID"
}
```

or:

```json
{
  "verdict": "INVALID"
}
```

The value passed through GenLayer's strict equality principle is therefore only the normalized verdict:

```text
VALID | INVALID
```

Human-readable reasoning is generated deterministically after consensus.

This avoids requiring validators to produce identical free-form natural-language explanations in order to agree on the same semantic decision.

## V1 → V2 Consensus Improvement

An earlier implementation returned both the verdict and free-form AI reasoning inside the value evaluated by strict equality.

Different validators could agree that a claim was invalid while expressing their reasoning differently. That unnecessarily enlarged the nondeterministic consensus surface and could result in an `UNDETERMINED` transaction.

V2 changed the architecture:

```text
V1

AI
 ↓
{ verdict, free-form reasoning }
 ↓
strict_eq
```

became:

```text
V2

AI
 ↓
canonical verdict
 ↓
strict_eq
 ↓
deterministic explanation
```

The V2 design was subsequently validated through a complete live GenLayer lifecycle.

## Live Deployment

BLUFF V2 is deployed on **GenLayer Studio Devnet**.

```text
Contract
0x4f044fe38ac4d5E01CaCcB70Cd81069BDb94b070
```

Chain ID:

```text
61997
```

## Verified Live Example

Game:

```text
submission-demo-v2-001
```

Scenario:

> You are locked inside a room. The room contains a wooden table, a chair, a locked door, and a key lying on the table.

Rules:

> You may use only objects explicitly present in the room. You cannot break the door or invent additional tools.

Submitted claim:

> I use a crowbar to force open the locked door.

The crowbar does not exist in the scenario and the rules explicitly prohibit inventing additional tools.

The claim was challenged and submitted to GenLayer adjudication.

Final persisted state:

```text
status:    RESOLVED
verdict:   INVALID
reasoning: Claim rejected by GenLayer validator consensus.
```

Resolution transaction:

```text
0xd674fc382bc78e7896200a46d51942468e217b971593f9feac95cb599b05dd25
```

Consensus result:

```text
MAJORITY_AGREE
ACCEPTED
```

This demonstrates the complete lifecycle:

```text
CREATE
  ↓
CLAIM
  ↓
CHALLENGE
  ↓
AI ADJUDICATION
  ↓
GENLAYER CONSENSUS
  ↓
INVALID
  ↓
RESOLVED
```

## Intelligent Contract

The production contract is:

```text
contracts/bluff.py
```

### Write Methods

#### `create_game`

Creates a new scenario and rule set.

#### `submit_claim`

Submits a player's claim to an open game.

#### `challenge_claim`

Challenges an existing claim.

#### `resolve_game`

Runs GenLayer AI adjudication and resolves the challenged game through validator consensus.

### Read Methods

#### `get_game`

Returns a specific game's complete state.

#### `get_games`

Returns stored games.

## Project Structure

```text
contracts/
  bluff.py                 # BLUFF V2 Intelligent Contract

tests/
  direct/
    test_bluff.py          # BLUFF direct-mode tests
    conftest.py            # GenVM v0.6 test compatibility setup

gltest.config.yaml
pyproject.toml
requirements.txt
README.md
LICENSE
```

The repository originates from the GenLayer project boilerplate, so additional boilerplate examples and tooling may also remain in the repository.

## Requirements

- Python 3.12+
- GenLayer CLI
- GenLayer test tooling
- GenVM linter

Create a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Testing

BLUFF includes direct-mode contract tests.

Run:

```bash
.venv/bin/python -m pytest tests/direct/test_bluff.py -q
```

Current verified result:

```text
8 passed
```

The tests cover the core contract lifecycle and validation behavior.

## Linting

Run:

```bash
.venv/bin/genvm-lint contracts/bluff.py
```

Current verified result:

```text
Lint passed (3 checks)
```

## Reading the Deployed Game

Using the GenLayer CLI:

```bash
genlayer call \
  0x4f044fe38ac4d5E01CaCcB70Cd81069BDb94b070 \
  get_game \
  --args "submission-demo-v2-001"
```

The verified deployed game returns:

```text
status: RESOLVED
verdict: INVALID
reasoning: Claim rejected by GenLayer validator consensus.
```

## What BLUFF Demonstrates

BLUFF is intentionally small at the contract layer.

Its purpose is not to encode one particular game. It demonstrates a reusable adjudication primitive:

```text
Scenario
+ Rules
+ Claim
+ Challenge
+ AI Reasoning
+ Validator Consensus
= Verified Outcome
```

That primitive can be extended to bluffing games, strategy games, role-playing environments, disputes, simulations, agent interactions, and other applications where correctness depends on contextual reasoning.

## Status

- Intelligent Contract implemented
- GenVM lint passing
- 8 direct tests passing
- deployed to GenLayer Studio Devnet
- live create flow verified
- live claim flow verified
- live challenge flow verified
- live AI adjudication verified
- validator consensus verified
- persisted `RESOLVED / INVALID` state verified

## License

MIT. See [LICENSE](LICENSE).
