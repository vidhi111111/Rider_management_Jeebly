# Angular 14 + Flask Register App

A ready-to-run registration project built for the requested stack:

- Angular 14
- Standalone Angular components
- Angular Router
- Reactive Forms
- Bootstrap 5
- Node.js 16.x
- NVM Windows
- Python Flask
- `POST /register`
- JSON parsing and server-side validation
- Password/confirm-password validation on the frontend
- CORS enabled for local Angular development

## Project structure

```text
angular14-flask-register/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/
│   │   │   │   └── services/
│   │   │   │       └── auth.service.ts
│   │   │   ├── pages/
│   │   │   │   └── register/
│   │   │   │       ├── register.component.ts
│   │   │   │       ├── register.component.html
│   │   │   │       └── register.component.css
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   ├── app.component.css
│   │   │   └── app.routes.ts
│   │   ├── assets/
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── styles.css
│   ├── angular.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   └── .gitignore
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── validators.py
│   ├── run.py
│   ├── requirements.txt
│   └── .gitignore
└── README.md
```

## 1. Node / NVM

Open PowerShell and use Node 16:

```powershell
nvm list
nvm use 16.20.2
node -v
npm -v
```

If Node 16 is not installed:

```powershell
nvm install 16.20.2
nvm use 16.20.2
```

> Angular 14 is the Angular version used by this project. NVM is a Node version manager; the project does not use an "NVM 14" Node version.

## 2. Start the Flask backend

Open PowerShell in the `backend` folder:

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

Backend runs on:

`http://localhost:5000`

## 3. Start Angular

Open a second PowerShell window:

```powershell
cd frontend
npm install
npx ng serve
```

Open:

`http://localhost:4200`

## Registration API

`POST http://localhost:5000/register`






The API validates:

- name required
- email required and valid
- mobile required and valid
- password required and minimum 8 characters
- JSON request body

For this learning project, registration is intentionally kept as an API validation exercise. It does not persist users to a database and it does not return or store the submitted password.
