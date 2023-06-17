from functools import wraps


def validate_json(*expected_args):
    print(expected_args)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            json_object = {}
            for expected_arg in expected_args:
                if expected_arg not in json_object:
                    print(400)
            return func(*args, **kwargs)
        return wrapper
    return decorator


@validate_json('student_id')
def update_grade():
    json_data = {

    }
    print(json_data)
    # update database
    return "success!"

update_grade()