# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed

class ReviewForm(FlaskForm):
    """Форма для добавления отзыва"""
    rating = SelectField(
        'Оценка',
        choices=[
            (5, '5 ★ - Отлично'),
            (4, '4 ★ - Хорошо'), 
            (3, '3 ★ - Удовлетворительно'),
            (2, '2 ★ - Плохо'),
            (1, '1 ★ - Очень плохо')
        ],
        validators=[DataRequired(message='Выберите оценку')],
        coerce=int,
        default=5
    )
    
    text = TextAreaField(
        'Текст отзыва',
        validators=[
            DataRequired(message='Напишите текст отзыва'),
            Length(min=10, max=2000, message='Отзыв должен быть от 10 до 2000 символов')
        ],
        render_kw={
            'rows': 6,
            'placeholder': 'Расскажите о вашем опыте взаимодействия с продавцом...'
        }
    )
    
    product_id = HiddenField('ID товара')
    
    submit = SubmitField('Отправить отзыв')