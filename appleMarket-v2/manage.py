#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# [시스템 설정] AI 라이브러리 간 OpenMP 중복 로드 에러(Error #15) 방지용 코드
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True' 

def main():
# [추가] OpenMP 중복 로드 허용 설정 (이 두 줄을 추가하세요!)

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()