import uuid
import random


class Email:
    def generate_one(self):
        return {
            "id": str(uuid.uuid4()),
            "priority": random.randint(1, 3),
            "attempts": 0,
            "status": "pending",
        }

    def generate_many(self, quantity):
        return [self.generate_one() for _ in range(quantity)]
