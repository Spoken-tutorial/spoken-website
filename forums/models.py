# Third Party Stuff
from django.contrib.auth.models import User
from django.db import models


class Question(models.Model):
    uid = models.IntegerField()
    category = models.CharField(max_length=200)
    tutorial = models.CharField(max_length=200)
    minute_range = models.CharField(max_length=10)
    second_range = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=1)
    status = models.IntegerField(default=1)
    # votes = models.IntegerField(default=0)

    def get_slugified_title(self):
        return self.title.replace(' ', '-')

    def user(self):
        user = User.objects.get(id=self.uid)
        return user.username

    class Meta:
        db_table = 'website_question'
        get_latest_by = "date_created"


class QuestionVote(models.Model):
    uid = models.IntegerField()
    question = models.ForeignKey(Question)

    class Meta:
        db_table = 'website_questionvote'


class QuestionComment(models.Model):
    uid = models.IntegerField()
    question = models.ForeignKey(Question)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'website_questioncomment'


class Answer(models.Model):
    uid = models.IntegerField()
    question = models.ForeignKey(Question)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    # votes = models.IntegerField(default=0)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user.username

    class Meta:
        db_table = 'website_answer'


class AnswerVote(models.Model):
    uid = models.IntegerField()
    answer = models.ForeignKey(Answer)

    class Meta:
        db_table = 'website_answervote'


class AnswerComment(models.Model):
    uid = models.IntegerField()
    answer = models.ForeignKey(Answer)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user.username

    class Meta:
        db_table = 'website_answercomment'


class Notification(models.Model):
    uid = models.IntegerField()
    pid = models.IntegerField()
    qid = models.IntegerField()
    aid = models.IntegerField(default=0)
    cid = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)

    def poster(self):
        user = User.objects.get(id=self.pid)
        return user.username

    class Meta:
        db_table = 'website_notification'
