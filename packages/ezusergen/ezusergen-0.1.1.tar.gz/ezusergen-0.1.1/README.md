# Usergen

`ezusergen` is a simple Python package that generates usernames by combining random words and a random number.

## Installation

```bash
pip install ezusergen
```

```python
#Usage
import ezusergen as gen

username = gen.generate(7) # 7 = word length, default (if left blank) = 7
print(username)  # Example: SeedmanWelding532
```
