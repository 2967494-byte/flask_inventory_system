# app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ReviewForm(FlaskForm):
    """Форма для добавления отзыва"""

    rating = SelectField(
        "Оценка",
        choices=[
            (5, "5 ★ - Отлично"),
            (4, "4 ★ - Хорошо"),
            (3, "3 ★ - Удовлетворительно"),
            (2, "2 ★ - Плохо"),
            (1, "1 ★ - Очень плохо"),
        ],
        validators=[DataRequired(message="Выберите оценку")],
        coerce=int,
        default=5,
    )

    text = TextAreaField(
        "Текст отзыва",
        validators=[
            DataRequired(message="Напишите текст отзыва"),
            Length(
                min=10, max=2000, message="Отзыв должен быть от 10 до 2000 символов"
            ),
        ],
        render_kw={
            "rows": 6,
            "placeholder": "Расскажите о вашем опыте взаимодействия с продавцом...",
        },
    )

    product_id = HiddenField("ID товара")

    submit = SubmitField("Отправить отзыв")


class MessageForm(FlaskForm):
    """Форма для отправки сообщения"""

    recipient_id = HiddenField("ID получателя", validators=[DataRequired()])
    subject = StringField(
        "Тема",
        validators=[
            DataRequired(message="Укажите тему сообщения"),
            Length(min=3, max=200, message="Тема должна быть от 3 до 200 символов"),
        ],
        render_kw={"placeholder": "Тема сообщения"},
    )
    body = TextAreaField(
        "Сообщение",
        validators=[
            DataRequired(message="Напишите текст сообщения"),
            Length(
                min=10, max=2000, message="Сообщение должно быть от 10 до 2000 символов"
            ),
        ],
        render_kw={"rows": 8, "placeholder": "Текст вашего сообщения..."},
    )
    product_id = HiddenField("ID товара")  # Опционально, если сообщение касается товара
    submit = SubmitField("Отправить сообщение")


class MessageReplyForm(FlaskForm):
    """Форма для ответа на сообщение"""

    body = TextAreaField(
        "Ответ",
        validators=[
            DataRequired(message="Напишите текст ответа"),
            Length(
                min=10, max=2000, message="Ответ должен быть от 10 до 2000 символов"
            ),
        ],
        render_kw={"rows": 6, "placeholder": "Ваш ответ..."},
    )
    submit = SubmitField("Отправить ответ")
