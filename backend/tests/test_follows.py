class TestFollow:
    def test_follow_and_list(self, client, auth, register, login):
        from conftest import OTHER

        target = register(OTHER)
        resp = client.post(f"/api/v1/follow/{target['id']}", headers=auth)
        assert resp.status_code == 201
        following = client.get("/api/v1/following", headers=auth).get_json()["data"]
        assert [u["id"] for u in following] == [target["id"]]
        assert "email" not in following[0]

    def test_follow_is_one_directional(self, client, auth, register, login):
        from conftest import OTHER

        target = register(OTHER)
        client.post(f"/api/v1/follow/{target['id']}", headers=auth)
        other_headers, _ = login(OTHER)
        assert client.get("/api/v1/following", headers=other_headers).get_json()["data"] == []

    def test_cannot_follow_self(self, client, auth):
        me = client.get("/api/v1/user/me", headers=auth).get_json()["data"]
        resp = client.post(f"/api/v1/follow/{me['id']}", headers=auth)
        assert resp.status_code == 400

    def test_follow_twice_conflicts(self, client, auth, other_auth):
        client.post("/api/v1/follow/2", headers=auth)
        assert client.post("/api/v1/follow/2", headers=auth).status_code == 409

    def test_follow_missing_user_404(self, client, auth):
        assert client.post("/api/v1/follow/999", headers=auth).status_code == 404

    def test_unfollow(self, client, auth, other_auth):
        client.post("/api/v1/follow/2", headers=auth)
        resp = client.post("/api/v1/unfollow/2", headers=auth)
        assert resp.status_code == 200
        assert client.get("/api/v1/following", headers=auth).get_json()["data"] == []

    def test_unfollow_when_not_following_404(self, client, auth, other_auth):
        assert client.post("/api/v1/unfollow/2", headers=auth).status_code == 404

    def test_unfollow_self_400(self, client, auth):
        me = client.get("/api/v1/user/me", headers=auth).get_json()["data"]
        assert client.post(f"/api/v1/unfollow/{me['id']}", headers=auth).status_code == 400

    def test_endpoints_require_auth(self, client):
        assert client.post("/api/v1/follow/1").status_code == 401
        assert client.post("/api/v1/unfollow/1").status_code == 401
        assert client.get("/api/v1/following").status_code == 401
