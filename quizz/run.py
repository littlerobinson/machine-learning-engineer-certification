# Quizz v2

class Quizz():
    
    # Init class method
    def __init__(self, question_list = [], lives = 3):
        print("Here you have our quiz !")
        # Init class attributes
        self.question_list = question_list
        self.lives = lives
    
    # Function to run the quizz
    def run(self):
        for question in self.question_list:
            if self.check_lives() == False:
                break
            else:
                while self.check_question(question) == False and self.check_lives():
                    print("Too bad! that is not the correct answer, you have", self.lives, "chances left, retry")
        # Print result
        if self.check_lives() == False:
            print("Oh no, you lost the quiz...")
        else:
            print("Good job, you have {} live(s) left and you win!".format(self.lives))
    
    # Function to check question
    def check_question(self, question = {}):
        try:
            if not question:
                raise NoQuestionError
        except NoQuestionError:
            print("Error: there is no question")

        # Ask question to user and save the answer
        user_answer = input(question["question"])
        if user_answer.lower() == question["answer"].lower():
            return True
        else:
            # Decrease lives
            self.lives -= 1
            return False
        

    # Function to check left lives
    def check_lives(self):
        if self.lives > 0:
            return True
        else:
            return False

# Questions dict variable initialization
question_list = [
    {
        "question": "Couleur du cheval blanc d'henry IV ?", 
        "answer": "Blanc"
    },
    {
        "question": "Prefecture des Hautes-Alpes ?", 
        "answer": "Gap"
    },
    {
        "question": "Capitale du Chili ?", 
        "answer": "Santiago"
    },
]

nb_lives = 3

quizz = Quizz(question_list, nb_lives)
quizz.run()