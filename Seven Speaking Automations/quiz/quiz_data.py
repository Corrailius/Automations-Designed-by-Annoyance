import json
import time


class QuizData:
    def __init__(self, driver):
        self.driver = driver
        self.quiz_request_id = None
        self.quiz_response_received = False

        self.collector = self.driver.network.add_data_collector(
            data_types=["response"], max_encoded_data_size=1024 * 1024
        )

        self.collector_id = self.collector["collector"]

        self.driver.network.add_event_handler(
            "before_request_sent", self.log_network_event
        )

        self.driver.network.add_event_handler(
            "response_completed", self.log_response_event
        )

    def log_network_event(self, event):
        request = event["request"]

        if "quiz.cfc" in request["url"]:
            self.quiz_request_id = request["request"]

    def log_response_event(self, event):
        response = event.response

        if "quiz.cfc" in response["url"]:
            self.quiz_response_received = True

    def get_questions(self):
        print("Waiting for quiz API response...")

        while not self.quiz_response_received:
            time.sleep(0.1)

        print("Quiz API response received.")
        print("Retrieving response body...")

        data = self.driver.network.get_data(
            data_type="response",
            collector=self.collector_id,
            request=self.quiz_request_id,
        )

        print("Response body retrieved.")

        json_text = data["bytes"]["value"]
        quiz_data = json.loads(json_text)

        questions = quiz_data["payload"]["questions"]["data"]

        print(f"\nReceived {len(questions)} questions.")

        return questions