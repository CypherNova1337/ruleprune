# ruleprune

Cuts a wordlist down to only the passwords a given policy would actually allow.

![license](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![python](https://img.shields.io/badge/python-3.6%2B-3776AB?style=flat-square)

## What it does

You're cracking hashes from a target whose password policy requires at least 10
characters, one uppercase letter and one digit. Your wordlist has 14 million
entries, and most of them are things like `password`, `dragon` and `letmein`.

None of those can possibly be right. The policy forbade them. Every one you try
is a guess you knew would fail before you made it.

ruleprune removes them. Point it at a wordlist, answer a few questions about the
policy, and it writes a new list containing only the entries that satisfy every
rule. Same attack, much smaller haystack.

It's the kind of thing you could do with a long `grep -P` one-liner, if you
felt like getting the regex right at two in the morning.

## Why you'd use it

- **Interactive** — it asks about the policy in plain questions, so there are no
  flags to remember and no regex to get wrong.
- **Rules can require more than one** of a character class, for policies that
  demand two digits rather than one.
- **Standard library only.** No pip install, nothing to break.

## Install

```bash
git clone https://github.com/CypherNova1337/ruleprune
cd ruleprune
./install.sh
```

`install.sh` puts it on your `PATH` as `ruleprune`. You can also just run
`python3 ruleprune.py` from the checkout.

Needs Python 3.6 or newer.

## Usage

```bash
ruleprune
```

It asks for the input wordlist, then walks through the policy:

```
Minimum length: 10
Maximum length: [blank for none]
Require an uppercase letter? [Y/n]
  How many? 1
Require a lowercase letter? [Y/n]
Require a digit? [Y/n]
Require a special character? [Y/n]
```

Then it writes the filtered list and tells you how many entries survived.

Tab completion works on the file path prompts, so you don't have to type a full
path from memory.

## Good to know

- **Match the policy exactly, then stop.** If you guess stricter than the real
  policy you will prune away the correct password and never know.
- **Policies are often not enforced retroactively.** An account created before
  the rule changed can still hold a password the current policy would reject, so
  keep the original list around.
- **Check the surviving count before you commit to it.** A policy that looks
  reasonable can cut a 14-million-entry list to a few thousand, which usually
  means a rule was entered wrong.
- **It filters, it doesn't mutate.** If you want `Password1!` generated from
  `password`, that's a rule engine's job — run this afterwards.

## Authorised use

Cracking hashes is only legal against systems you own or have written permission
to test.

## License

MIT — see [LICENSE](LICENSE).
