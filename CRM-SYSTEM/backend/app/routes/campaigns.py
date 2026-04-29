from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import Campaign, Client, campaign_clients

campaigns_bp = Blueprint("campaigns", __name__)


@campaigns_bp.get("/")
def list_campaigns():
    status = request.args.get("status")
    query = Campaign.query
    if status:
        query = query.filter_by(status=status)
    campaigns = query.order_by(Campaign.created_at.desc()).all()
    return jsonify([c.to_dict() for c in campaigns])


@campaigns_bp.post("/")
def create_campaign():
    body = request.get_json(silent=True) or {}
    if not body.get("name"):
        return jsonify({"error": "Campo 'name' é obrigatório"}), 422

    scheduled_at = None
    if body.get("scheduled_at"):
        try:
            scheduled_at = datetime.fromisoformat(body["scheduled_at"])
        except ValueError:
            return jsonify({"error": "Formato inválido para scheduled_at (use ISO 8601)"}), 422

    campaign = Campaign(
        name=body["name"],
        description=body.get("description"),
        channel=body.get("channel", "email"),
        status=body.get("status", "rascunho"),
        target_segment=body.get("target_segment"),
        scheduled_at=scheduled_at,
    )
    db.session.add(campaign)
    db.session.flush()

    # Adiciona clientes automaticamente pelo segmento
    segment = body.get("target_segment")
    if segment:
        clients = Client.query.filter_by(status=segment).all()
        campaign.clients.extend(clients)

    db.session.commit()
    return jsonify(campaign.to_dict(full=True)), 201


@campaigns_bp.get("/<int:campaign_id>")
def get_campaign(campaign_id):
    return jsonify(Campaign.query.get_or_404(campaign_id).to_dict(full=True))


@campaigns_bp.put("/<int:campaign_id>")
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    body = request.get_json(silent=True) or {}

    for field in ("name", "description", "channel", "status", "target_segment"):
        if field in body:
            setattr(campaign, field, body[field])

    if "scheduled_at" in body and body["scheduled_at"]:
        try:
            campaign.scheduled_at = datetime.fromisoformat(body["scheduled_at"])
        except ValueError:
            return jsonify({"error": "Formato inválido para scheduled_at"}), 422

    db.session.commit()
    return jsonify(campaign.to_dict())


@campaigns_bp.delete("/<int:campaign_id>")
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"message": "Campanha removida"}), 200


# ── POST /api/campaigns/:id/send ─────────────────────────────────────────────
@campaigns_bp.post("/<int:campaign_id>/send")
def send_campaign(campaign_id):
    """Marca campanha como enviada e atualiza status dos clientes."""
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.status == "concluida":
        return jsonify({"error": "Campanha já foi concluída"}), 409

    campaign.status = "concluida"
    campaign.sent_at = datetime.utcnow()

    # Atualiza status de cada cliente na campanha para "enviado"
    db.session.execute(
        campaign_clients.update()
        .where(campaign_clients.c.campaign_id == campaign_id)
        .values(status="enviado")
    )
    db.session.commit()
    return jsonify({"message": "Campanha enviada!", "campaign": campaign.to_dict()})


# ── POST /api/campaigns/:id/clients ──────────────────────────────────────────
@campaigns_bp.post("/<int:campaign_id>/clients")
def add_clients(campaign_id):
    """Adiciona clientes individualmente a uma campanha."""
    campaign = Campaign.query.get_or_404(campaign_id)
    body = request.get_json(silent=True) or {}
    client_ids = body.get("client_ids", [])

    added = 0
    for cid in client_ids:
        client = Client.query.get(cid)
        if client and client not in campaign.clients:
            campaign.clients.append(client)
            added += 1

    db.session.commit()
    return jsonify({"message": f"{added} cliente(s) adicionado(s)", "total": len(campaign.clients)})


# ── GET /api/campaigns/stats ──────────────────────────────────────────────────
@campaigns_bp.get("/stats")
def stats():
    from sqlalchemy import func
    total = Campaign.query.count()
    by_status = db.session.query(Campaign.status, func.count()).group_by(Campaign.status).all()
    by_channel = db.session.query(Campaign.channel, func.count()).group_by(Campaign.channel).all()
    return jsonify({
        "total": total,
        "by_status": {s: c for s, c in by_status},
        "by_channel": {ch: c for ch, c in by_channel},
    })
