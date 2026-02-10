from flask import Blueprint, request, jsonify
from extensions import db
from models.admin import Admin

admin_auth_bp = Blueprint("admin_auth", __name__)

@admin_auth_bp.route("/admin/register", methods=["POST"])
def register_admin():
    """
    Register an admin user
    ---
    tags:
      - Admin Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Ishmael"
            position:
              type: string
              example: "Sanctuary Manager"
            password:
              type: string
              example: "StrongPassword123"
    responses:
      201:
        description: Admin registered
      400:
        description: Validation error
    """

    data = request.get_json()

    name = data.get("name")
    position = data.get("position")
    password = data.get("password")

    if not name or not position or not password:
        return jsonify({"error": "name, position and password are required"}), 400

    admin = Admin(name=name, position=position)
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    return jsonify({"message": "Admin registered successfully"}), 201
