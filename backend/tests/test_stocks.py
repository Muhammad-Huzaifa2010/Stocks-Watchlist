# CRUD on your own stocks. Every request sends a logged-in user's token,
# because all /stocks endpoints require authentication (Phase 11).


def test_create_stock(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    response = client.post(
        "/stocks",
        json={
            "symbol": "LUCK",
            "company_name": "Lucky Cement",
            "market": "PSX",
            "sector": "Cement",
            "notes": "Test stock"
        },
        headers=headers
    )

    # 201 Created (Phase 1, L4)
    assert response.status_code == 201

    data = response.json()

    assert data["symbol"] == "LUCK"
    assert data["company_name"] == "Lucky Cement"
    assert data["market"] == "PSX"
    assert data["sector"] == "Cement"
    assert data["notes"] == "Test stock"
    assert "id" in data


def test_get_all_stocks(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    client.post(
        "/stocks",
        json={
            "symbol": "LUCK",
            "company_name": "Lucky Cement",
            "market": "PSX",
            "sector": "Cement",
            "notes": "Test stock"
        },
        headers=headers
    )

    response = client.get("/stocks", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["symbol"] == "LUCK"


def test_get_single_stock(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    create_response = client.post(
        "/stocks",
        json={
            "symbol": "OGDC",
            "company_name": "Oil and Gas Development Company",
            "market": "PSX",
            "sector": "Oil & Gas",
            "notes": "Test stock"
        },
        headers=headers
    )

    stock_id = create_response.json()["id"]

    response = client.get(f"/stocks/{stock_id}", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == stock_id
    assert data["symbol"] == "OGDC"


def test_update_stock(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    create_response = client.post(
        "/stocks",
        json={
            "symbol": "LUCK",
            "company_name": "Lucky Cement",
            "market": "PSX",
            "sector": "Cement",
            "notes": "Old notes"
        },
        headers=headers
    )

    stock_id = create_response.json()["id"]

    response = client.put(
        f"/stocks/{stock_id}",
        json={
            "symbol": "LUCK",
            "company_name": "Lucky Cement Limited",
            "market": "PSX",
            "sector": "Cement",
            "notes": "Updated notes"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == stock_id
    assert data["company_name"] == "Lucky Cement Limited"
    assert data["notes"] == "Updated notes"


def test_delete_stock(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    create_response = client.post(
        "/stocks",
        json={
            "symbol": "HUBC",
            "company_name": "Hub Power Company",
            "market": "PSX",
            "sector": "Power",
            "notes": "Test stock"
        },
        headers=headers
    )

    stock_id = create_response.json()["id"]

    response = client.delete(f"/stocks/{stock_id}", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == stock_id
    assert data["symbol"] == "HUBC"

    # It is really gone.
    assert client.get(f"/stocks/{stock_id}", headers=headers).status_code == 404


def test_get_stock_not_found(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    response = client.get("/stocks/999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock not found"


def test_update_stock_not_found(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    response = client.put(
        "/stocks/999",
        json={
            "symbol": "LUCK",
            "company_name": "Lucky Cement",
            "market": "PSX",
            "sector": "Cement",
            "notes": "Test stock"
        },
        headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock not found"


def test_delete_stock_not_found(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    response = client.delete("/stocks/999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Stock not found"


def test_create_stock_invalid_data(client, auth_headers):
    headers = auth_headers("testuser", "testuser@gmail.com")

    response = client.post(
        "/stocks",
        json={
            "symbol": "LUCK",
            "market": "PSX"
        },
        headers=headers
    )

    assert response.status_code == 422