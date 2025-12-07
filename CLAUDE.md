# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Pokemon Card Management Web Application built with Django 5.0, PostgreSQL 16, and containerized using Docker. The frontend uses Tailwind CSS with DaisyUI for styling and HTMX for dynamic interactions without full page reloads.

**Tech Stack:**
- Python 3.11 with Poetry for dependency management
- Django 5.0 framework
- PostgreSQL 16 database
- Tailwind CSS + DaisyUI for styling
- HTMX for partial page updates
- Docker & Docker Compose for containerization

## Development Commands

### Docker Operations

```bash
# Initial build and start
docker-compose up --build -d

# Start services (after initial build)
docker-compose up -d

# Stop services
docker-compose down

# Access web container shell
docker-compose exec web bash
```

### Django Management Commands

All Django commands should be run inside the web container:

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run development server (already running in docker-compose)
docker-compose exec web python manage.py runserver 0.0.0.0:8000

# Django shell
docker-compose exec web python manage.py shell
```

### Python Dependency Management

```bash
# Add new Python package
docker-compose exec web poetry add <package-name>

# Add dev dependency
docker-compose exec web poetry add --group dev <package-name>

# Update dependencies
docker-compose exec web poetry update
```

After modifying dependencies, commit both `pyproject.toml` and `poetry.lock`.

### Frontend CSS Build

```bash
# Build CSS once
npm run build

# Watch for changes (auto-rebuild)
npm run watch
```

Note: `npm run watch` is automatically started in docker-compose.yml alongside the Django server.

## Architecture Overview

### Application Structure

This is a single Django app architecture:
- **config/**: Django project settings and root URL configuration
- **cards/**: Main Django app containing all Pokemon card management logic
- **templates/**: Global templates with base.html
- **static/**: Static files (compiled CSS output)
- **media/**: User-uploaded card images
- **docs/**: Project documentation

### Core Models (cards/models.py)

The data model consists of a central `PokemonCard` model with related lookup tables:

- **PokemonCard**: Main model storing card information (name, quantity, image, memo, evolves_from)
  - ForeignKey to `EvolutionStage` (たね, 1進化, 2進化, etc.)
  - ManyToMany to `Type` (炎, 水, 草, etc.)
  - ManyToMany to `SpecialFeature` (ex, V, VSTAR, etc.)
  - ManyToMany to `MoveType` (わざのエネルギータイプ)

All lookup models (`Type`, `EvolutionStage`, `SpecialFeature`, `MoveType`) have:
- `name`: The display name
- `display_order`: For controlling sort order in UI

### HTMX-Driven Architecture

This application uses HTMX extensively for dynamic updates without full page reloads:

**Key Patterns:**
- Views check `request.htmx` to return partial templates for AJAX requests
- Partial templates are prefixed with `_` (e.g., `_card_item.html`, `_card_form.html`)
- `HX-Trigger` response headers signal frontend actions (e.g., `closeModal`)
- CRUD operations return updated HTML fragments that replace targeted DOM elements

**Important Views:**
- `CardListView`: Returns full page or `_card_list_content.html` based on htmx
- `card_create/card_edit`: Return `_card_form.html` for modal forms, `_card_item.html` on success
- `increase_card_quantity/decrease_card_quantity`: Return updated `_card_item.html`
- `card_delete`: Returns confirmation modal on GET, empty response with HX-Trigger on DELETE
- `card_name_suggestions`: Provides autocomplete suggestions for "evolves_from" field

### Filtering System (cards/filters.py)

Uses django-filter's `PokemonCardFilter` for search and filtering:
- Text search on card name (icontains)
- Multi-select filters for types, evolution_stage, special_features, move_types
- OrderingFilter for sorting by name, quantity, evolution order, or creation date
- Filter state is preserved in URL query parameters
- Checkbox widgets for multi-select fields

### Query Optimization

All views use `select_related()` and `prefetch_related()` to avoid N+1 queries:

```python
queryset = PokemonCard.objects.select_related(
    'evolution_stage'
).prefetch_related(
    'types', 'special_features', 'move_types'
)
```

Always maintain this pattern when querying PokemonCard objects.

### URL Structure (cards/urls.py)

- `/`: Card list with search/filter
- `/new/`: Create new card (HTMX modal)
- `/<pk>/edit/`: Edit card (HTMX modal)
- `/<pk>/increase/`: Increment quantity
- `/<pk>/decrease/`: Decrement quantity
- `/<pk>/delete/`: Delete card with confirmation
- `/suggestions/`: Autocomplete endpoint for card names

### Configuration Notes

- Settings use environment variables from `.env` file
- Database credentials, SECRET_KEY, DEBUG, ALLOWED_HOSTS all from environment
- Language: Japanese (`LANGUAGE_CODE = 'ja'`)
- Timezone: Asia/Tokyo
- Media files served in DEBUG mode via `static()` helper
- HTMX middleware is enabled in MIDDLEWARE

### Tailwind CSS Configuration

- Input: `static/css/src/input.css`
- Output: `static/css/dist/styles.css`
- DaisyUI plugin enabled for component library
- Scans templates and Python files (forms.py, filters.py) for class names
- Must run `npm run build` or `npm run watch` after modifying CSS classes

## Development Guidelines

### When Adding New Features

1. Update models in `cards/models.py` if needed
2. Create and run migrations: `docker-compose exec web python manage.py makemigrations && docker-compose exec web python manage.py migrate`
3. Add views to `cards/views.py` following HTMX pattern (check `request.htmx`, return partials)
4. Add URL patterns to `cards/urls.py`
5. Create templates (full page + `_partial.html` for HTMX)
6. Update filters in `cards/filters.py` if adding searchable fields
7. Update admin in `cards/admin.py` if new models are added

### When Modifying the Data Model

- Always use `select_related()` for ForeignKey fields
- Always use `prefetch_related()` for ManyToMany fields
- Maintain `display_order` field on lookup models for UI sorting
- Set appropriate `on_delete` behavior (PROTECT for critical lookups)

### Working with Templates

- Base template: `templates/base.html`
- Card-specific templates: `templates/cards/`
- Partial templates (for HTMX): Start with `_` prefix
- Use DaisyUI components for consistent styling
- Include `{% load widget_tweaks %}` when using form customization

### Testing Locally

Access the application at `http://localhost:8000` after running `docker-compose up`.

Admin interface available at `http://localhost:8000/admin/` (requires superuser).
