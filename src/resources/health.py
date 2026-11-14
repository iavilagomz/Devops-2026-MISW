from flask_restful import Resource


class HealthResource(Resource):
    """GET /health - usado por el health check de AWS Beanstalk."""

    def get(self):
        return {"status": "ok", "version": "v2"}, 200
