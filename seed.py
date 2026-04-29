"""
Script para popular o banco com dados de exemplo.
Execute: python seed.py
"""
from app import create_app, db
from app.models import Client, Contact, Interaction, Tag, Campaign

app = create_app("development")

with app.app_context():
    db.drop_all()
    db.create_all()

    # Tags
    tags = {
        "vip": Tag(name="VIP", color="#f59e0b"),
        "tech": Tag(name="Tech", color="#3b82f6"),
        "varejo": Tag(name="Varejo", color="#10b981"),
        "prospecto": Tag(name="Prospecto", color="#8b5cf6"),
    }
    for t in tags.values():
        db.session.add(t)

    # Clientes
    c1 = Client(
        name="João Silva", email="joao@techcorp.com", phone="(41) 99999-1111",
        company="TechCorp Ltda", status="ativo", source="indicação",
        notes="Cliente desde 2022. Interesse em upgrade de plano.",
    )
    c1.tags = [tags["vip"], tags["tech"]]

    c2 = Client(
        name="Maria Oliveira", email="maria@varejo.com.br", phone="(41) 98888-2222",
        company="Varejo Premium", status="ativo", source="site",
        notes="Compra mensal recorrente.",
    )
    c2.tags = [tags["varejo"]]

    c3 = Client(
        name="Carlos Mendes", email="carlos@startup.io", phone="(11) 97777-3333",
        company="Startup IO", status="prospecto", source="linkedin",
        notes="Em fase de avaliação do produto.",
    )
    c3.tags = [tags["prospecto"], tags["tech"]]

    c4 = Client(
        name="Ana Costa", email="ana@redesul.com", phone="(51) 96666-4444",
        company="Rede Sul", status="inativo", source="evento",
    )

    for c in (c1, c2, c3, c4):
        db.session.add(c)
    db.session.flush()

    # Contatos
    db.session.add_all([
        Contact(client_id=c1.id, name="João Silva", email="joao@techcorp.com", role="CEO", is_primary=True),
        Contact(client_id=c1.id, name="Fernanda Lima", email="fernanda@techcorp.com", role="CTO"),
        Contact(client_id=c2.id, name="Maria Oliveira", email="maria@varejo.com.br", role="Diretora", is_primary=True),
        Contact(client_id=c3.id, name="Carlos Mendes", email="carlos@startup.io", role="Fundador", is_primary=True),
    ])

    # Interações
    db.session.add_all([
        Interaction(client_id=c1.id, type="reuniao", subject="Renovação de contrato",
                    description="Reunião para discutir upgrade de plano anual.", outcome="positivo"),
        Interaction(client_id=c1.id, type="email", subject="Proposta enviada",
                    description="Proposta comercial enviada por e-mail.", outcome="neutro"),
        Interaction(client_id=c2.id, type="ligacao", subject="Suporte técnico",
                    description="Ligação para resolver dúvidas de integração.", outcome="positivo"),
        Interaction(client_id=c3.id, type="email", subject="Apresentação inicial",
                    description="Primeiro contato por e-mail apresentando a solução.", outcome="neutro"),
    ])

    # Campanhas
    camp1 = Campaign(
        name="Black Friday 2024",
        description="Campanha de descontos especiais para clientes ativos.",
        channel="email",
        status="concluida",
        target_segment="ativo",
    )
    camp1.clients = [c1, c2]

    camp2 = Campaign(
        name="Reativação Q1 2025",
        description="Campanha para reativar clientes inativos.",
        channel="whatsapp",
        status="rascunho",
        target_segment="inativo",
    )
    camp2.clients = [c4]

    camp3 = Campaign(
        name="Onboarding Prospectos",
        description="Nurturing de leads em fase de avaliação.",
        channel="email",
        status="em_andamento",
        target_segment="prospecto",
    )
    camp3.clients = [c3]

    for camp in (camp1, camp2, camp3):
        db.session.add(camp)

    db.session.commit()
    print("✅ Banco populado com sucesso!")
    print(f"   • {Client.query.count()} clientes")
    print(f"   • {Contact.query.count()} contatos")
    print(f"   • {Interaction.query.count()} interações")
    print(f"   • {Campaign.query.count()} campanhas")
    print(f"   • {Tag.query.count()} tags")
