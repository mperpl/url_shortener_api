# 🔗 URL Shortener API

A simple, robust RESTful API built in Python for shortening long URLs and managing redirection.

---

## 🛠️ Key Technologies

* **Language:** Python 3.x
* **API Framework:** **FastAPI**
* **Database:** **SQLite** (using SQLAlchemy for persistence)
* **Feature:** Custom URL encoding logic (`encoding.py`)

---

## ✨ Features

1.  **Shorten URL:** Accepts a long URL and returns a unique, shortened code.
2.  **Redirect:** Redirects users from the short code URL directly to the original long URL.
3.  **Data Storage:** Stores mappings in a local SQLite database (`url_maps.db`).
