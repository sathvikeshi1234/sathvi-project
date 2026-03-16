from django.contrib.auth.models import User
from users.models import UserProfile, Role

print('=== Agent Users ===')
agents = User.objects.filter(userprofile__role__name='Agent')
for agent in agents:
    print(f'Username: {agent.username}, Email: {agent.email}, Active: {agent.is_active}, Staff: {agent.is_staff}')
    profile = getattr(agent, 'userprofile', None)
    if profile:
        print(f'  Profile Active: {profile.is_active}, Role: {profile.role.name if profile.role else "None"}')
    print('---')
print(f'Total agents: {agents.count()}')

print('\n=== Testing Agent Authentication ===')
if agents.exists():
    test_agent = agents.first()
    print(f'Testing agent: {test_agent.username}')
    print(f'User exists: {User.objects.filter(username=test_agent.username).exists()}')
    print(f'Can authenticate: {test_agent.check_password("your_test_password")}')  # This will show False since we don't know the password
