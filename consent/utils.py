import hashlib


def compute_file_hash(file_path):
    digest = hashlib.sha256()
    with open(file_path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(8192), b''):
            digest.update(chunk)
    return digest.hexdigest()


def is_student_user(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return False
    return True
