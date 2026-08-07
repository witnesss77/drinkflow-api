import pytest
from fastapi.testclient import TestClient
from core.auth.router import get_current_user
from core.main import app
import random
import json
import uuid


class TestDrinkAPI:
    def test_get_drinks(self, test_client):
        response = test_client.get("/drinks")
        print(response.text)
        assert response.status_code == 200


    @pytest.mark.parametrize("page", [1, 0])
    def test_get_drinks_pagination(self, page, test_client):
        response = test_client.get("/drinks", params={"page":page})
        print(response.text)
        assert response.status_code == 200


    def test_set_drinks(self, test_client, create_factory):
        obj = {
        "name": "test",
        "desc": "none",
        "alcoholic": True,
        "price": 111,
        "factory_id": create_factory,
        }

        response = test_client.post("/drinks", json=obj)
        print(response.text)
        assert response.status_code == 201


    @pytest.mark.parametrize(
        ["page", "name", "desc", "alcoholic", "price", "factory_id"],
        [
            (None, None, None, True, None, None),
        ],)
        
    def test_get_drinks_with_params(self, test_client, page, name, desc, alcoholic, price, factory_id):
        params={
        "page":page, 
        "name":name, 
        "desc":desc, 
        "alcoholic":alcoholic, 
        "price":price,
        "factory_id":factory_id}
        
        fix = {k:v for k,v in params.items() if v != None}

        response = test_client.get("/drinks", params = fix)
        print(response.text)
        assert response.status_code == 200


    def test_patch_drinks(self, test_client: TestClient, create_factory):
        obj = {
        "name": "test",
        "desc": "none",
        "alcoholic": True,
        "price": 111,
        "factory_id": create_factory,
        }

        response = test_client.post("/drinks", json=obj)
        print(response.text)
        drink_id = response.json()["id"]
        
        response = test_client.patch(f"/drinks/{drink_id}", json = {"name": "test"})
        print(response.text)
        assert response.status_code == 200


    def test_delete_drinks(self, test_client, create_factory):

        obj = {
                "name": "test",
                "desc": "none",
                "alcoholic": True,
                "price": 111,
                "factory_id": create_factory,
                }

        response = test_client.post("/drinks", json=obj)
        drink_id = response.json()["id"]
        response = test_client.delete(f"/drinks/{drink_id}")

        print(response.text)
        assert response.status_code == 200


class TestFactoriesAPI:
    def test_get_factories(self, test_client):
        response = test_client.get("/factories")
        print(response.text)
        print(response.text)
        assert response.status_code == 200

    def test_set_factory(self, test_client):
        obj = {
                "name": "test",
                "location": "test_location"
        }

        response = test_client.post("/factories", json=obj)
        print(response.text)
        print(response.text)
        assert response.status_code == 201


    def test_patch_factory(self, test_client: TestClient):
        obj = {
            "name": "zavod",
            "location": "ekodqkodq"
        }

        response = test_client.post("/factories", json=obj)
        print(response.text)
        factory_id = response.json()["id"]

        response = test_client.patch(f"/factories/{factory_id}", json = {"name": "test"})
        print(response.text)
        assert response.status_code == 200


    def test_delete_factory(self, test_client):
        obj = {"name": "test", "location": "test_location"}

        response = test_client.post("/factories", json=obj)
        factory_id = response.json()["id"]

        response = test_client.delete(f"/factories/{factory_id}")
        print(response.text)
        print(response.text)
        assert response.status_code == 200


