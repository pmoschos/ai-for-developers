"""
Tests for hitl_search_agent.utils.image_utils
"""

from hitl_search_agent.utils.image_utils import extract_image_urls


class TestExtractImageUrls:
    """Unit tests for extract_image_urls."""

    def test_none_input(self):
        assert extract_image_urls(None) == []

    def test_empty_dict(self):
        assert extract_image_urls({}) == []

    def test_empty_list(self):
        assert extract_image_urls([]) == []

    def test_top_level_string_images(self):
        raw = {"images": ["http://img1.png", "http://img2.png"]}
        result = extract_image_urls(raw)
        assert result == ["http://img1.png", "http://img2.png"]

    def test_top_level_dict_images(self):
        raw = {"images": [{"url": "http://img1.png"}, {"src": "http://img2.png"}]}
        result = extract_image_urls(raw)
        assert result == ["http://img1.png", "http://img2.png"]

    def test_results_with_image_url(self):
        raw = {
            "results": [
                {"image_url": "http://a.png"},
                {"image_url": "http://b.png"},
            ]
        }
        result = extract_image_urls(raw)
        assert result == ["http://a.png", "http://b.png"]

    def test_nested_images_in_results(self):
        raw = {
            "results": [
                {"images": ["http://nested1.png", "http://nested2.png"]},
            ]
        }
        result = extract_image_urls(raw)
        assert result == ["http://nested1.png", "http://nested2.png"]

    def test_list_format(self):
        raw = [
            {"image_url": "http://list1.png"},
            {"image": "http://list2.png"},
        ]
        result = extract_image_urls(raw)
        assert result == ["http://list1.png", "http://list2.png"]

    def test_deduplication(self):
        raw = {"images": ["http://dup.png", "http://dup.png", "http://other.png"]}
        result = extract_image_urls(raw)
        assert result == ["http://dup.png", "http://other.png"]

    def test_mixed_formats(self):
        raw = {
            "images": ["http://top.png"],
            "results": [
                {"image_url": "http://res.png", "images": ["http://nested.png"]},
            ],
        }
        result = extract_image_urls(raw)
        assert result == ["http://top.png", "http://res.png", "http://nested.png"]

    def test_skips_none_values(self):
        raw = {
            "images": [None, "http://valid.png"],
            "results": [{"image_url": None}],
        }
        result = extract_image_urls(raw)
        assert result == ["http://valid.png"]
