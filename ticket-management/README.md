# 🎫 Sathvi Ticket Management System

A comprehensive, multi-role ticket management system built with Django, featuring subscription-based billing, real-time chat, and advanced analytics.

## 🌟 Features

### 🎯 Core Functionality
- **Multi-Role System**: SuperAdmin, Admin, Agent, and User roles
- **Complete Ticket Lifecycle**: Create → Assign → Track → Resolve → Close
- **Real-Time Chat**: In-app messaging between users and agents
- **File Attachments**: Support for multiple file uploads on tickets
- **Advanced Search & Filtering**: Find tickets quickly with smart filters

### 💰 Subscription & Billing
- **Tiered Plans**: Basic, Standard, Premium, Enterprise
- **Trial Period Management**: Configurable free trials
- **Payment Processing**: Razorpay integration
- **Automated Billing**: Subscription expiry and renewal
- **Revenue Analytics**: Comprehensive financial reporting

### 📊 Analytics & Dashboards
- **Super Admin Dashboard**: System overview, company management, revenue tracking
- **Admin Dashboard**: Ticket management, user administration, performance metrics
- **Agent Dashboard**: Assigned tickets, response times, productivity metrics
- **User Dashboard**: Personal tickets, profile management, ticket history

### 🔧 Advanced Features
- **REST API**: Complete API endpoints for integration
- **Email Notifications**: Automated email alerts and updates
- **Dark Mode**: Modern UI with theme switching
- **Responsive Design**: Works seamlessly on all devices
- **Audit Trail**: Complete history of ticket status changes
- **Multi-Language Support**: Framework for internationalization

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.2.25, Python 3.x
- **Database**: MySQL (production), SQLite (development)
- **Frontend**: Bootstrap 5.3.0, modern CSS/JavaScript
- **Payment**: Razorpay Gateway
- **Email**: Gmail SMTP (configurable)

### Project Structure
```
ticket-management/
├── apps/
│   ├── api/           # REST API endpoints
│   ├── core/          # Subscription & payment models
│   ├── dashboards/    # Multi-role dashboard views
│   ├── payments/      # Payment processing
│   ├── superadmin/    # Super admin functionality
│   ├── tickets/       # Ticket management
│   └── users/         # User authentication & profiles
├── config/            # Django settings and URLs
├── static/            # CSS, JavaScript, images
├── templates/         # HTML templates
├── media/             # User uploads
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+ (or SQLite for development)
- Node.js (for asset management, optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ticket-management
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Database Setup**

**For MySQL (Production):**
```sql
CREATE DATABASE ticket_system;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'Sathvi@123';
GRANT ALL PRIVILEGES ON ticket_system.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

**For SQLite (Development):**
- No setup needed - Django will create it automatically

5. **Configure Settings**
Edit `config/settings.py`:
```python
# Update database credentials
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ticket_system',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Update email settings
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Update Razorpay settings
RAZORPAY_KEY_ID = 'your_key_id'
RAZORPAY_KEY_SECRET = 'your_key_secret'
```

6. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create Superuser**
```bash
python manage.py createsuperuser
```

8. **Collect Static Files**
```bash
python manage.py collectstatic
```

9. **Start Development Server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 👥 User Roles & Access

### 🔑 SuperAdmin
- **URL**: `/superadmin/`
- **Access**: System-wide management
- **Features**: 
  - Company management
  - Plan creation and pricing
  - Subscription oversight
  - Revenue analytics
  - System settings

### 👨‍💼 Admin
- **URL**: `/dashboard/admin-dashboard/`
- **Access**: Company-level management
- **Features**:
  - User management
  - Ticket oversight
  - Agent assignment
  - Performance reports

### 🎯 Agent
- **URL**: `/dashboard/agent-dashboard/`
- **Access**: Assigned tickets only
- **Features**:
  - Ticket resolution
  - Customer chat
  - Status updates
  - Performance metrics

### 👤 User/Customer
- **URL**: `/dashboard/user-dashboard/`
- **Access**: Personal tickets only
- **Features**:
  - Create tickets
  - Track ticket status
  - Chat with agents
  - Profile management

## 💳 Payment & Subscription Setup

