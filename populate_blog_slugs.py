#!/usr/bin/env python3
"""
Script to populate slugs for existing blog posts
"""

import os
import sys
import django
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tours_travels.settings')
django.setup()

from blog.models import Post

def populate_slugs():
    """Populate slugs for existing posts"""
    posts_without_slugs = Post.objects.filter(slug__isnull=True) | Post.objects.filter(slug='')
    
    print(f"Found {posts_without_slugs.count()} posts without slugs")
    
    for post in posts_without_slugs:
        base_slug = slugify(post.title)
        slug = base_slug
        counter = 1
        
        # Ensure unique slug
        while Post.objects.filter(slug=slug).exclude(pk=post.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        post.slug = slug
        post.save()
        print(f"Updated post '{post.title[:50]}...' with slug: {slug}")
    
    print(f"Successfully updated {posts_without_slugs.count()} posts")

if __name__ == "__main__":
    populate_slugs()
