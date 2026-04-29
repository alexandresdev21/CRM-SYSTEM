from flask import Blueprint, request, jsonify
from app import db
from app.models import Interaction, Client

interactions_bp = Blueprint("interactions", __name__)


@interactions_bp.get("/")
def list_interactions():
    client_id = request.args.get("client_id", type=int)
    type_ = request.args.get("type")
    query = Interaction.query
    if client_id:
        query = query.filter_by(client_id=client_id)
    if type_:
        query = query.filter_by(type=type_)
    items = query.order_by(Interaction.occurred_at.desc()).all()
    return jsonify([i.to_dict() for i in items])


@interactions_bp.post("/")
def create_interaction():
    body = request.get_json(silent=True) or {}
    required = ("client_id", "type")
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"Campos obrigatórios: {', '.join(missing)}"}), 422

    Client.query.get_or_404(body["client_id"])

    interaction = Interaction(
        client_id=body["client_id"],
        type=body["type"],
        subject=body.get("subject"),
        description=body.get("description"),
        outcome=body.get("outcome"),
    )
    db.session.add(interaction)
    db.session.commit()
    return jsonify(interaction.to_dict()), 201


@interactions_bp.get("/<int:interaction_id>")
def get_interaction(interaction_id):
    return jsonify(Interaction.query.get_or_404(interaction_id).to_dict())


@interactions_bp.put("/<int:interaction_id>")
def update_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    body = request.get_json(silent=True) or {}
    for field in ("type", "subject", "description", "outcome"):
        if field in body:
            setattr(interaction, field, body[field])
    db.session.commit()
    return jsonify(interaction.to_dict())


@interactions_bp.delete("/<int:interaction_id>")
def delete_interaction(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    db.session.delete(interaction)
    db.session.commit()
    return jsonify({"message": "Interação removida"}), 200
