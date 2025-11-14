# coding: utf-8
"""
发布功能 API 测试
"""
import pytest
import tempfile
import os
import json
from pathlib import Path
import frontmatter

from app import app
from services.post_service import PostService


class TestPublishAPI:

    @pytest.fixture
    def client(self):
        """测试客户端"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def temp_content_dir(self):
        """临时内容目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            content_dir = Path(temp_dir) / 'content'
            content_dir.mkdir()
            yield content_dir

    @pytest.fixture
    def temp_article(self, temp_content_dir):
        """临时测试文章"""
        article_path = temp_content_dir / 'test-article.md'
        article_content = """---
title: Test Article
draft: true
date: 2025-11-14
categories: ["tech"]
tags: ["test"]
---

This is test content for the article.
"""
        article_path.write_text(article_content)
        yield article_path

    def test_publish_article_success(self, client, temp_article):
        """测试成功发布文章"""
        response = client.post('/api/article/publish',
                             json={'file_path': str(temp_article)})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'operation_id' in data
        assert data['article_path'] == str(temp_article)

        # 验证文件被实际更改
        post = frontmatter.load(str(temp_article))
        assert post.get('draft') is False

    def test_publish_already_published(self, client, temp_article):
        """测试发布已发布的文章"""
        # 首先发布一次
        client.post('/api/article/publish', json={'file_path': str(temp_article)})

        # 再次尝试发布
        response = client.post('/api/article/publish',
                             json={'file_path': str(temp_article)})

        assert response.status_code == 409
        data = response.get_json()
        assert data['success'] is False
        assert 'already published' in data['error'].lower()

    def test_get_article_status(self, client, temp_article):
        """测试获取文章状态"""
        response = client.get(f'/api/article/status?file_path={str(temp_article)}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['status']['is_draft'] is True
        assert data['status']['is_publishable'] is True

    def test_publish_nonexistent_file(self, client):
        """测试发布不存在的文件"""
        response = client.post('/api/article/publish',
                             json={'file_path': '/nonexistent/path.md'})

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error'].lower()

    def test_publish_invalid_file_path(self, client):
        """测试发布无效文件路径"""
        response = client.post('/api/article/publish',
                             json={'file_path': '../../../etc/passwd'})

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_get_status_nonexistent_file(self, client):
        """测试获取不存在文件的状态"""
        response = client.get('/api/article/status?file_path=/nonexistent/path.md')

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error'].lower()