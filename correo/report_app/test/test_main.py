from uuid import uuid4
import pytest
from faker import Faker
from fastapi import status, HTTPException, Header

from typing import Annotated

from fastapi.testclient import TestClient
from sqlmodel import create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime,timedelta

from app.dependencies import Database, create_db_and_tables,validate_user  

from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    async def validate_user_override(
        authorization: Annotated[str | None, Header()] = None
    ):
        if authorization is None:
            raise HTTPException(status_code=403, detail="No hay token en la solicitud")
        elif authorization == "authorization":
            return {
                "id": "541a12c5-9388-4f48-93f3-dd56d553c4c3",
                "username": "felicita",
                "email": "josefina37@hotmail.com",
                "fullName": "dr. doug smith",
                "dni": "849",
                "phoneNumber": "7063069022",
                "status": "NO_VERIFICADO",
            }
        else:
            raise HTTPException(
                status_code=401, detail="El token no es válido o está vencido."
            )

    app.dependency_overrides[validate_user] = validate_user_override
    Database._engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    create_db_and_tables()
    client = TestClient(app)
    yield client
   

@pytest.fixture
def fake():
    return Faker()

def test_create_post(client: TestClient, fake: Faker):
    post_data = {
        "routeId":  fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat()
    }
    
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert data["id"] is not None
    assert data["createdAt"] is not None

def test_create_post_expirate(client: TestClient, fake: Faker):

    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()- timedelta(days=2)).isoformat(),
    }
    response =  client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    
    assert response.status_code == 412

def test_token_invalid(client: TestClient, fake: Faker):
    post_data = {
        "routeId":  fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat()
    }

    response =  client.post("/posts", json=post_data, headers={"Authorization": "valid"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_post_sin_datos(client: TestClient, fake: Faker):
    post_data = {
        "routeId": None,
        "expireAt": None,
    }
    
    response =  client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    
    assert response.status_code == 400

def test_get_All_post(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=10)).isoformat()
    }

    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    response_get = client.get("/posts", headers={"Authorization": "authorization"})
    
    data = response_get.json()
    first_post = data[0]

    assert response_get.status_code == status.HTTP_200_OK
    assert len(data) > 0  

    assert first_post["routeId"] is not None
    assert first_post["userId"] is not None
    assert first_post["expireAt"] is not None
    assert first_post["createdAt"] is not None
    
def test_get_None_post_with_filter(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat()
    }
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    assert response.status_code == status.HTTP_201_CREATED  # Verificar que la creación del post fue exitosa

    response_get = client.get(f"/posts?expire=true&route={post_data['routeId']}", headers={"Authorization": "authorization"})

    assert response_get.status_code == status.HTTP_200_OK  

    data = response_get.json()
    assert len(data) == 0
    
def test_get_post_with_filter(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat()
    }
    
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    assert response.status_code == status.HTTP_201_CREATED  # Verificar que la creación del post fue exitosa
    dataCreate = response.json()

    response_get = client.get(f"/posts?expire=false&route={post_data['routeId']}", headers={"Authorization": "authorization"})

    assert response_get.status_code == status.HTTP_200_OK  

    data = response_get.json()
    first_post = data[0]

    assert len(data) > 0
    assert first_post["routeId"] is not None
    assert first_post["userId"] is not None
    assert first_post["expireAt"] is not None
    assert first_post["userId"] == dataCreate["userId"]

def test_get_error_post_with_filter(client: TestClient, fake: Faker):
   
    response_get = client.get(f"/posts?expire={'routeId'}", headers={"Authorization": "authorization"})

    assert response_get.status_code == status.HTTP_400_BAD_REQUEST  

def test_get_one_post_by_id(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat()
    }
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    assert response.status_code == status.HTTP_201_CREATED 

    response_get_all = client.get(f"/posts?route={post_data['routeId']}", headers={"Authorization": "authorization"})
    data = response_get_all.json()
    first_post = data[0]
    
    idPost = first_post["id"]
    response_get_one = client.get(f"/posts/{idPost}", headers={"Authorization": "authorization"})
    
    dataPost = response_get_one.json()

    assert response_get_one.status_code == status.HTTP_200_OK  
    assert dataPost["id"] is not None
    assert dataPost["createdAt"] is not None
    
def test_get_one_post_by_id_error(client: TestClient, fake: Faker):
    
    response_get_one = client.get(f"/posts/{True}", headers={"Authorization": "authorization"})
    
    assert response_get_one.status_code == status.HTTP_400_BAD_REQUEST  
    
def test_get_one_post_by_id_not_found(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat()
    }
    
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    assert response.status_code == status.HTTP_201_CREATED 
    response_get_one = client.get(f"/posts/{fake.uuid4()}", headers={"Authorization": "authorization"})
    
    assert response_get_one.status_code == status.HTTP_404_NOT_FOUND  
    
def test_delete_post_by_id(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat(),
    }
    
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    assert response.status_code == status.HTTP_201_CREATED 
    dataCreate = response.json()
    response_get_all = client.get(f"/posts?route={post_data['routeId']}", headers={"Authorization": "authorization"})
    data = response_get_all.json()
    first_post = data[0]
    idPost = first_post["id"]
    response_get_one = client.delete(f"/posts/{idPost}", headers={"Authorization": "authorization"})

    assert response_get_one.status_code == status.HTTP_200_OK  

def test_delete_post_by_id_not_found(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat(),
    }
    
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    assert response.status_code == status.HTTP_201_CREATED 
    response_get_one = client.delete(f"/posts/{fake.uuid4()}", headers={"Authorization": "authorization"})
    
    assert response_get_one.status_code == status.HTTP_404_NOT_FOUND  

def test_delete_post_by_id_invalid(client: TestClient, fake: Faker):
    post_data = {
        "routeId": fake.uuid4(),
        "expireAt": (datetime.utcnow()+ timedelta(days=1)).isoformat(),
    }
    
    response = client.post("/posts", json=post_data, headers={"Authorization": "authorization"})
    assert response.status_code == status.HTTP_201_CREATED 
    response_get_one = client.delete(f"/posts/{'123'}", headers={"Authorization": "authorization"})
    
    assert response_get_one.status_code == status.HTTP_400_BAD_REQUEST  

def test_healthcheck(client: TestClient):
    response = client.get(f"/posts/ping")

    assert response.status_code == 200
    assert response.text == "PONG"

def test_reset_db(client: TestClient):
    response = client.post(f"/posts/reset")
    data = response.json()

    assert response.status_code == 200
    assert data["msg"] == "Todos los datos fueron eliminados"

