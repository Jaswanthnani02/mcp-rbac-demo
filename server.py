"""Minimal MCP-style tool server with API-key auth and RBAC."""

from __future__ import annotations

from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)

API_KEYS = {
    "viewer-key": "viewer",
    "agent-key": "agent",
    "admin-key": "admin",
}

ROLE_RANK = {"viewer": 1, "agent": 2, "admin": 3}

TOOLS = {
    "list_tickets": {
        "description": "List open tickets from the mock PSA API",
        "min_role": "viewer",
        "method": "GET",
    },
    "get_doc": {
        "description": "Fetch a documentation article from the mock knowledge base (IT Glue–style)",
        "min_role": "viewer",
        "method": "GET",
    },
    "update_ticket": {
        "description": "Update ticket status or notes",
        "min_role": "agent",
        "method": "POST",
    },
    "create_quote": {
        "description": "Create a quote in the mock CPQ system",
        "min_role": "admin",
        "method": "POST",
    },
}

MOCK_TICKETS = [
    {"id": "TCK-1", "summary": "VPN down", "status": "Open"},
    {"id": "TCK-2", "summary": "Mailbox full", "status": "Open"},
]

MOCK_DOCS = {
    "vpn-reset": {"title": "VPN client reset", "body": "Redacted runbook steps…"},
}


def current_role():
    key = request.headers.get("X-API-Key", "")
    return API_KEYS.get(key)


def require_auth(min_role: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = current_role()
            if role is None:
                return jsonify({"error": "unauthorized", "hint": "Send X-API-Key"}), 401
            if ROLE_RANK[role] < ROLE_RANK[min_role]:
                return jsonify({
                    "error": "forbidden",
                    "role": role,
                    "required": min_role,
                }), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.get("/tools")
@require_auth("viewer")
def list_tools():
    role = current_role()
    visible = [
        {"name": name, **meta}
        for name, meta in TOOLS.items()
        if ROLE_RANK[role] >= ROLE_RANK[meta["min_role"]]
    ]
    return jsonify({"role": role, "tools": visible})


@app.get("/tools/list_tickets")
@require_auth("viewer")
def list_tickets():
    return jsonify({"tickets": MOCK_TICKETS})


@app.get("/tools/get_doc")
@require_auth("viewer")
def get_doc():
    doc_id = request.args.get("id", "vpn-reset")
    doc = MOCK_DOCS.get(doc_id)
    if not doc:
        return jsonify({"error": "not_found"}), 404
    return jsonify(doc)


@app.post("/tools/update_ticket")
@require_auth("agent")
def update_ticket():
    body = request.get_json(force=True, silent=True) or {}
    ticket_id = body.get("ticket_id")
    status = body.get("status", "Updated")
    ticket = next((t for t in MOCK_TICKETS if t["id"] == ticket_id), None)
    if not ticket:
        return jsonify({"error": "not_found"}), 404
    ticket["status"] = status
    return jsonify({"ok": True, "ticket": ticket})


@app.post("/tools/create_quote")
@require_auth("admin")
def create_quote():
    body = request.get_json(force=True, silent=True) or {}
    return jsonify({
        "ok": True,
        "quote_id": "Q-1001",
        "account": body.get("account", "Unknown"),
        "amount": body.get("amount", 0),
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8787, debug=False)
