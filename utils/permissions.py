from roles.models import Permission



def add_permissions(models,session):
    permissions = []
    actions = ["add", "read", "update", "delete"]
    for model in models:
        for action in actions:
            permissions.append(
                {
                    "name": f"{action}_{model}",
                    "description": f"can {action} {model}"
                }
            )
    session.execute(Permission.__table__.insert(), permissions)  
    session.commit()

      