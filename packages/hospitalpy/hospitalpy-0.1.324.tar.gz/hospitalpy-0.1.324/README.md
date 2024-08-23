This is the temporary landing page for _hospitalpy_.

## What is _hospitalpy_?

_hospitalpy_ provides natural language processing tools to global health researchers. It uses a combination of machine learning and rule-based methods to extract information from unstructured text data. It is written in Python and R, but an R distribution is not required to use the package nor is a standalone R package available.

## What can _hospitalpy_ do?

1. Parse EMS narratives.

### Quicksart

```python

from hospitalpy import Tokenizer as tk

aString = "RTA ICH GCS13"
tokens = tk.Tokenizer(aString)
print(tokens)

```

