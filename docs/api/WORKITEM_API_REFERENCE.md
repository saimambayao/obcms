# WorkItem API Reference

**Document Type**: API Documentation
**Target Audience**: Software Developers, Integration Engineers
**API Version**: 1.0
**Last Updated**: October 6, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [Rate Limiting](#rate-limiting)
8. [Changelog](#changelog)

---

## Overview

The WorkItem API provides RESTful endpoints for managing PPA WorkItem integration, enabling external systems to:
- Enable WorkItem tracking for PPAs
- Retrieve budget allocation trees
- Distribute budget across work items
- Synchronize progress and status

**Base URL:**
```
Production: https://obcms.oobc.barmm.gov.ph/api/v1/
Staging: https://staging.obcms.oobc.barmm.gov.ph/api/v1/
Development: http://localhost:8000/api/v1/
```

**API Versioning:**
- Current Version: `v1`
- API version is included in the URL path
- Breaking changes will result in new version (e.g., `v2`)

---

## Authentication

### JWT Authentication (Recommended)

All API requests require authentication using JSON Web Tokens (JWT).

#### Obtaining Access Token

**Endpoint:** `POST /api/token/`

**Request:**
```http
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Token Expiration:**
- Access Token: 1 hour
- Refresh Token: 7 days

#### Refreshing Access Token

**Endpoint:** `POST /api/token/refresh/`

**Request:**
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Using Access Token

Include the access token in the `Authorization` header:

```http
GET /api/v1/monitoring/entries/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## API Endpoints

### 1. Enable WorkItem Tracking

Enable WorkItem-based execution tracking for a PPA.

**Endpoint:** `POST /api/v1/monitoring/entries/{ppa_id}/enable-workitem-tracking/`

**Method:** `POST`

**Authentication:** Required

**Path Parameters:**
- `ppa_id` (UUID, required): Monitoring Entry (PPA) ID

**Request Body:**
```json
{
  "structure_template": "activity",
  "budget_distribution_policy": "equal",
  "auto_sync_progress": true,
  "auto_sync_status": true
}
```

**Request Fields:**

| Field | Type | Required | Options | Description |
|-------|------|----------|---------|-------------|
| `structure_template` | string | No | `program`, `activity`, `milestone`, `minimal` | Work breakdown structure template |
| `budget_distribution_policy` | string | No | `equal`, `weighted`, `manual` | How to distribute budget |
| `auto_sync_progress` | boolean | No | `true`, `false` | Auto-sync progress from work items |
| `auto_sync_status` | boolean | No | `true`, `false` | Auto-sync status from work items |

**Success Response (201 Created):**
```json
{
  "structure_template": "activity",
  "execution_project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "execution_project_title": "Livelihood Training Program - Execution Plan",
  "work_items_created": 8,
  "structure_summary": {
    "project": 1,
    "activities": 3,
    "tasks": 4,
    "subtasks": 0
  }
}
```

**Error Responses:**

**400 Bad Request** - Invalid request or PPA already has execution project:
```json
{
  "error": "WorkItem tracking already enabled for this PPA",
  "execution_project_id": "existing-project-uuid"
}
```

**403 Forbidden** - User lacks permission:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found** - PPA does not exist:
```json
{
  "detail": "Not found."
}
```

---

### 2. Get Budget Allocation Tree

Retrieve hierarchical budget allocation tree for a PPA.

**Endpoint:** `GET /api/v1/monitoring/entries/{ppa_id}/budget-allocation-tree/`

**Method:** `GET`

**Authentication:** Required

**Path Parameters:**
- `ppa_id` (UUID, required): Monitoring Entry (PPA) ID

**Success Response (200 OK):**
```json
{
  "ppa_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "ppa_title": "Livelihood Training Program",
  "total_budget": "5000000.00",
  "allocated_budget": "4850000.00",
  "unallocated_budget": "150000.00",
  "budget_currency": "PHP",
  "tree": [
    {
      "work_item_id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
      "title": "Livelihood Training Program - Execution Plan",
      "work_type": "project",
      "work_type_display": "Project",
      "allocated_budget": "4850000.00",
      "actual_expenditure": "1200000.00",
      "variance": "-3650000.00",
      "variance_pct": -75.26,
      "status": "in_progress",
      "progress": 25,
      "children": [
        {
          "work_item_id": "c3d4e5f6-g7h8-9012-cdef-234567890123",
          "title": "Activity 1: Needs Assessment",
          "work_type": "activity",
          "work_type_display": "Activity",
          "allocated_budget": "500000.00",
          "actual_expenditure": "500000.00",
          "variance": "0.00",
          "variance_pct": 0.0,
          "status": "completed",
          "progress": 100,
          "children": []
        },
        {
          "work_item_id": "d4e5f6g7-h8i9-0123-defg-345678901234",
          "title": "Activity 2: Skills Training",
          "work_type": "activity",
          "allocated_budget": "3500000.00",
          "actual_expenditure": "700000.00",
          "variance": "-2800000.00",
          "variance_pct": -80.0,
          "status": "in_progress",
          "progress": 20,
          "children": [
            {
              "work_item_id": "e5f6g7h8-i9j0-1234-efgh-456789012345",
              "title": "Task: Training materials",
              "work_type": "task",
              "allocated_budget": "500000.00",
              "actual_expenditure": "200000.00",
              "variance": "-300000.00",
              "variance_pct": -60.0,
              "status": "in_progress",
              "progress": 40,
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

**Error Responses:**

**400 Bad Request** - WorkItem tracking not enabled:
```json
{
  "error": "WorkItem tracking not enabled for this PPA"
}
```

---

### 3. Distribute Budget

Distribute PPA budget across work items using specified method.

**Endpoint:** `POST /api/v1/monitoring/entries/{ppa_id}/distribute-budget/`

**Method:** `POST`

**Authentication:** Required

**Path Parameters:**
- `ppa_id` (UUID, required): Monitoring Entry (PPA) ID

**Request Body (Equal Distribution):**
```json
{
  "method": "equal"
}
```

**Request Body (Weighted Distribution):**
```json
{
  "method": "weighted",
  "weights": {
    "b2c3d4e5-f6g7-8901-bcde-f12345678901": 0.5,
    "c3d4e5f6-g7h8-9012-cdef-234567890123": 0.3,
    "d4e5f6g7-h8i9-0123-defg-345678901234": 0.2
  }
}
```

**Request Body (Manual Distribution):**
```json
{
  "method": "manual",
  "allocations": {
    "b2c3d4e5-f6g7-8901-bcde-f12345678901": "2500000.00",
    "c3d4e5f6-g7h8-9012-cdef-234567890123": "1500000.00",
    "d4e5f6g7-h8i9-0123-defg-345678901234": "1000000.00"
  }
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `method` | string | Yes | Distribution method: `equal`, `weighted`, or `manual` |
| `weights` | object | Conditional | Required for `weighted` method. Map of work_item_id → weight (must sum to 1.0) |
| `allocations` | object | Conditional | Required for `manual` method. Map of work_item_id → budget amount (must sum to PPA budget) |

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Budget distributed successfully using equal method",
  "work_items_updated": 3,
  "distribution": {
    "b2c3d4e5-f6g7-8901-bcde-f12345678901": "1666666.67",
    "c3d4e5f6-g7h8-9012-cdef-234567890123": "1666666.67",
    "d4e5f6g7-h8i9-0123-defg-345678901234": "1666666.66"
  },
  "total_allocated": "5000000.00"
}
```

**Error Responses:**

**400 Bad Request** - Invalid distribution:
```json
{
  "error": "Budget distribution failed: Weights must sum to 1.0 (current sum: 0.95)"
}
```

---

### 4. Sync from WorkItem

Synchronize PPA progress and status from WorkItem hierarchy.

**Endpoint:** `POST /api/v1/monitoring/entries/{ppa_id}/sync-from-workitem/`

**Method:** `POST`

**Authentication:** Required

**Path Parameters:**
- `ppa_id` (UUID, required): Monitoring Entry (PPA) ID

**Request Body:** (None required)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Progress and status synchronized successfully",
  "previous_progress": 45,
  "updated_progress": 67,
  "previous_status": "ongoing",
  "updated_status": "ongoing",
  "work_items_analyzed": 12,
  "sync_timestamp": "2025-10-06T10:30:00Z"
}
```

**Error Responses:**

**400 Bad Request** - WorkItem tracking not enabled:
```json
{
  "error": "WorkItem tracking not enabled for this PPA"
}
```

**500 Internal Server Error** - Sync failed:
```json
{
  "error": "Synchronization failed: Database connection error"
}
```

---

## Request/Response Formats

### Content Type

All requests and responses use JSON format:
```http
Content-Type: application/json
```

### Date/Time Format

All timestamps use ISO 8601 format:
```
2025-10-06T10:30:00Z  (UTC)
2025-10-06T18:30:00+08:00  (with timezone)
```

### Decimal Format

All decimal values (budgets, percentages) are returned as strings:
```json
{
  "budget": "5000000.00",  // String, not number
  "variance_pct": -75.26   // Number for percentages
}
```

### UUID Format

All UUIDs use standard hyphenated format:
```
a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Error Handling

### Error Response Structure

All error responses follow this structure:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional context"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `204` | No Content | Request successful, no response body |
| `400` | Bad Request | Invalid request parameters or data |
| `401` | Unauthorized | Authentication required or token expired |
| `403` | Forbidden | User lacks permission for this action |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | Resource conflict (e.g., duplicate) |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error |

### Common Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `AUTHENTICATION_REQUIRED` | No or invalid auth token | Include valid JWT token in Authorization header |
| `TOKEN_EXPIRED` | Access token has expired | Refresh token using `/api/token/refresh/` |
| `PERMISSION_DENIED` | User lacks required permission | Contact admin for role assignment |
| `VALIDATION_ERROR` | Request validation failed | Check request parameters and body |
| `RESOURCE_NOT_FOUND` | Requested resource does not exist | Verify resource ID is correct |
| `WORKITEM_ALREADY_ENABLED` | WorkItem tracking already enabled | Use existing execution project |
| `BUDGET_ROLLUP_MISMATCH` | Budget distribution doesn't match PPA budget | Adjust allocations to match total |

---

## Code Examples

### Python (requests library)

```python
import requests
import json

# Authentication
auth_url = "https://obcms.oobc.barmm.gov.ph/api/token/"
auth_data = {
    "username": "your_username",
    "password": "your_password"
}

response = requests.post(auth_url, json=auth_data)
tokens = response.json()
access_token = tokens["access"]

# Set headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Enable WorkItem tracking
ppa_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
enable_url = f"https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/{ppa_id}/enable-workitem-tracking/"
enable_data = {
    "structure_template": "activity",
    "budget_distribution_policy": "equal"
}

response = requests.post(enable_url, json=enable_data, headers=headers)
if response.status_code == 201:
    result = response.json()
    print(f"Execution project created: {result['execution_project_id']}")
    print(f"Work items created: {result['work_items_created']}")
else:
    print(f"Error: {response.json()}")

# Get budget allocation tree
budget_url = f"https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/{ppa_id}/budget-allocation-tree/"
response = requests.get(budget_url, headers=headers)
budget_tree = response.json()

print(f"Total Budget: ₱{float(budget_tree['total_budget']):,.2f}")
print(f"Allocated: ₱{float(budget_tree['allocated_budget']):,.2f}")
print(f"Unallocated: ₱{float(budget_tree['unallocated_budget']):,.2f}")

# Distribute budget (weighted)
distribute_url = f"https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/{ppa_id}/distribute-budget/"
distribute_data = {
    "method": "weighted",
    "weights": {
        "b2c3d4e5-f6g7-8901-bcde-f12345678901": 0.5,
        "c3d4e5f6-g7h8-9012-cdef-234567890123": 0.3,
        "d4e5f6g7-h8i9-0123-defg-345678901234": 0.2
    }
}

response = requests.post(distribute_url, json=distribute_data, headers=headers)
if response.status_code == 200:
    result = response.json()
    print(f"Budget distributed: {result['work_items_updated']} items updated")
else:
    print(f"Error: {response.json()}")

# Sync progress from WorkItems
sync_url = f"https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/{ppa_id}/sync-from-workitem/"
response = requests.post(sync_url, headers=headers)
sync_result = response.json()

print(f"Progress updated: {sync_result['previous_progress']}% → {sync_result['updated_progress']}%")
```

### JavaScript (fetch API)

```javascript
// Authentication
const authUrl = "https://obcms.oobc.barmm.gov.ph/api/token/";
const authData = {
  username: "your_username",
  password: "your_password"
};

const response = await fetch(authUrl, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(authData)
});

const tokens = await response.json();
const accessToken = tokens.access;

// Enable WorkItem tracking
const ppaId = "a1b2c3d4-e5f6-7890-abcd-ef1234567890";
const enableUrl = `https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/${ppaId}/enable-workitem-tracking/`;
const enableData = {
  structure_template: "activity",
  budget_distribution_policy: "equal"
};

const enableResponse = await fetch(enableUrl, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${accessToken}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify(enableData)
});

