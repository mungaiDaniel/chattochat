from conftest import GIF_BYTES, JPEG_BYTES, PNG_BYTES, WEBP_BYTES


class TestUsers:
    def test_list_users_is_public_and_hides_emails(self, client, register):
        register()
        resp = client.get("/api/v1/user")
        assert resp.status_code == 200
        users = resp.get_json()["data"]
        assert len(users) == 1
        assert "email" not in users[0]

    def test_list_users_empty(self, client):
        assert client.get("/api/v1/user").get_json()["data"] == []

    def test_get_one_user(self, client, register):
        user = register()
        resp = client.get(f"/api/v1/user/{user['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["username"] == "testuser"

    def test_get_missing_user_404(self, client):
        resp = client.get("/api/v1/user/12345")
        assert resp.status_code == 404
        assert resp.get_json()["message"] == "User not found"

    def test_me_returns_own_email(self, client, auth):
        resp = client.get("/api/v1/user/me", headers=auth)
        assert resp.status_code == 200
        assert resp.get_json()["data"]["email"] == "test.user@example.com"

    def test_me_requires_auth(self, client):
        assert client.get("/api/v1/user/me").status_code == 401


class TestProfile:
    def test_update_profile_pictures(self, client, auth):
        resp = client.put(
            "/api/v1/user/profile",
            json={"personPic": "uploads/photos/a.png", "coverPic": "https://example.com/c.jpg"},
            headers=auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["personPic"] == "/uploads/photos/a.png"
        assert data["coverPic"] == "https://example.com/c.jpg"

    def test_requires_at_least_one_field(self, client, auth):
        assert client.put("/api/v1/user/profile", json={}, headers=auth).status_code == 422

    def test_rejects_arbitrary_path(self, client, auth):
        resp = client.put("/api/v1/user/profile", json={"personPic": "../../etc/passwd"}, headers=auth)
        assert resp.status_code == 422

    def test_requires_auth(self, client):
        assert client.put("/api/v1/user/profile", json={"personPic": "uploads/x.png"}).status_code == 401


class TestRole:
    def test_upgrade_and_downgrade(self, client, auth):
        up = client.put("/api/v1/premium", json={"user_role": "premium"}, headers=auth)
        assert up.status_code == 200 and up.get_json()["data"]["user_role"] == "premium"
        down = client.put("/api/v1/premium", json={"user_role": "user"}, headers=auth)
        assert down.get_json()["data"]["user_role"] == "user"

    def test_cannot_set_arbitrary_role(self, client, auth):
        resp = client.put("/api/v1/premium", json={"user_role": "admin"}, headers=auth)
        assert resp.status_code == 422

    def test_requires_auth(self, client):
        assert client.put("/api/v1/premium", json={"user_role": "premium"}).status_code == 401


class TestUpload:
    def test_upload_each_supported_format(self, client, auth, image_file):
        cases = [("a.png", PNG_BYTES), ("a.jpg", JPEG_BYTES), ("a.gif", GIF_BYTES), ("a.webp", WEBP_BYTES)]
        for name, content in cases:
            resp = client.post(
                "/api/v1/upload-photo",
                data={"photo": image_file(name, content)},
                headers=auth,
                content_type="multipart/form-data",
            )
            assert resp.status_code == 200, name
            body = resp.get_json()
            assert body["photo_url"].startswith("/uploads/photos/")
            assert body["filename"].endswith(name.split(".")[1])

    def test_uploaded_file_is_served_back(self, client, auth, image_file):
        resp = client.post(
            "/api/v1/upload-photo", data={"photo": image_file()}, headers=auth,
            content_type="multipart/form-data",
        )
        served = client.get(resp.get_json()["photo_url"])
        assert served.status_code == 200
        assert served.data == PNG_BYTES

    def test_rejects_wrong_extension(self, client, auth, image_file):
        resp = client.post(
            "/api/v1/upload-photo", data={"photo": image_file("evil.exe", PNG_BYTES)},
            headers=auth, content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_rejects_disguised_non_image(self, client, auth, image_file):
        resp = client.post(
            "/api/v1/upload-photo", data={"photo": image_file("shell.png", b"<?php echo 1; ?>")},
            headers=auth, content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_missing_file_400(self, client, auth):
        resp = client.post("/api/v1/upload-photo", data={}, headers=auth,
                           content_type="multipart/form-data")
        assert resp.status_code == 400

    def test_requires_auth(self, client, image_file):
        resp = client.post("/api/v1/upload-photo", data={"photo": image_file()},
                           content_type="multipart/form-data")
        assert resp.status_code == 401

    def test_unknown_upload_404_and_no_traversal(self, client):
        assert client.get("/uploads/photos/missing.png").status_code == 404
        assert client.get("/uploads/../app/config.py").status_code == 404
