# ruleprune

An interactive wordlist policy filter.

You hand it a wordlist and describe a password policy by answering a few
questions — minimum length, whether an uppercase / lowercase / digit / special
character is required, and so on. It walks the wordlist and writes a new one
containing only the entries that satisfy every rule.

Yes, you can do most of this with a long `grep -P` one-liner. `ruleprune`
exists so you don't have to remember the regex. Everything is asked
interactively, so there are no flags to look up.

## Requirements

Python 3.6 or newer. No third-party packages.

## Install (run it from anywhere)

```
git clone https://github.com/CypherNova1337/ruleprune.git
cd ruleprune
sh install.sh
```

`install.sh` symlinks the script into a directory on your `PATH`
(`/usr/local/bin` when writable, otherwise `~/.local/bin`) as the command
`ruleprune`. After that, run it from any directory:

```
ruleprune
```

If the installer says its target directory isn't on your `PATH`, add the line
it prints to your shell profile and open a new shell.

You don't have to install it — `python3 ruleprune.py` works too.

## Updating

```
git pull
```

Because the install is a symlink into the repo, pulling the latest version
updates the `ruleprune` command automatically — there's no need to re-run the
installer.

## Usage

```
ruleprune          # if installed
python3 ruleprune.py   # if not
```

At the path prompts you can:

- Use `~/`, `~user/`, and `$VARS` — e.g. `~/Documents/Wordlists/rockyou.txt`
  resolves to your home directory.
- Press **Tab** to complete file and directory names (where your platform
  provides readline).

Then answer the prompts. A typical run:

```
Path to the source wordlist: rockyou.txt
Path for the filtered output [rockyou.pruned.txt]:
Drop duplicate entries from the output? [y/N]: n

Minimum length (blank for none): 12
Maximum length (blank for none):
Require an uppercase letter? [Y/n]: y
  How many uppercase letters at minimum [1]: 1
Require a lowercase letter? [Y/n]: y
  How many lowercase letters at minimum [1]: 1
Require a digit? [Y/n]: y
  How many digits at minimum [1]: 1
Require a special character? [Y/n]: y
  How many special characters at minimum [1]: 1
  Customize which characters count as special? [y/N]: n
Require a minimum number of distinct character classes ...? [y/N]: n
Reject entries containing non-ASCII characters? [y/N]: n

Policy summary:
  - minimum length: 12
  - uppercase letters required: at least 1
  - lowercase letters required: at least 1
  - digits required: at least 1
  - special characters required: at least 1

Start filtering with these rules? [Y/n]: y
```

At the end it reports how many entries were read, how many were kept, how many
were removed, the pass rate, and where the output was written.

## What the rules mean

| Prompt                        | Effect                                                        |
|-------------------------------|---------------------------------------------------------------|
| Minimum / maximum length      | Entry length must fall within the range (blank = no bound).   |
| Require uppercase             | Must contain at least N of `A-Z`.                             |
| Require lowercase             | Must contain at least N of `a-z`.                             |
| Require digit                 | Must contain at least N of `0-9`.                             |
| Require special character     | Must contain at least N characters from the special set.      |
| Customize special set         | Replace the default punctuation set with your own characters. |
| Distinct character classes    | Must draw from at least N of the four classes above.          |
| Reject non-ASCII              | Drop any entry containing a byte outside ASCII.               |

The default special set is:

```
!@#$%^&*()-_=+[]{};:'",.<>/?\|`~ (space)
```

## Notes

- The source wordlist is never modified; results go to a separate file.
- If the output file already exists you are asked before it is overwritten.
- Blank lines in the source are skipped and not counted.
- Reading and writing use `surrogateescape`, so odd bytes in a wordlist pass
  through instead of crashing the run.
