from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from ..utils.kg_schema import validate_schema, apply_constraints_and_indexes, monitor_consistency

ns = Namespace("kg", description="Knowledge Graph governance & monitoring")


@ns.route("/schema/validate")
class KGSchemaValidate(Resource):
    @jwt_required()
    def get(self):
        return validate_schema(), 200


@ns.route("/schema/apply")
class KGSchemaApply(Resource):
    @jwt_required()
    def post(self):
        # Advisory: real application should be done with cypher scripts
        return apply_constraints_and_indexes(), 200


@ns.route("/monitor/integrity")
class KGIntegrity(Resource):
    @jwt_required()
    def get(self):
        return monitor_consistency(), 200
