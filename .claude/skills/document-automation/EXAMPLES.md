# Document Automation Examples

Real-world examples of using the Document Automation skill.

## Example 1: Analyze Open Source Project

### Request
```
Analyze the repository at https://github.com/tiangolo/fastapi
```

### What Happens

1. **Clone Repository**
   ```bash
   git clone --depth 1 https://github.com/tiangolo/fastapi /tmp/fastapi
   ```

2. **Analyze Structure**
   - Detect Python project (pyproject.toml)
   - Identify FastAPI framework
   - Parse dependencies

3. **Extract Features**
   - API endpoints from examples
   - Type hints and schemas
   - Documentation strings

4. **Generate Report**
   ```markdown
   # FastAPI Analysis

   ## Overview
   - Type: Python Web Framework
   - Framework: FastAPI (self)
   - License: MIT

   ## Key Features
   - High-performance async API
   - Automatic OpenAPI documentation
   - Pydantic validation

   ## Dependencies
   - starlette>=0.27.0
   - pydantic>=2.0
   - typing-extensions>=4.8.0
   ```

---

## Example 2: Document Local Project

### Request
```
Generate comprehensive documentation for my project at C:/Projects/my-flask-app
```

### What Happens

1. **Analyze Project**
   ```
   my-flask-app/
   ├── app/
   │   ├── __init__.py
   │   ├── routes/
   │   ├── models/
   │   └── templates/
   ├── tests/
   ├── requirements.txt
   └── config.py
   ```

2. **Detect Framework**
   - Flask detected via imports
   - SQLAlchemy for ORM
   - Jinja2 for templates

3. **Extract APIs**
   ```python
   # Found in app/routes/api.py
   @app.route('/api/users', methods=['GET', 'POST'])
   @app.route('/api/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
   @app.route('/api/products', methods=['GET'])
   ```

4. **Generate Documentation**
   ```markdown
   # My Flask App

   A Flask web application with user and product management.

   ## Architecture

   ```mermaid
   flowchart TB
       Client --> Flask[Flask Server]
       Flask --> Routes[Route Handlers]
       Routes --> Models[SQLAlchemy Models]
       Models --> DB[(PostgreSQL)]
       Flask --> Templates[Jinja2 Templates]
   ```

   ## API Endpoints

   | Method | Path | Description |
   |--------|------|-------------|
   | GET | /api/users | List all users |
   | POST | /api/users | Create user |
   | GET | /api/users/:id | Get user by ID |
   | PUT | /api/users/:id | Update user |
   | DELETE | /api/users/:id | Delete user |
   | GET | /api/products | List products |

   ## Installation

   ```bash
   pip install -r requirements.txt
   flask db upgrade
   flask run
   ```
   ```

---

## Example 3: API Documentation Only

### Request
```
Document all API endpoints in my Express.js project at /home/user/node-api
```

### What Happens

1. **Detect Express.js**
   - Found in package.json dependencies
   - Router patterns in routes/

2. **Parse Routes**
   ```javascript
   // routes/users.js
   router.get('/', userController.list);
   router.post('/', userController.create);
   router.get('/:id', userController.show);
   router.put('/:id', userController.update);
   router.delete('/:id', userController.destroy);

   // routes/auth.js
   router.post('/login', authController.login);
   router.post('/register', authController.register);
   router.post('/logout', authController.logout);
   ```

3. **Generate API Docs**
   ```markdown
   # API Reference

   Base URL: `http://localhost:3000/api`

   ## Authentication

   ### POST /auth/login
   Authenticate user and receive JWT token.

   **Request Body:**
   ```json
   {
     "email": "user@example.com",
     "password": "secret123"
   }
   ```

   **Response:**
   ```json
   {
     "token": "eyJhbGciOiJIUzI1NiIs...",
     "user": { "id": 1, "email": "user@example.com" }
   }
   ```

   ### POST /auth/register
   Create new user account.

   ### POST /auth/logout
   Invalidate current session.

   ## Users

   ### GET /users
   List all users (requires auth).

   **Headers:**
   - `Authorization: Bearer <token>`

   **Response:**
   ```json
   {
     "users": [...],
     "total": 100,
     "page": 1
   }
   ```
   ```

---

## Example 4: Update Existing README

### Request
```
Update the README.md based on current code in this project
```

### What Happens

1. **Read Current README**
   - Parse existing sections
   - Identify outdated content

2. **Analyze Current Code**
   - New features added
   - Dependencies changed
   - API endpoints modified

3. **Generate Updates**
   ```diff
   # My Project

   ## Features
   - User authentication
   - Product catalog
   + - Shopping cart (NEW)
   + - Payment processing (NEW)

   ## Dependencies
   - express: ^4.18.0
   - mongoose: ^7.0.0
   + - stripe: ^12.0.0 (NEW)

   ## API Endpoints
   + ### Cart
   + - POST /cart/add
   + - GET /cart
   + - DELETE /cart/:id
   ```

---

## Example 5: Multi-Format Export

### Request
```
Generate documentation in Markdown, HTML, and PDF formats
```

### What Happens

1. **Generate Markdown**
   ```bash
   python scripts/generate-docs.py . --format markdown --output docs/README.md
   ```

2. **Generate HTML**
   ```bash
   python scripts/generate-docs.py . --format html --output docs/index.html
   ```

3. **Generate PDF**
   ```bash
   python scripts/generate-docs.py . --format pdf --output docs/documentation.pdf
   ```

### Output Files
```
docs/
├── README.md           # Markdown documentation
├── index.html          # Styled HTML documentation
├── documentation.pdf   # Printable PDF
└── assets/
    ├── styles.css      # HTML styles
    └── diagrams/       # Generated diagrams
