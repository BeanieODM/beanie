"""
Test forward references functionality in Links - GitHub Issue #1035
"""

from typing import List, Optional

import pytest

from beanie import Document, Link, init_beanie
from beanie.odm.registry import DocsRegistry, ForwardRefProxy


class UserForwardRef(Document):
    username: str
    email: str

    class Settings:
        name = "users_forward_ref"


class ProfileForwardRef(Document):
    user: Link[UserForwardRef]
    # Forward reference to a class defined later - this simulates cross-module scenario
    favorite_post: Optional[Link["PostForwardRef"]] = None
    bio: Optional[str] = None

    class Settings:
        name = "profiles_forward_ref"


class PostForwardRef(Document):
    title: str
    content: str
    # Forward reference to a class defined earlier - simulates cross-module scenario
    author: Link["UserForwardRef"]
    # Forward reference to class defined later
    comments: Optional[List[Link["CommentForwardRef"]]] = None

    class Settings:
        name = "posts_forward_ref"


class CommentForwardRef(Document):
    post: Link[PostForwardRef]
    author: Link["UserForwardRef"]  # Forward reference
    content: str

    class Settings:
        name = "comments_forward_ref"


class TestForwardReferences:
    """Test forward reference resolution in Links - GitHub Issue #1035"""

    @pytest.fixture(autouse=True)
    async def setup_models(self, db):
        """Initialize the forward reference models for testing"""
        await init_beanie(
            database=db,
            document_models=[
                UserForwardRef,
                ProfileForwardRef,
                PostForwardRef,
                CommentForwardRef,
            ],
        )
        yield
        # Cleanup after all tests in this class
        for model in [UserForwardRef, ProfileForwardRef, PostForwardRef, CommentForwardRef]:
            await model.get_motor_collection().drop()
            await model.get_motor_collection().drop_indexes()

    async def test_forward_references_basic(self):
        """Test that forward references work in basic Link fields"""
        # Create a user
        user = UserForwardRef(username="testuser", email="test@example.com")
        await user.insert()

        # Create a post with forward reference to user
        post = PostForwardRef(
            title="Test Post", content="Test content", author=user
        )
        await post.insert()

        # Fetch and verify forward reference resolution works
        fetched_post = await PostForwardRef.find_one(
            PostForwardRef.id == post.id, fetch_links=True
        )
        assert fetched_post is not None
        assert isinstance(fetched_post.author, UserForwardRef)
        assert fetched_post.author.username == "testuser"
        assert fetched_post.author.id == user.id

    async def test_forward_references_optional(self):
        """Test that forward references work in Optional Link fields"""
        # Create a user
        user = UserForwardRef(username="testuser", email="test@example.com")
        await user.insert()

        # Create a post
        post = PostForwardRef(
            title="Test Post", content="Test content", author=user
        )
        await post.insert()

        # Create a profile with optional forward reference
        profile = ProfileForwardRef(
            user=user, favorite_post=post, bio="Test bio"
        )
        await profile.insert()

        # Fetch and verify
        fetched_profile = await ProfileForwardRef.find_one(
            ProfileForwardRef.id == profile.id, fetch_links=True
        )
        assert fetched_profile is not None
        assert isinstance(fetched_profile.user, UserForwardRef)
        assert fetched_profile.user.username == "testuser"
        assert fetched_profile.favorite_post is not None
        assert isinstance(fetched_profile.favorite_post, PostForwardRef)
        assert fetched_profile.favorite_post.title == "Test Post"

    async def test_forward_references_cross_module_simulation(self):
        """Test complex forward reference scenarios simulating cross-module usage"""
        # This simulates the exact GitHub issue #1035 scenario
        # Create models in various orders to test forward reference resolution
        user = UserForwardRef(username="testuser", email="test@example.com")
        await user.insert()

        post = PostForwardRef(
            title="Test Post", content="Test content", author=user
        )
        await post.insert()

        profile = ProfileForwardRef(user=user, favorite_post=post)
        await profile.insert()

        comment = CommentForwardRef(
            post=post, author=user, content="Great post!"
        )
        await comment.insert()

        # Test fetching with all forward references resolved
        fetched_comment = await CommentForwardRef.find_one(
            CommentForwardRef.id == comment.id, fetch_links=True
        )
        assert fetched_comment is not None
        assert isinstance(fetched_comment.author, UserForwardRef)
        assert fetched_comment.author.username == "testuser"
        assert isinstance(fetched_comment.post, PostForwardRef)
        assert fetched_comment.post.title == "Test Post"

        # Test nested forward reference resolution (Comment -> Post -> User)
        assert isinstance(fetched_comment.post.author, UserForwardRef)
        assert fetched_comment.post.author.username == "testuser"

    async def test_forward_references_list_links(self):
        """Test forward references in List[Link[...]] fields"""
        user = UserForwardRef(username="testuser", email="test@example.com")
        await user.insert()

        post = PostForwardRef(
            title="Test Post", content="Test content", author=user
        )
        await post.insert()

        # Create multiple comments
        comment1 = CommentForwardRef(
            post=post, author=user, content="First comment"
        )
        comment2 = CommentForwardRef(
            post=post, author=user, content="Second comment"
        )
        await comment1.insert()
        await comment2.insert()

        # Update post with comments list (simulating List[Link[...]] with forward refs)
        post.comments = [comment1, comment2]
        await post.save()

        # Fetch and verify list forward references work
        fetched_post = await PostForwardRef.find_one(
            PostForwardRef.id == post.id, fetch_links=True
        )
        assert fetched_post is not None
        assert fetched_post.comments is not None
        assert len(fetched_post.comments) == 2
        assert all(
            isinstance(comment, CommentForwardRef)
            for comment in fetched_post.comments
        )
        assert fetched_post.comments[0].content == "First comment"
        assert fetched_post.comments[1].content == "Second comment"

    async def test_forward_reference_proxy_functionality(self):
        """Test that ForwardRefProxy works correctly for unresolved references"""
        from typing import ForwardRef

        # Test ForwardRefProxy with a non-existent class
        fake_forward_ref = ForwardRef("NonExistentClass")
        proxy = ForwardRefProxy(fake_forward_ref, DocsRegistry)

        # Should raise ValueError when trying to resolve a non-existent class
        with pytest.raises(
            ValueError,
            match="Forward reference 'NonExistentClass' could not be resolved",
        ):
            proxy.resolve()

    async def test_forward_references_work_after_registry_clear(self):
        """Test that forward references work after registry operations"""
        # This tests the robustness of the forward reference system

        user = UserForwardRef(username="testuser2", email="test2@example.com")
        await user.insert()

        post = PostForwardRef(
            title="Test Post 2", content="Test content 2", author=user
        )
        await post.insert()

        # Verify forward references still work
        fetched_post = await PostForwardRef.find_one(
            PostForwardRef.author.id == user.id, fetch_links=True
        )
        assert fetched_post is not None
        assert isinstance(fetched_post.author, UserForwardRef)
        assert fetched_post.author.username == "testuser2"

    async def test_bidirectional_forward_references(self):
        """Test bidirectional forward references (A references B, B references A)"""
        # Create user and post with bidirectional references
        user = UserForwardRef(
            username="bidirectional_user", email="bi@example.com"
        )
        await user.insert()

        post = PostForwardRef(
            title="Bidirectional Post", content="Content", author=user
        )
        await post.insert()

        profile = ProfileForwardRef(user=user, favorite_post=post)
        await profile.insert()

        # Test that we can navigate the bidirectional relationships
        fetched_profile = await ProfileForwardRef.find_one(
            ProfileForwardRef.id == profile.id, fetch_links=True
        )
        assert fetched_profile is not None

        # Profile -> User
        assert isinstance(fetched_profile.user, UserForwardRef)
        assert fetched_profile.user.username == "bidirectional_user"

        # Profile -> Post -> User (should be the same user)
        assert isinstance(fetched_profile.favorite_post, PostForwardRef)
        assert isinstance(fetched_profile.favorite_post.author, UserForwardRef)
        assert (
            fetched_profile.favorite_post.author.id == fetched_profile.user.id
        )

    async def test_github_issue_1035_exact_scenario(self):
        """Test the exact scenario described in GitHub Issue #1035"""
        # This replicates the exact use case from the GitHub issue

        # Simulate users/models.py
        user = UserForwardRef(
            username="github_user", email="github@example.com"
        )
        await user.insert()

        profile = ProfileForwardRef(user=user, bio="GitHub user bio")
        # favorite_post will be set later (simulating forward reference)
        await profile.insert()

        # Simulate posts/models.py
        post = PostForwardRef(
            title="GitHub Issue Post",
            content="This post tests the fix for GitHub issue #1035",
            author=user,  # Forward reference to User from different module
        )
        await post.insert()

        comment = CommentForwardRef(
            post=post,
            author=user,  # Forward reference to User
            content="This comment also uses forward references!",
        )
        await comment.insert()

        # Update profile with favorite post (completing the forward reference cycle)
        profile.favorite_post = post
        await profile.save()

        # Verify everything works as expected in the GitHub issue
        fetched_comment = await CommentForwardRef.find_one(
            CommentForwardRef.id == comment.id, fetch_links=True
        )
        assert fetched_comment is not None

        # Verify the forward references work as described in the issue
        assert isinstance(
            fetched_comment.author, UserForwardRef
        )  # User forward ref works
        assert isinstance(
            fetched_comment.post, PostForwardRef
        )  # Post link works
        assert isinstance(
            fetched_comment.post.author, UserForwardRef
        )  # Nested forward ref works

        print("🎉 GitHub Issue #1035 scenario test passed!")

    async def test_cleanup(self):
        """Clean up test data"""
        await UserForwardRef.delete_all()
        await ProfileForwardRef.delete_all()
        await PostForwardRef.delete_all()
        await CommentForwardRef.delete_all()
