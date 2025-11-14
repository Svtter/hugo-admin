# coding: utf-8
"""
文章管理服务
负责文章的读取、保存、搜索等操作
复用 tasks.py 中的 BlogPost 类
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import yaml

# 导入内部模块
from utils.blog_parser import BlogPost, get_blog_posts, filter_posts_by_search
from services.cache_service import CacheService


class PostService:
    """文章管理服务"""

    def __init__(self, content_dir, use_cache=True):
        """
        初始化文章服务

        Args:
            content_dir: 内容目录路径
            use_cache: 是否使用缓存
        """
        self.content_dir = Path(content_dir)
        self.post_dir = self.content_dir / 'post'
        self.use_cache = use_cache

        # 初始化缓存服务
        if use_cache:
            self.cache_service = CacheService(content_dir)
        else:
            self.cache_service = None

    def get_posts(self, query='', category='', tag='', page=1, per_page=20):
        """
        获取文章列表

        Args:
            query: 搜索关键词
            category: 分类筛选
            tag: 标签筛选
            page: 页码
            per_page: 每页数量

        Returns:
            dict: 包含文章列表和分页信息
        """
        # 使用缓存或直接扫描
        if self.use_cache and self.cache_service:
            return self.cache_service.get_posts(query, category, tag, page, per_page)

        # 回退到原有的直接扫描方式
        # 获取所有文章
        all_posts = get_blog_posts(str(self.content_dir))

        # 应用搜索过滤
        if query:
            all_posts = filter_posts_by_search(all_posts, query, search_fields=['all'])

        # 按分类过滤
        if category:
            all_posts = [p for p in all_posts if category in p.categories]

        # 按标签过滤
        if tag:
            all_posts = [p for p in all_posts if tag in p.tags]

        # 计算分页
        total = len(all_posts)
        total_pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page

        # 获取当前页文章
        page_posts = all_posts[start:end]

        # 转换为 JSON 可序列化格式
        posts_data = []
        for post in page_posts:
            # BlogPost 类已经统一处理了所有字段类型，这里直接使用即可
            posts_data.append({
                'title': post.title,
                'path': str(post.relative_path),
                'full_path': str(post.file_path),
                'date': post.date[:10] if post.date else '',  # date 已经是字符串
                'description': post.description,
                'excerpt': post.excerpt,
                'tags': post.tags,  # 已经是列表
                'categories': post.categories,  # 已经是列表
                'mod_time': datetime.fromtimestamp(post.mod_time).strftime("%Y-%m-%d %H:%M")
            })

        return {
            'posts': posts_data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }

    def get_all_tags(self):
        """
        获取所有标签

        Returns:
            list: 标签列表(包含文章数量)
        """
        # 使用缓存或直接扫描
        if self.use_cache and self.cache_service:
            return self.cache_service.get_all_tags()

        # 回退到原有的直接扫描方式
        all_posts = get_blog_posts(str(self.content_dir))
        tag_count = {}

        for post in all_posts:
            # BlogPost 已经保证 tags 是列表
            for tag in post.tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1

        # 按文章数量排序
        tags = [{'name': tag, 'count': count} for tag, count in tag_count.items()]
        tags.sort(key=lambda x: x['count'], reverse=True)

        return tags

    def get_all_categories(self):
        """
        获取所有分类

        Returns:
            list: 分类列表(包含文章数量)
        """
        # 使用缓存或直接扫描
        if self.use_cache and self.cache_service:
            return self.cache_service.get_all_categories()

        # 回退到原有的直接扫描方式
        all_posts = get_blog_posts(str(self.content_dir))
        category_count = {}

        for post in all_posts:
            # BlogPost 已经保证 categories 是列表
            for category in post.categories:
                category_count[category] = category_count.get(category, 0) + 1

        # 按文章数量排序
        categories = [{'name': cat, 'count': count} for cat, count in category_count.items()]
        categories.sort(key=lambda x: x['count'], reverse=True)

        return categories

    def read_file(self, file_path):
        """
        读取文件内容

        Args:
            file_path: 文件路径(相对于 content 目录或绝对路径)

        Returns:
            (success, content): 成功标志和文件内容
        """
        try:
            # 处理路径
            if not Path(file_path).is_absolute():
                file_path = self.content_dir / file_path

            file_path = Path(file_path)

            # 安全检查:确保文件在 content 目录下
            if not self._is_safe_path(file_path):
                return False, "访问被拒绝:文件不在允许的目录中"

            # 检查文件是否存在
            if not file_path.exists():
                return False, f"文件不存在: {file_path}"

            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return True, content

        except Exception as e:
            return False, f"读取文件失败: {str(e)}"

    def save_file(self, file_path, content):
        """
        保存文件内容

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            (success, message): 成功标志和消息
        """
        try:
            # 处理路径
            if not Path(file_path).is_absolute():
                file_path = self.content_dir / file_path

            file_path = Path(file_path)

            # 安全检查
            if not self._is_safe_path(file_path):
                return False, "访问被拒绝:文件不在允许的目录中"

            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 更新缓存
            if self.use_cache and self.cache_service:
                self.cache_service.invalidate_post(str(file_path))

            return True, "文件保存成功"

        except Exception as e:
            return False, f"保存文件失败: {str(e)}"

    def create_post(self, title):
        """
        创建新文章

        Args:
            title: 文章标题

        Returns:
            (success, result): 成功标志和文件路径或错误消息
        """
        try:
            # 生成文件名
            post_name = str(datetime.now().date()) + f"-{title}"
            post_name = post_name.replace(" ", "-")

            # 创建文章目录
            post_folder = self.post_dir / post_name
            post_folder.mkdir(exist_ok=True)

            # 创建文章文件
            post_file = post_folder / "index.md"

            # 生成 frontmatter
            frontmatter = {
                'title': title,
                'date': datetime.now().isoformat(),
                'draft': True,
                'categories': [],
                'tags': []
            }

            # 写入文件
            content = "---\n"
            content += yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
            content += "---\n\n"
            content += "在这里编写你的文章内容...\n"

            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # 返回相对路径
            rel_path = post_file.relative_to(self.content_dir)

            # 更新缓存
            if self.use_cache and self.cache_service:
                self.cache_service.invalidate_post(str(post_file))

            return True, str(rel_path)

        except Exception as e:
            return False, f"创建文章失败: {str(e)}"

    def _is_safe_path(self, file_path):
        """
        检查路径是否安全(在 content 目录下)

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否安全
        """
        try:
            file_path = Path(file_path).resolve()
            content_dir = self.content_dir.resolve()

            # 检查是否在 content 目录下
            return str(file_path).startswith(str(content_dir))

        except Exception:
            return False

    def save_image(self, article_path, file):
        """
        保存图片到文章目录

        Args:
            article_path: 文章路径(相对于 content 目录)
            file: 上传的文件对象

        Returns:
            (success, result): 成功标志和图片URL或错误消息
        """
        try:
            # 构建文章目录路径
            if not Path(article_path).is_absolute():
                article_file = self.content_dir / article_path
            else:
                article_file = Path(article_path)

            # 获取文章所在目录
            article_dir = article_file.parent

            # 创建 pics 目录
            pics_dir = article_dir / 'pics'
            pics_dir.mkdir(exist_ok=True)

            # 生成安全的文件名
            filename = file.filename
            # 移除特殊字符
            safe_filename = "".join(c for c in filename if c.isalnum() or c in '.-_')

            # 保存文件
            file_path = pics_dir / safe_filename
            file.save(str(file_path))

            # 返回相对URL（相对于文章）
            relative_url = f"pics/{safe_filename}"

            return True, relative_url

        except Exception as e:
            return False, f"保存图片失败: {str(e)}"

    def list_images(self, article_path):
        """
        列出文章目录下的所有图片

        Args:
            article_path: 文章路径(相对于 content 目录)

        Returns:
            (success, result): 成功标志和图片列表或错误消息
        """
        try:
            # 构建文章目录路径
            if not Path(article_path).is_absolute():
                article_file = self.content_dir / article_path
            else:
                article_file = Path(article_path)

            # 获取文章所在目录
            article_dir = article_file.parent
            pics_dir = article_dir / 'pics'

            if not pics_dir.exists():
                return True, []

            # 支持的图片格式
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}

            # 列出所有图片
            images = []
            for img_path in pics_dir.iterdir():
                if img_path.is_file() and img_path.suffix.lower() in image_extensions:
                    images.append({
                        'name': img_path.name,
                        'url': f"pics/{img_path.name}",
                        'size': img_path.stat().st_size,
                        'modified': img_path.stat().st_mtime
                    })

            # 按修改时间倒序排列
            images.sort(key=lambda x: x['modified'], reverse=True)

            return True, images

        except Exception as e:
            return False, f"获取图片列表失败: {str(e)}"
