# Jeebly RMS - Frontend

The frontend for the **Jeebly RMS (Rider Management System)**, an operations and dispatch web application built with **Angular 14** using standalone components, reactive forms, and Bootstrap 5.

---

## 1. Project Overview

Jeebly RMS provides an administrative portal for logistics and last-mile delivery operations:
- Authenticates users with JWT tokens.
- Manages rider onboarding, profile photos, status, and fleet availability.
- Tracks delivery orders from creation through assignment and fulfillment.
- Visualizes operational KPIs and order metrics on a real-time dashboard.
- Supports user profile management and light/dark appearance modes.

---

## 2. Tech Stack

| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **Angular** | `~14.2.0` | Core framework using Standalone Components |
| **Angular CLI** | `~14.2.13` | Build toolchain and development server |
| **TypeScript** | `~4.7.4` | Application programming language |
| **Bootstrap** | `^5.3.8` | Responsive layout, grid, and base UI utilities |
| **RxJS** | `~7.5.0` | Reactive streams, search debouncing, and state management |
| **Zone.js** | `~0.11.4` | Angular change detection execution context |
| **Node.js** | `v16.20.2` | Runtime environment (recommended via NVM Windows) |
| **npm** | `8.19.4` | Package manager |

---

## 3. Features

- **Authentication**: User registration with strict password policies, login with JWT storage, and session logout.
- **Master Layout**: Responsive collapsible sidebar, dynamic breadcrumbs, user avatar with initial generation, and light/dark theme toggle.
- **Dashboard**: Operational KPI cards (total, delivered, cancelled, in-progress), fleet availability breakdown, recent orders, and available riders.
- **Rider Management**: Full CRUD operations, debounced search (`300ms`), status/availability filters, column sorting, pagination, profile photo upload with local preview and removal, and confirmation dialogs.
- **Order Management**: Paginated order list, multi-criteria filters (date, status, rider, search), inline rider assignment, status lifecycle progression, modal creation, and deletion confirmations.
- **Profile & Security**: Update profile name and phone number with live `localStorage` and header sync, plus password changes with current password verification.
- **Feedback & Notifications**: Reusable toast notification component (`app-toast`) with auto-dismiss timers and modal confirmation backdrops.

---

## 4. Project Structure

```text
frontend/src/
├── app/
│   ├── core/                     # Application-wide singletons
│   │   ├── guards/
│   │   │   └── auth.guard.ts           # Route guard protecting private views
│   │   ├── interceptors/
│   │   │   └── auth.interceptor.ts     # Attaches JWT Bearer token & handles 401s
│   │   └── services/
│   │       ├── auth.service.ts         # Authentication & session storage
│   │       ├── dashboard.service.ts    # Dashboard analytics metrics
│   │       ├── order.service.ts        # Order CRUD, status, & dispatch
│   │       ├── profile.service.ts      # Profile, password, & settings
│   │       └── rider.service.ts        # Rider CRUD, filtering, & pagination
│   ├── layout/                   # Main application layout shell
│   │   ├── layout.component.ts         # Sidebar drawer, header avatar, theme logic
│   │   ├── layout.component.html
│   │   └── layout.component.css
│   ├── pages/                    # Lazy-loaded feature views
│   │   ├── change-password/            # Change password form
│   │   ├── dashboard/                  # KPI metrics and fleet overview
│   │   ├── login/                      # User login
│   │   ├── orders/                     # Orders table, dispatch modal, filters
│   │   ├── profile/                    # User profile view and update
│   │   ├── register/                   # User registration with custom validators
│   │   ├── rider-form/                 # Standalone rider add/edit page
│   │   └── riders/                     # Rider list, modal CRUD, photo upload
│   ├── shared/                   # Reusable presentational components
│   │   ├── breadcrumb/                 # Dynamic route-based breadcrumb trail
│   │   └── toast/                      # Global notification alert component
│   ├── app.component.ts          # Root component hosting <router-outlet>
│   └── app.routes.ts             # Route table with lazy loading definitions
├── assets/images/                # Static assets (Jeebly logo, favicons)
├── environments/                 # Environment configurations (API base URL)
├── index.html                    # Single HTML page shell
├── main.ts                       # Application bootstrap entry point
└── styles.css                    # Global CSS variables, fonts, and dark theme
```

---

## 5. Prerequisites

