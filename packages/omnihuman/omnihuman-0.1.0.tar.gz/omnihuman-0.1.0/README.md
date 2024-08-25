# OmniHuman

AI model that understands text and humanoids.

<div align="center">

[![python](https://img.shields.io/pypi/pyversions/omnihuman?logo=python)](https://pypi.org/project/omnihuman/)
[![PyPi](https://img.shields.io/pypi/v/omnihuman?logo=pypi)](https://pypi.org/project/omnihuman/)
[![Documentation Status](https://readthedocs.org/projects/omnihuman/badge/?version=latest)](https://omnihuman.readthedocs.io/en/latest/?badge=latest)

[![GitHub Repo stars](https://img.shields.io/github/stars/mdsrqbl/omnihuman?logo=github)](https://github.com/mdsrqbl/omnihuman/stargazers)
[![Downloads](https://img.shields.io/pepy/dt/omnihuman?color=purple&logoColor=white&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iODAwIiBmaWxsPSJub25lIiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxwYXRoIGZpbGw9IiMwMDAiIGZpbGwtcnVsZT0iZXZlbm9kZCIgZD0iTTkuMiAyLjhjLS4yLjMtLjIuOC0uMiAxLjZWMTFINy44Yy0uOSAwLTEuMyAwLTEuNS4yYS44LjggMCAwIDAtLjMuNmMwIC4zLjMuNiAxIDEuMmw0LjEgNC40LjcuNmEuNy43IDAgMCAwIC40IDBsLjctLjZMMTcgMTNjLjYtLjYuOS0xIC45LTEuMmEuOC44IDAgMCAwLS4zLS42Yy0uMi0uMi0uNi0uMi0xLjUtLjJIMTVWNC40YzAtLjggMC0xLjMtLjItMS42YTEuNSAxLjUgMCAwIDAtLjYtLjZjLS4zLS4yLS44LS4yLTEuNi0uMmgtMS4yYy0uOCAwLTEuMyAwLTEuNi4yYTEuNSAxLjUgMCAwIDAtLjYuNnpNNSAyMWExIDEgMCAwIDAgMSAxaDEyYTEgMSAwIDEgMCAwLTJINmExIDEgMCAwIDAtMSAxeiIgY2xpcC1ydWxlPSJldmVub2RkIi8+PC9zdmc+)](https://pepy.tech/projects/omnihuman/)<br>

| **Support Us** ❤️ | [![PayPal](https://img.shields.io/badge/PayPal-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=7SNGNSKUQXQW2) |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |

</div>

---

1. [OmniHuman](#omnihuman)
   1. [Installation](#installation)
   2. [Usage](#usage)
   3. [Citation \& License](#citation--license)

## Installation

```bash
pip install omnihuman
```

or install editable from source

```bash
git clone https://github.com/mdsrqbl/omnihuman.git
cd omnihuman
pip install -e .
```

## Usage

```python
import omnihuman
import numpy as np
from PIL import Image

text = "Raise both hands and clap overhead."
image = Image.open("person.jpg")
image = [np.array(image)]

# model = omnihuman.OmniHuman()
# frames = model.video_generation(text, image)

Image.fromarray(frames[-1]).show()
```

Full documentation is available at [omnihuman.readTheDocs.io](https://omnihuman.readthedocs.io/en/latest/).

## Citation & License

```bibtex
@misc{mdsr2024omnihuman,
  author = {Mudassar Iqbal},
  title = {OmniHuman: AI model that understands text and humanoids.},
  year = {2024},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/mdsrqbl/omnihuman}}
}
```

This project is licensed under Apache License 2.0 - see the [LICENSE](<[git](https://github.com/mdsrqbl/omnihuman/blob/main/LICENSE)>) file for details.

You are permitted to use the library & models, create modified versions, or incorporate pieces of the code into your own work. Your product or research, whether commercial or non-commercial, must provide appropriate credit to the original author(s) by citing this repository & research papers.

Stay tuned for research papers!
