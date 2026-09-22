#!/usr/bin/env python3
"""
ruleprune - interactive wordlist policy filter.

Point it at a wordlist and describe a password policy in plain answers to a
few questions (minimum length, whether an uppercase / lowercase / digit /
special character is required, and so on). It walks the wordlist and writes a
new one containing only the entries that satisfy every rule you set.

Everything you could set with flags is asked interactively, so there is
nothing to memorize. Run it with no arguments to start the questionnaire.
"""

import os
import string
import sys

DEFAULT_SPECIALS = "!@#$%^&*()-_=+[]{};:'\",.<>/?\\|`~ "


def _clear_carriage(text):
    # Wordlists often carry stray CR/LF or surrounding whitespace; strip the
    # line ending but keep the password bytes intact.
    return text.rstrip("\r\n")


class Policy:
    """A set of rules a candidate line must satisfy to be kept."""

    def __init__(self):
        self.min_length = None
        self.max_length = None
        self.require_upper = 0
        self.require_lower = 0
        self.require_digit = 0
        self.require_special = 0
        self.specials = set(DEFAULT_SPECIALS)
        self.min_classes = None  # require at least N of the 4 character classes
        self.reject_non_ascii = False

    def describe(self):
        lines = []
        if self.min_length is not None:
            lines.append(f"  - minimum length: {self.min_length}")
        if self.max_length is not None:
            lines.append(f"  - maximum length: {self.max_length}")
        if self.require_upper:
            lines.append(f"  - uppercase letters required: at least {self.require_upper}")
        if self.require_lower:
            lines.append(f"  - lowercase letters required: at least {self.require_lower}")
        if self.require_digit:
            lines.append(f"  - digits required: at least {self.require_digit}")
        if self.require_special:
            lines.append(f"  - special characters required: at least {self.require_special}")
        if self.min_classes is not None:
            lines.append(f"  - distinct character classes required: at least {self.min_classes}")
        if self.reject_non_ascii:
            lines.append("  - non-ASCII characters: rejected")
        if not lines:
            lines.append("  (no rules set - every entry would pass)")
        return "\n".join(lines)

    def matches(self, word):
        """Return True if `word` satisfies every configured rule."""
        length = len(word)
        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False

        n_upper = n_lower = n_digit = n_special = 0
        for ch in word:
            if ch in string.ascii_uppercase:
                n_upper += 1
            elif ch in string.ascii_lowercase:
                n_lower += 1
            elif ch in string.digits:
                n_digit += 1
            elif ch in self.specials:
                n_special += 1

        if self.reject_non_ascii:
            try:
                word.encode("ascii")
            except UnicodeEncodeError:
                return False

        if n_upper < self.require_upper:
            return False
        if n_lower < self.require_lower:
            return False
        if n_digit < self.require_digit:
            return False
        if n_special < self.require_special:
            return False

        if self.min_classes is not None:
            classes_present = sum(
                1 for count in (n_upper, n_lower, n_digit, n_special) if count > 0
            )
            if classes_present < self.min_classes:
                return False

        return True


# ---------------------------------------------------------------------------
# Interactive prompt helpers
# ---------------------------------------------------------------------------

def ask_text(prompt, default=None, allow_blank=False):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        try:
            raw = input(f"{prompt}{suffix}: ").strip()
        except EOFError:
            raw = ""
        if not raw:
            if default is not None:
                return default
            if allow_blank:
                return ""
            print("  Please enter a value.")
            continue
        return raw


def ask_yes_no(prompt, default=False):
    hint = "Y/n" if default else "y/N"
    while True:
        try:
            raw = input(f"{prompt} [{hint}]: ").strip().lower()
        except EOFError:
            raw = ""
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  Please answer y or n.")


