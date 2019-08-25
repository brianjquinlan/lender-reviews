from flask import Flask
from reviews_app.database import db_session, init_db

from flask_restful import Api
from reviews_app.resources import ReviewsResource


def create_app():
    # app init
    app = Flask(__name__)
    app.debug = True

    init_db()
    api = Api(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    api.add_resource(ReviewsResource, '/reviews', '/reviews/<lender_name>')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=3000)

