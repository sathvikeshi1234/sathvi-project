# Role-Based Logout Redirect Solution

## Problem
When users logged out from any dashboard (admin, agent, user), they were all redirected to the same landing page (`home`). The requirement was to redirect each role to their specific login page.

## Solution Implemented

### Modified `apps/users/views.py`

Updated the `logout_view` function to:

1. **Detect user role before logout** using the existing helper functions:
   - `_is_admin()` for admin users
   - `_is_agent()` for agent users  
   - Default to regular user for others

2. **Redirect based on role** after logout:
   - **Admin users** → `/admin-login/` (`users:admin_login`)
   - **Agent users** → `/agent-login/` (`users:agent_login`)
   - **Regular users** → `/user-login/` (`users:user_login`)

### Code Changes

```python
def logout_view(request):
    # Store user role before logout
    user_role = None
    if request.user.is_authenticated:
        if _is_admin(request.user):
            user_role = 'admin'
        elif _is_agent(request.user):
            user_role = 'agent'
        else:
            user_role = 'user'
    
    logout(request)
    
    messages.success(request, "Logged out successfully.")
    
    # Redirect based on user role
    if user_role == 'admin':
        return redirect('users:admin_login')
    elif user_role == 'agent':
        return redirect('users:agent_login')
    else:
        return redirect('users:user_login')
```

## Testing Results

✅ **Basic functionality verified**: Logout redirects correctly to `/user-login/` when no user is logged in (default behavior).

## Expected Behavior

| User Role | Login URL | Logout Redirect |
|-----------|-----------|-----------------|
| **Admin** | `/admin-login/` | `/admin-login/` |
| **Agent** | `/agent-login/` | `/agent-login/` |
| **Regular User** | `/user-login/` | `/user-login/` |
| **Not logged in** | - | `/user-login/` (default) |

## Manual Testing Steps

1. **Admin Test**:
   - Go to `/admin-login/`
   - Login with admin credentials
   - Click logout
   - **Expected**: Redirect to `/admin-login/`

2. **Agent Test**:
   - Go to `/agent-login/`
   - Login with agent credentials
   - Click logout
   - **Expected**: Redirect to `/agent-login/`

3. **User Test**:
   - Go to `/user-login/`
   - Login with regular user credentials
   - Click logout
   - **Expected**: Redirect to `/user-login/`

## Benefits

- **Better UX**: Users return to their specific login page
- **Role Consistency**: Maintains the context of each user type
- **Backward Compatible**: Still works if user roles change
- **Simple Implementation**: Minimal code changes, no database changes

## Files Modified

- `apps/users/views.py` - Updated `logout_view` function

The solution is now ready for testing with your actual user accounts.
