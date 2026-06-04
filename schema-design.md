# Schema design checklist

Questions to answer before writing code that handles structured data. The first group
is load-bearing: answer all of them, in order, every time. The second group is
situational: check whether each applies to this project, skip the ones that do not.

## Core questions (always ask, in this order)

1. What are my sources, and what does each actually contain?
   Read the real data, not an idealized version. List the fields each source really
   provides. Messy real samples beat clean imagined ones.

2. What is one record? (the grain)
   Decide what a single record represents. Most important and most expensive to change.
   Test: a record is the smallest thing you assign one decision to and describe in one
   sentence.
   Rule: store at the finest grain you will operate on. Fine to coarse is a filter;
   coarse to fine is a re-parse. Always store fine.

3. What is shared across all records, and what differs by type?
   Find the common "head" fields every record has, and the "tail" fields only some
   types have. This tells you whether you have one shape or a family of shapes.

4. How do I tell the types apart? (the discriminator)
   If records have different tails, add one field naming the type. Makes filtering and
   measuring by type trivial later.

5. What can I fill in deterministically vs what must wait?
   For each field ask: do I actually have this at parse time? If a field can only be
   produced later (by a model, lookup, or calculation), it does not belong in the raw
   schema. Separate the raw record from the enriched result record.

6. What should I refuse to make deterministic?
   If filling a field correctly requires interpreting text that changes with an external
   tool's version or format, do not hardcode it. Capture the raw evidence and let a
   smarter later layer judge it.

7. Keep concerns separate.
   Each layer does one job. Note which layer owns which responsibility and do not let
   them bleed (e.g. the parser captures and routes; it does not judge).

8. Build the simple version first.
   If the "correct" design is confusing you, build the simplest thing that works, run
   it, and let the pain show where elegance is actually needed. Do not abstract ahead
   of a felt need.

## Situational questions (check if they apply, skip if not)

9. Relationships between records.
   Do records reference each other (a host has many findings, an order has many items)?
   If so, decide how they link: nest them inside, or reference by an ID. Skip if your
   records are independent.

10. Identity and uniqueness.
    What makes two records the same one? Is there a natural unique key? What happens if
    you parse the same input twice, do you get duplicates? Skip if dedup does not matter.

11. Required vs optional, and defaults.
    Which fields must be present for a record to be valid, which may be missing, and
    what is a sensible default for the optional ones.

12. Field constraints and validation.
    Beyond the type: allowed ranges (port 1 to 65535), allowed values (kind is one of a
    fixed set), required patterns. Decide what is allowed into each field, not just its
    type.

13. Evolution and versioning.
    Schemas change over time. Will old data still load when the shape changes? A version
    tag on the record (like servicescan/1.0) is how you plan for this. Skip for
    throwaway or short-lived data.

14. Naming and consistency.
    Use consistent field names across records and sources. Pick one term for a concept
    and stick to it. Boring, but it prevents quiet bugs.

## How to use this

Run questions 1 to 8 every time, in order, because each depends on the one before.
Then glance at 9 to 14 and ask "does this project need it?" Most projects need only a
few of the situational ones. The skill is knowing which apply, and that comes from
practice, not from the list.
