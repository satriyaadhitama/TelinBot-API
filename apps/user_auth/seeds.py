from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


def seed_superuser():
    User = get_user_model()
    email = "admin@email.com"
    if not User.objects.filter(email=email).exists():
        superuser = User.objects.create_superuser(
            first_name="Jack",
            last_name="Dawson",
            email=email,
            phone_number="+628144023168",
            password="123",
            position="Administrator",
        )
        group = Group.objects.get(name="Admin")
        # Add the user to the group.
        superuser.groups.add(group)


def seed_groups():
    User = get_user_model()
    groups = [
        {
            "name": "Admin",
            "permissions": [
                {
                    "name": "user",
                    "actions": ["add", "change", "delete", "view"],
                    "model": User,
                },
                {
                    "name": "outstandingtoken",
                    "actions": ["add", "change", "delete", "view"],
                    "model": OutstandingToken,
                },
                {
                    "name": "blacklistedtoken",
                    "actions": ["add", "change", "delete", "view"],
                    "model": BlacklistedToken,
                },
            ],
        },
        {
            "name": "Employee",
            "permissions": [],
        },
    ]

    for group in groups:
        group_name = group["name"]
        permissions = group["permissions"]

        # Create new group
        group, _ = Group.objects.get_or_create(name=group_name)

        if len(permissions) > 0:
            for permission in permissions:
                perm_name = permission["name"]
                model = permission["model"]
                actions = permission["actions"]

                content_type = ContentType.objects.get_for_model(model)
                available_permissions = []
                # Check all available permissions for each groups
                for action in actions:
                    codename = action + "_" + perm_name
                    action_permitted = Permission.objects.get(
                        codename=codename, content_type=content_type
                    )
                    available_permissions.append(action_permitted)
                # Add all permissions to group
                group.permissions.add(*available_permissions)


def seed_users():
    users = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@email.com",
            "phone_number": "+6285867235034",
            "position": "Frontend Developer",
            "password": "123",
            "group": "Employee",
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@email.com",
            "phone_number": "+628300394259",
            "position": "Data Analyst",
            "password": "123",
            "group": "Employee",
        },
    ]

    User = get_user_model()
    for user in users:
        if not User.objects.filter(email=user["email"]).exists():
            new_user = User.objects.create_user(
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                phone_number=user["phone_number"],
                password=user["password"],
                position=user["position"],
            )
            # Adding group to user
            group = Group.objects.get(name=user["group"])
            new_user.groups.add(group)
