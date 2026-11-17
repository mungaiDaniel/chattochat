class TestComments:
    def test_add_comment(self, client, auth, make_post):
        post = make_post(auth)
        resp = client.post(f"/api/v1/comment/{post['id']}", json={"body": "Great post!"}, headers=auth)
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["body"] == "Great post!"
        assert data["post_id"] == post["id"]
        assert data["author"]["username"] == "testuser"
        assert "email" not in data["author"]

    def test_add_comment_requires_auth(self, client, auth, make_post):
        post = make_post(auth)
        assert client.post(f"/api/v1/comment/{post['id']}", json={"body": "x"}).status_code == 401

    def test_add_comment_to_missing_post_404(self, client, auth):
        assert client.post("/api/v1/comment/999", json={"body": "x"}, headers=auth).status_code == 404

    def test_add_comment_validation(self, client, auth, make_post):
        post = make_post(auth)
        url = f"/api/v1/comment/{post['id']}"
        assert client.post(url, json={}, headers=auth).status_code == 422
        assert client.post(url, json={"body": " "}, headers=auth).status_code == 422
        assert client.post(url, json={"body": "x" * 401}, headers=auth).status_code == 422

    def test_list_comments_for_post(self, client, auth, other_auth, make_post):
        post = make_post(auth)
        other_post = make_post(auth, "unrelated")
        client.post(f"/api/v1/comment/{post['id']}", json={"body": "one"}, headers=auth)
        client.post(f"/api/v1/comment/{post['id']}", json={"body": "two"}, headers=other_auth)
        client.post(f"/api/v1/comment/{other_post['id']}", json={"body": "elsewhere"}, headers=auth)
        resp = client.get(f"/api/v1/comments/{post['id']}")
        assert resp.status_code == 200
        assert [c["body"] for c in resp.get_json()["data"]] == ["one", "two"]

    def test_list_comments_empty(self, client, auth, make_post):
        post = make_post(auth)
        assert client.get(f"/api/v1/comments/{post['id']}").get_json()["data"] == []

    def test_list_comments_missing_post_404(self, client):
        assert client.get("/api/v1/comments/999").status_code == 404

    def test_get_single_comment(self, client, auth, make_post):
        post = make_post(auth)
        created = client.post(
            f"/api/v1/comment/{post['id']}", json={"body": "find me"}, headers=auth
        ).get_json()["data"]
        resp = client.get(f"/api/v1/comment/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["body"] == "find me"

    def test_get_missing_comment_404(self, client):
        assert client.get("/api/v1/comment/999").status_code == 404
