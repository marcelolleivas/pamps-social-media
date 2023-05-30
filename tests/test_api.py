import pytest

from pamps.models import Social


@pytest.mark.order(1)
def test_post_create_user_1(api_client_user_1):
    """Create 2 posts with user 1"""
    for n in (1, 2):
        response = api_client_user_1.post(
            "/post/",
            json={
                "text": f"hello test {n}",
            },
        )
        assert response.status_code == 201
        result = response.json()
        assert result["text"] == f"hello test {n}"
        assert result["parent_id"] is None


@pytest.mark.order(2)
def test_reply_on_post_1(api_client, api_client_user_1, api_client_user_2):
    """each user will add a reply to the first post"""
    posts = api_client.get("/post/user/user_1/").json()
    first_post = posts[0]
    for n, client in enumerate((api_client_user_1, api_client_user_2), 1):
        response = client.post(
            "/post/",
            json={
                "text": f"reply from user{n}",
                "parent_id": first_post["id"],
            },
        )
        assert response.status_code == 201
        result = response.json()
        assert result["text"] == f"reply from user{n}"
        assert result["parent_id"] == first_post["id"]


@pytest.mark.order(3)
def test_post_list_without_replies(api_client):
    response = api_client.get("/post/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    for result in results:
        assert result["parent_id"] is None
        assert "hello test" in result["text"]


@pytest.mark.order(4)
def test_post_1_detail(api_client):
    posts = api_client.get("/post/user/user_1/").json()
    first_post = posts[0]
    first_post_id = first_post["id"]

    response = api_client.get(f"/post/{first_post_id}/")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == first_post_id
    assert result["user_id"] == first_post["user_id"]
    assert result["text"] == "hello test 1"
    assert result["parent_id"] is None
    replies = result["replies"]
    assert len(replies) == 2
    for reply in replies:
        assert reply["parent_id"] == first_post_id
        assert "reply from user" in reply["text"]


@pytest.mark.order(5)
def test_all_posts_from_user_1(api_client):
    response = api_client.get("/post/user/user_1/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    for result in results:
        assert result["parent_id"] is None
        assert "hello test" in result["text"]


@pytest.mark.order(6)
def test_all_posts_from_user_1_with_replies(api_client):
    response = api_client.get(
        "/post/user/user_1/", params={"include_replies": True}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3


@pytest.mark.order(7)
def test_user_1_follows_user_2(session, api_client_user_1, api_client_user_2):
    response = api_client_user_1.post("/user/follow/2")
    assert response.status_code == 204
    assert len(response.content) == 0

    following_succeeded = (
        session.query(Social)
        .filter(Social.from_id == 1, Social.to_id == 2)
        .first()
    )
    assert following_succeeded


@pytest.mark.order(8)
def test_user_tries_following_non_existent_user_and_get_404(
        session, api_client_user_1, api_client_user_2
):
    response = api_client_user_1.post("/user/follow/3")
    assert response.status_code == 404
    result = response.json()
    following_succeeded = (
        session.query(Social)
        .filter(Social.from_id == 1, Social.to_id == 3)
        .first()
    )
    assert result["detail"] == "User not found"
    assert not following_succeeded


@pytest.mark.order(9)
def test_user_tries_following_negative_integer_and_get_400(session, api_client_user_1):
    response = api_client_user_1.post("/user/follow/-1")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Invalid user_id"


@pytest.mark.order(10)
def test_user_tries_following_himself_and_get_400(session, api_client_user_1):
    response = api_client_user_1.post("/user/follow/1")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Invalid user_id"


@pytest.mark.order(11)
def test_user_tries_following_again_and_get_204(
        session, api_client_user_1, api_client_user_2
):
    response = api_client_user_1.post("/user/follow/2")
    assert response.status_code == 204
    assert len(response.content) == 0
    following_count = (
        session.query(Social)
        .filter(Social.from_id == 1, Social.to_id == 2)
        .count()
    )
    assert following_count == 1


@pytest.mark.order(12)
def test_user_tries_unfollowing_negative_integer_and_get_400(
        session, api_client_user_1
):
    response = api_client_user_1.delete("/user/follow/-1")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Invalid user_id"


@pytest.mark.order(13)
def test_user_tries_unfollowing_himself_and_get_400(session, api_client_user_1):
    response = api_client_user_1.delete("/user/follow/1")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Invalid user_id"


@pytest.mark.order(13)
def test_user_tries_unfollowing_non_existent_user_and_get_404(
        session, api_client_user_1, api_client_user_2
):
    response = api_client_user_1.delete("/user/follow/3")
    assert response.status_code == 404
    result = response.json()
    following_succeeded = (
        session.query(Social)
        .filter(Social.from_id == 1, Social.to_id == 3)
        .first()
    )
    assert result["detail"] == "User not found"
    assert not following_succeeded


@pytest.mark.order(14)
def test_user_unfollows_user_and_get_204(
        session, api_client_user_1, api_client_user_2
):
    response = api_client_user_1.delete("/user/follow/2")
    assert response.status_code == 204
    assert len(response.content) == 0
    following_count = (
        session.query(Social)
        .filter(Social.from_id == 1, Social.to_id == 2)
        .count()
    )
    assert following_count == 0


@pytest.mark.order(15)
def test_user_tries_unfollowing_not_following_and_get_204(
        session, api_client_user_1, api_client_user_2
):
    response = api_client_user_2.delete("/user/follow/1")
    assert response.status_code == 204
    assert len(response.content) == 0
    following_count = (
        session.query(Social)
        .filter(Social.from_id == 2, Social.to_id == 1)
        .count()
    )
    assert following_count == 0
