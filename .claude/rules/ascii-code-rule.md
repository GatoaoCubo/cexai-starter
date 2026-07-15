# Rule: ASCII-Only Executable Code

> Enforced since 2026-04-06. Pre-commit hook + sanitizer + CI gate.

## The Rule

**All executable code MUST be ASCII-only (0x00-0x7F).**

Applies to: `.py`, `.ps1`, `.sh`, `.cmd`, `.bat`

## Allowed Exceptions

- `.ps1` files MAY have a UTF-8 BOM (U+FEFF) at byte position 0 -- PowerShell needs this.
- `.py` files MAY use `\uXXXX` escape sequences in string literals when runtime values must be non-ASCII (e.g., accent-stripping maps, i18n regex). Source bytes stay ASCII; Python interprets escapes at runtime.

## Why

1. Python 3 source reads UTF-8 fine, but `print()` uses the terminal codec
2. Windows terminal defaults to cp1252 (NOT UTF-8)
3. Any non-ASCII in print/log output = `UnicodeEncodeError` crash
4. PowerShell without BOM reads scripts as ANSI = parse failure
5. Silent failures: code "works" in VS Code (UTF-8) but crashes in production terminal

## Replacement Table

| Non-ASCII | ASCII Replacement |
|-----------|-------------------|
| Em-dash (U+2014) | `--` |
| En-dash (U+2013) | `-` |
| Smart quotes | Straight quotes `"` `'` |
| Box drawing (U+2500-257F) | `= - + \|` |
| Arrows (U+2190-21FF) | `->` `<-` `^` `v` |
| Check mark (U+2705) | `[OK]` |
| Cross mark (U+274C) | `[FAIL]` |
| Warning (U+26A0) | `[WARN]` |
| Emoji (misc) | `[!!]` `[>>]` `[i]` `[$]` |
| Accented (display) | Unaccented: `missao`, `visao`, `acao` |
| Accented (functional) | Unicode escape: `\u00e3`, `\u00e7` |

## Where Non-ASCII IS Allowed

- `.md` content files (KCs, handoffs, docs) -- humans read these
- `.yaml` data values (brand config, descriptions) -- data, not code
- User-facing templates with `{{BRAND_*}}` placeholders
- **Narration / TTS input / phonetic scripts / subtitles / ANY media text** -- these are
  NOT code. They MUST keep full PT-BR diacritics.

## CRITICAL: never strip accents from media/TTS text (added 2026-06-09)

The ASCII-only rule above is for **EXECUTABLE CODE ONLY** (`.py/.ps1/.sh/.cmd/.bat`).
Narration scripts, the phonetic TTS-input, and subtitles MUST keep full PT-BR accents.
Stripping them makes the founder-voice TTS **mispronounce** (reads flat, "sem acento").
This regression shipped once (m01 course rebuild 2026-06-09: phonetic.md had 0 accents
vs the source's 364 -> garbled audio, caught only by the founder's ear).

**Mandatory pre-TTS gate** (run before ANY media TTS, exit 1 = stripped):
```
python _tools/cex_accent_guard.py <narration_or_phonetic.md>
python _tools/cex_accent_guard.py <phonetic.md> --source <narration.md>   # compare mode
```
When writing N07 handoffs that embed narration, KEEP the accents in the embedded text --
do NOT ASCII-fy narration the way you would code. Phonetic prep RESPELLS specific foreign
tokens (Git->guiti) but NEVER strips the Portuguese diacritics.

## Enforcement (3 layers)

1. **Pre-commit hook**: `cex_hooks.py pre-commit` rejects staged code with non-ASCII
2. **Sanitizer**: `python _tools/cex_sanitize.py --check --scope _tools/` (exit 1 = dirty)
3. **Fix tool**: `python _tools/cex_sanitize.py --fix --scope _tools/` auto-replaces all

## For LLM Builders

When generating `.py` or `.ps1` code:
- Never use emoji in print statements
- Never use em-dash in comments or strings
- Never use accented characters in variable names, comments, or output
- For functional i18n strings, use `\uXXXX` escapes (e.g., `"\u00e3"` not the literal char)
- Use `[OK]`, `[FAIL]`, `[WARN]` tags instead of emoji status indicators
