def test_get_carrier_statuses(client):
    # when
    resp = client.get("/carriers")
    # then
    assert resp.status_code == 200
    assert resp.json() == {
        "carriers": [
            {"code": "A", "enabled": True},
            {"code": "B", "enabled": True},
        ]
    }


def test_status_code_when_set_enabled_non_existent_carrier(client):
    # WHEN requesting to enable/disable carrier that does not exist
    resp = client.post("/carriers", json={"code": "OOO", "enabled": True})
    resp2 = client.post("/carriers", json={"code": "OOO", "enabled": False})

    # THEN status 422 is returned
    assert resp.status_code == 422
    assert resp2.status_code == 422
