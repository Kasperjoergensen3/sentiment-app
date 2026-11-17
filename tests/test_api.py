def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_index_serves_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Sentiment checker" in response.text


def test_predict_saves_and_lists(client):
    response = client.post("/api/predict", json={"text": "I love it"})
    assert response.status_code == 201
    body = response.json()
    assert body["label"] in {"positive", "negative"}
    assert 0.0 <= body["score"] <= 1.0

    history = client.get("/api/predictions").json()
    assert history[0]["id"] == body["id"]


def test_empty_text_is_rejected(client):
    assert client.post("/api/predict", json={"text": ""}).status_code == 422
