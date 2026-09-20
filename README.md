# MCP RBAC Demo (Mock Tools API)

Public demo of an **MCP-style tool server** with API-key auth and role-based access control (RBAC). Tools talk to a **mock** PSA / documentation API — no production systems.

## Roles

| Role   | Can call                                      |
|--------|-----------------------------------------------|
| viewer | `list_tickets`, `get_doc`                     |
| agent  | viewer + `update_ticket`                      |
| admin  | agent + `create_quote`                        |

## Run

```bash
python -m pip install -r requirements.txt
python server.py
```

Try:

```bash
# viewer — allowed
curl -s -H "X-API-Key: viewer-key" http://127.0.0.1:8787/tools/list_tickets

# viewer — forbidden
curl -s -H "X-API-Key: viewer-key" -X POST http://127.0.0.1:8787/tools/update_ticket \
  -H "Content-Type: application/json" -d "{\"ticket_id\":\"TCK-1\",\"status\":\"Closed\"}"

# admin — allowed
curl -s -H "X-API-Key: admin-key" -X POST http://127.0.0.1:8787/tools/create_quote \
  -H "Content-Type: application/json" -d "{\"account\":\"Acme\",\"amount\":1200}"
```

## Keys (demo only)

- `viewer-key` → viewer
- `agent-key` → agent
- `admin-key` → admin

## Not included

Azure Container deployment, ConnectWise OAuth, or live product APIs. This is the auth + RBAC + tool-description pattern.
