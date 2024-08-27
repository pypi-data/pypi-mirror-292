# 🛡️ Kaspersky TIP API

**[Kaspersky Threat Intelligence Portal](https://opentip.kaspersky.com/)** unofficial API for Python

# ✨ Features
- Search by **hash** (md5, sha1, sha256)
- Search by **IP address**
- Search by **domain**
- Search by **URL**
- Upload **samples**

# 📥 Installation

```
pip install kasperskytip
```

# ▶️ Getting Started

```python
import kasperskytip

ks = kasperskytip.kaspersky_tip()
site = ks.search("google.com")

print(site.is_safe)
>>> True
```

# 📝 Usage

Please, see the usage examples on [readthedocs](https://kaspersky-tip.readthedocs.io/en/latest/)