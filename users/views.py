from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages

from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm


class LoginUser(LoginView):
    """
    View for user login.

    Presents a form for user login.
    """
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Вход в в профиль пользователя'}


class RegisterUser(CreateView):
    """
    View for registering a new user.

    Presents a form for registering a new user. On successful registration, redirects
    to the login page.

    Attributes:
        form_class (Form): The form class for user registration.
        template_name (str): The name of the template to render.
        extra_context (dict): Extra context data to pass to the template.
        success_url (str): The URL to redirect to after successful registration.
    """
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация  пользователя'}
    success_url = reverse_lazy('users:login')


class ProfileUser(LoginRequiredMixin, UpdateView):
    """
    View for updating user profile information.

    Presents a form for updating user profile information. Only accessible to logged-in users.
    """
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль пользователя'}

    def get_success_url(self):
        return reverse('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Ваши данные были успешно обновлены!')
        return super().form_valid(form)


class UserPasswordChange(PasswordChangeView):
    """
    View for changing user password.

    Presents a form for changing the user password.
    """
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
    extra_context = {'title': "Изменение пароля"}
