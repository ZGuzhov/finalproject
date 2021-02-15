from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from polls.models import Poll, QuestionInPoll, Question, Answer, UserAnswers
from datetime import date


def main(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    if request.user.is_staff:
        context['staff'] = True
    return render(request, 'main.html', context)


def signup(request):
    params = request.GET.dict()
    username = params.get('username')
    password1 = params.get('password1')
    password2 = params.get('password2')
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    if request.user.is_staff:
        context['staff'] = True
    
    if username and password1 and password2:
        user = User.objects.filter(username=username).first()
        if user:
            context['error'] = 'Пользователь с именем ' + username + ' уже существует.'
            return render(request, 'signup.html', context)
        elif password1 != password2:
            context['error'] = 'Пароли не совпадают.'
            context['username_input'] = username
            return render(request, 'signup.html', context)
        else:
            user = User.objects.create_user(username=username)
            user.set_password(password1)
            user.save()
            return HttpResponseRedirect(reverse_lazy('login'))
    else:
        return render(request, 'signup.html', context)


@login_required
def polls_list(request, polls_choice):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    if request.user.is_staff:
        context['staff'] = True
    context['current_date'] = date.today()
    context['polls_choice'] = polls_choice

    questions_poll = {}
    q_in_p = QuestionInPoll.objects.all()
    for i in q_in_p:
        if i.poll.id in questions_poll:
            questions_poll[i.poll.id] += 1
        else:
            questions_poll[i.poll.id] = 1
    
    answered_poll = {}
    poll_points = {}
    user_ans = UserAnswers.objects.filter(user=request.user)
    for i in user_ans:
        if i.question_in_poll.poll.id in answered_poll:
            answered_poll[i.question_in_poll.poll.id] += 1
        else:
            answered_poll[i.question_in_poll.poll.id] = 1

        scores = 0
        for ans in i.answer.all():
            scores += ans.score
        if i.question_in_poll.poll.id in poll_points:
            poll_points[i.question_in_poll.poll.id] += scores * i.question_in_poll.weight
        else:
            poll_points[i.question_in_poll.poll.id] = scores * i.question_in_poll.weight

    context['poll_points'] = poll_points

    checked_polls = []
    for p in questions_poll:
        if p in answered_poll and questions_poll.get(p) == answered_poll.get(p):
            checked_polls.append(p)
        
    context['checked_polls'] = checked_polls

    if polls_choice == 'all':
        polls = Poll.objects.all()
        context['polls'] = polls
    elif polls_choice == 'checked':
        polls = Poll.objects.filter(id__in=checked_polls)
        context['polls'] = polls
    elif polls_choice == 'not-available':
        polls = Poll.objects.filter(public__gt=date.today())
        context['polls'] = polls
    elif polls_choice == 'available':
        polls = Poll.objects.exclude(public__gt=date.today()).exclude(id__in=checked_polls)
        context['polls'] = polls

    return render(request, 'polls-list.html', context)
    

@login_required
def poll_detail(request, poll_id, scroll_id):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    if request.user.is_staff:
        context['staff'] = True
    context['poll_title'] = Poll.objects.get(id=poll_id).title
    context['poll_id'] = poll_id
    context['scroll_id'] = scroll_id
    
    q_in_p_list = []
    q_in_p = QuestionInPoll.objects.filter(poll__id=poll_id)
    for i in q_in_p:
        q_in_p_list.append(i.question.id)
    context['q_in_p'] = q_in_p
    
    answers = Answer.objects.filter(question__id__in=q_in_p_list)
    context['answers'] = answers

    checked_answers = []
    answered_questions = []
    question_points = {}
    user_ans = UserAnswers.objects.filter(user=request.user)
    for i in user_ans:
        if poll_id == i.question_in_poll.poll.id:
            scores = 0
            for ans in i.answer.all():
                checked_answers.append(ans.id)
                scores += ans.score
            answered_questions.append(i.question_in_poll.question.id)
            if i.question_in_poll.id in question_points:
                question_points[i.question_in_poll.id] += scores * i.question_in_poll.weight
            else:
                question_points[i.question_in_poll.id] = scores * i.question_in_poll.weight

    context['answered_questions'] = answered_questions
    context['checked_answers'] = checked_answers
    context['question_points'] = question_points

    return render(request, 'poll-detail.html', context)


@login_required
def user_answers(request, poll_id, q_in_p_id, a_id):
    q_in_p = QuestionInPoll.objects.get(id=q_in_p_id)
    answer_double = UserAnswers.objects.filter(user=request.user, question_in_poll=q_in_p)
    params = request.GET.dict()
    # повторная отправка ответа заблокирована в шаблоне, но на всякий случай ещё раз проверяю здесь и игнорирую 
    if not answer_double and len(params) != 0:
        u_a = UserAnswers.objects.create(user=request.user, question_in_poll=q_in_p)
        if a_id == 0:
            for i in params:
                a = Answer.objects.get(id=i)
                u_a.answer.add(a)
        else:
            a = Answer.objects.get(id=a_id)
            u_a.answer.add(a)
    
    return redirect('/poll/' + str(poll_id) + '/' + str(q_in_p.question.id))


@login_required
def statistics(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    context['user_choice'] = request.user.username
    if request.user.is_staff:
        context['staff'] = True
        users = User.objects.all()
        users_list = []
        for u in users:
            users_list.append(u.username)
        context['users_list'] = users_list
        params = request.GET.dict()
        user_choice = params.get('user_choice')
        if user_choice:
            context['user_choice'] = user_choice

    n_polls = Poll.objects.all().count()
    context['n_polls'] = n_polls

    if n_polls == 0:
        return render(request, 'statistics.html', context)

    questions_poll = {}
    q_in_p = QuestionInPoll.objects.all()
    for i in q_in_p:
        if i.poll.id in questions_poll:
            questions_poll[i.poll.id] += 1
        else:
            questions_poll[i.poll.id] = 1

    selected_user = request.user
    if request.user.is_staff and user_choice:
        selected_user = User.objects.get(username=user_choice)
    
    answered_poll = {}
    poll_points = {}
    user_ans = UserAnswers.objects.filter(user=selected_user)
    for i in user_ans:
        if i.question_in_poll.poll.id in answered_poll:
            answered_poll[i.question_in_poll.poll.id] += 1
        else:
            answered_poll[i.question_in_poll.poll.id] = 1
        scores = 0
        for ans in i.answer.all():
            scores += ans.score
        if i.question_in_poll.poll.id in poll_points:
            poll_points[i.question_in_poll.poll.id] += scores * i.question_in_poll.weight
        else:
            poll_points[i.question_in_poll.poll.id] = scores * i.question_in_poll.weight

    checked_polls = []
    for p in questions_poll:
        if p in answered_poll and questions_poll.get(p) == answered_poll.get(p):
            checked_polls.append(p)
        
    polls = Poll.objects.filter(id__in=checked_polls)
    n_polls_not_av = Poll.objects.filter(public__gt=date.today()).count()
    percent_checked = round(len(polls) / n_polls * 100)
    percent_not_av = round(n_polls_not_av / n_polls * 100)

    context['polls'] = polls
    context['n_polls_checked'] = len(polls)
    context['n_polls_not_av'] = n_polls_not_av
    context['n_polls_av'] = n_polls - n_polls_not_av - len(polls)
    context['percent_checked'] = percent_checked
    context['percent_not_av'] = percent_not_av
    context['percent_av'] = 100 - percent_not_av - percent_checked
    
    min_poll_points = {}
    max_poll_points = {}
    users_points = {}
    users = User.objects.all()
    for u in users:
        user_ans = UserAnswers.objects.filter(user=u)
        p_points = {}
        for i in user_ans:
            scores = 0
            for ans in i.answer.all():
                scores += ans.score
            if i.question_in_poll.poll.id in p_points:
                p_points[i.question_in_poll.poll.id] += scores * i.question_in_poll.weight
            else:
                p_points[i.question_in_poll.poll.id] = scores * i.question_in_poll.weight
        if len(p_points) != 0:
            for key, value in p_points.items():
                if key in min_poll_points:
                    if value < min_poll_points[key]:
                        min_poll_points[key] = value
                else:
                    min_poll_points[key] = value
                if key in max_poll_points:
                    if value > max_poll_points[key]:
                        max_poll_points[key] = value
                else:
                    max_poll_points[key] = value
                if u.username in users_points:
                    users_points[u.username] += value
                else:
                    users_points[u.username] = value
    
    users_points_sorted = {}
    users_points_sorted_list = sorted(users_points, key=users_points.get, reverse=True)
    for key in users_points_sorted_list:
        users_points_sorted[key] = users_points[key]
    context['users_points_sorted'] = users_points_sorted

    polls_stat = {}
    for p in polls:
        if p.id in poll_points:
            polls_stat[p.title] = [poll_points[p.id], min_poll_points[p.id], max_poll_points[p.id]]
    context['polls_stat'] = polls_stat

    q_in_p_dict = {}
    answers_selected_dict = {}
    for poll in polls:
        q_in_p_list = []
        q_in_p = QuestionInPoll.objects.filter(poll__id=poll.id)
        for i in q_in_p:
            q_in_p_list.append(i.question.id)
        
        checked_answers = []
        answered_questions = []
        user_ans = UserAnswers.objects.filter(user=selected_user)
        for i in user_ans:
            if poll.id == i.question_in_poll.poll.id:
                scores = 0
                for ans in i.answer.all():
                    checked_answers.append(ans.id)
                    scores += ans.score
                answered_questions.append(i.question_in_poll.question.id)

        q_in_p_dict[poll.id] = q_in_p
        answers_selected = Answer.objects.filter(question__id__in=q_in_p_list).filter(id__in=checked_answers)
        answers_selected_dict[poll.id] = answers_selected

    context['q_in_p_dict'] = q_in_p_dict
    context['answers_selected_dict'] = answers_selected_dict

    return render(request, 'statistics.html', context)