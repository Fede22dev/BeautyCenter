# 💅 BeautyCenter

[![Build Status]()]()
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![PySide6](https://img.shields.io/badge/Qt-PySide6-6f42c1.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()
[![Status: Alpha](https://img.shields.io/badge/status-alpha-yellow.svg)]()

---

## ✨ What is BeautyCenter?

**BeautyCenter** is a desktop application built with **Python** and **Qt (PySide6)**
to manage appointments, clients, treatments, and settings for a beauty or wellness center.

> ⚙️ Designed with modularity, clarity, and future cloud sync in mind.

---

## 🖼️ UI Architecture

The user interface is built using **Qt Designer** (`.ui` files) and follows a modular pattern.

- A `QStackedWidget` is used to dynamically switch between different pages.
- Each UI page is composed of two main files:
    - A `.ui` file for the **view** (the layout).
    - A `.py` file for the **controller** (the application logic).

---

## 🚀 Future Features

Here's what's planned for the future:

- [ ] ☁️ **Cloud Sync:** [Supabase](https://supabase.com) integration for cloud data synchronization and authentication.
- [ ] 📱 **Mobile App:** A native Android companion app built with Kotlin.
- [ ] 🧠 **Client Insights:** Detailed client history and visit statistics.
- [ ] 🛠️ **Customization:** UI theming and personalization options.

---

## 🐍 Dependencies

All required dependencies are listed in the `requirements.txt` file.
To install them, run the following command:

```bash
pip install -r requirements.txt
```

## Author

Made with ❤️ by [Fede22](https://github.com/Fede22dev)
