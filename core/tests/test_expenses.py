# core/tests/test_eppenses.py


def test_expenses_list_200(auth_client, expense_factory):
    expense_factory(username="usertest", n=8)
    
    resp = auth_client.get("/api/v1/expenses")
    assert resp.status_code == 200
    
    data = resp.json()
    assert data["total_items"] == 8
    assert len(data["result"]) == 8


def test_expenses_list_401(anon_client):
    
    resp = anon_client.get("/api/v1/expenses")
    assert resp.status_code == 401


def test_expense_detail_200(auth_client, expense_factory):
    expense = expense_factory(username="usertest", n=1)
    # expense is a list [Expense(id=1, description=expense 1, amount=100)]
    resp = auth_client.get(f"/api/v1/expenses/{expense[0].id}")
    assert resp.status_code == 200


def test_expense_detail_404(auth_client):
    resp = auth_client.get(f"/api/v1/expenses/10000")
    assert resp.status_code == 404


def test_expense_detail_404_json_shape(auth_client):
    resp = auth_client.get("/api/v1/expenses/999999")
    assert resp.status_code == 404

    data = resp.json()
    assert data["ok"] is False
    assert data["status"] == 404
    assert data["error"] == "EXPENSE_NOT_FOUND"
    assert "not found" in data["message"].lower()
    assert data["path"] == "/api/v1/expenses/999999"


def test_expense_delete_404(auth_client):
    resp = auth_client.delete("/api/v1/expenses/424242")
    assert resp.status_code == 404
    data = resp.json()
    assert data["ok"] is False
    assert data["status"] == 404
    assert data["error"] == "EXPENSE_NOT_FOUND"
    assert "not found" in data["message"].lower()


def test_expense_delete_200(auth_client, expense_factory):
    item = expense_factory(username="usertest", n=1)[0]
    resp = auth_client.delete(f"/api/v1/expenses/{item.id}")
    assert resp.status_code in (200, 204)

    if resp.status_code == 200:
        data = resp.json()
        assert data["ok"] is True
        assert data["status"] == 200
        assert "deleted" in data["message"].lower()