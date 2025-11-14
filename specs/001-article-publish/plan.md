# Implementation Plan: Article Publishing

**Branch**: `001-article-publish` | **Date**: 2025-11-14 | **Spec**: ./spec.md
**Input**: Feature specification from `/specs/001-article-publish/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This implementation plan addresses the core requirement from the feature specification: **adding publish button functionality to the article editor interface** that changes draft status from `draft: true` to `draft: false`.

**Technical Approach**: Extend the existing Flask application's PostService with publishing methods using the python-frontmatter library for safe YAML manipulation, implement cross-platform file locking for concurrent access protection, and add UI components using existing HTMX/Alpine.js patterns for seamless user experience.

The solution leverages Hugo's built-in draft handling mechanism while providing robust error handling, comprehensive testing, and integration with the existing cache system for optimal performance.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+
**Primary Dependencies**: Flask==3.0.0, flask-socketio==5.3.5, PyYAML==6.0.1, python-frontmatter==1.1.0
**Storage**: File-based (Hugo markdown files with YAML frontmatter)
**Testing**: pytest (existing test structure in tests/)
**Target Platform**: Linux server (web application)
**Project Type**: Single web application (Flask-based)
**Performance Goals**: <3 seconds for publish operation, <2 seconds for UI feedback
**Constraints**: Must preserve existing file structure, work with Hugo static site generator
**Scale/Scope**: Single admin interface, managing blog articles (typically <1000 articles)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Post-Design Evaluation**: ✅ PASSED

### Gates Evaluated:

**✅ Simplicity**: Feature follows existing patterns and extends current architecture without introducing unnecessary complexity. Uses file-based workflow that matches Hugo's design philosophy.

**✅ Test-First Ready**: Comprehensive testing strategy defined with unit, integration, and E2E test coverage. All testable requirements identified in quickstart.md.

**✅ Observability**: Clear operation tracking with operation IDs, status feedback, and error logging. Users receive immediate feedback on publish operations.

**✅ Single Responsibility**: Each component has clear purpose - PostService handles business logic, API endpoints handle HTTP concerns, UI components handle user interaction.

**✅ Integration Focus**: Focuses on external system integration (Hugo) without reinventing existing Hugo capabilities.

### Complexity Tracking: No violations identified

The implementation stays within reasonable complexity bounds:
- Uses existing libraries and patterns
- No additional infrastructure required
- Follows established Flask application patterns
- Maintains file-based simplicity of Hugo workflow

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Hugo Admin - Single Flask Application
app.py                     # Main Flask application
config.py                  # Configuration management
services/                  # Business logic layer
├── post_service.py       # Article management service
├── cache_service.py      # Caching service
├── hugo_service.py       # Hugo integration service
└── __init__.py
models/                    # Data models and database
├── database.py           # Database models and setup
└── __init__.py
utils/                     # Utility functions
├── blog_parser.py        # Markdown/frontmatter parsing
└── __init__.py
static/                    # Static assets
├── css/                  # Stylesheets
└── js/                   # JavaScript files
templates/                 # Jinja2 templates
├── base.html             # Base template
├── editor.html           # Article editor interface
├── posts.html            # Article list view
├── index.html            # Main dashboard
└── server.html           # Server status template
tests/                     # Test suite
├── test_api.py           # API endpoint tests
├── test_cache.py         # Cache service tests
├── test_db_only.py       # Database tests
└── test_path.py          # Path handling tests
```

**Structure Decision**: Single Flask application with service layer architecture, following existing codebase patterns. The article publishing feature will extend the `services/post_service.py` and add new UI components to `templates/editor.html` and `templates/posts.html`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
