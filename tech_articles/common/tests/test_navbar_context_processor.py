"""Tests for navbar context processor."""
import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from tech_articles.common.context_processors.navbar import navbar_menu

User = get_user_model()


@pytest.mark.django_db
class TestNavbarContextProcessor:
    """Test suite for navbar menu context processor."""

    def test_navbar_menu_returns_dict(self):
        """Test that navbar_menu returns a dictionary."""
        request = HttpRequest()
        request.user = User()
        result = navbar_menu(request)
        assert isinstance(result, dict)
        assert 'navbar_menu_items' in result

    def test_navbar_menu_items_is_list(self):
        """Test that navbar_menu_items is a list."""
        request = HttpRequest()
        request.user = User()
        result = navbar_menu(request)
        assert isinstance(result['navbar_menu_items'], list)

    def test_public_items_shown_to_anonymous(self):
        """Test that public menu items are shown to anonymous users."""
        request = HttpRequest()
        request.user = User()
        result = navbar_menu(request)
        items = result['navbar_menu_items']
        
        # Should include Home, Appointments, Articles, Resources, About
        public_labels = ['Home', 'Appointments', 'Articles', 'Resources', 'About']
        item_labels = [str(item['label']) for item in items]
        
        for label in public_labels:
            assert label in item_labels

    def test_authenticated_items_hidden_from_anonymous(self):
        """Test that authenticated-only items are hidden from anonymous users."""
        request = HttpRequest()
        request.user = User()
        result = navbar_menu(request)
        items = result['navbar_menu_items']
        
        # Dashboard should not be in the list for anonymous users
        item_labels = [str(item['label']) for item in items]
        assert 'Dashboard' not in item_labels

    @pytest.mark.django_db
    def test_authenticated_items_shown_to_logged_in(self):
        """Test that authenticated items are shown to logged-in users."""
        request = HttpRequest()
        request.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        result = navbar_menu(request)
        items = result['navbar_menu_items']
        
        # Dashboard should be in the list for authenticated users
        item_labels = [str(item['label']) for item in items]
        assert 'Dashboard' in item_labels

    def test_items_sorted_by_order(self):
        """Test that menu items are sorted by order field."""
        request = HttpRequest()
        request.user = User()
        result = navbar_menu(request)
        items = result['navbar_menu_items']
        
        # Check that items are in ascending order
        orders = [item['order'] for item in items]
        assert orders == sorted(orders)

    def test_all_items_have_required_fields(self):
        """Test that all menu items have required fields."""
        request = HttpRequest()
        request.user = User()
        result = navbar_menu(request)
        items = result['navbar_menu_items']
        
        required_fields = ['order', 'label', 'url']
        for item in items:
            for field in required_fields:
                assert field in item, f"Item missing required field: {field}"

    def test_items_have_icons(self):
        """Test that menu items have icon data."""
        request = HttpRequest()
        request.user = User()
        result = navbar_menu(request)
        items = result['navbar_menu_items']
        
        for item in items:
            # Each item should have either 'icon' or 'icon_fill'
            assert 'icon' in item or 'icon_fill' in item, \
                f"Item {item['label']} missing icon data"
