from flask import Flask, render_template
from flask_cors import CORS
from config import config
from extensions import limiter
from routes import auth_bp, profile_bp, skills_bp, matching_bp, requests_bp, reviews_bp, chat_bp

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY not set!")
    
    # Enable CORS
    CORS(app)
    
    # Initialize Limiter
    limiter.init_app(app)
    
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(chat_bp)
    
    # Home route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Auth routes (templates)
    @app.route('/login')
    def login_page():
        return render_template('auth/login.html')
    
    @app.route('/signup')
    def signup_page():
        return render_template('auth/signup.html')
    
    # Dashboard route
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard/user_dashboard.html')
    
    # Profile routes
    @app.route('/profile/<int:user_id>')
    def view_profile(user_id):
        return render_template('profile/view.html')
    
    @app.route('/profile/edit')
    def edit_profile():
        return render_template('profile/edit.html')
    
    # Skills routes
    @app.route('/skills')
    def browse_skills():
        return render_template('skills/browse.html')
    
    @app.route('/skills/search')
    def search_skills():
        return render_template('skills/search.html')
    
    # Matching route
    @app.route('/matching')
    def matching():
        return render_template('matching/matches.html')

    # Requests routes
    @app.route('/requests')
    def view_requests():
        return render_template('requests/list.html')

    # Reviews routes
    @app.route('/reviews/add')
    def add_review():
        return render_template('reviews/add.html')
    
    # Chat route
    @app.route('/chat')
    def chat_page():
        return render_template('chat/index.html')

    @app.route('/health')
    def health():
        return {"status": "OK"}, 200
    
    return app

app = create_app()

with app.app_context():
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ Database init failed:", str(e))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


   