class TestStocksAPI:
    def test_get_stocks(self, test_client):
        response = test_client.get("/stocks")
        assert response.status_code == 200

    def test_set_stock(self, test_client, create_drink, create_warehouse):
        obj = {
            "drink_id": create_drink,
            "warehouse_id": create_warehouse,
            "quantity": 10,
            "reserved_quantity": 1
        }

        response = test_client.post("/stocks", json=obj)
        print(response.text)
        assert response.status_code == 200


    def test_patch_stock(self, test_client, create_drink, create_warehouse):
        obj = {
        "drink_id": create_drink,
        "warehouse_id": create_warehouse,
        "quantity": 10,
        "reserved_quantity": 1
        }
        
        response = test_client.post("/stocks", json=obj)
        stock_id = response.json()["id"]
        response = test_client.patch(f"/stocks/{stock_id}", json = {"quantity": 32})
        print(response.text)
        assert response.status_code == 200


    def test_delete_stock(self, test_client, create_drink, create_warehouse):
        obj = {
        "drink_id": create_drink,
        "warehouse_id": create_warehouse,
        "quantity": 10,
        "reserved_quantity": 1
        }
                
        response = test_client.post("/stocks", json=obj)
        stock_id = response.json()["id"]
        response = test_client.delete(f"/stocks/{stock_id}")
        print(response.text)
        assert response.status_code == 200

class TestWarehouseAPI:
    def test_get_warehouses(self, test_client):
        response = test_client.get("/warehouses")
        assert response.status_code == 200

    def test_set_warehouse(self, test_client):
        obj = {
                "name": "test",
                "address": "test_location"
            }
            
        response = test_client.post("/warehouses", json=obj)
        assert response.status_code == 201
    
       
    def test_patch_warehouse(self, test_client: TestClient, create_warehouse):
        w_id = create_warehouse
        response = test_client.patch(f"/warehouses/{w_id}", json = {"location": "moscow"})
        assert response.status_code == 200
        

    def test_delete_warehouse(self, test_client, create_warehouse):
        w_id = create_warehouse

        response = test_client.delete(f"/warehouses/{w_id}")
        assert response.status_code == 200

class TestOrdersAPI:
    def test_get_orders(self, test_client: TestClient):
        response = test_client.get("/orders")
        assert response.status_code == 200

    @pytest.mark.parametrize("page, user_id, warehouse_id, status, is_paid",
            [(None, None, None, None, False),
            ])
    def test_get_orders_with_params(self,
        test_client, 
        page, 
        user_id, 
        warehouse_id, 
        status, 
        is_paid):

        obj = {
        "page":page, 
        "user_id":user_id, 
        "warehouse_id":warehouse_id, 
        "status":status, 
        "is_paid":is_paid
        }

        obj = json.dumps(obj)
        response = test_client.get("/orders", 
        params=obj)
        print(response.status_code)
        print(response.text)
        assert response.status_code == 200
    
    @pytest.mark.parametrize("page", [1, 0])
    def test_get_orders_pagination(self, page, test_client: TestClient):
        response = test_client.get("/orders", params={"page":page})
        assert response.status_code == 200

    
    def test_set_order(self, test_client, create_user, create_warehouse):
        obj = {"user_id": create_user, "warehouse_id": create_warehouse}
        
        response = test_client.post("/orders", json = obj)
        print(response.text)
        assert response.status_code == 201
    

    def test_change_order_status(self, test_client: TestClient, create_order):
        order_id = create_order
        response = test_client.patch(f"/orders/{order_id}/change_status", json={"status": "in test", "is_paid": False})
        print(response.text)
        assert response.status_code == 200
    
    
    def test_order_payment(self, test_client: TestClient, create_order):
        order_id = create_order
        response = test_client.patch(f"/orders/{order_id}/payment")
        print(response.status_code)
        print(response.text)
        assert response.status_code == 200


    def test_delete_order(self, test_client: TestClient, create_order):
        order_id = create_order
        response = test_client.delete(f"/orders/{order_id}")
        assert response.status_code == 200


    def test_get_order_items(self, test_client: TestClient):
        response = test_client.get("/orders/order_items")
        assert response.status_code == 200


    @pytest.mark.parametrize(
        "order_id, user_id, drink_id, quantity, pricier",
        [
            (1,None,None,None,1),
            (1,None,None,None,None)
        ]
    )
    def test_get_order_items_with_params(self, test_client, order_id, user_id, drink_id, quantity, pricier):
        query = {"order_id":order_id, 
                    "user":user_id, 
                    "drink_id":drink_id, 
                    "quantity":quantity, 
                    "pricier":pricier}

        fixed = {k:v for k,v in query.items() if v != None}
        response = test_client.get("/orders/order_items", params = fixed)
        print(response.text)
        assert response.status_code == 200

    
    def test_add_item_to_order(self, test_client, create_warehouse, create_order, create_user, create_drink):
        stock = {
        "drink_id": create_drink,
        "warehouse_id": create_warehouse,
        "quantity": 100,
        "reserved_quantity": 0
        }

        stock_response = test_client.post("/stocks",json=stock)

        w_id = create_warehouse
        obj = {
            "order_id": create_order,
            "user_id": create_user,
            "drink_id": create_drink,
            "quantity": 10,
            "price_per_item": 100
            }
            
        request = test_client.post('/orders/order_items', params = {"warehouse_id": w_id}, json = obj)
        print(request.text)
        assert request.status_code == 200



    def test_change_item_quantity(self, test_client: TestClient, create_order_item):
        item_id = create_order_item
        payload = {"quantity": 1, "price_per_item": 100}
        response = test_client.patch(f"/orders/order_items/{item_id}", json=payload)
        assert response.status_code == 200

    def test_delete_order_item(self, test_client, create_order_item):
        item_id = create_order_item
        response = test_client.delete(f"/orders/order_items/{item_id}")
        assert response.status_code == 200
    
