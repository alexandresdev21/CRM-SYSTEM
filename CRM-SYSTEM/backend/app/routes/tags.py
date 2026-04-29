from flask import Blueprint, request, jsonify
from app import db
from app.models import Tag

tags_bp = Blueprint("tags", __name__)


@tags_bp.get("/")
def list_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([t.to_dict() for t in tags])


@tags_bp.post("/")
def create_tag():
    body = request.get_json(silent=True) or {}
    if not body.get("name"):
        return jsonify({"error": "Campo 'name' é obrigatório"}), 422
    if Tag.query.filter_by(name=body["name"]).first():
        return jsonify({"error": "Tag já existe"}), 409

    tag = Tag(name=body["name"], color=body.get("color", "#6366f1"))
    db.session.add(tag)
    db.session.commit()
    return jsonify(tag.to_dict()), 201


@tags_bp.delete("/<int:tag_id>")
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return jsonify({"message": "Tag removida"}), 200
