# 💅 BeautyCenter

> Desktop appointment manager for beauty & wellness centers — powered by Python + Qt.

---

### 📊 Status & Metrics

[![Build](https://github.com/Fede22dev/BeautyCenter/actions/workflows/build-and-release.yml/badge.svg)](https://github.com/Fede22dev/BeautyCenter/actions/workflows/build-and-release.yml)
[![Pytest](https://github.com/Fede22dev/BeautyCenter/actions/workflows/pytest.yml/badge.svg)](https://github.com/Fede22dev/BeautyCenter/actions/workflows/pytest.yml)
[![Security Scan](https://github.com/Fede22dev/BeautyCenter/actions/workflows/bandit.yml/badge.svg)](https://github.com/Fede22dev/BeautyCenter/actions/workflows/bandit.yml)
[![Lint Check](https://github.com/Fede22dev/BeautyCenter/actions/workflows/pylint.yml/badge.svg)](https://github.com/Fede22dev/BeautyCenter/actions/workflows/pylint.yml)

[![License](https://img.shields.io/github/license/Fede22dev/BeautyCenter)](./LICENSE)
[![Wakatime](https://wakatime.com/badge/user/4c30271a-c306-4489-9e2a-7b78bf7ef8cf/project/d295b96d-f86a-46b6-9f69-dc035a28f72e.svg)](https://wakatime.com/badge/user/4c30271a-c306-4489-9e2a-7b78bf7ef8cf/project/d295b96d-f86a-46b6-9f69-dc035a28f72e)
[![Last Commit](https://img.shields.io/github/last-commit/Fede22dev/BeautyCenter)](https://github.com/Fede22dev/BeautyCenter/commits)

---

### 🧰 Tech Stack

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![PySide6](https://img.shields.io/badge/Qt-PySide6-6f42c1.svg)](https://doc.qt.io/qtforpython/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![Supabase](https://img.shields.io/badge/Backend-Supabase-3ECF8E.svg?logo=supabase&logoColor=white)](https://supabase.com/)

---

## ✨ What is BeautyCenter?

**BeautyCenter** is a sleek and modular desktop application built in **Python** with **Qt (PySide6)**.  
It helps beauty and wellness centers manage:

- 🧍‍♀️ Clients
- 📅 Appointments
- 💆‍♀️ Treatments
- ⚙️ Settings and business logic

> 🧠 Designed for maintainability, offline-first usage, and cloud sync in future releases.

---

## 🖼️ UI Architecture

The app uses **Qt Designer** and a **modular MVC pattern**:

- Each page is split into:
  - `.ui` file (view/layout)
  - `.py` file (logic/controller)

---

## 🔮 Roadmap

- [ ] ☁️ **Cloud Sync** via [Supabase](https://supabase.com)
- [ ] 📱 **Android App** in native **Kotlin**
- [ ] 📈 **Client Analytics** & visit history
- [ ] 🎨 **Theming & Customization**

---

## 📦 Install & Run

Clone the repo and install the dependencies:

```bash
git clone https://github.com/Fede22dev/BeautyCenter.git
cd BeautyCenter
pip install -r requirements.txt
```

Then run the app:
```pycon
python start_bc.py
```

## Author

Made with ❤️ by [Fede22dev](https://github.com/Fede22dev)
