Table Of Contents
=================

- [API](#api)
  - [Auth API](#auth-api)
  - [Register API](#register-api)
  - [Search API](#search-api)
  - [Predict API](#predict-api)
- [Page Links](#page-links)
  - [Claim Resources](#claim-resources)
  - [User Resources](#user-resources)

# Api

## Auth API

### Usage

- URL: `/api/auth/`
- Content-Type: `application/json`
- Field:
  - username > Username
  - password > User password

### Response

**_Api Key_**

### Description

User login to get **_Api Key_**.

## Register API

### Usage

- URL: `/api/registration/`
- Content-Type: `application/json`
- Field:
  - username > Username
  - email > User email
  - password > User password

### Response

Response status

### Description

Register new user

## Search API

### Usage

- URL: `/api/search/`
- Content-Type: `application/json`
- x-api-key: <USER_API_KEY>
- Field:
  - keyword > "Text to search"
  - begin > Start index [Optional]
  - limit > Maximum Result [Optional]

### Response

Dictionary of search result:
{ "attachment",
"author_id",
"comment_id",
"date_created",
"description",
"downvote",
"fake",
"id",
"num_click":,
"title",
"upvote",
"url",
"verified_by" }

### Description

Search claims with given keywords.

## Predict API

### Usage

- URL: `/api/predict/`
- Content-Type: `application/json`
- Field:
  - title > Title of claim
  - content > Content of claim

### Response

Dictionary of claim prediction
{ "claim":,
"prediction",
"val_prediction" }

### Description

Predict claim fake or fact

# Page Links

## Claim Resources

- URL: `/uploads/claim/<resources>`
- Content-Type: **None**
- x-api-key: <USER_API_KEY>

# Page Links

## User Resources

- URL: `/uploads/profil/<resources>`
- Content-Type: **None**
- x-api-key: <User API Key>
