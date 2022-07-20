Table Of Contents
=================

- [API](#api)
  - [Auth API](#auth-api)
  - [Register API](#register-api)
  - [Search API](#search-api)
  - [Predict API](#predict-api)
  - [Get Profile Details](#get-profile-details)
  - [Get Claim Details](#get-claim-details)
  - [Set Own Profile](#set-own-profile)
  - [Set Claim Details](#set-claim-details)
  - [Create New Claim](#create-new-claim)
  - [Delete Claim](#delete-claim)
  - [List My Claims](#list-my-claims)
  - [Add bookmarks](#add-bookmarks)
  - [Remove bookmarks](#remove-bookmarks)
  - [List bookmarks](#list-bookmarks)
  - [Up Votes](#up-votes)
  - [Up Votes](#down-votes)
  - [Get Comments](#get-comments)
  - [Create Comments](#create-comments)
  - [Delete Comments](#delete-comments)
  - [Reset Password by Email](#reset-password-by-email)
  - [Confirm Verification Code](#confirm-verification-code)
  - [Reset Password](#reset-password)
  - [Change Password](#change-password)
  - [Get API Session](#get-api-session)
  - [Logout](#logout)
- [Page Links](#page-links)
  - [Claim Resources](#claim-resources)
  - [User Avatar](#user-avatar)

# Api

## Auth API

### Usage

- URL: `/api/auth/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- Fields:
  - email > Email
  - password > User password

### Response

Dictonary of result
```json
{
"Api Key",
"user_id"
}
```

### Description

User login to get **_Api Key_**.

## Register API

### Usage

- URL: `/api/registration/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- Fields:
  - username > Username
  - email > User email
  - full_name > Full name [Optional]
  - password > User password

### Response

Give Dictionary of user details

**Error**:
> `Username already exist` `Invalid username format` `Invalid email format` `Password too short` `Email already exist`

### Description

Register new user

## Search API

### Usage

- URL: `/api/search/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - keyword > "Text to search"
  - begin > Start index [Optional]
  - limit > Maximum Result [Optional]

### Response

Array of dictionary search result:

```json
{ 
  "attachment",
  "author_id",
  "comment_id",
  "date_created",
  "description",
  "downvote",
  "fake",
  "id",
  "num_click",
  "title",
  "upvote",
  "url",
  "verified_by"
  }
  ```

### Description

Search claims with given keywords.

## Predict API

### Usage

- URL: `/api/predict/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - title > Title of claim
  - content > Content of claim

### Response

Dictionary of claim prediction

```json
{
  "claim",
  "prediction",
  "val_prediction"
}
```

### Description

Predict claim fake or fact

## Get Profile Details

### Usage

- URL: `/api/get/profile/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id > Target User ID to Query

### Response

Dictionary of User Details
Return null for personal information like email, bookmarks, votes

```json
{
  "id",
  "username",
  "full_name",
  "email",
  "bookmarks",
  "date_created",
  "verified",
  "votes"
}
```

### Description

Get user details by ID

## Get Claim Details

### Usage

- URL: `/api/get/claim/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id > Target Claim ID to Query

### Response

Dictionary of User Details

```json
{
  "id",
  "title",
  "description",
  "fake",
  "author_id",
  "date_created",
  "attachment",
  "url",
  "upvote",
  "downvote",
  "num_click",
  "verified_by",
  "comment_id"
}
```
**Error**:
> _NOT ACCEPTABLE_

### Description

Get claim details by ID

## Set Own Profile

### Usage

- URL: `/api/set/profile/`
- Content-Type: `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Maximum File Size Allowed: `2 MiB`
- Allowed Upload Extensions: `JPG` `JPEG` `PNG` `BMP` 
- Changeable Fields:
  - email > Change email [Optional]
  - full_name > Change Full name [Optional]
  - bookmarks > Change bookmarks list [Optional]
  - avatar > Change Profile Picture (Upload File) [Optional]

### Response

**Error**:
> _Extension not allowed_,  _File size is too big_, _Email already exist_, _Invalid email format_

### Description

Set Own Profile Attributes

## Set Claim Details

### Usage

- URL: `/api/set/claim/`
- Content-Type: `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Maximum File Size Allowed: `5 MiB`
- Allowed Upload Extensions: `JPG` `JPEG` `PNG` `BMP` 
- Required Fields:
  - id -> Claim id
- Changeable Fields:
  - title > Change claim title [Optional]
  - description > Change claim description [Optional]
  - fake > Change status Fake or Fact (**as integer**) [Optional]
  - url > Change url
  - bookmarks > User bookmarks 
  - [...attachment_files...] > Change attachment files (just upload file with random field) [Optional]

### Response

**Error**:
> _Extension not allowed_, _File size is too big_

### Description

Set claim details

## Create new Claim

### Usage

- URL: `/api/create/claim/`
- Content-Type: `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Maximum File Size Allowed: `5 MiB`
- Allowed Upload Extensions: `JPG` `JPEG` `PNG` `BMP` 
- Fields:
  - title > Change claim title
  - description > Change claim description
  - fake > Change status Fake or Fact (**as integer**)
  - url > Change url
  - [...attachment_files...] > Change attachment files (just upload file with random field) [Optional]

### Response

**Error**:
> _Extension not allowed_, _File size is too big_

### Description

Create new Claim

## Delete Claim

### Usage

- URL: `/api/delete/claim/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id -> Claim id

### Response

**Error**:
> Forbidden 403

### Description

Delete Claim

## List My Claims

### Usage

- URL: `/api/get/myclaims/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Field:
  - start -> Start index [Optional]
  - limit -> Max total result [Optional]

### Response

Give array of claim details

### Description

List all of claims created by user

## Add Bookmarks

### Usage

- URL: `/api/bookmarks/add/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id -> Claim ID

### Response

Response status

### Description

Add claim to current user bookmarks

## Remove Bookmarks

### Usage

- URL: `/api/bookmarks/remove/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id -> Claim ID
### Response

Response status

### Description

Remove claim to current user bookmarks

## List Bookmarks

### Usage

- URL: `/api/bookmarks/list/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>

### Response

Array of claim details

### Description

List all bookmarked claims by current user

## Up Votes

### Usage

- URL: `/api/votes/up/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id -> Claim ID
### Response

Response status

### Description

Votes up given claim

## Down Votes

### Usage

- URL: `/api/votes/down/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id -> Claim ID
### Response

Response status

### Description

Votes down given claim

## Get Comments

### Usage

- URL: `/api/get/comments/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - claim_id -> Claim ID

### Response

List of comment

### Description

Get comments for selected claim

## Create Comments

### Usage

- URL: `/api/create/comments/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - claim_id -> Claim ID
  - text -> Comment Text

### Response

return `Comment.ID`

### Description

Create new comment

## Delete Comments

### Usage

- URL: `/api/delete/comments/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - id -> Comment ID

### Response

**Error**:
> _User not have permission_

### Description

Delete comment by ID

## Reset Password By Email

### Usage

- URL: `/api/auth/reset/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- Fields:
  - email -> User email want to reset

### Response

Return `User.ID`

**ERROR**:
> _User not found_

### Description

Reset password by sent verification code to user email

## Confirm Verification Code

### Usage

- URL: `/api/auth/confirm/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- Fields:
  - user_id -> User ID who doing verification
  - verification_code -> Verification code that already sent to user email

### Response

Return 24 digit `reset_key`

**ERROR**:
> _Wrong verification code_, _Reset timeout_, _The user is not resetting the password_

### Description

Get Reset key to continue to change password

## Reset Password

### Usage

- URL: `/api/set/password/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- Fields:
  - reset_key -> Reset key given after confirm verification code
  - new_password -> New password

### Response

**Error**:
> `This user is not resetting the password`

### Description

Change password by reset key

## Change Password

### Usage

- URL: `/api/set/password/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>
- Fields:
  - current_password -> User current password
  - new_password -> New password

### Response

**Error**:
> _Password to short_, _Wrong current password_

### Description

Change password by give current password

## Logout

### Usage

- URL: `/api/logout/`
- Content-Type: `application/json` or `application/x-www-form-urlencoded` or `multipart/form-data`
- x-api-key: <USER_API_KEY>

### Response

No Response

### Description

Delete current api key and logout

# Page Links

## Get API Session

### Usage

- URL: `/api/session/`
- x-api-key: <USER_API_KEY>

### Response

Return dictionary of api_key, user_id, date_login

### Description

Return current session

## Claim Resources

- URL: `/uploads/claim/<claim_id>/<resources_path>`
- Content-Type: **None**

## User Avatar

- URL: `/uploads/avatar/<user_id>`
- Content-Type: **None**
- x-api-key: <User_API_Key>