if (enableResponse.ok) {
  const result = await enableResponse.json();
  console.log(`Execution project created: ${result.execution_project_id}`);
  console.log(`Work items created: ${result.work_items_created}`);
} else {
  const error = await enableResponse.json();
  console.error("Error:", error);
}

// Get budget allocation tree
const budgetUrl = `https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/${ppaId}/budget-allocation-tree/`;
const budgetResponse = await fetch(budgetUrl, {
  headers: { "Authorization": `Bearer ${accessToken}` }
});

const budgetTree = await budgetResponse.json();
console.log(`Total Budget: ₱${parseFloat(budgetTree.total_budget).toLocaleString()}`);
console.log(`Allocated: ₱${parseFloat(budgetTree.allocated_budget).toLocaleString()}`);

// Sync progress
const syncUrl = `https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/${ppaId}/sync-from-workitem/`;
const syncResponse = await fetch(syncUrl, {
  method: "POST",
  headers: { "Authorization": `Bearer ${accessToken}` }
});

const syncResult = await syncResponse.json();
console.log(`Progress: ${syncResult.previous_progress}% → ${syncResult.updated_progress}%`);
```

### cURL

```bash
# Authentication
curl -X POST https://obcms.oobc.barmm.gov.ph/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Save the access token from response
ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Enable WorkItem tracking
curl -X POST https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/a1b2c3d4-e5f6-7890-abcd-ef1234567890/enable-workitem-tracking/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"structure_template": "activity", "budget_distribution_policy": "equal"}'

