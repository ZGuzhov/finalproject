from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Question(models.Model):
    title = models.CharField(max_length=250, verbose_name=u'Вопрос')
    mode = models.IntegerField(choices=[(1, 'Один ответ'), (2, 'Несколько ответов')], default=1, verbose_name=u'Тип вопроса')
    image = models.ImageField(upload_to='images', blank=True, verbose_name=u'Картинка')

    class Meta:
        verbose_name = u'Вопрос'
        verbose_name_plural = u'Вопросы'
    
    def __str__(self):
        return self.title


class QuestionInPoll(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, verbose_name=u'Вопрос', related_name='questions')
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE, related_name='polls')
    weight = models.IntegerField(default=1, verbose_name=u'Вес вопроса в опросе') 

    class Meta:
        verbose_name = u'Вопрос в опросе'
        verbose_name_plural = u'Вопросы в опросе'
    
    def __str__(self):
        return 'Вопрос: "{}" в опросе: "{}"'.format(self.question.title, self.poll.title)


class Answer(models.Model):
    title = models.CharField(max_length=250, verbose_name=u'Ответ')
    score = models.IntegerField(default=0, verbose_name=u'Кол-во баллов')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')

    class Meta:
        verbose_name = u'Ответ'
        verbose_name_plural = u'Ответы'

    def __str__(self):
        return 'Ответ: "{}" в вопросе: "{}"'.format(self.title, self.question.title)


class Poll(models.Model):
    title = models.CharField(max_length=250, verbose_name=u'Опрос')
    description = models.CharField(max_length=250, verbose_name=u'Описание')
    public = models.DateField(default=date.today, verbose_name=u'Дата публикации')

    class Meta:
        verbose_name = u'Опрос'
        verbose_name_plural = u'Опросы'
    
    def __str__(self):
        return self.title


class UserAnswers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u'Пользователь', related_name='users')
    question_in_poll = models.ForeignKey('QuestionInPoll', on_delete=models.CASCADE, verbose_name=u'Вопрос в опросе', related_name='q_in_p')
    answer = models.ManyToManyField('Answer', verbose_name=u'Ответ', blank=True, related_name='user_answers')