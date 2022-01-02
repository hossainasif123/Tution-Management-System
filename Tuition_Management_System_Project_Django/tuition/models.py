from django.db import models
from users.models import User


class Ad(models.Model):
    ad_time = models.DateTimeField(auto_now=True, verbose_name='Ad time')
    title = models.CharField(max_length=1000, null=False, verbose_name='Title')
    description = models.TextField(verbose_name='Description')
    subjects = models.CharField(max_length=1000, null=False, verbose_name='Subjects')
    type = models.CharField(max_length=200, null=False, verbose_name='Type')
    grade = models.CharField(max_length=200, null=False, verbose_name='Class')
    gender = models.CharField(max_length=20, verbose_name='Gender')
    pref_gender = models.CharField(max_length=20, verbose_name='Preferred Gender')
    std_count = models.IntegerField(verbose_name='Student Count')
    time = models.CharField(max_length=200, verbose_name='Teaching Time')
    days = models.IntegerField(null=False, verbose_name='How many days a week')
    location = models.CharField(max_length=1000, null=False, verbose_name='Location')
    salary = models.IntegerField(null=False, verbose_name='Monthly Salary')
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    taken = models.BooleanField(default=False, verbose_name='Taken')  # Whether the job is taken
    timeout = models.DateTimeField(null=False, verbose_name='Run This Ad Until')  # The Ad will be available until that time

    def __str__(self):
        return self.title


class Question(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    question = models.CharField(max_length=1000, null=False, verbose_name='Question')

    def __str__(self):
        return self.question.__str__()


class Assignee(models.Model):  # taken = True
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name="Ad")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tutor")
    from_date = models.DateField(null=False, verbose_name="Date Started")
    to_date = models.DateField(null=True, verbose_name="Date finished", blank=True)

    def __str__(self):
        return self.tutor.__str__()


class Proposal(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name="Ad")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    proposal = models.TextField(null=True)
    date = models.DateField(auto_now=True, verbose_name="Date proposed")

    def __str__(self):
        return self.ad.__str__()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    answer = models.TextField(verbose_name='Answer')

    def __str__(self):
        return self.question.__str__()