def ask_int(prompt, default=None, minimum=None, maximum=None, allow_blank=False):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        try:
            raw = input(f"{prompt}{suffix}: ").strip()
        except EOFError:
            raw = ""
        if not raw:
            if default is not None:
                return default
            if allow_blank:
                return None
            print("  Please enter a number.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"  Please enter a number >= {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"  Please enter a number <= {maximum}.")
            continue
        return value


# ---------------------------------------------------------------------------
# Building a policy from the questionnaire
# ---------------------------------------------------------------------------

def build_policy():
    print()
    print("Describe the password policy. Press Enter to accept a default or to")
    print("skip a rule you don't care about.")
    print()

    policy = Policy()

    policy.min_length = ask_int(
        "Minimum length (blank for none)", minimum=0, allow_blank=True
    )
    policy.max_length = ask_int(
        "Maximum length (blank for none)", minimum=0, allow_blank=True
    )
    if (
        policy.min_length is not None
        and policy.max_length is not None
        and policy.max_length < policy.min_length
    ):
        print("  Maximum is below minimum; ignoring the maximum.")
        policy.max_length = None

    if ask_yes_no("Require an uppercase letter?", default=True):
        policy.require_upper = ask_int(
            "  How many uppercase letters at minimum", default=1, minimum=1
        )

    if ask_yes_no("Require a lowercase letter?", default=True):
        policy.require_lower = ask_int(
            "  How many lowercase letters at minimum", default=1, minimum=1
        )

    if ask_yes_no("Require a digit?", default=True):
        policy.require_digit = ask_int(
            "  How many digits at minimum", default=1, minimum=1
        )

    if ask_yes_no("Require a special character?", default=True):
        policy.require_special = ask_int(
            "  How many special characters at minimum", default=1, minimum=1
        )
        if ask_yes_no("  Customize which characters count as special?", default=False):
            print(f"  Default special set: {DEFAULT_SPECIALS!r}")
            custom = ask_text(
                "  Enter the exact characters to treat as special", allow_blank=True
            )
            if custom:
                policy.specials = set(custom)

    if ask_yes_no(
        "Require a minimum number of distinct character classes "
        "(upper/lower/digit/special)?",
        default=False,
    ):
        policy.min_classes = ask_int(
            "  How many of the four classes at minimum",
            default=3,
            minimum=1,
            maximum=4,
        )

    policy.reject_non_ascii = ask_yes_no(
        "Reject entries containing non-ASCII characters?", default=False
    )

    return policy


# ---------------------------------------------------------------------------
# Running the filter
# ---------------------------------------------------------------------------

def run_filter(input_path, output_path, policy, keep_duplicates=True):
    total = 0
    kept = 0
    seen = set()

    try:
        infile = open(input_path, "r", encoding="utf-8", errors="surrogateescape")
    except OSError as exc:
        print(f"Could not open input wordlist: {exc}")
        return None

    try:
        outfile = open(output_path, "w", encoding="utf-8", errors="surrogateescape")
    except OSError as exc:
        infile.close()
        print(f"Could not open output file: {exc}")
        return None

    with infile, outfile:
        for line in infile:
            word = _clear_carriage(line)
            if word == "":
                continue
            total += 1
            if not policy.matches(word):
                continue
            if not keep_duplicates:
                if word in seen:
                    continue
                seen.add(word)
            outfile.write(word + "\n")
            kept += 1

    return total, kept


def confirm_overwrite(path):
    if os.path.exists(path):
        return ask_yes_no(f"'{path}' already exists. Overwrite it?", default=False)
    return True


def main():
    print("=" * 60)
    print(" ruleprune - wordlist policy filter")
    print("=" * 60)
    print()
    print("This walks an existing wordlist and writes a new one containing")
    print("only the entries that satisfy a password policy you describe.")

    input_path = ask_text("\nPath to the source wordlist")
    while not os.path.isfile(input_path):
        print(f"  No file found at '{input_path}'.")
        input_path = ask_text("Path to the source wordlist")

    default_out = os.path.splitext(os.path.basename(input_path))[0] + ".pruned.txt"
    output_path = ask_text("Path for the filtered output", default=default_out)
    while not confirm_overwrite(output_path):
        output_path = ask_text("Path for the filtered output", default=default_out)

    dedupe = ask_yes_no("Drop duplicate entries from the output?", default=False)

    policy = build_policy()

    print()
    print("Policy summary:")
    print(policy.describe())
    print()
    if not ask_yes_no("Start filtering with these rules?", default=True):
        print("Aborted. No output written.")
        return 0

    print()
    print("Filtering...")
    result = run_filter(input_path, output_path, policy, keep_duplicates=not dedupe)
    if result is None:
        return 1

    total, kept = result
    removed = total - kept
    print()
    print("Done.")
    print(f"  Read:    {total} entries")
    print(f"  Kept:    {kept} entries")
    print(f"  Removed: {removed} entries")
    if total:
        print(f"  Pass rate: {kept / total * 100:.2f}%")
    print(f"  Output written to: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. No further output written.")
        sys.exit(130)
