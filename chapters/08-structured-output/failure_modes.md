# Semantic failure modes

One line per rejection, written by you, as you run the trials. This file starts
almost empty on purpose. The entries are your observations, and nobody can
write them for you.

It is also the regression set Chapter 9's silent-failure detector earns its reps
against, so keep it honest and keep it growing.

## What goes in here

A rejection means the model produced something the schema accepted and the
validator refused. That gap, shape-valid and meaning-wrong, is the whole subject
of Domain 4 and Domain 5. Note what the model did, not just which assertion
fired.

The book's own example of the format, from ch08:234:

> Trial 7: model invented a payment term not in the document

## The trials

| Sample | Rejected? | Failure mode |
|---|---|---|
| 01-saas-subscription | | |
| 02-consulting-retainer | | |
| 03-warehouse-lease | | |
| 04-data-processing | | |
| 05-equipment-supply | | |
| 06-content-licence | | |
| 07-employment-fixed | | |
| 08-joint-development | | |
| 09-distribution | | |
| 10-maintenance | | |
| 11-nda-no-duration | | |
| 12-referral-no-duration | | |
| 13-sponsorship-vague-term | | |
| 14-single-party | | |
| 15-short-party-name | | |
| 16-multi-currency | | |
| 17-milestone-payments | | |
| 18-evergreen | | |
| 19-revshare | | |
| 20-future-dated | | |

## What the samples were built to do

This is a fact about the fixtures, not a result. Nobody has run these against
Claude to see what actually comes back. That is your run, on your key.

Fifteen of the twenty are ordinary contracts with a clean duration, two or more
properly-named parties, and an unambiguous governing law. Five were written to
put pressure somewhere specific:

- **11-nda-no-duration** and **12-referral-no-duration** have termination
  clauses with no duration unit at all ("upon written notice", "at will").
  `must_mention_duration` should fire, unless the model helpfully invents a
  notice period that is not in the document, which is a more interesting
  failure and belongs in the table above.
- **13-sponsorship-vague-term** ends "when the parties agree it has run its
  course." Same trap, softer.
- **14-single-party** is a one-party undertaking, not a two-party contract.
  `at_least_two_parties` should fire, unless the model pads the list to two by
  naming the subsidiaries, which is exactly the hallucination the validator
  exists to catch.
- **15-short-party-name** has a two-character party, "IQ", which
  `parties_are_named_entities` rejects at `len(p) >= 3`. This one is worth
  arguing with: the party name is real and the rule is wrong. A validator that
  fires on a correct extraction is a false alarm, and a validator you cannot
  trust gets switched off. Write down what you would change.
- **20-future-dated** has an effective date in 2036. Nothing in the Chapter 8
  validators catches that; Chapter 9's `must_be_within_decade` does. Note
  whether it slips through here, because that is the point of Chapter 9.

A run where none of the five gets rejected is not a clean bill of health. It
means either the model is smoothing over the gaps or your assertions are too
loose. Both are worth a line in the table.
