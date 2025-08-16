# RuineGestion Commerciale

## Overview

RuineGestion Commerciale is a comprehensive business management system built with Flask, designed for small to medium-sized retail operations. The application provides complete business workflow management including product inventory, sales tracking, client management, stock control, delivery coordination, and reservation handling. The system features real-time financial analytics with automatic profit/loss calculations in Ariary currency, stock level alerts, and a responsive dashboard for business oversight.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM for database operations
- **Authentication**: JWT tokens combined with Flask sessions for user management
- **Password Security**: Bcrypt for password hashing and verification
- **Database Models**: Comprehensive entity relationships covering Users, Products, Clients, Sales, Stock Movements, Deliveries, and Reservations
- **Service Layer**: Dedicated service classes (AuthService, VenteService, StockService, LivraisonService, ReservationService) that encapsulate business logic and database operations
- **Route Organization**: Blueprint-based modular routing with dedicated controllers for each business domain

### Frontend Architecture
- **Template Engine**: Jinja2 with Bootstrap 5 dark theme for responsive UI
- **Styling**: Custom CSS with CSS variables for theming and Font Awesome icons
- **JavaScript**: Custom utility functions for currency formatting (Ariary), number formatting, and toast notifications
- **Layout**: Base template with navigation bar and modular content blocks

### Data Management
- **Database**: SQLite with SQLAlchemy ORM (configured for easy PostgreSQL migration)
- **Relationships**: Proper foreign key relationships between entities with backref navigation
- **Business Logic**: Automatic stock updates, profit margin calculations, low stock alerts, and financial statistics
- **Data Validation**: Form validation and business rule enforcement at the service layer

### Security & Session Management
- **Authentication Flow**: Username/password authentication with session storage
- **Authorization**: Login decorators for route protection
- **Token Management**: JWT tokens stored in sessions for API compatibility
- **Environment Configuration**: Environment-based configuration for secrets and database URLs

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme from cdn.replit.com
- **Font Awesome 6.0.0**: Icon library from cdnjs.cloudflare.com
- **Chart.js**: JavaScript charting library from cdn.jsdelivr.net

### Python Packages
- **Flask**: Web framework with SQLAlchemy, Bcrypt, and JWT extensions
- **Werkzeug**: WSGI utilities including ProxyFix middleware for deployment

### Database
- **SQLite**: Default development database (easily configurable for PostgreSQL production deployment)

### Development Tools
- **Flask Development Server**: Built-in development server with debug mode and hot reload