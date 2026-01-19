# GitHub PR Manager - Real-World Examples

This document provides comprehensive, real-world examples of using the GitHub PR Manager skill for various code review and PR management scenarios.

## Table of Contents

1. [Small PR Review](#small-pr-review)
2. [Large PR Review](#large-pr-review)
3. [Security-Focused Review](#security-focused-review)
4. [Performance Review](#performance-review)
5. [Test Coverage Review](#test-coverage-review)
6. [Cross-Repository PR Review](#cross-repository-pr-review)
7. [Automated Review Workflows](#automated-review-workflows)
8. [Team Review Coordination](#team-review-coordination)

---

## Small PR Review

### Scenario
A developer submits a small bug fix PR with 3 files changed and ~50 lines modified.

### Conversation Flow

**User:** "Review PR #234 in myorg/myapp"

**Claude Response:**
```
I'll review PR #234 in myorg/myapp. Let me start by getting an overview.
```

**Commands Executed:**
```bash
gh pr view 234 --repo myorg/myapp --json title,body,author,additions,deletions,changedFiles
```

**Claude Analysis:**
```
PR #234: "Fix null pointer exception in user service"
Author: @developer123
Files changed: 3
Additions: 42 / Deletions: 8

Files affected:
  - src/services/UserService.js (+30/-5)
  - src/services/UserService.test.js (+10/-2)
  - src/utils/validators.js (+2/-1)

This is a focused bug fix. Let me review each file:
```

**Commands Executed:**
```bash
gh pr diff 234 --repo myorg/myapp -- src/services/UserService.js
gh pr diff 234 --repo myorg/myapp -- src/services/UserService.test.js
gh pr diff 234 --repo myorg/myapp -- src/utils/validators.js
```

**Claude Review:**
```
### Code Review Summary

**src/services/UserService.js**
✅ Properly adds null check before accessing user.profile
✅ Maintains backward compatibility
💡 Suggestion at line 45: Consider adding an early return for better readability

**src/services/UserService.test.js**
✅ Adds test case for null user scenario
✅ Verifies error handling

**src/utils/validators.js**
✅ Updates validator to handle null cases

### Overall Assessment
- Code quality: Good
- Test coverage: Adequate
- Security: No issues
- Performance: No impact

**Recommendation: APPROVE**
```

**Action:**
```bash
gh pr review 234 --repo myorg/myapp --approve --body "LGTM! Good fix with proper test coverage. Consider the readability suggestion at UserService.js:45, but not blocking."
```

---

## Large PR Review

### Scenario
A major feature PR with 50+ files and 2000+ line changes.

### Conversation Flow

**User:** "Review PR #567 in company/platform - it's a big one"

**Claude Response:**
```
I'll review PR #567. Let me first assess the scope.
```

**Commands Executed:**
```bash
gh pr view 567 --repo company/platform --json title,body,additions,deletions,changedFiles,files
```

**Claude Analysis:**
```
PR #567: "Add OAuth2 authentication system"
Files changed: 52
Additions: 2,847 / Deletions: 234

This is a large PR. I'll organize the review by component:

📊 File Breakdown:
- Authentication: 15 files (+1,200 lines)
- API endpoints: 12 files (+800 lines)
- Database migrations: 5 files (+300 lines)
- Tests: 18 files (+500 lines)
- Documentation: 2 files (+47 lines)

Recommended review order:
1. Database schema changes (foundation)
2. Core authentication logic (critical)
3. API endpoints (integration)
4. Tests (verification)
5. Documentation (completeness)

Let me start with database migrations:
```

**Commands Executed:**
```bash
gh pr diff 567 --repo company/platform -- 'db/migrations/*.sql'
```

**Claude Review - Phase 1: Database**
```
### Database Migrations Review

**db/migrations/001_add_oauth_tables.sql**
✅ Proper foreign key constraints
✅ Indexes on frequently queried columns
⚠️  Line 23: Consider adding index on `token_hash` for lookup performance
✅ Includes rollback script

**db/migrations/002_add_user_oauth_links.sql**
✅ Maintains data integrity with ON DELETE CASCADE
✅ Proper unique constraints

Continuing to authentication logic...
```

**Commands Executed:**
```bash
gh pr diff 567 --repo company/platform -- 'src/auth/*.js'
```

**Claude Review - Phase 2: Authentication**
```
### Core Authentication Logic Review

**src/auth/OAuthProvider.js** (350 lines)
This file is large. Let me review it in sections:

[Reads first 200 lines]

Lines 1-100: Configuration and initialization
✅ Proper config validation
✅ Secure token storage
⚠️  Line 45: Hard-coded redirect URI - should be configurable

Lines 101-200: Token exchange flow
✅ Proper PKCE implementation
⚠️  Line 156: Missing rate limiting on token exchange
🔴 Line 178: SECURITY - Token stored in plain text! Should use encryption

Lines 201-350: Token refresh logic
✅ Proper expiration handling
✅ Atomic token rotation

[Continues with other auth files...]
```

**Commands Executed:**
```bash
# Review API endpoints
gh pr diff 567 --repo company/platform -- 'src/api/*.js'

# Review tests
gh pr diff 567 --repo company/platform -- 'tests/*.test.js'
```

**Claude Final Summary:**
```
### Complete Review Summary

#### Critical Issues (Must Fix)
1. 🔴 src/auth/OAuthProvider.js:178 - Plain text token storage
2. 🔴 src/api/auth.js:89 - SQL injection vulnerability in user lookup
3. 🔴 tests/auth.test.js - Missing test for token refresh edge case

#### Important Issues (Should Fix)
1. ⚠️  src/auth/OAuthProvider.js:45 - Hard-coded redirect URI
2. ⚠️  src/auth/OAuthProvider.js:156 - Missing rate limiting
3. ⚠️  db/migrations/001_add_oauth_tables.sql:23 - Performance index needed

#### Suggestions (Nice to Have)
1. 💡 Consider extracting token validation to separate utility
2. 💡 Add monitoring/logging for failed auth attempts
3. 💡 Documentation could include sequence diagrams

#### What's Good
✅ Comprehensive test coverage (85%)
✅ Proper PKCE implementation
✅ Database schema well-designed
✅ Good error handling throughout

**Recommendation: REQUEST CHANGES**
Critical security issues must be addressed before merging.
```

**Action:**
```bash
gh pr review 567 --repo company/platform --request-changes --body-file - <<EOF
# Security & Implementation Review

## Critical Issues (Must Fix Before Merge)

### 1. Plain Text Token Storage (src/auth/OAuthProvider.js:178)
Tokens are stored without encryption, violating security best practices.

**Fix:** Use `crypto.encrypt()` before storage:
\`\`\`javascript
const encryptedToken = await crypto.encrypt(token, process.env.TOKEN_KEY);
await db.tokens.save({ token: encryptedToken });
\`\`\`

### 2. SQL Injection Vulnerability (src/api/auth.js:89)
User input is directly interpolated into SQL query.

**Fix:** Use parameterized queries:
\`\`\`javascript
const user = await db.query('SELECT * FROM users WHERE email = $1', [email]);
\`\`\`

### 3. Missing Critical Test Case
Token refresh logic lacks edge case testing for concurrent refresh attempts.

**Fix:** Add test in tests/auth.test.js

## Important Issues

- Hard-coded redirect URI needs configuration
- Rate limiting missing on token exchange endpoint
- Performance index needed on token_hash column

## Positive Aspects

Great work on:
- PKCE implementation
- Overall test coverage
- Database schema design
- Error handling

Please address the critical issues, and I'll re-review promptly.
EOF
```

---

## Security-Focused Review

### Scenario
Review a PR for security vulnerabilities and best practices.

**User:** "Do a security review of PR #890"

**Claude Workflow:**

```bash
# Get PR overview
gh pr view 890 --json title,files

# Focus on security-sensitive files
gh pr diff 890 -- 'src/auth/*' 'src/api/*' '*.config.js'
```

**Claude Security Checklist:**

```
🔒 Security Review for PR #890

### Authentication & Authorization
- [ ] Password hashing with proper algorithm (bcrypt/argon2)
- [ ] Session tokens properly validated
- [ ] Authorization checks on all endpoints
- [ ] Rate limiting on auth endpoints

### Input Validation
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (input sanitization, output encoding)
- [ ] CSRF tokens on state-changing operations
- [ ] File upload validation

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS enforced for data in transit
- [ ] No secrets in code or logs
- [ ] PII handling compliant with regulations

### Dependencies
- [ ] No known vulnerable dependencies
- [ ] Regular security updates planned

Running detailed analysis...
```

**Findings:**

```
### Security Findings

#### Critical ⚠️
1. **SQL Injection** (src/api/users.js:45)
   ```javascript
   // Vulnerable
   db.query(`SELECT * FROM users WHERE id = ${userId}`)

   // Fixed
   db.query('SELECT * FROM users WHERE id = $1', [userId])
   ```

2. **Missing Authorization Check** (src/api/admin.js:67)
   ```javascript
   // Missing check
   app.delete('/api/users/:id', async (req, res) => {
     await deleteUser(req.params.id);
   });

   // Should be
   app.delete('/api/users/:id', requireAdmin, async (req, res) => {
     await deleteUser(req.params.id);
   });
   ```

#### High Priority ⚠️
3. **Weak Password Policy** (src/auth/password.js:23)
   - Minimum 8 characters required
   - No complexity requirements
   - Suggest: min 12 chars, require mixed case, numbers, symbols

4. **Session Timeout Too Long** (config/session.js:10)
   - Current: 7 days
   - Recommend: 24 hours with refresh token

#### Recommendations 💡
- Enable Content Security Policy headers
- Add rate limiting (express-rate-limit)
- Implement security headers (helmet.js)
- Add audit logging for sensitive operations

**Overall Risk: HIGH** - Critical issues must be fixed.
```

---

## Performance Review

### Scenario
Review PR for performance implications.

**User:** "Check PR #445 for performance issues"

**Claude Workflow:**

```bash
gh pr view 445 --json title,files
gh pr diff 445
```

**Claude Performance Analysis:**

```
⚡ Performance Review for PR #445

### Database Queries
📍 src/services/OrderService.js:67
❌ **N+1 Query Problem Detected**

Current code:
\`\`\`javascript
const orders = await Order.findAll();
for (const order of orders) {
  order.items = await OrderItem.findAll({ orderId: order.id });
}
\`\`\`

This executes 1 + N queries (1 for orders, N for each order's items).

**Fix with eager loading:**
\`\`\`javascript
const orders = await Order.findAll({
  include: [{ model: OrderItem }]
});
\`\`\`

**Impact:**
- Current: 1,001 queries for 1,000 orders
- Fixed: 1 query
- Performance gain: ~99% faster

---

### Loop Optimization
📍 src/utils/calculator.js:34
⚠️  **Inefficient Array Operation**

\`\`\`javascript
// Current: O(n²) complexity
items.forEach(item => {
  total += items.filter(i => i.category === item.category).length;
});
\`\`\`

**Better approach:**
\`\`\`javascript
// O(n) complexity with reduce
const categoryCount = items.reduce((acc, item) => {
  acc[item.category] = (acc[item.category] || 0) + 1;
  return acc;
}, {});
\`\`\`

---

### Memory Usage
📍 src/services/ReportGenerator.js:89
⚠️  **Loading Entire Dataset into Memory**

\`\`\`javascript
const allRecords = await db.records.findAll(); // Could be millions
const report = processRecords(allRecords);
\`\`\`

**Fix with streaming:**
\`\`\`javascript
const stream = db.records.stream();
for await (const batch of batchStream(stream, 1000)) {
  await processRecordsBatch(batch);
}
\`\`\`

---

### Caching Opportunities
📍 src/api/products.js:45
💡 **Missing Cache for Expensive Operation**

\`\`\`javascript
app.get('/api/products', async (req, res) => {
  const products = await calculatePricesWithDiscounts(); // Heavy computation
  res.json(products);
});
\`\`\`

**Recommendation: Add caching**
\`\`\`javascript
const cache = new NodeCache({ stdTTL: 300 }); // 5-minute cache

app.get('/api/products', async (req, res) => {
  let products = cache.get('products');
  if (!products) {
    products = await calculatePricesWithDiscounts();
    cache.set('products', products);
  }
  res.json(products);
});
\`\`\`

---

### Summary
- 🔴 Critical: N+1 query (1000x slower)
- ⚠️  High: O(n²) loop operation
- ⚠️  High: Memory-inefficient data loading
- 💡 Suggestion: Add caching layer

**Estimated Performance Gain:** 10-100x improvement after fixes
```

---

## Test Coverage Review

### Scenario
Ensure new features have adequate test coverage.

**User:** "Check test coverage for PR #332"

**Claude Workflow:**

```bash
# Get changed files
gh pr diff 332 --name-status

# Identify source files vs test files
gh pr diff 332 --name-only | grep -E '(src/|lib/)'
gh pr diff 332 --name-only | grep -E '(test/|spec/|\.test\.|\.spec\.)'

# Review implementation files
gh pr diff 332 -- 'src/**/*.js'

# Review test files
gh pr diff 332 -- 'tests/**/*.test.js'
```

**Claude Test Coverage Analysis:**

```
🧪 Test Coverage Analysis for PR #332

### Source Files Added/Modified
1. src/services/PaymentService.js (+180 lines)
   - New method: processPayment()
   - New method: refundPayment()
   - New method: validateCard()

2. src/services/EmailService.js (+45 lines)
   - New method: sendReceipt()

3. src/utils/currency.js (+30 lines)
   - New method: convertCurrency()

### Test Files
1. tests/services/PaymentService.test.js (+95 lines)
2. tests/utils/currency.test.js (+40 lines)

### Coverage Analysis

#### ✅ Well Tested
**PaymentService.processPayment()**
- ✅ Happy path: successful payment
- ✅ Error case: insufficient funds
- ✅ Error case: invalid card
- ✅ Edge case: zero amount
- ✅ Integration: database transaction rollback

**currency.convertCurrency()**
- ✅ Basic conversion
- ✅ Rounding behavior
- ✅ Invalid currency codes

#### ⚠️  Partially Tested
**PaymentService.refundPayment()**
- ✅ Happy path: successful refund
- ❌ Missing: partial refund scenario
- ❌ Missing: refund of already-refunded payment
- ❌ Missing: concurrent refund attempts

#### ❌ Not Tested
**PaymentService.validateCard()**
- ❌ No tests found for this method
- This is a critical security function!

**EmailService.sendReceipt()**
- ❌ No tests found
- ❌ Email failures are not tested

### Missing Test Scenarios

#### Critical Missing Tests
1. **Card Validation Edge Cases**
   \`\`\`javascript
   describe('PaymentService.validateCard', () => {
     it('should reject expired cards', async () => {
       const card = { number: '4111111111111111', expiry: '01/20' };
       await expect(service.validateCard(card)).rejects.toThrow('Card expired');
     });

     it('should reject invalid card numbers', async () => {
       const card = { number: '1234567890123456', expiry: '12/25' };
       await expect(service.validateCard(card)).rejects.toThrow('Invalid card');
     });

     it('should validate CVV format', async () => {
       const card = { number: '4111111111111111', expiry: '12/25', cvv: '12' };
       await expect(service.validateCard(card)).rejects.toThrow('Invalid CVV');
     });
   });
   \`\`\`

2. **Email Failure Handling**
   \`\`\`javascript
   describe('EmailService.sendReceipt', () => {
     it('should retry on transient failures', async () => {
       // Mock email provider failure then success
     });

     it('should log permanently failed emails', async () => {
       // Verify logging when email cannot be sent
     });
   });
   \`\`\`

3. **Refund Edge Cases**
   \`\`\`javascript
   describe('PaymentService.refundPayment', () => {
     it('should prevent double refunds', async () => {
       await service.refundPayment(paymentId);
       await expect(service.refundPayment(paymentId)).rejects.toThrow();
     });

     it('should handle partial refunds correctly', async () => {
       // Test partial refund scenarios
     });
   });
   \`\`\`

### Test Quality Issues

1. **Insufficient Assertions** (PaymentService.test.js:45)
   \`\`\`javascript
   // Weak test
   it('processes payment', async () => {
     await service.processPayment(payment);
     // No assertions!
   });

   // Better test
   it('processes payment and records transaction', async () => {
     const result = await service.processPayment(payment);
     expect(result.status).toBe('success');
     expect(result.transactionId).toBeDefined();
     const record = await db.transactions.findById(result.transactionId);
     expect(record.amount).toBe(payment.amount);
   });
   \`\`\`

2. **Missing Mock Verification** (PaymentService.test.js:67)
   - Email service is mocked but never verified
   - Add: `expect(emailService.sendReceipt).toHaveBeenCalled()`

### Coverage Summary
- **processPayment()**: 90% covered ✅
- **refundPayment()**: 60% covered ⚠️
- **validateCard()**: 0% covered ❌
- **sendReceipt()**: 0% covered ❌
- **convertCurrency()**: 85% covered ✅

**Overall Assessment: INCOMPLETE**

### Recommendations
1. Add critical missing tests before merge
2. Improve test quality with better assertions
3. Consider adding integration tests for payment flow
4. Run coverage tool: `npm run test:coverage`

**Cannot approve without tests for validateCard() and sendReceipt()**
```

---

## Cross-Repository PR Review

### Scenario
Review a PR that depends on changes in another repository.

**User:** "Review PR #678 in frontend-app - it depends on backend changes"

**Claude Workflow:**

```bash
# Review frontend PR
gh pr view 678 --repo org/frontend-app

# Check PR description for backend dependency
gh pr view 678 --repo org/frontend-app --json body

# Find linked backend PR
# (Usually referenced in description like "Depends on org/backend-api#123")

# Review backend PR
gh pr view 123 --repo org/backend-api
```

**Claude Analysis:**

```
📊 Cross-Repository Review: Frontend PR #678

### Dependency Chain
Frontend PR #678 ← depends on → Backend PR #123

### Backend PR #123 Review (org/backend-api)
**Status:** ✅ Merged
**Changes:** Added new `/api/v2/user-preferences` endpoint

Key changes:
- New endpoint: GET /api/v2/user-preferences
- New endpoint: PUT /api/v2/user-preferences
- Response format: `{ theme: string, language: string, notifications: boolean }`

### Frontend PR #678 Review (org/frontend-app)

**Integration Points:**
1. src/api/preferences.js - Calls new backend endpoints
2. src/components/Settings.jsx - Uses preference data
3. src/hooks/usePreferences.js - Hook for preference management

**Verification Checklist:**
- ✅ API endpoints match backend implementation
- ✅ Request/response formats align
- ✅ Error handling covers backend error codes
- ⚠️  Missing: Loading states during API calls
- ⚠️  Missing: Retry logic for failed requests

**Compatibility Check:**
\`\`\`javascript
// Frontend code (src/api/preferences.js:12)
const response = await fetch('/api/v2/user-preferences');
const data = await response.json();
return {
  theme: data.theme,
  language: data.language,
  notifications: data.notifications
};
\`\`\`

Backend response schema matches ✅

**Recommendation:**
- Add loading states and retry logic
- Otherwise integration looks good
- Backend changes are already deployed
```

---

## Automated Review Workflows

### Scenario
Set up automated review criteria that Claude applies consistently.

**User:** "Create an automated review checklist for all PRs"

**Claude Creates:**

```yaml
# .claude/pr-review-checklist.yml

code_quality:
  - Check for duplicate code
  - Verify function length < 50 lines
  - Check for proper error handling
  - Verify meaningful variable names
  - Check for commented-out code (should be removed)

security:
  - SQL injection prevention
  - XSS prevention
  - CSRF protection on state-changing operations
  - Authentication/authorization checks
  - No hard-coded secrets

performance:
  - No N+1 queries
  - Efficient algorithms (avoid O(n²) where possible)
  - Proper database indexing
  - Caching for expensive operations
  - Memory-efficient data handling

testing:
  - New features have tests
  - Tests cover edge cases
  - Tests cover error paths
  - Integration tests for API changes
  - Test assertions are specific

documentation:
  - Public APIs documented
  - Complex logic has comments
  - README updated if needed
  - API changes documented
  - Breaking changes highlighted

dependencies:
  - No unnecessary dependencies
  - Dependencies are up-to-date
  - No known vulnerabilities
  - License compatibility checked
```

**Usage:**

```
User: "Review PR #789 using the standard checklist"

Claude: [Runs through checklist systematically]

✅ Code Quality
  ✅ No duplicate code found
  ✅ All functions under 50 lines
  ⚠️  Missing error handling in uploadFile() (src/upload.js:45)
  ✅ Variable names are clear
  ✅ No commented-out code

🔒 Security
  ✅ Parameterized queries used
  ✅ Input sanitization present
  ❌ Missing CSRF token on POST /api/upload
  ✅ Proper authorization checks
  ✅ No secrets in code

[... continues through checklist ...]
```

---

## Team Review Coordination

### Scenario
Coordinate reviews across multiple team members.

**User:** "Assign reviewers for PR #890 based on the changes"

**Claude Workflow:**

```bash
# Analyze changed files
gh pr view 890 --json files

# Check team structure (from CODEOWNERS or documentation)
cat CODEOWNERS
```

**Claude Response:**

```
📋 Review Assignment Recommendations for PR #890

Based on changed files and expertise areas:

### Primary Reviewers Needed

**@alice (Backend Lead)** - Priority: HIGH
- src/api/payment.js (+150 lines)
- src/services/PaymentProcessor.js (+200 lines)
- Reason: Payment processing logic requires security review

**@bob (Database Admin)** - Priority: HIGH
- db/migrations/005_add_payment_tables.sql (+80 lines)
- Reason: Schema changes need DBA approval

**@carol (Frontend Lead)** - Priority: MEDIUM
- src/components/Checkout.jsx (+120 lines)
- src/hooks/usePayment.js (+45 lines)
- Reason: UI changes for checkout flow

### Optional Reviewers

**@david (Security)** - Priority: MEDIUM
- All authentication/payment related files
- Reason: Security implications of payment handling

**@eve (QA Lead)** - Priority: LOW
- Review test coverage
- Reason: Ensure adequate testing

### Suggested Command
\`\`\`bash
gh pr edit 890 --add-reviewer alice,bob,carol
gh pr comment 890 --body "@david Could you do a security review when you have time?"
\`\`\`

Would you like me to execute these assignments?
```

---

## Summary

These examples demonstrate:
- ✅ Small PR quick reviews
- ✅ Large PR systematic navigation
- ✅ Security-focused analysis
- ✅ Performance optimization detection
- ✅ Test coverage verification
- ✅ Cross-repository coordination
- ✅ Automated review checklists
- ✅ Team collaboration patterns

The skill adapts to PR size, complexity, and review focus while maintaining thoroughness and managing context efficiently.
