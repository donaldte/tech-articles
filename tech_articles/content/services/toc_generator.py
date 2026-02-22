"""
Service for generating Table of Contents from markdown content.
"""
import re
from typing import List, Dict

from django.utils.text import slugify


class TOCGenerator:
    """Generates hierarchical TOC structure from markdown content."""

    # Regex to match markdown headings: # Heading, ## Heading, etc.
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    @classmethod
    def generate_from_article(cls, article) -> List[Dict]:
        """
        Generate TOC from all pages of an article.

        Returns:
            List of heading dictionaries with structure:
            {
                'id': 'heading-slug',
                'text': 'Heading Text',
                'level': 2,
                'page_number': 1,
                'children': []
            }
        """
        all_headings = []

        for page in article.pages.all().order_by('page_number'):
            headings = cls._extract_headings(page.content, page.page_number)
            all_headings.extend(headings)

        return cls._build_hierarchy(all_headings)

    @classmethod
    def _extract_headings(cls, markdown_text: str, page_number: int = 1) -> List[Dict]:
        """Extract all headings from markdown text."""
        headings = []
        matches = cls.HEADING_PATTERN.finditer(markdown_text)

        for match in matches:
            hashes, text = match.groups()
            level = len(hashes)
            heading_id = slugify(text)

            headings.append({
                'id': heading_id,
                'text': text.strip(),
                'level': level,
                'page_number': page_number,
                'children': []
            })

        return headings

    @classmethod
    def _build_hierarchy(cls, headings: List[Dict]) -> List[Dict]:
        """Convert flat list of headings into hierarchical structure."""
        if not headings:
            return []

        root = []
        stack = []

        for heading in headings:
            level = heading['level']

            while stack and stack[-1]['level'] >= level:
                stack.pop()

            if stack:
                stack[-1]['children'].append(heading)
            else:
                root.append(heading)

            stack.append(heading)

        return root
