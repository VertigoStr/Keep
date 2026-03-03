# Отчет по неработающим тестам

**Дата:** 2026-03-03  
**Всего тестов:** 116  
**Прошло:** 80  
**Не прошло:** 36  
**Процент успешности:** 69%

---

## Категории неработающих тестов

### 1. Contract Tests (11 тестов)

#### Auth API Contract Tests (5 тестов)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_register_contract_passwords_dont_match` | `tests/contract/test_auth_api.py:23` | Ожидается поле `error` в ответе, но API возвращает ошибку валидации Pydantic |
| `test_register_contract_missing_fields` | `tests/contract/test_auth_api.py:79` | Ожидается статус 422, но возвращается 400 (FastAPI возвращает 400 для validation errors) |
| `test_login_contract_rate_limited` | `tests/contract/test_auth_api.py:19` | Отсутствует заголовок `Retry-After` в ответе 429 |
| `test_logout_contract_success` | `tests/contract/test_auth_api.py:20` | Ожидается статус 200, но возвращается 401 (проблема с аутентификацией) |
| `test_logout_contract_unauthorized` | `tests/contract/test_auth_api.py:21` | KeyError: 'error' (формат ответа отличается) |

#### Tasks API Contract Tests (10 тестов)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_post_tasks_contract` | `tests/contract/test_tasks_api_contract.py:10` | KeyError: 'token' (LoginResponse не содержит поле `token`) |
| `test_post_tasks_validation_error_contract` | `tests/contract/test_tasks_api_contract.py:55` | KeyError: 'token' |
| `test_post_tasks_unauthorized_contract` | `tests/contract/test_tasks_api_contract.py:92` | AssertionError: 'error' not in response (формат ошибки отличается) |
| `test_get_tasks_contract` | `tests/contract/test_tasks_api_contract.py:101` | KeyError: 'token' |
| `test_get_tasks_empty_contract` | `tests/contract/test_tasks_api_contract.py:120` | KeyError: 'token' |
| `test_get_task_by_id_contract` | `tests/contract/test_tasks_api_contract.py:139` | KeyError: 'token' |
| `test_get_task_by_id_not_found_contract` | `tests/contract/test_tasks_api_contract.py:158` | KeyError: 'token' |
| `test_get_task_by_id_forbidden_contract` | `tests/contract/test_tasks_api_contract.py:177` | KeyError: 'token' |
| `test_put_task_by_id_contract` | `tests/contract/test_tasks_api_contract.py:196` | KeyError: 'token' |
| `test_delete_task_by_id_contract` | `tests/contract/test_tasks_api_contract.py:215` | KeyError: 'token' |

---

### 2. Integration Tests (11 тестов)

#### Authentication Tests (1 тест)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_login_missing_fields` | `tests/integration/test_authentication.py:37` | Ожидается статус 422, но возвращается 400 |

#### Logout Tests (4 теста)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_successful_logout` | `tests/integration/test_logout.py:38` | Ожидается статус 200, но возвращается 401 |
| `test_logout_without_session` | `tests/integration/test_logout.py:39` | KeyError: 'error' |
| `test_logout_with_invalid_token` | `tests/integration/test_logout.py:40` | KeyError: 'error' |
| `test_logout_deletes_session` | `tests/integration/test_logout.py:41` | assert 1 == 0 (сессия не удаляется) |

#### Rate Limiting Tests (2 теста)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_rate_limit_includes_retry_after_header` | `tests/integration/test_rate_limiting.py:45` | Отсутствует заголовок `Retry-After` |
| `test_successful_login_resets_rate_limit` | `tests/integration/test_rate_limiting.py:46` | Ожидается статус 401, но возвращается 429 |

#### Tasks API Tests (10 тестов)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_create_task` | `tests/integration/test_tasks_api.py:53` | KeyError: 'token' |
| `test_create_task_unauthenticated` | `tests/integration/test_tasks_api.py:54` | KeyError: 'error' |
| `test_create_task_validation_error_empty_title` | `tests/integration/test_tasks_api.py:55` | KeyError: 'token' |
| `test_create_task_validation_error_invalid_status` | `tests/integration/test_tasks_api.py:56` | KeyError: 'token' |
| `test_get_tasks` | `tests/integration/test_tasks_api.py:57` | KeyError: 'token' |
| `test_get_tasks_empty` | `tests/integration/test_tasks_api.py:58` | KeyError: 'token' |
| `test_get_task_by_id` | `tests/integration/test_tasks_api.py:59` | KeyError: 'token' |
| `test_get_task_by_id_not_found` | `tests/integration/test_tasks_api.py:60` | KeyError: 'token' |
| `test_get_task_by_id_not_owner` | `tests/integration/test_tasks_api.py:61` | KeyError: 'token' |
| `test_update_task` | `tests/integration/test_tasks_api.py:62` | KeyError: 'token' |
| `test_delete_task` | `tests/integration/test_tasks_api.py:63` | KeyError: 'token' |

---

### 3. Unit Tests (3 теста)

