import logging
import secrets
import string
from typing import Any, Optional

from django.utils.text import slugify

logger = logging.getLogger(__name__)


class DbFunctions:
    """Database utility functions for slug generation and random string creation."""

    RANDOM_SUFFIX_LENGTH = 4
    RANDOM_CHARS = string.ascii_lowercase + string.digits

    @staticmethod
    def random_string_generator(size: int = RANDOM_SUFFIX_LENGTH, chars: str = RANDOM_CHARS) -> str:
        """
        Generate a secure random string of specified size.

        Args:
            size: Length of the random string (default: 4)
            chars: Characters to choose from (default: lowercase + digits)

        Returns:
            A random string of the specified size.
        """
        return ''.join(secrets.choice(chars) for _ in range(size))

    @staticmethod
    def generate_unique_slug(
        instance: Any,
        field_value: str,
        new_slug: Optional[str] = None,
        max_attempts: int = 100,
    ) -> str:
        """
        Generate a unique slug for a given instance based on the provided field value.

        Args:
            instance: The model instance to generate a slug for.
            field_value: The string value to slugify.
            new_slug: Optional pre-generated slug (used internally for recursion).
            max_attempts: Maximum number of attempts to find a unique slug (prevents infinite loops).

        Returns:
            A unique slug string.

        Raises:
            ValueError: If unable to generate unique slug after max_attempts.
            AttributeError: If instance doesn't have a 'slug' field.
        """
        if new_slug is not None:
            slug = new_slug
        else:
            slug = slugify(field_value)

        klass = instance.__class__
        try:
            max_length = klass._meta.get_field('slug').max_length
        except Exception as e:
            logger.error(f"❌ Error retrieving slug field metadata for {klass.__name__}: {e}")
            raise AttributeError(f"Instance {klass.__name__} must have a 'slug' field") from e

        slug = slug[:max_length]

        # Check if slug already exists
        qs_exists = klass.objects.filter(slug=slug).exists()

        if not qs_exists:
            logger.info(f"✅ Unique slug generated: {slug}")
            return slug

        # Attempt counter to prevent infinite recursion
        if new_slug is not None:
            # Count how many hyphens exist (approximates attempt number)
            attempt_count = new_slug.count('-')
            if attempt_count >= max_attempts:
                error_msg = f"❌ Unable to generate unique slug after {max_attempts} attempts for {klass.__name__}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # Generate new slug with random suffix
        random_suffix = DbFunctions.random_string_generator(size=DbFunctions.RANDOM_SUFFIX_LENGTH)
        new_slug_candidate = f"{slug[:max_length - 5]}-{random_suffix}"
        logger.debug(f"Slug collision detected. Retrying with: {new_slug_candidate}")

        return DbFunctions.generate_unique_slug(
            instance,
            field_value,
            new_slug=new_slug_candidate,
            max_attempts=max_attempts,
        )

    @staticmethod
    def generate_unique_slug_for_related_object(
        instance: Any,
        field_value: str,
        related_field_name: str,
        new_slug: Optional[str] = None,
        max_attempts: int = 1000,
    ) -> str:
        """
        Generate a unique slug for an instance where the slug must be unique relative to a related object.

        Example: ArticlePage.slug must be unique per Article.

        Args:
            instance: The model instance to generate a slug for (e.g., ArticlePage instance).
            field_value: The string value to slugify (e.g., article_page.title).
            related_field_name: The name of the ForeignKey field linking to the parent (e.g., 'article').
            new_slug: Optional pre-generated slug (used internally for recursion).
            max_attempts: Maximum number of attempts to find a unique slug (prevents infinite loops).

        Returns:
            A unique slug string (unique per related object).

        Raises:
            ValueError: If unable to generate unique slug after max_attempts.
            AttributeError: If instance doesn't have a 'slug' field or the related field doesn't exist.

        Example:
            >>> article_page = ArticlePage(article=some_article, title="Introduction")
            >>> slug = DbFunctions.generate_unique_slug_for_related_object(
            ...     article_page,
            ...     article_page.title,
            ...     'article'
            ... )
            >>> article_page.slug = slug
            >>> article_page.save()
        """
        if new_slug is not None:
            slug = new_slug
        else:
            slug = slugify(field_value)

        klass = instance.__class__

        # Validate slug field exists
        try:
            max_length = klass._meta.get_field('slug').max_length
        except Exception as e:
            logger.error(f"❌ Error retrieving slug field metadata for {klass.__name__}: {e}")
            raise AttributeError(f"Instance {klass.__name__} must have a 'slug' field") from e

        # Validate related field exists
        try:
            related_instance = getattr(instance, related_field_name)
        except Exception as e:
            logger.error(f"❌ Error retrieving related field '{related_field_name}' for {klass.__name__}: {e}")
            raise AttributeError(
                f"Instance {klass.__name__} must have a ForeignKey field '{related_field_name}'"
            ) from e

        slug = slug[:max_length]

        # Check if slug already exists for THIS related object
        filter_kwargs = {
            'slug': slug,
            related_field_name: related_instance,
        }
        qs_exists = klass.objects.filter(**filter_kwargs).exists()

        if not qs_exists:
            logger.info(f"✅ Unique slug generated (relative to {related_field_name}): {slug}")
            return slug

        # Attempt counter to prevent infinite recursion
        if new_slug is not None:
            attempt_count = new_slug.count('-')
            if attempt_count >= max_attempts:
                error_msg = f"❌ Unable to generate unique slug after {max_attempts} attempts for {klass.__name__} (related to {related_field_name})"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # Generate new slug with random suffix
        random_suffix = DbFunctions.random_string_generator(size=DbFunctions.RANDOM_SUFFIX_LENGTH)
        new_slug_candidate = f"{slug[:max_length - 5]}-{random_suffix}"
        logger.debug(f"Slug collision detected (relative to {related_field_name}). Retrying with: {new_slug_candidate}")

        return DbFunctions.generate_unique_slug_for_related_object(
            instance,
            field_value,
            related_field_name,
            new_slug=new_slug_candidate,
            max_attempts=max_attempts,
        )

    @staticmethod
    def unique_slug_generator_by_title(
        instance: Any,
        new_slug: Optional[str] = None,
    ) -> str:
        """
        Generate a unique slug for the instance based on its 'title' field.

        Args:
            instance: The model instance with a 'title' attribute.
            new_slug: Optional pre-generated slug (used internally for recursion).

        Returns:
            A unique slug string.

        Raises:
            AttributeError: If instance doesn't have a 'title' attribute.
        """
        if not hasattr(instance, 'title'):
            raise AttributeError(f"Instance {instance.__class__.__name__} must have a 'title' attribute")

        return DbFunctions.generate_unique_slug(instance, instance.title, new_slug=new_slug)