- **Node.js**: `v16.20.2` (Angular 14 build tools require Node 14 or 16).
- **NVM for Windows** (Recommended): To easily switch Node versions (`nvm use 16.20.2`).
- **npm**: `8.19.4` (bundled with Node 16.20.2).
- **Backend**: A running instance of the Flask backend API (local on `http://127.0.0.1:5000` or deployed on Render).

---

## 6. Setup & Installation

### 1. Switch to Node 16
```powershell
nvm use 16.20.2
```

### 2. Navigate to Frontend Directory
```powershell
cd frontend
```

### 3. Install Dependencies
```powershell
npm install
```

### 4. Start Development Server
```powershell
npm start
```
*Or directly via Angular CLI:*
```powershell
npx ng serve
```

Open your browser at:
```text
http://localhost:4200
```

### 5. Build for Production
```powershell
npm run build
```
Compiled output is saved in `dist/angular14-register/`.

---

## 7. Configuration

Environment settings are located in `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'https://rider-management-jeebly-backend.onrender.com'
};
```

- **For Local Backend Development**:
  Change `apiUrl` to:
  ```typescript
  apiUrl: 'http://127.0.0.1:5000'
  ```

- **Authentication Storage**:
  - JWT Access Token: `localStorage.getItem('access_token')`
  - Current User: `localStorage.getItem('current_user')`
  - Theme Setting: `localStorage.getItem('theme')` (`'dark'` or `'light'`)

---

## 8. Implemented Concepts

- **Standalone Components**: Bootstrapped via `bootstrapApplication(AppComponent)` in `main.ts` without traditional `AppModule`.
- **Routing & Lazy Loading**: All feature routes use `loadComponent: () => import(...)` in `app.routes.ts`.
- **Reactive Forms**: Implemented in Login, Register, Rider, Profile, and Password forms using `FormBuilder`, `FormGroup`, and synchronous validators.
- **Template-driven Forms**: Used in the Create/Edit Order modal with `[(ngModel)]`.
- **Form Validation**: Built-in rules (`required`, `email`, `pattern`, `minLength`) and custom cross-field validators (`passwordsMatch`, `passwordValidator`).
- **Route Guard (`AuthGuard`)**: Evaluates `isLoggedIn()` and redirects unauthenticated users to `/login`.
- **HTTP Interceptor (`AuthInterceptor`)**: Automatically clones outgoing requests, attaches `Authorization: Bearer <token>`, and handles `401 Unauthorized` responses with redirect loop prevention.
- **Directives**: Structural (`*ngIf`, `*ngFor`), attribute (`[ngClass]`, `[disabled]`), and host listeners (`@HostListener('document:keydown.escape')`).
- **RxJS Operators**: `debounceTime(300)` and `distinctUntilChanged` on search inputs, `takeUntil(this.destroy$)` to prevent memory leaks, `finalize` for loading states, and `timeout(15000)`.
- **Component Communication**: `@Input()` and `@Output()` with `EventEmitter` in `ToastComponent`.

---

## 9. Common Issues & Solutions

### 1. OpenSSL / Node.js Version Error
- **Problem**: Running with Node 18+ causes `digital envelope routines::unsupported` build failures.
- **Solution**: Use Node 16 LTS via NVM: `nvm use 16.20.2`.

### 2. Interceptor 401 Redirect Loop
- **Problem**: When an access token expired, multiple concurrent API calls triggered multiple redirect calls, and login 401 errors caused an immediate self-redirect.
- **Solution**: Excluded `/login` and `/register` endpoints from 401 handling, added an `isRedirecting` mutex flag, and used `router.navigateByUrl('/login')`.

### 3. Inconsistent API Base URLs
- **Problem**: `AuthService` had a hardcoded URL, causing auth requests to miss the target backend.
- **Solution**: Unified all services to use `environment.apiUrl`.

### 4. Empty Table State on Record Deletion
- **Problem**: Deleting the only remaining item on page N (where N > 1) left the user on an empty page.
- **Solution**: Added page decrement logic: `if (this.riders.length === 1 && this.currentPage > 1) this.currentPage--;`.

### 5. Rider Photo Removal on Update
- **Problem**: Updating a rider without selecting a new photo kept the old image with no option to remove it.
- **Solution**: Added a "Remove Photo" action that sends `remove_photo: 'true'` in the `FormData` to `PUT /riders/:id`.
