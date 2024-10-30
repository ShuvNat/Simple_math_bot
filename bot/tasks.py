from random import choice, randint


class Tasks:
    def __init__(self):
        self.a = 0
        self.b = self.b = randint(2, 9)
        self.question = ''
        self.answer = 0
        self.name = ''


class MultiDiv(Tasks):

    def multi(self):
        self.name = 'multi'
        self.question = choice(
            [f'{self.a} * {self.b} = ',
             f'{self.b} * {self.a} = ']
        )
        self.answer = self.a * self.b

    def div(self):
        self.name = 'div'
        self.question = f'{self.a*self.b} : {self.a} = '
        self.answer = self.b

    def random(self):
        random_func = choice(
            [self.multi,
             self.div]
        )
        random_func()


class AllOperations(Tasks):
    def __init__(self):
        super().__init__()
        self.a = randint(2, 9)
        self.name = 'all_ops'

    def multi_add(self):
        c = randint(1, 100-self.a*self.b)
        self.question = choice(
            [f'{self.a} * {self.b} + {c} = ',
             f'{c} + {self.a} * {self.b} = ']
        )
        self.answer = self.a * self.b + c

    def multi_sub(self):
        c = randint(1, self.a*self.b)
        self.question = f'{self.a} * {self.b} - {c} = '
        self.answer = self.a * self.b - c

    def sub_multi(self):
        c = randint(self.a*self.b, 100)
        self.question = f'{c} - {self.a} * {self.b} = '
        self.answer = c - self.a * self.b

    def div_add(self):
        c = randint(1, 100-self.a)
        self.question = choice(
            [f'{self.a*self.b} : {self.b} + {c} = ',
             f'{c} + {self.a*self.b} : {self.b} = ']
        )
        self.answer = self.a + c

    def div_sub(self):
        c = randint(1, self.a-1)
        self.question = f'{self.a*self.b} : {self.b} - {c} = '
        self.answer = self.a - c

    def sub_div(self):
        c = randint(self.a, 100)
        self.question = f'{c} - {self.a*self.b} : {self.b} = '
        self.answer = c - self.a

    def random_task(self):
        random_func = choice(
            [self.multi_add,
             self.multi_sub,
             self.sub_multi,
             self.div_add,
             self.div_sub,
             self.sub_div]
        )
        random_func()