### Razorpay Configuration
1. Create a Razorpay account at [razorpay.com](https://razorpay.com)
2. Get your API keys from the dashboard
3. Update settings in `config/settings.py`:
```python
RAZORPAY_KEY_ID = 'rzp_test_your_key_id'
RAZORPAY_KEY_SECRET = 'your_secret_key'
```

### Creating Subscription Plans
1. Login as SuperAdmin
2. Navigate to Plans section
3. Create plans with pricing and features
4. Set trial periods and limits

## 📊 API Documentation

### Authentication
The API supports both session-based and JWT authentication.

### Key Endpoints

#### Users & Authentication
```
POST /api/users/login/          # User login
POST /api/users/logout/         # User logout
GET  /api/users/profile/        # Get user profile
PUT  /api/users/profile/        # Update profile
```

#### Tickets
```
GET    /api/tickets/            # List tickets
POST   /api/tickets/            # Create ticket
GET    /api/tickets/{id}/       # Get ticket details
PUT    /api/tickets/{id}/       # Update ticket
DELETE /api/tickets/{id}/       # Delete ticket
```

#### Admin API
```
GET /api/admin/users/           # List all users
GET /api/admin/companies/       # List companies
GET /api/admin/subscriptions/   # List subscriptions
```

### API Usage Example
```python              
import requests

# Login
response = requests.post('http://localhost:8000/api/users/login/', {
    'username': 'your_username',
    'password': 'your_password'
})
token = response.json()['token']

# Create ticket
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/tickets/', 
    headers=headers,
    json={
        'title': 'Support Request',
        'description': 'Need help with...',
        'priority': 'Medium',
        'category': 'Technical'
    }
)
```

## 🗃️ Database Schema

### Core Models
- **User & UserProfile**: Extended Django user with roles
- **Company**: Organization management
- **Plan**: Subscription plans with pricing
- **Subscription**: User/company subscriptions
- **Ticket**: Main ticket entity
- **TicketComment**: Ticket conversations
- **Payment**: Transaction records
- **ChatMessage**: Real-time messaging

### Relationships
- Users belong to Companies
- Companies have Subscriptions
- Tickets are created by Users and assigned to Agents
- Payments are linked to Subscriptions

## 🔧 Configuration

### Environment Variables
Create `.env` file in project root:
```bash
# Database
DB_NAME=ticket_system
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Razorpay
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# Django
SECRET_KEY=your-secret-key
DEBUG=True
```

### Static Files
- **Development**: Django serves static files automatically
- **Production**: Configure web server (Nginx/Apache) to serve static files

### Media Files
User uploads are stored in `media/` directory. Configure in production:
```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.tickets
python manage.py test apps.users

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Data
Create sample data for testing:
```bash
python scripts/create_sample_data.py
```

## 🚀 Deployment

### Production Checklist

1. **Settings**
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Set up production database
   - Configure email backend

2. **Static Files**
   - Run `python manage.py collectstatic --noinput`
   - Configure web server for static files

3. **Database**
   - Run migrations: `python manage.py migrate`
   - Create superuser: `python manage.py createsuperuser`

4. **Security**
   - Set strong `SECRET_KEY`
   - Configure HTTPS
   - Set up firewall rules
   - Enable CSRF protection

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Using Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=False
      - DB_HOST=db
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: ticket_system
      MYSQL_ROOT_PASSWORD: your_password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## 📈 Monitoring & Maintenance

### Database Maintenance
```bash
# Backup database
python manage.py dbbackup

# Check subscription expiry
python manage.py check_subscription_expiry

# Clean up old data
python manage.py cleanup_old_data
```

### Performance Monitoring
- Use Django Debug Toolbar in development
- Set up logging in production
- Monitor database queries
- Track response times

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database credentials in settings
   - Ensure MySQL server is running
   - Verify database exists

2. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check STATIC_URL setting
   - Verify file permissions

3. **Email Not Sending**
   - Check email configuration
   - Verify SMTP credentials
   - Check spam folder

4. **Payment Gateway Error**
   - Verify Razorpay API keys
   - Check webhook configuration
   - Ensure plan is active

### Debug Mode
Enable debug mode for development:
```python
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## 📚 Documentation

### Additional Documentation
- [API Reference](docs/api-reference.md)
- [Admin Guide](docs/admin-guide.md)
- [User Manual](docs/user-manual.md)
- [Development Guide](docs/development-guide.md)

### Code Documentation
The codebase includes comprehensive docstrings and comments. Generate documentation:
```bash
pip install sphinx
sphinx-apidoc -o docs/ apps/
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run test suite
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Email: sathvika.arikatla@gmail.com
- Documentation: Check the `docs/` directory
- Issues: Report via project repository

---

## 🎯 Key Metrics

- **Total Files**: 598+
- **Python Files**: 112+
- **Templates**: 100+
- **Database Models**: 15+
- **API Endpoints**: 25+
- **User Roles**: 4
- **Dashboard Types**: 4

**System Status**: ✅ Production Ready | ✅ Fully Tested | ✅ Documented

---

*Built with ❤️ using Django and modern web technologies*
