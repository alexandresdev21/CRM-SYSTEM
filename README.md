# 🗂️ CRM Backend — Flask + SQLAlchemy + SQLite

Sistema de CRM (Customer Relationship Management) com gestão de clientes e campanhas de marketing.

---

## 🏗️ Estrutura do Projeto

```
crm/
├── app/
│   ├── __init__.py          # App factory + extensões
│   ├── models/
│   │   └── __init__.py      # Todos os modelos SQLAlchemy
│   └── routes/
│       ├── clients.py       # CRUD de clientes + stats
│       ├── contacts.py      # Contatos por cliente
│       ├── campaigns.py     # Campanhas de marketing
│       ├── interactions.py  # Histórico de interações
│       └── tags.py          # Tags/labels
├── tests/
│   └── test_api.py          # Testes com pytest
├── config.py                # Configurações por ambiente
├── run.py                   # Entry point
├── seed.py                  # Popular banco com dados de exemplo
├── requirements.txt
└── .env.example
```

---

## 🚀 Instalação e Execução

```bash
# 1. Clone ou extraia o projeto
cd crm

# 2. Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env

# 5. Popule o banco com dados de exemplo
python seed.py

# 6. Inicie o servidor
python run.py
```

Acesse: `http://localhost:5000`

---

## 📡 Endpoints da API

### 🔍 Health Check
| Método | Rota          | Descrição         |
|--------|--------------|-------------------|
| GET    | /api/health  | Status da API     |

### 👥 Clientes
| Método | Rota                    | Descrição                        |
|--------|------------------------|----------------------------------|
| GET    | /api/clients/          | Lista clientes (com paginação)   |
| POST   | /api/clients/          | Cria novo cliente                |
| GET    | /api/clients/:id       | Detalhes do cliente              |
| PUT    | /api/clients/:id       | Atualiza cliente                 |
| DELETE | /api/clients/:id       | Remove cliente                   |
| GET    | /api/clients/stats     | Estatísticas gerais              |

**Query params para listagem:** `?status=ativo&search=joão&tag=VIP&page=1&per_page=20`

### 📋 Contatos
| Método | Rota                     | Descrição               |
|--------|-------------------------|-------------------------|
| GET    | /api/contacts/          | Lista (filtro client_id)|
| POST   | /api/contacts/          | Cria contato            |
| GET    | /api/contacts/:id       | Detalhe                 |
| PUT    | /api/contacts/:id       | Atualiza                |
| DELETE | /api/contacts/:id       | Remove                  |

### 📣 Campanhas
| Método | Rota                           | Descrição                        |
|--------|-------------------------------|----------------------------------|
| GET    | /api/campaigns/               | Lista campanhas                  |
| POST   | /api/campaigns/               | Cria campanha                    |
| GET    | /api/campaigns/:id            | Detalhes + clientes              |
| PUT    | /api/campaigns/:id            | Atualiza                         |
| DELETE | /api/campaigns/:id            | Remove                           |
| POST   | /api/campaigns/:id/send       | Marca como enviada               |
| POST   | /api/campaigns/:id/clients    | Adiciona clientes à campanha     |
| GET    | /api/campaigns/stats          | Estatísticas                     |

### 💬 Interações
| Método | Rota                        | Descrição               |
|--------|-----------------------------|-------------------------|
| GET    | /api/interactions/          | Lista (filtro client_id)|
| POST   | /api/interactions/          | Registra interação      |
| PUT    | /api/interactions/:id       | Atualiza                |
| DELETE | /api/interactions/:id       | Remove                  |

### 🏷️ Tags
| Método | Rota             | Descrição   |
|--------|-----------------|-------------|
| GET    | /api/tags/      | Lista tags  |
| POST   | /api/tags/      | Cria tag    |
| DELETE | /api/tags/:id   | Remove tag  |

---

## 📦 Exemplos de Payload

### Criar Cliente
```json
POST /api/clients/
{
  "name": "João Silva",
  "email": "joao@empresa.com",
  "phone": "(41) 99999-0000",
  "company": "Empresa Ltda",
  "status": "ativo",
  "source": "indicação",
  "tags": ["VIP", "Tech"]
}
```

### Criar Campanha
```json
POST /api/campaigns/
{
  "name": "Newsletter Março",
  "description": "Novidades do mês",
  "channel": "email",
  "target_segment": "ativo",
  "scheduled_at": "2025-03-01T09:00:00"
}
```

### Registrar Interação
```json
POST /api/interactions/
{
  "client_id": 1,
  "type": "reuniao",
  "subject": "Apresentação de proposta",
  "description": "Reunião de 1h com decisores.",
  "outcome": "positivo"
}
```

---

## 🧪 Testes

```bash
pip install pytest
python tests/test_api.py
```

---

## 🗄️ Modelos do Banco

```
Client ──── Contact (1:N)
       ──── Interaction (1:N)
       ──── Tag (N:N)  via client_tags
       ──── Campaign (N:N)  via campaign_clients
```

### Status de Clientes
`ativo` | `inativo` | `prospecto`

### Tipos de Interação
`email` | `ligacao` | `reuniao` | `whatsapp` | `outro`

### Status de Campanha
`rascunho` | `agendada` | `em_andamento` | `concluida` | `cancelada`

### Canais de Campanha
`email` | `sms` | `whatsapp` | `push`
