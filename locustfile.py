from locust import HttpUser, task, between

class MbdPageUser(HttpUser):
    wait_time = between(1, 3)  # 요청 사이 1~3초 대기

    @task(3)
    def index(self):
        self.client.get("/")

    @task(2)
    def docs(self):
        self.client.get("/docs")

    @task(1)
    def health(self):
        self.client.get("/health") 

# HttpUser     → 가상 사용자 1명
# wait_time    → 요청 사이 대기 시간 (실제 사람처럼)
# @task(3)     → 가중치 (숫자 높을수록 자주 요청)
# @task(2)     → docs 페이지는 두 번째로 자주
# @task(1)     → health는 가끔