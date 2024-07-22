# django_keycloak_auth

## Описание

В данном репозитории приведен пример интеграции **Open Source** приложения [**Keycloak**](https://www.keycloak.org/) с **Django**
### Для работы необходимо:
* Ваше работающее приложение **Keycloak**
* 
  ```
  django
  djangorestframework
  python-keycloak
  pyjwt = {extras = ["crypto"]}
  ```

# Процесс взаимодействия

### 1. Для начала нужно поднять само приложение **Keycloak**, пример развертывания **Keycloak** в продуктовой среде можно посмотреть [**ТУТ**](https://github.com/vlad-terehoff/keycloak_docker)
   
 1.1 Создать Realm
 
 1.2 Создать клиента (это приложение которое будет обращаться в Keycloak для аунтификации пользователей)

 1.3 Завести самих пользователей которые будут получать доступ уже в ваше приложение

### 2. Процесс взаимодействия с api на стороне вашего приложения Django
[**В данном разделе**](https://github.com/vlad-terehoff/django_keycloak_auth/blob/main/base/auth_keycloak/views.py) реализованны основные функции отвечающие за взаиможействие с вашим приложением **Keycloak**, выпуск ***access***  и ***refresh*** токенов, обновление ***access*** токена и выход из системы(logout).

Прежде чем начать работу, нужно сформировать файл *.env* и заполнить его своими данными в том числе из вашего приложения **Keycloak**

Пример заполнения файла *.env* приведен [**здесь**](https://github.com/vlad-terehoff/django_keycloak_auth/blob/main/base/example.env)

#### Теперь подробнее о каждой из функции:
Функция 
```python
def keycloak_login(request):
    return redirect(settings.CODE_URL)
```

Это начальная функция которая автоматически перенаправляет на ваш **Keycloak** для аунтификации пользователей, которые заведены в вашем приложение **Keycloak**.
После успешного прохождения аунтификации на стороне **Keycloak** вашего пользователя, **Keycloak** автоматически перенаправляется на api за которую отвечает функция:

```python
def callback(request):
    code = request.GET["code"]
    token_access_key, token_refresh_key = get_tokens_from_code(code)
    user = get_user_or_create(token=token_access_key)
    access = create_access_token(user)
    refresh_token = create_refresh_token(user)
    resp = Response()
    resp.data = {ACCESS_TOKEN_TYPE: access,
                 "token_type": "Bearer"}
    resp.set_cookie(key=REFRESH_TOKEN_TYPE, value=refresh_token, httponly=True)
    resp.set_cookie(key=KEY_TOKEN, value=token_refresh_key, httponly=True)
    return resp
```

Полный путь к данной функции находится по адресу https://your_keycloak.com/api/keycloak/callback/

И имеено данный путь нужно указать в самом **Keycloak** в поле ***Valid redirect URIs*** раздела ***Settings*** вашего Клиента

**Keycloak** Переадресуется по данному пути неся в запросе параметр под названием *code*. Данный код пакет ***python-keycloak*** сам под капотом обменяет на ***access***  и ***refresh*** токены от самого **Keycloak**

Так-как в данном примере реализована еще своя система выпуска и обновления JWT токенов на стороне самого приложения **Django** то ***access*** от приложения **Keycloak** мы используем только для получения или внесения (Если пользователь зашел впервые) пользователя в базу данных на стороне самого приложения **Django**.

Но вы можете не генерировать свои JWT токены а пользоваться ***access***  и ***refresh*** токенами от самого **Keycloak** и обновлять ***access*** через этот [***способ***](https://python-keycloak.readthedocs.io/en/latest/modules/openid_client.html#refresh-token) пакета ***python-keycloak***


Полученный от **Keycloak** ***refresh*** токен необходим для выхода из приложения **Keycloak**
```python
  def keycloak_logout(request):
    resp = Response()
    token_key = request.COOKIES.get(KEY_TOKEN)
    if request.COOKIES.get(REFRESH_TOKEN_TYPE):
        resp.delete_cookie(REFRESH_TOKEN_TYPE)

    if token_key:
        keycloak_openid.logout(token_key)
        resp.delete_cookie(KEY_TOKEN)

    return resp
```

Обновление ***access*** токена выпущенного уже на стороне самого приложения **Django** происходит через функцию
```python
  def refresh_token(request):

    refresh_token = request.COOKIES.get(REFRESH_TOKEN_TYPE)
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    payload = extract_payload_from_token(refresh_token)

    user = User.objects.filter(id=payload.get('sub')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    access_token = refresh_access_token(user)
    return Response({ACCESS_TOKEN_TYPE: access_token})
```

## Заключение

Сама проверка наличия ***access*** токена в *Headers* и его валидация происходит в [***данном***](https://github.com/vlad-terehoff/django_keycloak_auth/blob/main/base/auth_keycloak/authentication.py) классе.

Данный класс подключен в настройках приложения **Django**
```python
  REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "auth_keycloak.authentication.KeycloakAuthentication",
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
```
И выведен вперед как основной способ аунтификации.

Так же, хочется добавить, что пользователи добавленные из **Keycloak** на этапе проверки наличия пользователя в системе
```python
  def callback(request):
    code = request.GET["code"]
    token_access_key, token_refresh_key = get_tokens_from_code(code)
    user = get_user_or_create(token=token_access_key)
    access = create_access_token(user)
    refresh_token = create_refresh_token(user)
    resp = Response()
    resp.data = {ACCESS_TOKEN_TYPE: access,
                 "token_type": "Bearer"}
    resp.set_cookie(key=REFRESH_TOKEN_TYPE, value=refresh_token, httponly=True)
    resp.set_cookie(key=KEY_TOKEN, value=token_refresh_key, httponly=True)
    return resp

  def get_user_or_create(token):
    payload = get_payload(token)
    user, created = User.objects.get_or_create(username=payload.get("preferred_username"),
                                               last_name=payload.get('family_name'),
                                               first_name=payload.get('given_name'),
                                               )
    return user
```

Не будут иметь своего пароля на стороне приложения **Django**, следовательно попасть в админ панель приложения **Django** они не смогут.
