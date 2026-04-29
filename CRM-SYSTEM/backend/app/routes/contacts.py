from flask import Blueprint, request, jsonify
from app import db
from app.models import Contact, Client

contacts_bp = Blueprint("contacts", __name__)


@contacts_bp.get("/")
def list_contacts():
    client_id = request.args.get("client_id", type=int)
    query = Contact.query
    if client_id:
        query = query.filter_by(client_id=client_id)
    contacts = query.order_by(Contact.created_at.desc()).all()
    return jsonify([c.to_dict() for c in contacts])


@contacts_bp.post("/")
def create_contact():
    body = request.get_json(silent=True) or {}
    required = ("client_id", "name")
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"Campos obrigatórios: {', '.join(missing)}"}), 422

    Client.query.get_or_404(body["client_id"])  # valida existência

    # Garante apenas um contato primário por cliente
    if body.get("is_primary"):
        Contact.query.filter_by(client_id=body["client_id"], is_primary=True).update({"is_primary": False})

    contact = Contact(
        client_id=body["client_id"],
        name=body["name"],
        email=body.get("email"),
        phone=body.get("phone"),
        role=body.get("role"),
        is_primary=body.get("is_primary", False),
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify(contact.to_dict()), 201


@contacts_bp.get("/<int:contact_id>")
def get_contact(contact_id):
    return jsonify(Contact.query.get_or_404(contact_id).to_dict())


@contacts_bp.put("/<int:contact_id>")
def update_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    body = request.get_json(silent=True) or {}

    if body.get("is_primary"):
        Contact.query.filter_by(client_id=contact.client_id, is_primary=True).update({"is_primary": False})

    for field in ("name", "email", "phone", "role", "is_primary"):
        if field in body:
            setattr(contact, field, body[field])

    db.session.commit()
    return jsonify(contact.to_dict())


@contacts_bp.delete("/<int:contact_id>")
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message": "Contato removido"}), 200
