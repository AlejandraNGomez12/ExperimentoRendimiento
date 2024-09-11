# Gestión de publicaciones

El servicio de gestión de publicaciones permite crear, ver, filtrar y eliminar publicaciones realizando una autenticación de usuario previamente.

## Índice

1. [Estructura](#estructura)
2. [Requisitos](#requisitos)
3. [Ejecución](#ejecución)
4. [Uso](#uso)
5. [Pruebas](#pruebas)
6. [Otras caracteristicas](#otras-características)
7. [Autor](#autor)

## Estructura

```bash
├── app # Contiene el código principal del servicio de gestión de usuarios
│   ├── entities # Almacena las entidades del servicio
│   │   ├── __init__.py
│   │   └── post.py # Define la entidad de la publicacion utilizando SQLModel, así como entidades FastAPI Request/Response relacionadas.
│   ├── routers # Contiene las rutas del servicio
│   │   ├── __init__.py
│   │   └── post.py # Contiene los métodos expuestos por la ruta /posts
│   ├── __init__.py
│   ├── dependencies.py # Dependencias, pricipalmente instancia de base de datos
│   └── main.py # Punto de entrada de la aplicación
├── test # Código de pruebas
│   ├── __init__.py
│   └── test_main.py # Métodos de prueba de servicio de publicaciones
├── .env.template # Plantilla de las variables de entorno utilizadas
├── Dockerfile # Archivo para construcción de la imagen docker
├── README.md # Documentación del servicio de gestión de usuarios
└── requirements.txt # Lista de dependencias necesarias para producción y pruebas
```

## Requisitos

- Python 3.11
- Docker
- Postman
- Motor de base de datos SQL: PostgreSQL

## Ejecución

Se puede ejecutar por medio de docker-compose, las instrucciones las encontrará en este README.

Si desea ejecutar esto en su máquina y no por medio de docker, siga los siguientes pasos:

### Windows

1. Luego de clonar el repositorio cambie a este directorio

```powershell
cd .\post_app\
```

2. Copie el archivo `.env.template` a `env.development` y editelo según los datos de conexión de su base de datos

```powershell
cp .\.env.template .env.development
```

3. Cree el entorno virtual y activelo

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Instale las dependencias

```
pip install -r .\requirements.txt
```

5. Ejecute la aplicación (puede modificar el parámetro `--port` según su preferencia)

```bash
uvicorn app.main:app --reload --port 3000
```

## Uso

<details>
 <summary><code>POST</code> <code><b>/posts</b></code> <code>(Crear Publicación)</code></summary>

#### Descripción

Crea una publicación asociada al usuario al que pertenece el token.

#### Encabezado

`Authorization: Bearer token`

#### Cuerpo

> | Nombre      | Tipo     | Descripción                                                      |
> | ----------- | -------- | --------------------------------------------------------------   |
> | routeId     | string   | id del trayecto                                                  |
> | expireAt    | Datetime | fecha y hora máxima en que se recibirán ofertas en formato ISO   |


#### Respuestas


> | HTTP Code   | Response                                                         |
> | ----------- | --------------------------------------------------------------   |
> | 401         | El token no es válido o está vencido.                            |
> | 403         | No hay token en la solicitud	                                   |
> | 400         | El cuerpo de la petición no cuenta con un formato valido o no existe  |
> | 412         | <pre lang="json">{&#13; "msg": "La fecha expiración no es válida"&#13;}</pre> |
> | 201         | <pre lang="json">{&#13; "id": "29c08ee4-2c42-4171-9149-3bfe0620be8e",&#13; "userId": "28c08ff4-2c42-4171-9149-3bfe0620be8e" &#13; "createdAt": "2024-02-04T06:25:35.781980" &#13;}</pre>   |

</details>

<br/>


<details>
 <summary><code>GET</code> <code><b>/posts?expire={true|false}&route={routeId}&owner={id|me}</b></code> <code>(Ver y filtrar publicaciones)</code></summary>

#### Descripción

Crea una publicación asociada al usuario al que pertenece el token.

#### Parametros

> | Parametro   | Tipo     | Descripción                                                      |
> | ----------- | -------- | --------------------------------------------------------------   |
> | expire      | Boolean  | Busca las publicaciones expiradas o no expiradas                 |
> | route       | Id       | id del trayecto                                                  |
> | Owner       | Id       |  dueño de la publicación. Se reciben ids o el valor `me` que indica al usuario del token. En el caso de que ninguno esté presente se devolverá la lista de datos sin filtrar. Es decir, todas las publicaciones. |


#### Encabezado

`Authorization: Bearer token`

#### Respuestas


> | HTTP Code   | Response                                                         |
> | ----------- | --------------------------------------------------------------   |
> | 401         | El token no es válido o está vencido.                            |
> | 403         | No hay token en la solicitud	                                   |
> | 400         | El cuerpo de la petición no cuenta con un formato valido o no existe  |
> | 200         | <pre lang="json">{&#13; "id": "29c08ee4-2c42-4171-9149-3bfe0620be8e",&#13; "routeId": "28c08ff4-2c42-4171-9149-3bfe0620be8e",&#13; "userId": "28c08ff4-2c42-4171-9149-3bfe0620be8e" &#13; "expireAt": "2025-02-08T06:25:35.781980" &#13;  "createdAt": "2024-02-08T06:25:35.781980" &#13;}</pre>   |

</details>

<br/>


<details>
 <summary><code>GET</code> <code><b>/posts/{id}</b></code> <code>(Consultar una publicaciones)</code></summary>

#### Descripción

Retorna una publicación, solo un usuario autorizado puede realizar esta operación.

#### Parametros

> | Parametro   | Tipo     | Descripción                             |
> | ----------- | -------- | -------------------------------------   |
> | id          | Id       | id de la publicación a consultar        |

#### Encabezado

`Authorization: Bearer token`

#### Respuestas

> | HTTP Code   | Response                                                         |
> | ----------- | --------------------------------------------------------------   |
> | 401         | El token no es válido o está vencido.                            |
> | 403         | No hay token en la solicitud	                                   |
> | 400         | El id no cuenta con un formato valido                            |
> | 200         | <pre lang="json">{&#13; "id": "29c08ee4-2c42-4171-9149-3bfe0620be8e",&#13; "routeId": "28c08ff4-2c42-4171-9149-3bfe0620be8e",&#13; "userId": "28c08ff4-2c42-4171-9149-3bfe0620be8e" &#13; "expireAt": "2025-02-08T06:25:35.781980" &#13;  "createdAt": "2024-02-08T06:25:35.781980" &#13;}</pre>   |

</details>

<br/>


<details>
 <summary><code>DELETE</code> <code><b>/posts/{id}</b></code> <code>(Eliminar publicacion)</code></summary>

#### Descripción

Elimina una publicación, solo un usuario autorizado puede realizar esta operación.

#### Parametros

> | Parametro   | Tipo     | Descripción                             |
> | ----------- | -------- | -------------------------------------   |
> | id          | Id       | id de la publicación a consultar        |

#### Encabezado

`Authorization: Bearer token`

#### Respuestas

> | HTTP Code   | Response                                                         |
> | ----------- | --------------------------------------------------------------   |
> | 401         | El token no es válido o está vencido.                            |
> | 403         | No hay token en la solicitud	                                   |
> | 400         | El id no cuenta con un formato valido                            |
> | 200         | <pre lang="json">{&#13; "msg":"la publicación fue eliminada" }</pre>   |

</details>

<br/>


<details>
 <summary><code>GET</code> <code><b>/posts/ping</b></code> <code>(Consultar salud del servicio)</code></summary>

#### Descripción

Usado para verificar el estado del servicio.

#### Respuesta

> | HTTP Code   | Response                                                         |
> | ----------- | --------------------------------------------------------------   |
> | `200`       | `pong`   |

</details>

<br/>

<details>
 <summary><code>POST</code> <code><b>/users/reset</b></code> <code>(Restablecer base de datos)</code></summary>

#### Descripción

Usado para limpiar la base de datos del servicio.

#### Respuesta

> | HTTP Code   | Response                                                         |
> | ----------- | --------------------------------------------------------------   |
> | `200`       | <pre lang="json">{&#13; "msg": "Todos los datos fueron eliminados"&#13;} |

</details>

## Pruebas

Para ejecutar las pruebas se deben instalar unas dependencias adicionales que se encuentran en el archivo requirements-test.txt

```
pip install -r requirements-txt.txt
```

Puede establecer un porcentaje mínimo de cobertura de código y ejecutar las pruebas con las siguientes instrucciones (con y sin reporte HTML):

```
pytest --cov-fail-under=70 --cov=app
pytest --cov-fail-under=70 --cov=app --cov-report=html
```


## Autor

Alejandra Niño Gómez <ma.ninog12@uniandes.edu.co>
