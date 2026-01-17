# 🧪 SampleMind AI - Manual Testing Guide

**Version:** 1.0 Beta  
**Last Updated:** 2025-10-04  
**Estimated Time:** 30-45 minutes

---

## 📑 Table of Contents

1. [Pre-Testing Setup](#pre-testing-setup)
2. [Test Environment](#test-environment)
3. [Authentication Tests](#authentication-tests)
4. [Dashboard Tests](#dashboard-tests)
5. [Upload Tests](#upload-tests)
6. [Library Tests](#library-tests)
7. [Settings Tests](#settings-tests)
8. [Edge Cases & Error Handling](#edge-cases--error-handling)
9. [Performance Tests](#performance-tests)
10. [Test Results Summary](#test-results-summary)

---

## ✅ Pre-Testing Setup

### Prerequisites Checklist

```
┌─────────────────────────────────────────────────────────┐
│                 BEFORE YOU START                         │
└─────────────────────────────────────────────────────────┘

[ ] Services are running (./quick_start.sh)
[ ] Database is clean (optional: docker-compose down -v)
[ ] Browser is open (Chrome/Firefox recommended)
[ ] DevTools are open (F12)
[ ] Network tab is visible
[ ] Console has no errors
[ ] You have a pen and paper for notes
```

### Start the Application

```bash
# 1. Navigate to project directory
cd ~/Projects/samplemind-ai-v6

# 2. Start all services
./quick_start.sh

# 3. Wait for startup (2-3 minutes)
# ✓ Backend API: http://localhost:8000
# ✓ Frontend: http://localhost:3000
# ✓ MongoDB: localhost:27017
# ✓ Redis: localhost:6379

# 4. Verify services
./quick_start.sh status
```

### Test Data Preparation

```bash
# Create test audio files (if needed)
mkdir -p test_files

# Small test file (~1MB)
# Medium test file (~10MB)
# Large test file (~45MB)
```

---

## 🌐 Test Environment

### Browser Compatibility

Test in multiple browsers:

```
[ ] Chrome/Chromium (Primary)
[ ] Firefox
[ ] Safari (if on macOS)
[ ] Edge
```

### Screen Sizes

```
[ ] Desktop (1920x1080)
[ ] Laptop (1366x768)
[ ] Tablet (768x1024)
[ ] Mobile (375x667)
```

---

## 🔐 Authentication Tests

### Test 1: User Registration

**URL:** `http://localhost:3000/register`

**Test Steps:**

```
┌─────────────────────────────────────────────────────────┐
│              TEST 1.1: Successful Registration           │
└─────────────────────────────────────────────────────────┘

1. Navigate to /register
   [ ] Page loads without errors
   [ ] All form fields are visible
   [ ] Submit button is present

2. Fill in email
   [ ] Email field accepts input
   [ ] Email validation works (invalid@)
   [ ] Error shows for invalid email

3. Fill in username
   [ ] Username field accepts input
   [ ] Character limit shown (3-50)
   [ ] Pattern validation works (letters/numbers/underscore)
   [ ] Error shows for invalid characters

4. Fill in password: "test"
   [ ] Password strength meter appears
   [ ] Shows RED/Very Weak
   [ ] Feedback message displayed

5. Update password: "Test123"
   [ ] Meter changes to ORANGE/Fair
   [ ] Feedback updates

6. Update password: "Test123!"
   [ ] Meter changes to YELLOW/Good
   [ ] Feedback updates

7. Update password: "SecureTest2025!@#"
   [ ] Meter changes to GREEN/Strong
   [ ] Feedback shows "Great password!"

8. Confirm password (mismatch first)
   [ ] Type "WrongPassword"
   [ ] Red error appears: "Passwords do not match"

9. Confirm password (match)
   [ ] Type "SecureTest2025!@#"
   [ ] Green checkmark appears: "✓ Passwords match"

10. Try submit WITHOUT Terms checkbox
    [ ] Error toast appears
    [ ] Form does not submit
    [ ] Error message: "You must agree to the Terms of Service"

11. Check Terms of Service checkbox
    [ ] Checkbox is checked
    [ ] Links to Terms and Privacy are clickable

12. Submit form
    [ ] Loading state shows "Creating account..."
    [ ] Success toast appears
    [ ] Redirects to /dashboard
    [ ] Dashboard loads successfully

Result: [ ] PASS  [ ] FAIL
Notes: _______________________________________________
```

![Screenshot Placeholder: Registration Page with Password Strength Meter]

---

### Test 2: User Login

**URL:** `http://localhost:3000/login`

```
┌─────────────────────────────────────────────────────────┐
│              TEST 2.1: Successful Login                  │
└─────────────────────────────────────────────────────────┘

1. Navigate to /login
   [ ] Page loads without errors
   [ ] Email/Username field present
   [ ] Password field present
   [ ] Remember Me checkbox present
   [ ] Forgot password link present

2. Test "Remember Me" functionality
   [ ] Enter username: "testuser"
   [ ] Check "Remember Me" checkbox
   [ ] Enter password
   [ ] Click "Sign in"

3. Verify login success
   [ ] Success toast appears
   [ ] Redirects to /dashboard
   [ ] User data loads

4. Test persistent login
   [ ] Close browser tab
   [ ] Reopen and go to /login
   [ ] Username is pre-filled
   [ ] "Remember Me" is checked
   [ ] Only password needs to be entered

Result: [ ] PASS  [ ] FAIL
```

```
┌─────────────────────────────────────────────────────────┐
│              TEST 2.2: Failed Login                      │
└─────────────────────────────────────────────────────────┘

1. Wrong credentials
   [ ] Enter wrong username
   [ ] Enter wrong password
   [ ] Error toast appears
   [ ] Stays on login page

2. Empty fields
   [ ] Try submit with empty username
   [ ] Browser validation appears
   [ ] Try submit with empty password
   [ ] Browser validation appears

Result: [ ] PASS  [ ] FAIL
```

![Screenshot Placeholder: Login Page with Remember Me]

---

### Test 3: Forgot Password

**URL:** `http://localhost:3000/forgot-password`

```
┌─────────────────────────────────────────────────────────┐
│          TEST 3.1: Password Reset Flow                   │
└─────────────────────────────────────────────────────────┘

1. Click "Forgot password?" on login page
   [ ] Redirects to /forgot-password
   [ ] Email field is visible
   [ ] "Send Reset Link" button present
   [ ] "Back to sign in" link present

2. Enter invalid email
   [ ] Type "notanemail"
   [ ] Error appears: "Please enter a valid email address"

3. Enter valid email
   [ ] Type "test@example.com"
   [ ] No validation errors

4. Submit form
   [ ] Loading state shows "Sending..."
   [ ] Success state appears
   [ ] Shows "Check your email" message
   [ ] Email address is displayed
   [ ] "Send to different email" button visible

5. Test back navigation
   [ ] Click "Back to sign in"
   [ ] Redirects to /login

Result: [ ] PASS  [ ] FAIL
```

![Screenshot Placeholder: Forgot Password Success State]

---

## 📊 Dashboard Tests

**URL:** `http://localhost:3000/dashboard`

```
┌─────────────────────────────────────────────────────────┐
│          TEST 4.1: Dashboard Overview                    │
└─────────────────────────────────────────────────────────┘

1. Dashboard loads
   [ ] Page loads without errors
   [ ] Statistics cards visible
   [ ] Recent uploads section visible
   [ ] Quick actions buttons visible

2. Statistics display
   [ ] Total Files count shows
   [ ] Analyzed count shows
   [ ] Storage usage shows
   [ ] This week count shows

3. Recent uploads
   [ ] Up to 5 recent files shown
   [ ] File names displayed
   [ ] Status badges shown (Analyzed/Pending)
   [ ] Upload time shown

4. Quick actions
   [ ] "Upload New File" button works
   [ ] "View Library" button works
   [ ] "Settings" button works

Result: [ ] PASS  [ ] FAIL
```

---

## ⬆️ Upload Tests

**URL:** `http://localhost:3000/upload`

```
┌─────────────────────────────────────────────────────────┐
│          TEST 5.1: Audio File Upload                     │
└─────────────────────────────────────────────────────────┘

1. Navigate to upload page
   [ ] Drag & drop zone visible
   [ ] "Choose File" button works
   [ ] Supported formats listed

2. Upload small file (MP3, <5MB)
   [ ] Select file via file picker
   [ ] File name displays
   [ ] File size shows
   [ ] Tags field available
   [ ] Description field available

3. Add metadata
   [ ] Add tags: "test, electronic, 128bpm"
   [ ] Add description: "Test upload"
   [ ] Metadata saves with file

4. Upload file
   [ ] Click "Upload File"
   [ ] Progress bar appears
   [ ] Progress shows 0-100%
   [ ] Success message appears
   [ ] File appears in library

Result: [ ] PASS  [ ] FAIL

Notes on upload time: _______________
```

```
┌─────────────────────────────────────────────────────────┐
│          TEST 5.2: Upload Error Handling                 │
└─────────────────────────────────────────────────────────┘

1. Test unsupported format
   [ ] Try upload .txt file
   [ ] Error message appears
   [ ] Upload is rejected

2. Test file too large (>50MB)
   [ ] Try upload 60MB file
   [ ] Error: "File too large"
   [ ] Upload is rejected

3. Test duplicate upload
   [ ] Upload same file twice
   [ ] Behavior: (document what happens)

Result: [ ] PASS  [ ] FAIL
```

![Screenshot Placeholder: Upload Page with Progress Bar]

---

## 📚 Library Tests

**URL:** `http://localhost:3000/library`

```
┌─────────────────────────────────────────────────────────┐
│          TEST 6.1: Library Browse & Search               │
└─────────────────────────────────────────────────────────┘

1. Library page loads
   [ ] Files display in grid layout
   [ ] Each file card shows:
       [ ] Checkbox (top-right)
       [ ] File icon
       [ ] Filename
       [ ] File size
       [ ] Format badge
       [ ] Status badge
       [ ] Tags (if any)
       [ ] Upload date
       [ ] Action buttons

2. Search functionality
   [ ] Type filename in search box
   [ ] Results filter in real-time
   [ ] Matching files displayed
   [ ] Non-matching files hidden

3. Search by tags
   [ ] Type tag name in search
   [ ] Files with matching tags shown
   [ ] Results accurate

4. Empty state
   [ ] Delete all files (if any)
   [ ] Empty state appears
   [ ] Message: "No audio files yet"
   [ ] "Upload Files" button present

Result: [ ] PASS  [ ] FAIL
```

```
┌─────────────────────────────────────────────────────────┐
│          TEST 6.2: Individual File Actions               │
└─────────────────────────────────────────────────────────┘

1. View file details
   [ ] Click "Details" button
   [ ] Modal opens
   [ ] All file info displayed:
       [ ] File size
       [ ] Duration
       [ ] Format
       [ ] Sample rate
       [ ] Status
   [ ] Modal can be closed

2. Analyze file (if pending)
   [ ] Click "Analyze" button
   [ ] Confirmation or immediate start
   [ ] Status changes to "Processing"
   [ ] Eventually changes to "Analyzed"

Result: [ ] PASS  [ ] FAIL
```

![Screenshot Placeholder: Library Grid View]

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 6.3: Bulk Operations - CRITICAL!           │
└─────────────────────────────────────────────────────────┘

SETUP: Have at least 3 files in library

1. Individual selection
   [ ] Click checkbox on File 1
   [ ] Blue ring appears around card
   [ ] Card background changes to blue tint
   [ ] Count badge appears: "1 selected"
   [ ] Bulk toolbar appears

2. Multiple selection
   [ ] Click checkbox on File 2
   [ ] Both files highlighted
   [ ] Count badge: "2 selected"
   [ ] Click checkbox on File 3
   [ ] Count badge: "3 selected"

3. Deselect individual file
   [ ] Click checkbox on File 2 again
   [ ] File 2 unhighlights
   [ ] Count badge: "2 selected"
   [ ] Other files still selected

4. Select All functionality
   [ ] Click "Select All" button
   [ ] ALL files get checkboxes checked
   [ ] ALL files highlighted with blue ring
   [ ] Count badge shows correct total
   [ ] Button text changes to "Deselect All"

5. Deselect All functionality
   [ ] Click "Deselect All" button
   [ ] ALL checkboxes unchecked
   [ ] ALL files unhighlighted
   [ ] Bulk toolbar disappears
   [ ] Count badge disappears

Result: [ ] PASS  [ ] FAIL
```

![Screenshot Placeholder: Library with Files Selected]

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 6.4: Bulk Tag Operation                    │
└─────────────────────────────────────────────────────────┘

1. Select multiple files (2-3)
   [ ] Files are selected
   [ ] Count badge shows correct number

2. Click "Tag" button
   [ ] Modal opens: "Add Tags to Multiple Files"
   [ ] Shows count: "Adding tags to X file(s)"
   [ ] Tags input field present
   [ ] Helper text: "Separate multiple tags with commas"

3. Add tags
   [ ] Type: "summer, upbeat, new"
   [ ] No validation errors
   [ ] "Add Tags" button enabled

4. Submit
   [ ] Click "Add Tags"
   [ ] Loading state appears
   [ ] Success toast: "Tagged X file(s)"
   [ ] Modal closes
   [ ] Files deselected automatically
   [ ] Tags appear on file cards

5. Cancel operation
   [ ] Select files again
   [ ] Click "Tag"
   [ ] Click "Cancel" in modal
   [ ] Modal closes
   [ ] No changes made
   [ ] Files still selected

Result: [ ] PASS  [ ] FAIL
```

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 6.5: Bulk Export Operation                 │
└─────────────────────────────────────────────────────────┘

1. Select files
   [ ] Select 2-3 files
   [ ] Count badge correct

2. Click "Export" button
   [ ] Info toast: "Exporting X file(s)..."
   [ ] Success toast: "Export started! Download will begin shortly"
   [ ] Download begins (check browser downloads)

3. Verify download
   [ ] ZIP file downloaded
   [ ] File size reasonable
   [ ] Can open ZIP file
   [ ] Contains selected files

Result: [ ] PASS  [ ] FAIL
```

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 6.6: Bulk Delete Operation - CRITICAL!     │
└─────────────────────────────────────────────────────────┘

1. Select files to delete
   [ ] Select 2-3 files (MAKE COPIES FIRST!)
   [ ] Count badge shows correct number

2. Click "Delete" button (red)
   [ ] Modal opens: "Delete Multiple Files"
   [ ] Warning section (red background):
       [ ] Shows count: "⚠️ You are about to delete X file(s)"
       [ ] Warning text about permanent deletion
       [ ] Analysis deletion warning

3. Confirm deletion
   [ ] Click "Delete X File(s)" button
   [ ] Loading state appears
   [ ] Success toast: "Deleted X file(s)"
   [ ] Modal closes
   [ ] Files removed from library
   [ ] Count updates correctly

4. Cancel deletion
   [ ] Select files again
   [ ] Click "Delete"
   [ ] Click "Cancel" in modal
   [ ] Modal closes
   [ ] No files deleted
   [ ] Files still selected

Result: [ ] PASS  [ ] FAIL
```

![Screenshot Placeholder: Bulk Delete Confirmation Modal]

---

## ⚙️ Settings Tests

**URL:** `http://localhost:3000/settings`

```
┌─────────────────────────────────────────────────────────┐
│          TEST 7.1: Profile Information                   │
└─────────────────────────────────────────────────────────┘

1. Settings page loads
   [ ] Profile Information section visible
   [ ] Email field shows current email
   [ ] Username field shows current username
   [ ] "Save Changes" button present
   [ ] "Reset" button present

2. Edit fields
   [ ] Change email address
   [ ] Change username
   [ ] "Save Changes" button enables
   [ ] Click "Reset"
   [ ] Fields revert to original values

3. Save changes
   [ ] Make changes again
   [ ] Click "Save Changes"
   [ ] Success toast appears
   [ ] Changes persist after refresh

Result: [ ] PASS  [ ] FAIL
```

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 7.2: Change Password                       │
└─────────────────────────────────────────────────────────┘

1. Open password modal
   [ ] Click "Change Password" button
   [ ] Modal opens: "Change Password"
   [ ] Current password field present
   [ ] New password field present
   [ ] Confirm password field present

2. Test validation
   [ ] Leave current password empty
   [ ] Enter new password
   [ ] Button should be disabled

3. Test password mismatch
   [ ] Fill current password
   [ ] New password: "NewPass123!"
   [ ] Confirm: "DifferentPass"
   [ ] Error appears: "Passwords do not match"

4. Successful change
   [ ] Fill current password correctly
   [ ] New password: "NewSecure2025!"
   [ ] Confirm: "NewSecure2025!"
   [ ] Click "Change Password"
   [ ] Success toast appears
   [ ] Modal closes
   [ ] Fields cleared

5. Cancel operation
   [ ] Open modal again
   [ ] Fill fields
   [ ] Click "Cancel"
   [ ] Modal closes
   [ ] No changes made

Result: [ ] PASS  [ ] FAIL
```

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 7.3: Change Email - NEW FEATURE!           │
└─────────────────────────────────────────────────────────┘

1. Open email change modal
   [ ] Click "Change Email" button in Security section
   [ ] Modal opens: "Change Email Address"
   [ ] Shows current email in blue box
   [ ] New email field present
   [ ] Password field present (for confirmation)

2. Test validation
   [ ] Enter invalid email: "notanemail"
   [ ] Try to submit
   [ ] Error appears

3. Test with wrong password
   [ ] Enter valid new email
   [ ] Enter wrong password
   [ ] Click "Change Email"
   [ ] Error toast appears
   [ ] No change made

4. Successful change
   [ ] Enter valid new email
   [ ] Enter correct password
   [ ] Click "Change Email"
   [ ] Success toast: "Email change request sent! Check your new email to verify"
   [ ] Modal closes
   [ ] Fields cleared

5. Cancel operation
   [ ] Open modal
   [ ] Fill fields
   [ ] Click "Cancel"
   [ ] Modal closes
   [ ] No changes

Result: [ ] PASS  [ ] FAIL
```

![Screenshot Placeholder: Change Email Modal]

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 7.4: Delete Account - CRITICAL!            │
└─────────────────────────────────────────────────────────┘

⚠️  WARNING: Use a test account for this test!

1. Open delete account modal
   [ ] Scroll to "Danger Zone" section (red border)
   [ ] Click "Delete Account" button
   [ ] Modal opens: "Delete Account"

2. Verify warning section
   [ ] Red background warning box visible
   [ ] Warning title: "⚠️ Warning: This action is permanent!"
   [ ] Bullet points list consequences:
       [ ] All audio files will be deleted
       [ ] All analysis results will be lost
       [ ] Account cannot be recovered
       [ ] Action cannot be undone

3. Test password validation
   [ ] Leave password empty
   [ ] Type confirmation text: "DELETE"
   [ ] Button should be disabled

4. Test confirmation text validation
   [ ] Enter password
   [ ] Type "delete" (lowercase)
   [ ] Button should be disabled
   [ ] Type "DELET" (wrong spelling)
   [ ] Button should be disabled

5. Test cancel
   [ ] Fill both fields correctly
   [ ] Click "Cancel"
   [ ] Modal closes
   [ ] No deletion occurs

6. Successful deletion (TEST ACCOUNT ONLY!)
   [ ] Enter correct password
   [ ] Type exactly: "DELETE"
   [ ] Button enables
   [ ] Click "Delete My Account"
   [ ] Loading state appears
   [ ] Success toast appears
   [ ] Redirects to goodbye/login page
   [ ] Account is deleted
   [ ] Cannot login with old credentials

Result: [ ] PASS  [ ] FAIL  [ ] SKIPPED
```

![Screenshot Placeholder: Delete Account Confirmation Modal]

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 7.5: Account Status Section                │
└─────────────────────────────────────────────────────────┘

1. Verify displayed information
   [ ] Account Status badge (Active/Inactive)
   [ ] Email Verification badge
   [ ] Checkmark icon if verified
   [ ] Member Since date
   [ ] Total Uploads count

2. Verify formatting
   [ ] Date is formatted nicely
   [ ] Badges have correct colors
   [ ] Icons display correctly

Result: [ ] PASS  [ ] FAIL
```

---

```
┌─────────────────────────────────────────────────────────┐
│          TEST 7.6: 2FA Section (Future Feature)          │
└─────────────────────────────────────────────────────────┘

1. Verify 2FA section
   [ ] Section has blue background (not gray)
   [ ] Title: "Two-Factor Authentication"
   [ ] Description: "Add an extra layer of security (Coming in v1.1)"
   [ ] Badge says: "v1.1 Feature" (not "Coming Soon")
   [ ] No active button to enable 2FA

Result: [ ] PASS  [ ] FAIL
```

---

## 🚨 Edge Cases & Error Handling

```
┌─────────────────────────────────────────────────────────┐
│          TEST 8.1: Network Errors                        │
└─────────────────────────────────────────────────────────┘

1. Simulate offline mode
   [ ] Open DevTools → Network tab
   [ ] Set throttling to "Offline"
   [ ] Try to login
   [ ] Error toast appears
   [ ] Graceful error message shown

2. Simulate slow connection
   [ ] Set throttling to "Slow 3G"
   [ ] Try to upload file
   [ ] Progress bar updates slowly
   [ ] Eventually completes or times out gracefully

Result: [ ] PASS  [ ] FAIL
```

```
┌─────────────────────────────────────────────────────────┐
│          TEST 8.2: Session Expiry                        │
└─────────────────────────────────────────────────────────┘

1. Login and wait
   [ ] Login to application
   [ ] Wait for token to expire (30 minutes)
   [ ] Try to perform action
   [ ] Error or redirect to login
   [ ] Appropriate message shown

2. Test refresh token
   [ ] Login
   [ ] Use app normally for 15 minutes
   [ ] Token should refresh automatically
   [ ] No interruption to user

Result: [ ] PASS  [ ] FAIL
```

```
┌─────────────────────────────────────────────────────────┐
│          TEST 8.3: Browser Compatibility                 │
└─────────────────────────────────────────────────────────┘

Test in multiple browsers:

Chrome:
[ ] All features work
[ ] No console errors
[ ] Styling correct

Firefox:
[ ] All features work
[ ] No console errors
[ ] Styling correct

Safari (if available):
[ ] All features work
[ ] No console errors
[ ] Styling correct

Result: [ ] PASS  [ ] FAIL
```

---

## ⚡ Performance Tests

```
┌─────────────────────────────────────────────────────────┐
│          TEST 9.1: Page Load Performance                 │
└─────────────────────────────────────────────────────────┘

Use DevTools → Lighthouse

1. Dashboard performance
   [ ] Open /dashboard
   [ ] Run Lighthouse audit
   [ ] Performance score: ___/100
   [ ] First Contentful Paint: ___ms
   [ ] Time to Interactive: ___ms

2. Library performance (with many files)
   [ ] Upload 20+ files
   [ ] Navigate to library
   [ ] Page loads in <3 seconds
   [ ] Scrolling is smooth
   [ ] No lag when selecting files

Result: [ ] PASS  [ ] FAIL

Scores: _________________________________
```

```
┌─────────────────────────────────────────────────────────┐
│          TEST 9.2: Memory Leaks                          │
└─────────────────────────────────────────────────────────┘

1. Navigate between pages
   [ ] Open DevTools → Memory tab
   [ ] Take heap snapshot
   [ ] Navigate to all pages 5 times
   [ ] Take another snapshot
   [ ] Compare snapshots
   [ ] Memory increase should be minimal

Result: [ ] PASS  [ ] FAIL

Memory change: _________________________________
```

---

## 📋 Test Results Summary

### Overall Results

```
Test Category                    | Pass | Fail | Skip | Notes
---------------------------------|------|------|------|-------
Authentication (3 tests)         | [ ]  | [ ]  | [ ]  | 
Dashboard (1 test)               | [ ]  | [ ]  | [ ]  | 
Upload (2 tests)                 | [ ]  | [ ]  | [ ]  | 
Library Browse (2 tests)         | [ ]  | [ ]  | [ ]  | 
Bulk Operations (4 tests)        | [ ]  | [ ]  | [ ]  | 
Settings - Profile (1 test)      | [ ]  | [ ]  | [ ]  | 
Settings - Password (1 test)     | [ ]  | [ ]  | [ ]  | 
Settings - Email (1 test)        | [ ]  | [ ]  | [ ]  | 
Settings - Delete (1 test)       | [ ]  | [ ]  | [ ]  | 
Edge Cases (3 tests)             | [ ]  | [ ]  | [ ]  | 
Performance (2 tests)            | [ ]  | [ ]  | [ ]  | 
---------------------------------|------|------|------|-------
TOTAL (21 tests)                 | [ ]  | [ ]  | [ ]  | 
```

### Critical Features Status

```
Feature                          | Status | Priority | Notes
---------------------------------|--------|----------|-------
Login with Remember Me           | [ ]    | CRITICAL |
Password Strength Meter          | [ ]    | CRITICAL |
Bulk File Selection              | [ ]    | CRITICAL |
Bulk Delete with Confirmation    | [ ]    | CRITICAL |
Delete Account with Confirmation | [ ]    | CRITICAL |
Change Email                     | [ ]    | HIGH     |
Forgot Password Flow             | [ ]    | HIGH     |
File Upload                      | [ ]    | HIGH     |
Search & Filter                  | [ ]    | MEDIUM   |
```

### Bugs Found

```
Bug #  | Severity | Page     | Description              | Steps to Reproduce
-------|----------|----------|--------------------------|-------------------
1      | [ ]      | [ ]      |                          |
2      | [ ]      | [ ]      |                          |
3      | [ ]      | [ ]      |                          |
```

**Severity Levels:**
- 🔴 **Critical**: Prevents core functionality
- 🟠 **High**: Major feature broken
- 🟡 **Medium**: Minor feature issue
- 🟢 **Low**: Cosmetic or minor issue

---

## 📝 Testing Notes

### Environment Details

```
Date: _______________
Tester: _______________
Browser: _______________
OS: _______________
Screen Resolution: _______________
Backend Version: _______________
Frontend Version: _______________
```

### Additional Observations

```
Positive Findings:
- _________________________________________________
- _________________________________________________
- _________________________________________________

Areas for Improvement:
- _________________________________________________
- _________________________________________________
- _________________________________________________

Unexpected Behavior:
- _________________________________________________
- _________________________________________________
- _________________________________________________
```

---

## ✅ Sign-Off

```
[ ] All critical tests passed
[ ] All bugs documented
[ ] Screenshots captured (if needed)
[ ] Ready for beta release
[ ] Ready for production

Tester Signature: _______________
Date: _______________
```

---

## 🎯 Quick Testing Checklist (5 Minutes)

For rapid smoke testing:

```
[ ] Can register new account
[ ] Can login successfully
[ ] Password strength meter works
[ ] Can upload a file
[ ] Can select multiple files in library
[ ] Bulk delete shows confirmation modal
[ ] Delete account requires password + "DELETE"
[ ] Change email modal opens and works
[ ] All pages load without errors
[ ] No console errors in DevTools
```

---

## 📚 Related Documentation

- [USER_GUIDE.md](./USER_GUIDE.md) - Complete user guide
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Command reference
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Fix common issues
- [PROGRESS_REPORT.md](./PROGRESS_REPORT.md) - Development progress

---

**Testing Duration:** Estimated 30-45 minutes for full test  
**Quick Test:** 5 minutes for smoke test  
**Last Updated:** 2025-10-04

---

*Happy Testing! 🧪🔬*

**Remember:** The goal is not just to find bugs, but to ensure an amazing user experience! 🎯
