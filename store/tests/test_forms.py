import pytest
from django.contrib.auth.models import User
from store.forms import RegisterForm


@pytest.mark.django_db
class TestRegisterForm:
    def _valid_data(self, **kwargs):
        data = {
            'username': 'formuser',
            'email': 'formuser@example.com',
            'password1': 'SuperSecret99!',
            'password2': 'SuperSecret99!',
        }
        data.update(kwargs)
        return data
    
    def test_valid_form(self):
        form = RegisterForm(data=self._valid_data())
        assert form.is_valid()
    
    def test_duplicate_email_is_invalid(self):
        User.objects.create_user(username="existing", email="dup@example.com", password="pass")
        form = RegisterForm(data=self._valid_data(username="newuser", email="dup@example.com"))
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_mismatched_passwords_invalid(self):
        form = RegisterForm(data=self._valid_data(password2="WrongPassword!"))
        assert not form.is_valid()
    
    def test_missing_email_invalid(self):
        form = RegisterForm(data=self._valid_data(email=""))
        assert not form.is_valid()
        assert 'email' in form.errors