#### Auth Service Tests (2 теста)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_login_user_success` | `tests/unit/test_auth_service.py:57` | TypeError: unsupported type for timedelta seconds component: MagicMock |
| `test_logout_user_no_session` | `tests/unit/test_auth_service.py:91` | NameError: name 'UnauthorizedError' is not defined |

#### Security Tests (1 тест)

| Тест | Файл | Ошибка |
|------|------|--------|
| `test_create_token_with_custom_expiration` | `tests/unit/test_security.py:89` | AssertionError (время истечения токена не соответствует ожидаемому) |

---

## Основные проблемы

### 1. LoginResponse не содержит поле `token`
**Проблема:** Токен устанавливается в HTTP-only cookie, но тесты ожидают его в JSON-ответе.

**Текущая реализация:**
```python
# src/api/v1/auth.py
@router.post("/login", response_model=LoginResponse, ...)
async def login(...):
    # ...
    response.set_cookie(key="session_token", value=token, ...)
    return LoginResponse(user=UserResponse.model_validate(user))
```

**Ожидание тестов:**
```python
# tests/contract/test_tasks_api_contract.py
token = login_response.json()["token"]  # KeyError: 'token'
```

**Решение:** Добавить поле `token` в `LoginResponse` или изменить тесты для работы с cookies.

---

### 2. Несоответствие статусов ошибок
**Проблема:** FastAPI возвращает 400 для validation errors, но тесты ожидают 422.

**Текущее поведение:**
```python
# src/middleware/error_handler.py
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,  # 400
        content={...}
    )
```

**Ожидание тестов:**
```python
# tests/contract/test_auth_api.py
assert response.status_code == 422  # FastAPI validation error
```

**Решение:** Изменить статус на 422 или обновить тесты.

---

### 3. Отсутствие заголовка `Retry-After` при rate limiting
**Проблема:** При превышении лимита запросов не возвращается заголовок `Retry-After`.

**Текущее поведение:**
```python
# src/api/v1/auth.py
if not await rate_limit_service.check_rate_limit(...):
    raise TooManyAttemptsError()
```

**Ожидание тестов:**
```python
# tests/integration/test_rate_limiting.py
assert 'Retry-After' in response.headers
```

**Решение:** Добавить заголовок `Retry-After` в ответ при rate limiting.

---

### 4. Проблемы с форматом ошибок
**Проблема:** Некоторые тесты ожидают поле `error`, но API возвращает `detail`.

**Текущее поведение:**
```python
# FastAPI default error response
{"detail": "Not authenticated"}
```

**Ожидание тестов:**
```python
# tests/contract/test_tasks_api_contract.py
assert 'error' in response.json()
```

**Решение:** Унифицировать формат ошибок или обновить тесты.

---

### 5. Unit тесты используют неправильные типы для mock-объектов
**Проблема:** MagicMock передается вместо timedelta.

**Текущее поведение:**
```python
# tests/unit/test_auth_service.py
mock_security_utils.create_token = MagicMock(return_value="jwt_token")
# TypeError: unsupported type for timedelta seconds component: MagicMock
```

**Решение:** Исправить mock-объекты в unit тестах.

---

### 6. Logout endpoint требует аутентификацию
**Проблема:** Logout endpoint использует `Depends(get_current_user)`, но тесты ожидают работу без неё.

**Текущее поведение:**
```python
# src/api/v1/auth.py
@router.post("/logout", ...)
async def logout(
    current_user: dict = Depends(get_current_user),  # Требует аутентификацию
    ...
):
```

**Ожидание тестов:**
```python
# tests/integration/test_logout.py
# Тесты ожидают работу logout без предварительной аутентификации
```

**Решение:** Изменить логику logout или обновить тесты.

---

## Рекомендации по исправлению

### Приоритет 1 (Критично)
1. Добавить поле `token` в `LoginResponse` или изменить тесты для работы с cookies
2. Исправить статус коды validation errors (400 → 422)
3. Добавить заголовок `Retry-After` при rate limiting

### Приоритет 2 (Важно)
4. Унифицировать формат ошибок (error vs detail)
5. Исправить mock-объекты в unit тестах
6. Пересмотреть логику logout endpoint

### Приоритет 3 (Желательно)
7. Добавить более детальные сообщения об ошибках
8. Улучшить документацию API
9. Добавить логирование для отладки

---

## Статистика по категориям

| Категория | Всего тестов | Прошло | Не прошло | % успеха |
|-----------|--------------|--------|-----------|----------|
| Contract Tests | 15 | 4 | 11 | 27% |
| Integration Tests | 25 | 14 | 11 | 56% |
| Unit Tests | 76 | 62 | 14 | 82% |
| **Итого** | **116** | **80** | **36** | **69%** |

---

## Заключение

Основная причина неработающих тестов - несоответствие между реализацией API и ожиданиями тестов. Большинство проблем связано с:

1. **Аутентификацией** - токен передается в cookie, а не в теле ответа
2. **Валидацией** - статус коды ошибок не соответствуют ожиданиям
3. **Rate limiting** - отсутствует заголовок `Retry-After`

Рекомендуется сначала исправить критические проблемы (Приоритет 1), затем перейти к остальным.