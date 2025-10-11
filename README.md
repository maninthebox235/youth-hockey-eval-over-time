# Youth Hockey Development Tracker 🏒

A comprehensive web application for tracking and developing youth hockey players. Designed for coaches, parents, and team managers to assess skills, track progress, manage teams, and generate personalized training recommendations.

## Features

### Core Features (Free)
- **Player Profiles** - Track detailed player statistics and performance metrics
- **Skill Assessments** - Position-specific evaluation forms (Forward, Defense, Goalie)
- **Team Dashboards** - Team composition, performance analytics, and heatmaps
- **Coach Feedback System** - Structured evaluations and progress notes
- **Development Charts** - Visual progress tracking over time
- **Age-Appropriate Benchmarks** - Compare players against age group standards
- **Tryout Evaluation Mode** - Streamlined player assessment during tryouts

### Premium Features
- **AI-Assisted Drill Recommendations** - Contextual drill suggestions based on weaknesses
- **Personalized Training Plans** - Age-appropriate, customized development plans
- **Video Analysis** - Upload and analyze game footage (simulated)
- **Peer Comparison Analytics** - Anonymous benchmarking against similar players
- **Advanced Reporting** - PDF export and detailed progress reports

### Administrative Features
- **User Management** - Admin dashboard for user accounts and permissions
- **Email Configuration** - SMTP setup for notifications and password resets
- **System Analytics** - Usage statistics and platform metrics

## Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Flask (API and email services)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Visualization**: Plotly for interactive charts
- **Testing**: Pytest with coverage reporting
- **Code Quality**: Black formatter, Flake8 linter

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- SMTP server credentials (for email features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/maninthebox235/YouthHockeyTracker.git
   cd YouthHockeyTracker
   ```

2. **Install dependencies using uv** (recommended)
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt  # Note: requirements.txt needs to be generated
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   # Database
   DATABASE_URL=postgresql://user:password@localhost/hockey_dev
   
   # Security
   SECRET_KEY=your-secret-key-here
   
   # Email Configuration (optional)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

4. **Initialize the database**
   ```bash
   # Create database
   createdb hockey_dev
   
   # Run migrations
   uv run alembic upgrade head
   
   # (Optional) Seed with sample data
   uv run python -c "from utils.data_generator import seed_database; seed_database(20)"
   ```

### Running the Application

1. **Start the Flask backend** (for email services)
   ```bash
   uv run python app.py
   ```
   The Flask backend runs on `http://localhost:5001`

2. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   uv run streamlit run main.py
   ```
   The application will be available at `http://localhost:8501`

3. **Create an admin user** (optional)
   ```bash
   uv run python make_admin.py
   ```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_utils.py
```

### Code Formatting

```bash
# Format all Python files
uv run black .

# Check formatting without changes
uv run black --check .
```

### Linting

```bash
# Run flake8 linter
flake8 . --exclude=.venv,migrations --count --statistics
```

### Pre-commit Hooks (Recommended)

Install pre-commit hooks to automatically format code:

```bash
uv add --dev pre-commit
uv run pre-commit install
```

## Project Structure

```
YouthHockeyTracker/
├── main.py                 # Streamlit application entry point
├── app.py                  # Flask backend for email services
├── components/             # Streamlit UI components
│   ├── landing_page.py
│   ├── auth_interface.py
│   ├── player_profile.py
│   ├── skill_assessment.py
│   ├── team_dashboard.py
│   ├── coach_feedback.py
│   ├── drill_recommendations.py  # Premium
│   ├── training_plans.py         # Premium
│   ├── video_analysis.py         # Premium
│   ├── peer_comparison.py        # Premium
│   └── ...
├── database/
│   ├── models.py           # SQLAlchemy models
│   └── __init__.py
├── migrations/             # Alembic database migrations
├── utils/
│   ├── data_generator.py   # Database seeding and queries
│   ├── type_converter.py   # Type safety utilities
│   ├── email_service.py
│   └── ...
├── tests/                  # Test suite
│   ├── test_models.py
│   └── test_utils.py
├── static/                 # Static assets (images)
├── styles/                 # CSS styling
└── pyproject.toml          # Project configuration
```

## Database Models

### Core Models

- **User** - Authentication and user accounts
- **Player** - Player profiles with position-specific metrics
- **PlayerHistory** - Temporal snapshots for progress tracking
- **Team** - Team information and records
- **TeamMembership** - Many-to-many player-team relationships
- **CoachFeedback** - Structured evaluations from coaches
- **FeedbackTemplate** - Reusable feedback forms

## Configuration

### Premium Access

Currently, premium features are hardcoded for specific usernames. To grant premium access, modify the logic in `components/auth_interface.py`:

```python
# Premium users (hardcoded for now)
premium_users = ['aboehrig', 'lboehrig', 'coach1', 'your_username']
st.session_state.is_premium = st.session_state.user['username'] in premium_users
```

### Email Configuration

Email features require SMTP server credentials. Configure in `.env` or through the Admin Dashboard → Email Settings interface.

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password in `MAIL_PASSWORD`

## Troubleshooting

### Database Connection Issues

If you see "SQLALCHEMY_DATABASE_URI must be set":
- Verify your `.env` file contains `DATABASE_URL`
- Ensure PostgreSQL is running: `pg_isready`
- Check database exists: `psql -l`

### NumPy Type Errors

If you encounter `psycopg2.ProgrammingError: can't adapt type 'numpy.int64'`:
- The codebase includes type converters in `utils/type_converter.py`
- All database operations should use `to_int()`, `to_float()`, etc.

### Email Not Sending

- Test email configuration in Admin Dashboard → Email Settings
- Check SMTP credentials and firewall settings
- For Gmail, ensure "Less secure app access" is enabled or use App Password

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `uv run pytest`
5. Format code: `uv run black .`
6. Commit: `git commit -m "Add your feature"`
7. Push and create a pull request

## License

This project is private and not licensed for public use.

## Support

For issues, questions, or feature requests, please contact:
- **Email**: lboehrig@gmail.com
- **GitHub**: [@maninthebox235](https://github.com/maninthebox235)

## Roadmap

- [ ] Implement proper subscription/payment system for premium features
- [ ] Add real video analysis using computer vision
- [ ] Mobile app for on-ice data entry
- [ ] Integration with league management systems
- [ ] Multi-language support
- [ ] Offline mode with sync capabilities
- [ ] Advanced analytics and ML-based insights

---

**Built with ❤️ for youth hockey development**
