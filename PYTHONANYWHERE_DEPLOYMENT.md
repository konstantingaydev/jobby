# PythonAnywhere Deployment Guide

## Issues Fixed for Drag-and-Drop

### Problems Identified:
1. **Missing STATIC_ROOT** - PythonAnywhere couldn't serve static files (kanban.js)
2. **Inline Event Handlers** - CSP policies may block `ondrop`, `ondragover`, `ondragstart`
3. **CSRF Cookie Settings** - JavaScript couldn't read CSRF token
4. **ALLOWED_HOSTS** - Not configured for production

### Solutions Applied:

#### 1. Settings Configuration (`jobby/settings.py`)
- Added `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- Set `ALLOWED_HOSTS = ['*']` (configure with your domain)
- Added CSRF settings:
  ```python
  CSRF_COOKIE_SECURE = False  # Set to True if HTTPS only
  CSRF_COOKIE_HTTPONLY = False  # Must be False for JS access
  SESSION_COOKIE_SECURE = False  # Set to True if HTTPS only
  ```

#### 2. Removed Inline Event Handlers
- Removed `ondrop`, `ondragover`, `ondragstart` from HTML
- Added proper event listeners in JavaScript
- Improved error handling and visual feedback

## Deployment Steps for PythonAnywhere

### Step 1: Collect Static Files
Run this command in your PythonAnywhere bash console:
```bash
cd ~/jobby
python manage.py collectstatic --noinput
```

### Step 2: Configure Static Files in Web Tab
In PythonAnywhere Web tab, add static files mapping:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/jobby/staticfiles/`

### Step 3: Reload Web App
Click "Reload" button in the PythonAnywhere Web tab.

### Step 4: Test Drag-and-Drop
1. Log in as a recruiter
2. Navigate to kanban board
3. Try dragging a candidate card between stages
4. Check browser console (F12) for any JavaScript errors

## Troubleshooting

### If drag-and-drop still doesn't work:

#### Check Static Files Are Loading
1. Open browser developer tools (F12)
2. Go to Network tab
3. Refresh the kanban page
4. Look for `kanban.js` - should be status 200
5. If 404, rerun `collectstatic` and check static files mapping

#### Check CSRF Token
1. Open browser console
2. Type: `document.cookie`
3. Look for `csrftoken` cookie
4. If missing, check CSRF_COOKIE_HTTPONLY setting

#### Check for JavaScript Errors
1. Open browser console (F12)
2. Look for any red error messages
3. Common errors:
   - "Uncaught ReferenceError: dragStartHandler is not defined" → JS not loading
   - "Forbidden (CSRF token missing)" → CSRF settings issue
   - "Mixed Content" → HTTP/HTTPS issue

#### Enable Debug Mode Temporarily
In `settings.py` (ONLY for testing):
```python
DEBUG = True
```
Then check error messages. **Turn DEBUG off in production!**

## Production Security Settings

When going to production, update these settings:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECRET_KEY = os.environ.get('SECRET_KEY')  # Use environment variable
```

## Common PythonAnywhere Issues

### Issue: "Site can't be reached"
- Check ALLOWED_HOSTS includes your domain
- Reload web app

### Issue: Static files not loading
- Run `collectstatic` again
- Check static files mapping in Web tab
- Verify STATIC_ROOT path

### Issue: 500 Internal Server Error
- Check error log in PythonAnywhere Web tab
- Enable DEBUG temporarily to see detailed error
- Common cause: Database not migrated (`python manage.py migrate`)

### Issue: CSRF verification failed
- Check CSRF_COOKIE_HTTPONLY = False
- Verify cookie is being set (check browser cookies)
- Ensure fetch request includes X-CSRFToken header

## Testing Checklist

- [ ] Static files loading (check Network tab)
- [ ] Kanban page loads without errors
- [ ] Cards are draggable (cursor changes)
- [ ] Cards can be dropped in other columns
- [ ] Backend updates (refresh page to verify)
- [ ] No console errors
- [ ] CSRF token present in cookies
- [ ] Fetch requests succeed (check Network tab)

## Contact Support

If issues persist:
1. Check PythonAnywhere forums
2. Review error logs in Web tab
3. Verify all deployment steps completed
