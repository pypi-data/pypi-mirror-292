### webdriver-hj3415

#### Introduction 

각 운영체제별로 웹드라이버를 반환하는 프로젝트

---
#### Requirements

selenium>=4.22.0
webdriver-manager>=4.0.1

---
#### API

```python
from webdriver_hj3415 import drivers
drivers.get(browser='chrome', driver_version="127.0", headless=False)
drivers.get(browser='firefox', headless=False)
drivers.get_chrome(driver_version="127", headless=False)
drivers.get_firefox(headless=False)
drivers.get_safari()
drivers.get_edge()
```

---
#### Install

```bash
pip install webdriver-hj3415
```

---
#### Composition

---

