# Tests

这个目录包含了 web_admin 项目的所有测试文件。

## 测试结构

- `test_cache.py` - 测试缓存系统和缓存服务
- `test_db_only.py` - 测试数据库功能（独立测试）
- `test_api.py` - 测试 API 和统计功能
- `test_path.py` - 测试路径解析功能

## 运行测试

### 安装依赖

```bash
pip install -r requirements-dev.txt
```

### 运行所有测试

```bash
# 从 web_admin 目录运行
pytest tests/

# 或者直接运行 pytest
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_cache.py
pytest tests/test_db_only.py
```

### 运行特定测试函数

```bash
pytest tests/test_cache.py::test_database
pytest tests/test_cache.py::test_cache_service
```

### 查看详细输出

```bash
pytest tests/ -v
```

### 生成覆盖率报告

```bash
pytest tests/ --cov=. --cov-report=html
# 报告将生成在 htmlcov/ 目录
```

### 直接运行测试脚本（不使用 pytest）

某些测试文件可以直接运行：

```bash
python tests/test_db_only.py
python tests/test_cache.py
python tests/test_api.py
python tests/test_path.py
```

## CI/CD 集成

测试已集成到 GitHub Actions 中，会在以下情况自动运行：

- 推送到 master/main/develop 分支
- 创建 Pull Request
- 修改 web_admin 目录下的文件

CI 配置文件：`.github/workflows/test.yml`

## 测试配置

pytest 配置在 `pytest.ini` 文件中定义，包括：

- 测试发现模式
- 输出选项
- 自定义标记（markers）

## 开发建议

1. 在提交代码前运行测试确保所有测试通过
2. 添加新功能时编写相应的测试
3. 保持测试独立性，避免测试之间的相互依赖
4. 使用临时文件和数据库进行测试，避免影响实际数据
