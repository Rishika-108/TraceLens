import time
from datetime import timedelta
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification():
    raw_password = "SecretForensicPassword@2026!"
    hashed = hash_password(raw_password)

    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_lifecycle():
    payload = {"sub": "investigator_alice", "role": "INVESTIGATOR"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=5))

    assert isinstance(token, str)
    assert token.count(".") == 2

    # Verify decoding
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "investigator_alice"
    assert decoded["role"] == "INVESTIGATOR"
    assert "exp" in decoded


def test_jwt_token_expired():
    payload = {"sub": "expired_user", "role": "INVESTIGATOR"}
    # Token expired 10 seconds ago
    token = create_access_token(payload, expires_delta=timedelta(seconds=-10))

    decoded = decode_access_token(token)
    assert decoded is None


def test_jwt_token_invalid_signature():
    payload = {"sub": "tampered_user"}
    token = create_access_token(payload)

    parts = token.split(".")
    tampered_payload = parts[1] + "tamper"
    tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

    assert decode_access_token(tampered_token) is None


def test_auth_api_registration_and_login(client):
    # 1. Register
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "username": "det_holmes",
            "email": "holmes@scotlandyard.uk",
            "password": "Investigation221B!",
            "role": "INVESTIGATOR",
        },
    )
    assert reg_resp.status_code == 201
    token_data = reg_resp.json()
    assert "access_token" in token_data
    assert token_data["user"]["username"] == "det_holmes"

    token = token_data["access_token"]

    # 2. Login
    login_resp = client.post(
        "/api/auth/login",
        json={"username": "det_holmes", "password": "Investigation221B!"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["user"]["email"] == "holmes@scotlandyard.uk"

    # 3. Access Protected /me Endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "det_holmes"

    # 4. Access Protected /me without token should fail
    unauth_resp = client.get("/api/auth/me")
    assert unauth_resp.status_code == 401
