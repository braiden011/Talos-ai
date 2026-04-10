import json
import os
import random
from difflib import get_close_matches


class CleanAI:
    def __init__(self):
        self.filename = "Talos.json"
        self.journal_file = "Journal.txt"
        self.book_file = "Book.txt"  # This is your full book file
        self.memory = self.load_memory()
        self.passcode = "0907"

        self.hello_words = ["hi", "hello", "hey", "yo", "sup"]
        self.hello_responses = ["Hey there!", "Hello!", "Yo! What's up?"]

    def load_memory(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    content = f.read().strip()
                    if not content:  # If the file is empty
                        return {"user_name": "Braiden"}
                    return json.loads(content)
            except json.JSONDecodeError:  # If the file is corrupted
                return {"user_name": "Braiden"}
        return {"user_name": "Braiden"}

    def save_memory(self):
        with open(self.filename, "w") as f:
            json.dump(self.memory, f)

    def search_book(self, query):
        """Searches Book.txt for a sentence containing the query"""
        if not os.path.exists(self.book_file):
            return None

        with open(self.book_file, "r") as f:
            lines = f.readlines()
            # Look for the best matching line in the book
            for line in lines:
                if query.lower() in line.lower() and len(line) > 5:
                    return line.strip()
        return None

    def journal_mode(self):
        print(f"\n--- [TALOS SECURE JOURNAL] ---")
        code = input("Enter 4-digit passcode: ")
        if code != self.passcode:
            print("Access Denied.")
            return

        print("\nAccess Granted. (1: Read | 2: Write | 3: Delete | 4: Exit)")
        while True:
            choice = input("\nOption: ")
            if choice == "1":
                if os.path.exists(self.journal_file):
                    with open(self.journal_file, "r") as f:
                        print("\n--- JOURNAL ---\n" + f.read())
                else:
                    print("\n[Journal is empty.]")
            elif choice == "2":
                entry = input("Write: ")
                with open(self.journal_file, "a") as f:
                    f.write("- " + entry + "\n")
            elif choice == "4":
                break

    def chat(self, user_input):
        user_input = user_input.lower().strip()
        words = user_input.split()

        # 1. GREETINGS
        if any(word in self.hello_words for word in words):
            return random.choice(self.hello_responses)

        # 2. NAME RECOGNITION
        if "name is" in user_input:
            name = user_input.split("is")[-1].strip()
            self.memory["user_name"] = name
            self.save_memory()
            return f"Nice to meet you, {name}!"

        # 3. MEMORY CHECK
        memory_keys = list(self.memory.keys())
        for word in words:
            match = get_close_matches(word, memory_keys, n=1, cutoff=0.7)
            if match:
                return f"I remember: {match[0]} {self.memory[match[0]]}."

        # 4. FULL BOOK SEARCH (The "Smart" part)
        # If Talos doesn't know the answer, he scans the book
        for word in words:
            if len(word) > 3:  # Don't search for tiny words like 'the'
                fact = self.search_book(word)
                if fact:
                    return f"From the book, I found: '{fact}'"

        return "I couldn't find that in my memory or the book, Braiden."


# --- START ---
bot = CleanAI()
NAME = "Talos"

print(f"--- {NAME} IS ONLINE ---")

while True:
    try:
        user = input("You: ").lower().strip()

        # Check for Journal Command
        if "open" in user and "journal" in user:
            bot.journal_mode()
        elif user in ["quit", "exit", "stop"]:
            break
        else:
            print(f"{NAME}: {bot.chat(user)}")
    except EOFError:
        break
