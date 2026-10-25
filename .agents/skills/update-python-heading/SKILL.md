---
name: update-python-heading
description: Add or update the title, author, GPT model attribution, and update date in Python file headings in MASSMa-codes when the programmer requests a heading update or invokes $update-python-heading. Do not apply during ordinary Python edits without a heading-update request.
---

# Update Python Heading

Update only the requested `.py` files in the `MASSMa-codes` repository. Resolve
targets from the request and conversation; ask for clarification if ambiguous.
Do not expand a single-file request to every Python file in the repository.

## Heading format

Use a module docstring with this layout, replacing the title, model, and date:

```python
"""
Short descriptive title

Author: Paolo Rossi
Co-author: GPT (<actual model name>)
Date: YYYY-MM-DD
"""
```

- Use the programmer's title when supplied; otherwise infer a concise English
  title from the program's purpose.
- Set the author to `Paolo Rossi`.
- Identify the actual model from reliable active-session context. Use its
  available name, without inventing a version or copying this skill's example
  placeholder. If no model identity is available, ask for it before editing.
- Use the current calendar date in `Europe/Rome`, formatted `YYYY-MM-DD`.
  This is the date of the requested heading update, not the creation date.
  Obtain it at invocation time, for example with
  `datetime.now(ZoneInfo("Europe/Rome")).date().isoformat()` in Python.

## Editing rules

- Read each target before editing. Update its existing heading in place,
  whether it is a module docstring or a leading comment heading; do not leave
  a second copy of the title or managed metadata.
- If there is no heading, add the docstring before imports or executable code,
  after any shebang and encoding declaration. Keep those declarations in their
  valid positions and any `from __future__` imports after the module docstring.
- Preserve unrelated documentation and attribution. If a module docstring also
  contains explanatory text, retain that text below the managed heading fields
  within the same docstring. Preserve license or copyright notices separately.
  If an existing heading attributes other contributors, retain their credit
  separately from the managed author and GPT co-author fields.
- Preserve executable code, file encoding, byte-order mark if present, and
  existing line endings. Do not reformat the rest of the file or run the program
  merely to update its heading.

## Verification and response

- Inspect the diff: only the requested heading and any necessary placement of
  preserved heading text should change.
- Check Python syntax without executing the program or writing bytecode. Where
  feasible, compare ASTs before and after, excluding only the leading module
  docstring, to confirm executable code is unchanged. If the original source
  cannot be parsed, report that limitation without fixing unrelated code.
- Confirm that applying the same update again on the same day would leave one
  heading with the same content, rather than duplicate or accumulate metadata.
- Report the files updated and the model attribution and date used.
