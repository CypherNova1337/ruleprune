# ruleprune

An interactive wordlist policy filter.

Point it at a wordlist, answer a few questions about a password policy —
minimum length, whether an uppercase / lowercase / digit / special character is
required, and so on — and it writes a new wordlist containing only the entries
that satisfy every rule. Same idea as a long `grep -P` one-liner, without
having to remember the regex.

## Requirements

Python 3.6 or newer. Standard library only — no third-party packages.

## Install

```
git clone https://github.com/CypherNova1337/ruleprune.git
cd ruleprune
sh install.sh
```

`install.sh` links the script onto your `PATH` as `ruleprune`, so you can run
it from any directory. (You can also just run `python3 ruleprune.py`.)

## Usage

```
ruleprune
```

Then answer the prompts:

```
Path to the source wordlist: ~/Documents/Wordlists/rockyou.txt
Path for the filtered output [rockyou.pruned.txt]:
Drop duplicate entries from the output? [y/N]: n

Minimum length (blank for none): 12
Maximum length (blank for none):
Require an uppercase letter? [Y/n]: y
Require a lowercase letter? [Y/n]: y
Require a digit? [Y/n]: y
Require a special character? [Y/n]: y
```

At the end it reports how many entries were read, kept, and removed, the pass
rate, and where the output was written. The source wordlist is never modified.

At the path prompts you can use `~/` and `$VARS`, and press **Tab** to complete
file and directory names.

## Rules

| Prompt                      | Effect                                                   |
|-----------------------------|----------------------------------------------------------|
| Minimum / maximum length    | Length must fall within the range (blank = no bound).    |
| Require uppercase           | At least N characters from `A-Z`.                        |
| Require lowercase           | At least N characters from `a-z`.                        |
| Require digit               | At least N characters from `0-9`.                        |
| Require special character   | At least N from the special set (customizable).          |
| Distinct character classes  | Must draw from at least N of the four classes above.     |
| Reject non-ASCII            | Drop any entry containing a non-ASCII character.         |

Default special set:

```
!@#$%^&*()-_=+[]{};:'",.<>/?\|`~ (space)
```
