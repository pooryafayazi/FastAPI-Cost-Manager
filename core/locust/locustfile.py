# core/locust/locustfile.py
import os
import random
from locust import HttpUser, task, between, events

API_PREFIX = "/api/v1" 
USERS_LOGIN = f"{API_PREFIX}/users/login-cookie"
USERS_REFRESH = f"{API_PREFIX}/users/refresh-cookie"
USERS_LOGOUT = f"{API_PREFIX}/users/logout-cookie"

EXPENSES_BASE = f"{API_PREFIX}/expenses"

USERNAME = os.getenv("LOCUST_USERNAME", "poorya")
PASSWORD = os.getenv("LOCUST_PASSWORD", "poory@152")

class AuthenticatedUser(HttpUser):
    wait_time = between(0.5, 2.0)

    # --- helpers ---
    def _set_csrf_header(self):
        csrf = self.client.cookies.get("csrf_token")
        if csrf:
            self.client.headers.update({"x-csrf-token": csrf})
        else:
            self.client.headers.pop("x-csrf-token", None)

    def _login(self) -> bool:
        r = self.client.post(USERS_LOGIN, json={"username": USERNAME, "password": PASSWORD})
        if r.status_code == 200:
            self._set_csrf_header()
            return True
        return False

    def on_start(self):
        if not self._login():
            if self.environment and self.environment.runner:
                self.environment.runner.quit()

        with self.client.post(
            USERS_LOGIN,
            json={"username": USERNAME, "password": PASSWORD},
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Login failed: {resp.status_code} {resp.text}")
                # If login fails, abort the entire test
                if self.environment and self.environment.runner:
                    self.environment.runner.quit()
                return
            else:
                resp.success()
        
        access_csrf = self.client.cookies.get("csrf_token") or self.client.cookies.get("csrf_access_token")
        refresh_csrf = self.client.cookies.get("csrf_refresh_token") 
        
        self.refresh_headers = {}
        if refresh_csrf:
            self.refresh_headers["x-csrf-token"] = refresh_csrf

        if access_csrf:
            self.client.headers.update({"x-csrf-token": access_csrf})
        else:
            print("[WARN] csrf for access not set")

    # Read list (with random parameters for variety)
    @task(3)
    def list_expenses(self):
        params = {
            "page": random.randint(1, 3),
            "limit": random.choice([5, 10, 20]),
        }
        if random.random() < 0.5:
            params["search"] = random.choice(["rent", "food", "book"])
        self.client.get(EXPENSES_BASE, params=params, name=f"{EXPENSES_BASE}?list")

    # Create (with a return on 401)
    @task(5)
    def create_expense(self):
        payload = {
            "description": random.choice(["coffee", "book", "ticket", "rent", "food"]),
            "amount": random.randint(1, 500),
        }
        with self.client.post(EXPENSES_BASE, json=payload,
                              name=f"{EXPENSES_BASE} [POST]",
                              catch_response=True) as resp:
            if resp.status_code in (200, 201):
                resp.success()
                return
            # If it gets 401, refresh and retry once
            if resp.status_code == 401:
                rf_ok = self._try_refresh()
                if rf_ok:
                    resp.retry()
                    r2 = self.client.post(EXPENSES_BASE, json=payload, name=f"{EXPENSES_BASE} [POST]")
                    if r2.status_code in (200, 201):
                        return
                    else:
                        resp.failure(f"Create after refresh failed: {r2.status_code} {r2.text}")
                        return
            resp.failure(f"Create failed: {resp.status_code} {resp.text}")

    #  Read one / Update / Delete (chaining) (no return for shortening)
    @task(2)
    def crud_chain(self):
        # Create
        payload = {"description": "locust item", "amount": random.randint(10, 300)}
        r_create = self.client.post(EXPENSES_BASE, json=payload, name=f"{EXPENSES_BASE} [POST]")
        if r_create.status_code not in (200, 201):
            return
        exp = r_create.json()
        exp_id = exp.get("id")
        # exp_id = r_create.json().get("id")
        if not exp_id:
            return

        # Get detail
        self.client.get(f"{EXPENSES_BASE}/{exp_id}", name=f"{EXPENSES_BASE}/:id [GET]")

        # Update
        upd = {"description": "locust item updated", "amount": random.randint(50, 400)}
        self.client.put(f"{EXPENSES_BASE}/{exp_id}", json=upd, name=f"{EXPENSES_BASE}/:id [PUT]")

        # Delete
        self.client.delete(f"{EXPENSES_BASE}/{exp_id}", name=f"{EXPENSES_BASE}/:id [DELETE]")

    # Refresh token (with CSRF) 
    @task(1)
    def refresh_access_token(self):
        if "x-csrf-token" not in self.client.headers:
            #No CSRF header → 403 Forbidden
            return
        with self.client.post(USERS_REFRESH, name=f"{USERS_REFRESH} [POST]", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Refresh failed: {resp.status_code} {resp.text}")
    
    # helper: Attempt to refresh
    def _try_refresh(self) -> bool:
        if "x-csrf-token" not in self.client.headers:
            print("[ERROR] Missing x-csrf-token header for refresh")
            return False
        r = self.client.post(USERS_REFRESH, name=f"{USERS_REFRESH} [POST]")
        if r.status_code == 200:
            return True
        print(f"[ERROR] Refresh failed {r.status_code}: {r.text}")
        return False

    # Logout (requires CSRF)
    @task(1)
    def logout_flow(self):
        # requires CSRF
        if "x-csrf-token" not in self.client.headers:
            return

        # 1) logout
        with self.client.post(USERS_LOGOUT, name=f"{USERS_LOGOUT} [POST]", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Logout failed: {resp.status_code} {resp.text}")
                return
            resp.success()

        # After logout, cookies should be cleared
        self._set_csrf_header()  # also clear the CSRF header if the cookie has been deleted

        # 2) Send a protected request and expect a 401
        with self.client.get(EXPENSES_BASE, name=f"{EXPENSES_BASE} after logout [GET]", catch_response=True) as r2:
            if r2.status_code == 401:
                r2.success()
            else:
                r2.failure(f"Expected 401 after logout, got {r2.status_code}")

        # 3) Log in again to return the user to the cycle
        ok = self._login()
        if not ok:
            # If the login does not return, it is better to stop the user instance so that the statistics are not corrupted
            print("[ERROR] Re-login failed after logout")

