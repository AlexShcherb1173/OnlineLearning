from django.contrib.auth.models import User, Group

u = User.objects.get(email="user@example.com")
g = Group.objects.get(name="Контент-менеджер")
u.groups.add(g)
