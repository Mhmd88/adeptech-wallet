from flask import Flask

def register_blueprints(app: Flask):
    from .users import bp as users_bp
    from .balances import bp as balances_bp

    app.register_blueprint(users_bp, url_prefix="/v1/users")
    app.register_blueprint(balances_bp, url_prefix="/v1/balances")