class TestAuthAPI:
    def test_register(self, test_client):
        email = f"test_{uuid.uuid4()}@test.com"
        obj = {
            "name": "test",
            "email": email,
            "password": "12345678",
            "role": "user"
        }
        response = test_client.post('/auth/register', json = obj)
        assert response.status_code == 201


    def test_get_protected_route(self, test_client):
        response = test_client.get("/auth/me")
        assert response.status_code == 200


    def test_tokens(self, test_client):
        nums = random.randint(1000,9999)
        email = f"test_{uuid.uuid4()}@test.com"
        user = {
            "name": f"test{nums}",
            "email": email,
            "password": "12345678",
            "role": "user"
        }
        register = test_client.post("/auth/register",json=user)
        assert register.status_code == 201
        
        payload = {"username": user["name"],"password": "12345678"}
        response = test_client.post("/auth/token",data=payload)
        token = response.json()["refresh_token"]

        response2 = test_client.post("/auth/refresh",json={"refresh_token":token})
        print(response2.text)
        assert response2.status_code == 200



class TestAPINegativeCases:
    def test_negative_stock(self, test_client, create_drink, create_warehouse):
        obj = {
                "drink_id": create_drink,
                "warehouse_id": create_warehouse,
                "quantity": -1,
                "reserved_quantity": 10
        }
        
        response = test_client.post("/stocks", json=obj)
        print(response.text)
        assert response.status_code == 422

    def test_order_item_limit(self, test_client, create_warehouse, create_order, create_user, create_drink):
        stock = {
                "drink_id": create_drink,
                "warehouse_id": create_warehouse,
                "quantity": 10,
                "reserved_quantity": 0
                }
        
        stock_response = test_client.post("/stocks", json=stock)
        
        w_id = create_warehouse
        obj = {
            "order_id": create_order,
            "user_id": create_user,
            "drink_id": create_drink,
            "quantity": 100,
            "price_per_item": 100
            }
                    
        request = test_client.post('/orders/order_items', params = {"warehouse_id": w_id}, json = obj)
        print(request.text)
        assert request.status_code == 409

    def test_already_paid_order(self, test_client, create_order):
        order_id = create_order
        response = test_client.patch(f"/orders/{order_id}/payment")
        response2 = test_client.patch(f"/orders/{order_id}/payment")
        assert response2.status_code == 409

    def test_delete_not_existing_order(self, test_client):
        response = test_client.delete("/orders/3223")
        assert response.status_code == 409

    def test_delete_not_existing_factory(self, test_client):
            response = test_client.delete("/factory/3223")
            assert response.status_code == 404

    def test_wrong_refresh_token(self, test_client):
        response = test_client.post(
            "/auth/refresh",
            json={"refresh_token": "qeffwRFDSCX"}
        )

        assert response.status_code == 401

    def test_incorrect_login(self, test_client):
        response = test_client.post("/auth/token", json = {"username": "wrong_name", "password":"some_password"})
        assert response.status_code == 422