```

---

## Example 6: CI/CD Integration

### Request
```
Set up automatic documentation generation in my GitHub Actions workflow
```

### Generated Workflow
```yaml
# .github/workflows/docs.yml
name: Generate Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Document Automation
        run: |
          git clone https://github.com/vedantparmar12/Document-Automation.git
          cd Document-Automation
          pip install -r requirements.txt

      - name: Generate Documentation
        run: |
          cd Document-Automation
          python scripts/generate-docs.py ${{ github.workspace }} \
            --format html \
            --output ${{ github.workspace }}/docs/

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

---

## Example 7: Custom Analysis Focus

### Request
```
Analyze only the security-related code in my project
```

### What Happens

1. **Identify Security Files**
   ```
   src/
   ├── auth/
   │   ├── authentication.py
   │   ├── authorization.py
   │   └── jwt_handler.py
   ├── security/
   │   ├── encryption.py
   │   ├── validation.py
   │   └── sanitization.py
   └── middleware/
       └── auth_middleware.py
   ```

2. **Extract Security Patterns**
   - JWT token handling
   - Password hashing (bcrypt)
   - Input validation
   - CORS configuration

3. **Generate Security Report**
   ```markdown
   # Security Analysis

   ## Authentication
   - JWT-based authentication
   - Token expiry: 24 hours
   - Refresh token support

   ## Password Security
   - Algorithm: bcrypt
   - Salt rounds: 12
   - Password requirements enforced

   ## Input Validation
   - Pydantic schemas for all inputs
   - SQL injection prevention (parameterized queries)
   - XSS prevention (content sanitization)

   ## Recommendations
   - [ ] Add rate limiting to auth endpoints
   - [ ] Implement CSRF protection
   - [ ] Add security headers middleware
   ```

---

## Example 8: Monorepo Analysis

### Request
```
Analyze this monorepo with multiple packages
```

### What Happens

1. **Detect Monorepo Structure**
   ```
   monorepo/
   ├── packages/
   │   ├── api/
   │   ├── web/
   │   ├── mobile/
   │   └── shared/
   ├── apps/
   │   └── admin/
   └── tools/
       └── scripts/
   ```

2. **Analyze Each Package**
   - api: Express.js API server
   - web: React frontend
   - mobile: React Native app
   - shared: Common utilities
   - admin: Admin dashboard

3. **Generate Unified Docs**
   ```markdown
   # Monorepo Documentation

   ## Packages

   ### @monorepo/api
   Express.js REST API server.
   - Port: 3000
   - Database: PostgreSQL

   ### @monorepo/web
   React SPA frontend.
   - Framework: React 18
   - State: Redux Toolkit

   ### @monorepo/mobile
   React Native mobile app.
   - Platforms: iOS, Android

   ### @monorepo/shared
   Shared utilities and types.
   - TypeScript definitions
   - Validation schemas
   - API client

   ## Architecture

   ```mermaid
   flowchart TB
       subgraph Frontend
           Web[Web App]
           Mobile[Mobile App]
           Admin[Admin Dashboard]
       end
       subgraph Backend
           API[API Server]
           DB[(Database)]
       end
       subgraph Shared
           Types[TypeScript Types]
           Utils[Utilities]
       end

       Web --> API
       Mobile --> API
       Admin --> API
       API --> DB
       Web --> Shared
       Mobile --> Shared
       API --> Shared
   ```
   ```

---

## Tips for Best Results

1. **Be Specific**: Mention what aspects you want documented
2. **Provide Context**: Share the project type and purpose
3. **Iterate**: Start with overview, then request detailed sections
4. **Review Output**: Verify generated content accuracy
5. **Customize**: Request specific formats and sections as needed