# Get budget allocation tree
curl -X GET https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/a1b2c3d4-e5f6-7890-abcd-ef1234567890/budget-allocation-tree/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Distribute budget (equal)
curl -X POST https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/a1b2c3d4-e5f6-7890-abcd-ef1234567890/distribute-budget/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"method": "equal"}'

# Sync from WorkItem
curl -X POST https://obcms.oobc.barmm.gov.ph/api/v1/monitoring/entries/a1b2c3d4-e5f6-7890-abcd-ef1234567890/sync-from-workitem/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Rate Limiting

### Rate Limit Rules

- **Authenticated Requests**: 1000 requests per hour
- **Unauthenticated Requests**: 100 requests per hour
- **Budget Distribution Operations**: 60 requests per hour

### Rate Limit Headers

Response headers include rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1696577400
```

### Handling Rate Limits

When rate limit is exceeded (429 Too Many Requests):

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 3600,
  "limit": 1000,
  "reset_at": "2025-10-06T12:00:00Z"
}
```

**Recommended handling:**
```python
import time

response = requests.post(url, headers=headers, json=data)

if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
    time.sleep(retry_after)
    response = requests.post(url, headers=headers, json=data)
```

---

## Changelog

### Version 1.0 (2025-10-06)

**Initial Release:**
- `POST /enable-workitem-tracking/` - Enable WorkItem tracking
- `GET /budget-allocation-tree/` - Get budget tree
- `POST /distribute-budget/` - Distribute budget
- `POST /sync-from-workitem/` - Sync progress and status

---

## Support

**For API technical support:**
- Email: bicto-api@oobc.barmm.gov.ph
- Developer Portal: https://developers.obcms.oobc.barmm.gov.ph
- API Status: https://status.obcms.oobc.barmm.gov.ph

**Report Bugs:**
- GitHub Issues: https://github.com/oobc-barmm/obcms/issues

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-06 | Initial API reference documentation | BICTO API Team |
