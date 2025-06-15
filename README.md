
# 👕 Weather Outfit AI

A Flask web app that suggests what to wear based on current temperature and weather conditions. Users get dynamic outfit predictions, can rate the suggestions, and admins can manage all predictions and feedback.

---

## 🌟 Features

- 🔐 User authentication: register, login, logout
- 🌦 Outfit predictions based on:
  - Temperature (°C)
  - Conditions: ☀️ Sunny, 🌧️ Rainy, ❄️ Snowy
- 🧠 Two AI modes:
  - Rule-based outfit logic
  - Learning-based model using feedback
- ✨ Feedback system:
  - 5-star rating
  - Optional comment field
- 🗂 User features:
  - View prediction history
  - Multilingual UI: Bulgarian 🇧🇬 and English 🇬🇧
- 👑 Admin dashboard:
  - View all predictions
  - Filter by user or condition
  - Delete users
  - Export predictions to CSV

---

## 🛠 Tech Stack

- **Python 3.12**
- **Flask** (+ Blueprints)
- **Flask-Login**, **Flask-WTF**, **Flask-SQLAlchemy**
- **SQLite** database
- **Bootstrap 5** frontend
- **Pytest** for testing

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/weather_outfit_app.git
cd weather_outfit_app
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# OR
.venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗃️ Setup the Database

Inside a Python shell:

```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

You can optionally insert an admin user manually if needed.

---

## ▶️ Running the App

```bash
flask run
```

Then visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Running Unit Tests

```bash
pytest
```

Tests include:
- Login and access control
- Outfit prediction
- Feedback submission
- Admin user deletion

---

## 📂 Project Structure

```
weather_outfit_app/
├── app/
│   ├── routes.py
│   ├── models.py
│   ├── forms.py
│   └── simple_model.py
├── templates/
├── static/
├── tests/
│   └── test_app.py
├── docs/
│   ├── user_stories.md
│   ├── sprint_log_week1.md
│   ├── sprint_log_week2.md
│   └── db-diagram.png
├── run.py
├── README.md
└── requirements.txt
```

---

## 📚 Documentation

See the [`docs/`](docs/) folder for:
- 🧩 User stories
- 🗓 Sprint logs (Week 1–2)
- 🧠 Database diagram (PNG)
- 💡 Future improvements

---

## 👨‍🎓 Course & Assignment Info

- **Course**: Web Programming (B Class)
- **Assignment**: Weather-based Outfit Suggestion App
- **University**: [Your School Name]
- **Year**: 2025
- **Author**: [Your Name]

---

## 📄 License

This project is licensed for educational purposes only.
