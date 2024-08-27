from db import Model, StringField, OneToManyField

class Question(Model):
    class Meta:
        fields = {
            'id': StringField(),
            'question': StringField(),
            'answer': StringField(),
        }

class Course(Model):
    def __init__(self, **kwargs):
        # get the questions from kwargs and convert them to Question objects
        # then call the super constructor with the new kwargs
        questions = kwargs.pop('questions', [])
        kwargs['questions'] = [Question(**q) for q in questions]
        super().__init__(**kwargs)

    class Meta:
        fields = {
            'id': StringField(),
            'name': StringField(),
            'questions': OneToManyField(Question)
        }
