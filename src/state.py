class UserState:
    def __init__(self):
        self.current_question_index = 0
        self.quiz_completed = False

    def next_question_index(self):
        self.current_question_index += 1
        return self.current_question_index

    def complete_quiz(self):
        self.quiz_completed = True

    def reset_state(self):
        self.current_question_index = 0
        self.quiz_completed = False
