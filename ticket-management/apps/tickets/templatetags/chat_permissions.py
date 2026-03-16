from django import template

register = template.Library()

@register.simple_tag
def can_chat_with_ticket(ticket, user):
    """
    Determine if the current user can chat about this ticket.
    
    Returns:
    - True if user can chat
    - False if user cannot chat
    - None if chat should be hidden (for agents not assigned)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Check if user has admin/staff privileges
    is_admin = (
        user.is_superuser or 
        user.is_staff or 
        (hasattr(user, 'userprofile') and 
         getattr(user.userprofile, 'role', None) and 
         getattr(user.userprofile.role, 'name', '').lower() in ['admin', 'superadmin'])
    )
    
    # Check if user is an agent
    is_agent = (
        hasattr(user, 'userprofile') and 
        getattr(user.userprofile, 'role', None) and 
        getattr(user.userprofile.role, 'name', '').lower() == 'agent'
    )
    
    # Admin can always chat
    if is_admin:
        return True
    
    # Agent can only chat if assigned to this ticket
    if is_agent:
        if ticket.assigned_to and ticket.assigned_to.id == user.id:
            return True
        else:
            return None  # Hide chat option for unassigned agents
    
    # Regular users (ticket creators) can always chat
    if ticket.created_by and ticket.created_by.id == user.id:
        return True
    
    return False

@register.simple_tag
def get_chat_partner_id(ticket, user):
    """
    Get the appropriate chat partner ID based on user role and ticket assignment.
    
    Returns:
    - Agent ID for users chatting with assigned agent
    - User ID for admins/agents chatting with ticket creator
    - Admin ID for users chatting with admin when no agent assigned
    """
    if not user or not user.is_authenticated:
        return None
    
    # Check if user has admin/staff privileges
    is_admin = (
        user.is_superuser or 
        user.is_staff or 
        (hasattr(user, 'userprofile') and 
         getattr(user.userprofile, 'role', None) and 
         getattr(user.userprofile.role, 'name', '').lower() in ['admin', 'superadmin'])
    )
    
    # Check if user is an agent
    is_agent = (
        hasattr(user, 'userprofile') and 
        getattr(user.userprofile, 'role', None) and 
        getattr(user.userprofile.role, 'name', '').lower() == 'agent'
    )
    
    # Admin chatting - chat with ticket creator
    if is_admin:
        return ticket.created_by.id if ticket.created_by else None
    
    # Agent chatting - chat with ticket creator
    if is_agent and ticket.assigned_to and ticket.assigned_to.id == user.id:
        return ticket.created_by.id if ticket.created_by else None
    
    # User (ticket creator) chatting
    if ticket.created_by and ticket.created_by.id == user.id:
        # If agent is assigned, chat with agent
        if ticket.assigned_to:
            return ticket.assigned_to.id
        # Otherwise, chat with admin (return a special value to indicate admin chat)
        else:
            return 'admin'
    
    return None

@register.simple_tag
def get_chat_display_text(can_chat_result, ticket):
    """
    Get the display text for the chat button based on permissions.
    """
    if can_chat_result is None:
        return "Not Assigned"
    elif can_chat_result:
        return "Chat"
    else:
        return "Chat"  # Default to "Chat" for consistency
