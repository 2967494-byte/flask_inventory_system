# Рефакторинг Dashboard - Документация изменений

## Обзор изменений

Была проведена полная реструктуризация личного кабинета (dashboard) для создания единой архитектуры со всеми страницами под одним префиксом `/dashboard/`.

## Структура URL (ДО и ПОСЛЕ)

### До рефакторинга:
- `/dashboard` - Мои объявления
- `/favorites` - Избранное
- `/profile` - Профиль
- `/messages/<user_id>/<product_id>` - Сообщения (старый формат)

### После рефакторинга:
- `/dashboard/` или `/dashboard/products` - Мои объявления
- `/dashboard/favorites` - Избранное
- `/dashboard/profile` - Профиль
- `/dashboard/messages` - Сообщения (главная)
- `/dashboard/messages/inbox` - Входящие сообщения
- `/dashboard/messages/sent` - Отправленные сообщения
- `/dashboard/messages/archived` - Архив сообщений

## Обратная совместимость

Для обеспечения обратной совместимости добавлены редиректы:
- `/profile` → `/dashboard/profile` (301)
- `/favorites` → `/dashboard/favorites` (301)
- `/messages/<user_id>/<product_id>` → `/dashboard/messages/inbox` (с уведомлением)

## Новые компоненты

### 1. `templates/dashboard_base.html`
Базовый шаблон для всех страниц dashboard, содержит:
- Общую структуру layout (sidebar + content)
- Базовые стили для всех страниц dashboard
- Блоки для расширения:
  - `{% block dashboard_content %}` - основной контент
  - `{% block dashboard_styles %}` - дополнительные стили
  - `{% block dashboard_scripts %}` - дополнительные скрипты

### 2. `templates/partials/dashboard_sidebar.html`
Унифицированный компонент бокового меню:
- Использует переменную `active_section` для подсветки активного раздела
- Автоматически обновляет счетчик непрочитанных сообщений
- Единый стиль для всех страниц

## Обновленные шаблоны

### `templates/favorites.html`
- Полностью переписан с использованием `dashboard_base.html`
- Упрощена структура (убраны дубликаты кода sidebar)
- Улучшена анимация удаления карточек
- Добавлена обработка ошибок

### `templates/profile.html`
- Полностью переписан с использованием `dashboard_base.html`
- Добавлены новые поля:
  - Юридический адрес
  - Должность
  - Отрасль
  - О компании
  - Корреспондентский счет
- Улучшена валидация пароля на клиенте
- Адаптивный дизайн для мобильных устройств

### `templates/messages.html` (НОВЫЙ)
- Полностью новая страница сообщений
- Табы для переключения между разделами (Входящие/Отправленные/Архив)
- Заготовка для будущей реализации функционала
- Автоматическое обновление счетчика непрочитанных сообщений

## Изменения в роутах (`app/blueprints/main.py`)

### Обновлены:
```python
@main.route("/dashboard/profile", methods=["GET", "POST"])
def profile():
    """User profile settings page"""

@main.route("/dashboard/favorites")
def favorites():
    """User's favorite products page"""

@main.route("/dashboard/messages")
@main.route("/dashboard/messages/<subsection>")
def messages(subsection="inbox"):
    """Messages page with inbox/sent subsections"""
```

### Добавлены (редиректы):
```python
@main.route("/profile")
def old_profile_redirect():
    """Redirect old profile URL to new dashboard/profile"""

@main.route("/favorites")
def old_favorites_redirect():
    """Redirect old favorites URL to new dashboard/favorites"""

@main.route("/messages/<int:user_id>/<int:product_id>")
def old_messages_redirect(user_id, product_id):
    """Redirect old message links to new messages page"""
```

## Стилизация

### Единые классы для всех страниц dashboard:
- `.db-container` - контейнер dashboard
- `.db-layout` - grid layout для sidebar + content
- `.db-sidebar` - боковое меню
- `.db-main` - основной контент
- `.db-header` - заголовок страницы
- `.db-title` - заголовок H1
- `.db-subtitle` - подзаголовок
- `.db-products-grid` - сетка товаров
- `.db-product-card` - карточка товара
- `.db-empty-state` - пустое состояние
- `.fav-btn` - кнопка избранного

### Адаптивность:
- Desktop: sidebar слева (280px), контент справа
- Mobile (< 900px): sidebar скрыт, контент на всю ширину

## Преимущества новой архитектуры

1. **Единообразие**: Все страницы личного кабинета имеют одинаковую структуру
2. **DRY принцип**: Нет дублирования кода sidebar
3. **Легкость поддержки**: Изменения в sidebar автоматически применяются ко всем страницам
4. **Расширяемость**: Легко добавить новые страницы в dashboard
5. **SEO-дружественность**: Логичная структура URL
6. **Обратная совместимость**: Старые ссылки работают через редиректы

## Как добавить новую страницу в dashboard

1. Создать новый шаблон, наследующийся от `dashboard_base.html`:
```html
{% extends "dashboard_base.html" %}
{% set active_section = 'my_section' %}
{% block title %}Моя страница - ASAUDA{% endblock %}

{% block dashboard_content %}
    <div class="db-header">
        <div class="db-title-box">
            <h1 class="db-title">Моя страница</h1>
            <p class="db-subtitle">Описание страницы</p>
        </div>
    </div>
    
    <!-- Ваш контент здесь -->
{% endblock %}
```

2. Добавить роут в `app/blueprints/main.py`:
```python
@main.route("/dashboard/my-section")
@login_required
def my_section():
    return render_template("my_section.html")
```

3. Добавить ссылку в `templates/partials/dashboard_sidebar.html`:
```html
<li style="margin-bottom: 0.5rem">
    <a href="{{ url_for('main.my_section') }}"
       class="nav-link {% if active_section == 'my_section' %}active{% endif %}">
        <i class="fas fa-icon"></i>
        Моя секция
    </a>
</li>
```

## Дальнейшие шаги

- [ ] Реализовать полноценный функционал сообщений
- [ ] Добавить API для работы с сообщениями
- [ ] Реализовать реальное время обновления счетчика сообщений
- [ ] Добавить уведомления в реальном времени
- [ ] Создать страницу настроек уведомлений
- [ ] Оптимизировать загрузку изображений в карточках товаров

## Известные проблемы

- Страница сообщений содержит только заготовку (пустые состояния)
- Функционал отправки сообщений в разработке
- Мобильный sidebar полностью скрыт (нужно добавить hamburger menu)

## Тестирование

Необходимо протестировать:
1. ✓ Редиректы со старых URL работают
2. ✓ Все страницы используют единый sidebar
3. ✓ Active состояние корректно подсвечивается
4. ✓ Стили применяются единообразно
5. ⏳ Избранное: добавление/удаление товаров
6. ⏳ Профиль: сохранение изменений
7. ⏳ Адаптивность на мобильных устройствах

---

**Дата рефакторинга**: 2024
**Версия**: 2.0
**Статус**: ✅ Завершено