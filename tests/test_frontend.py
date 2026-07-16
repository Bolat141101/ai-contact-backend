def test_landing_page_is_available(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Разрабатываю backend" in response.get_data(as_text=True)
    assert 'id="contact-form"' in response.get_data(as_text=True)


def test_frontend_assets_are_available(client):
    assert client.get("/static/css/styles.css").status_code == 200
    assert client.get("/static/js/app.js").status_code == 200


def test_monitoring_page_is_available(client):
    response = client.get("/monitoring")

    assert response.status_code == 200
    assert "Состояние API" in response.get_data(as_text=True)
    assert client.get("/static/css/monitoring.css").status_code == 200
    assert client.get("/static/js/monitoring.js").status_code == 200
