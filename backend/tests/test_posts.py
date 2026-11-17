from conftest import PNG_BYTES


class TestCreatePost:
    def test_create_post(self, client, auth):
        resp = client.post("/api/v1/post", json={"body": "  My first post  "}, headers=auth)
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["body"] == "My first post"
        assert data["likes"] == 0
        assert data["comments"] == []
        assert data["author"]["username"] == "testuser"

    def test_requires_auth(self, client):
        assert client.post("/api/v1/post", json={"body": "hi"}).status_code == 401

    def test_empty_body_422(self, client, auth):
        assert client.post("/api/v1/post", json={"body": ""}, headers=auth).status_code == 422
        assert client.post("/api/v1/post", json={"body": "   "}, headers=auth).status_code == 422

    def test_too_long_body_422(self, client, auth):
        assert client.post("/api/v1/post", json={"body": "x" * 501}, headers=auth).status_code == 422

    def test_missing_body_422(self, client, auth):
        assert client.post("/api/v1/post", json={}, headers=auth).status_code == 422

    def test_create_post_with_image_upload(self, client, auth, image_file):
        resp = client.post(
            "/api/v1/post",
            data={"body": "with picture", "photo": image_file()},
            headers=auth,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 201
        pic = resp.get_json()["data"]["postpic"]
        assert pic.startswith("/uploads/posts/")
        assert client.get(pic).data == PNG_BYTES

    def test_invalid_image_upload_400(self, client, auth, image_file):
        resp = client.post(
            "/api/v1/post",
            data={"body": "bad picture", "photo": image_file("x.png", b"not an image")},
            headers=auth,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_oversized_request_413(self, app, client, auth, image_file):
        app.config["MAX_CONTENT_LENGTH"] = 100
        resp = client.post(
            "/api/v1/post",
            data={"body": "big", "photo": image_file("x.png", PNG_BYTES + b"0" * 500)},
            headers=auth,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 413
        assert resp.get_json()["status"] == 413


class TestReadPosts:
    def test_feed_is_newest_first(self, client, auth, make_post):
        make_post(auth, "first")
        make_post(auth, "second")
        bodies = [p["body"] for p in client.get("/api/v1/post").get_json()["data"]]
        assert bodies == ["second", "first"]

    def test_feed_pagination(self, client, auth, make_post):
        for i in range(5):
            make_post(auth, f"post {i}")
        page = client.get("/api/v1/post?limit=2&offset=1").get_json()["data"]
        assert [p["body"] for p in page] == ["post 3", "post 2"]

    def test_feed_limit_is_capped(self, client, auth):
        assert client.get("/api/v1/post?limit=100000").status_code == 200

    def test_invalid_pagination_400(self, client):
        assert client.get("/api/v1/post?limit=abc").status_code == 400
        assert client.get("/api/v1/post?limit=0").status_code == 400
        assert client.get("/api/v1/post?offset=-1").status_code == 400

    def test_empty_feed(self, client):
        resp = client.get("/api/v1/post")
        assert resp.status_code == 200 and resp.get_json()["data"] == []

    def test_get_single_post_includes_comments(self, client, auth, make_post):
        post = make_post(auth)
        client.post(f"/api/v1/comment/{post['id']}", json={"body": "nice"}, headers=auth)
        data = client.get(f"/api/v1/post/{post['id']}").get_json()["data"]
        assert len(data["comments"]) == 1

    def test_get_missing_post_404(self, client):
        resp = client.get("/api/v1/post/145678")
        assert resp.status_code == 404
        assert resp.get_json() == {"status": 404, "message": "Post not found"}

    def test_my_posts_only_returns_own(self, client, auth, other_auth, make_post):
        make_post(auth, "mine")
        make_post(other_auth, "theirs")
        mine = client.get("/api/v1/mypost", headers=auth).get_json()["data"]
        assert [p["body"] for p in mine] == ["mine"]

    def test_my_posts_requires_auth(self, client):
        assert client.get("/api/v1/mypost").status_code == 401


class TestModifyPosts:
    def test_owner_can_edit(self, client, auth, make_post):
        post = make_post(auth)
        resp = client.put(f"/api/v1/post/{post['id']}", json={"body": "edited"}, headers=auth)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["body"] == "edited"

    def test_edit_validates_body(self, client, auth, make_post):
        post = make_post(auth)
        assert client.put(f"/api/v1/post/{post['id']}", json={"body": ""}, headers=auth).status_code == 422

    def test_other_user_cannot_edit(self, client, auth, other_auth, make_post):
        post = make_post(auth)
        resp = client.put(f"/api/v1/post/{post['id']}", json={"body": "hijack"}, headers=other_auth)
        assert resp.status_code == 403
        assert client.get(f"/api/v1/post/{post['id']}").get_json()["data"]["body"] != "hijack"

    def test_owner_can_delete_and_comments_cascade(self, client, auth, make_post):
        post = make_post(auth)
        client.post(f"/api/v1/comment/{post['id']}", json={"body": "c"}, headers=auth)
        resp = client.delete(f"/api/v1/post/{post['id']}", headers=auth)
        assert resp.status_code == 204
        assert client.get(f"/api/v1/post/{post['id']}").status_code == 404
        assert client.get(f"/api/v1/comment/1").status_code == 404

    def test_other_user_cannot_delete(self, client, auth, other_auth, make_post):
        post = make_post(auth)
        assert client.delete(f"/api/v1/post/{post['id']}", headers=other_auth).status_code == 403
        assert client.get(f"/api/v1/post/{post['id']}").status_code == 200

    def test_delete_missing_404(self, client, auth):
        assert client.delete("/api/v1/post/999", headers=auth).status_code == 404

    def test_delete_requires_auth(self, client, auth, make_post):
        post = make_post(auth)
        assert client.delete(f"/api/v1/post/{post['id']}").status_code == 401
