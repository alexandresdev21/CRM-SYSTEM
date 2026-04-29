from datetime import datetime
from app import db

# ─── Tabela associativa: Cliente ↔ Tag ───────────────────────────────────────
client_tags = db.Table(
    "client_tags",
    db.Column("client_id", db.Integer, db.ForeignKey("clients.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)

# ─── Tabela associativa: Campanha ↔ Cliente ──────────────────────────────────
campaign_clients = db.Table(
    "campaign_clients",
    db.Column("campaign_id", db.Integer, db.ForeignKey("campaigns.id"), primary_key=True),
    db.Column("client_id", db.Integer, db.ForeignKey("clients.id"), primary_key=True),
    db.Column("status", db.String(30), default="pendente"),  # pendente | enviado | respondido | cancelado
    db.Column("joined_at", db.DateTime, default=datetime.utcnow),
)


class Tag(db.Model):
    """Label livre para categorizar clientes."""
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default="#6366f1")  # hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "color": self.color}


class Client(db.Model):
    """Empresa / pessoa jurídica ou física cliente."""
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    company = db.Column(db.String(120))
    document = db.Column(db.String(20))          # CPF / CNPJ
    website = db.Column(db.String(200))
    address = db.Column(db.String(250))
    status = db.Column(db.String(20), default="ativo")  # ativo | inativo | prospecto
    source = db.Column(db.String(60))            # como conheceu: indicação, site, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    contacts = db.relationship("Contact", backref="client", lazy=True, cascade="all, delete-orphan")
    interactions = db.relationship("Interaction", backref="client", lazy=True, cascade="all, delete-orphan")
    tags = db.relationship("Tag", secondary=client_tags, backref="clients", lazy="subquery")

    def to_dict(self, full=False):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "document": self.document,
            "website": self.website,
            "address": self.address,
            "status": self.status,
            "source": self.source,
            "notes": self.notes,
            "tags": [t.to_dict() for t in self.tags],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if full:
            data["contacts"] = [c.to_dict() for c in self.contacts]
            data["interactions"] = [i.to_dict() for i in self.interactions]
        return data


class Contact(db.Model):
    """Pessoa de contato dentro de um cliente."""
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    role = db.Column(db.String(80))          # cargo / função
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_primary": self.is_primary,
            "created_at": self.created_at.isoformat(),
        }


class Interaction(db.Model):
    """Histórico de interações com o cliente (ligação, e-mail, reunião…)."""
    __tablename__ = "interactions"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    type = db.Column(db.String(40), nullable=False)   # email | ligacao | reuniao | whatsapp | outro
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    outcome = db.Column(db.String(60))                # positivo | neutro | negativo
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "type": self.type,
            "subject": self.subject,
            "description": self.description,
            "outcome": self.outcome,
            "occurred_at": self.occurred_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class Campaign(db.Model):
    """Campanha de marketing enviada para um grupo de clientes."""
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    channel = db.Column(db.String(40), default="email")  # email | sms | whatsapp | push
    status = db.Column(db.String(20), default="rascunho")  # rascunho | agendada | em_andamento | concluida | cancelada
    target_segment = db.Column(db.String(60))   # ex: "ativo", "prospecto", tag específica
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Clientes vinculados
    clients = db.relationship("Client", secondary=campaign_clients, backref="campaigns", lazy="subquery")

    @property
    def stats(self):
        from sqlalchemy import text
        result = db.session.execute(
            text("SELECT status, COUNT(*) as cnt FROM campaign_clients WHERE campaign_id=:cid GROUP BY status"),
            {"cid": self.id},
        ).fetchall()
        return {row[0]: row[1] for row in result}

    def to_dict(self, full=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "channel": self.channel,
            "status": self.status,
            "target_segment": self.target_segment,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat(),
            "total_clients": len(self.clients),
            "stats": self.stats,
        }
        if full:
            data["clients"] = [c.to_dict() for c in self.clients]
        return data
