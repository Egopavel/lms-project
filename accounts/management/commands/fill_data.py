import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import CustomUser
from courses.models import Course
from tests.models import Test, Question, Answer, TestResult, StudentProfile

class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Начинаем заполнение базы...')

        # 1. Создаем пользователей
        self.stdout.write('👥 Создание пользователей...')
        students = []
        for i in range(1, 6):
            user, created = CustomUser.objects.get_or_create(
                username=f'student{i}',
                defaults={
                    'email': f'student{i}@sao.ru',
                    'role': 'student',
                    'first_name': f'Студент',
                    'last_name': f'№{i}',
                    'department': 'Аспирантура'
                }
            )
            if created:
                user.set_password('12345')
                user.save()
                StudentProfile.objects.create(user=user, group=f'GR-202{i}')
            students.append(user)

        # 2. Создаем курсы
        self.stdout.write('📚 Создание курсов...')
        c1, _ = Course.objects.get_or_create(
            title='Основы астрофизики',
            defaults={'description': 'Вводный курс для аспирантов.', 'status': 'published'}
        )
        c2, _ = Course.objects.get_or_create(
            title='Обработка данных радиотелескопа',
            defaults={'description': 'Практический курс по работе с RAW данными.', 'status': 'published'}
        )

        # 3. Создаем тесты и вопросы
        self.stdout.write('📝 Создание тестов...')
        
        # Тест для Курса 1
        t1, _ = Test.objects.get_or_create(
            title='Итоговый тест: Астрофизика',
            course=c1,
            defaults={'time_limit': 20, 'passing_score': 70, 'max_attempts': 3}
        )
        
        # Вопросы для Теста 1
        self.create_questions(t1, [
            ('Что такое парсек?', [('Единица длины', True), ('Единица времени', False), ('Название звезды', False)]),
            ('Самая большая структура во Вселенной?', [('Сверхскопление галактик', True), ('Черная дыра', False), ('Туманность', False)]),
        ])

        # Тест для Курса 2
        t2, _ = Test.objects.get_or_create(
            title='Тест: Сигналы и Шумы',
            course=c2,
            defaults={'time_limit': 15, 'passing_score': 80, 'max_attempts': 2}
        )

        # Вопросы для Теста 2
        self.create_questions(t2, [
            ('Что такое отношение сигнал/шум (SNR)?', [('Мощность сигнала к мощности шума', True), ('Частота сигнала', False)]),
            ('В какой полосе работает RATAN-600?', [('Сантиметровой', True), ('Рентгеновской', False)]),
        ])

        # 4. Генерируем результаты (чтобы преподавателю было что смотреть)
        self.stdout.write('📊 Генерация результатов тестов...')
        for student in students:
            # 70% студентов сдали тест 1
            if random.choice([True, True, True, False]): 
                TestResult.objects.create(
                    test=t1, student=student, score=85, max_score=100, passed=True, attempt_number=1
                )
            else:
                TestResult.objects.create(
                    test=t1, student=student, score=40, max_score=100, passed=False, attempt_number=1
                )

        self.stdout.write(self.style.SUCCESS('✅ Готово! База заполнена.'))
        self.stdout.write('Логин студента: student1, пароль: 12345')

    def create_questions(self, test, questions_data):
        for q_text, answers in questions_data:
            q = Question.objects.create(test=test, text=q_text, question_type='single', points=10)
            for a_text, is_correct in answers:
                Answer.objects.create(question=q, text=a_text, is_correct=is_correct)