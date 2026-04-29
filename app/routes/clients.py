from flask import Blueprint, request, jsonify
from app import db
from app.models import Client, Tag

clients_bp = Blueprint("clients", __name__)


def _parse_filters(query):
    """Aplica filtros opcionais via query string."""
    status = request.args.get("status")
    search = request.args.get("search")
    tag = request.args.get("tag")

    if status:
        query = query.filter(Client.status == status)
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Client.name.ilike(like), Client.email.ilike(like), Client.company.ilike(like))
        )
    if tag:
        query = query.join(Client.tags).filter(Tag.name == tag)
    return query


# ── GET /api/clients ──────────────────────────────────────────────────────────
@clients_bp.get("/")
def list_clients():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = _parse_filters(Client.query.order_by(Client.created_at.desc()))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [c.to_dict() for c in pagination.items],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    })


# ── POST /api/clients ─────────────────────────────────────────────────────────
@clients_bp.post("/")
def create_client():
    body = request.get_json(silent=True) or {}
    required = ("name", "email")
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"Campos obrigatórios: {', '.join(missing)}"}), 422

    if Client.query.filter_by(email=body["email"]).first():
        return jsonify({"error": "E-mail já cadastrado"}), 409

    client = Client(
        name=body["name"],
        email=body["email"],
        phone=body.get("phone"),
        company=body.get("company"),
        document=body.get("document"),
        website=body.get("website"),
        address=body.get("address"),
        status=body.get("status", "ativo"),
        source=body.get("source"),
        notes=body.get("notes"),
    )

    # Vincular tags se informadas
    for tag_name in body.get("tags", []):
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        client.tags.append(tag)

    db.session.add(client)
    db.session.commit()
    return jsonify(client.to_dict(full=True)), 201


# ── GET /api/clients/:id ──────────────────────────────────────────────────────
@clients_bp.get("/<int:client_id>")
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify(client.to_dict(full=True))


# ── PUT /api/clients/:id ──────────────────────────────────────────────────────
@clients_bp.put("/<int:client_id>")
def update_client(client_id):
    client = Client.query.get_or_404(client_id)
    body = request.get_json(silent=True) or {}

    for field in ("name", "email", "phone", "company", "document", "website",
                  "address", "status", "source", "notes"):
        if field in body:
            setattr(client, field, body[field])

    if "tags" in body:
        client.tags.clear()
        for tag_name in body["tags"]:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            client.tags.append(tag)

    db.session.commit()
    return jsonify(client.to_dict(full=True))


# ── DELETE /api/clients/:id ───────────────────────────────────────────────────
@clients_bp.delete("/<int:client_id>")
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Cliente removido com sucesso"}), 200


# ── GET /api/clients/stats ────────────────────────────────────────────────────
@clients_bp.get("/stats")
def stats():
    from sqlalchemy import func
    total = Client.query.count()
    by_status = db.session.query(Client.status, func.count()).group_by(Client.status).all()
    by_source = db.session.query(Client.source, func.count()).group_by(Client.source).all()
    return jsonify({
        "total": total,
        "by_status": {s: c for s, c in by_status},
        "by_source": {s or "desconhecido": c for s, c in by_source},
    })
