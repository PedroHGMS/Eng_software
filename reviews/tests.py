from django.test import TestCase
from django.contrib.auth.models import User
from universities.models import Professor, Disciplina
from reviews.models import Review
from django.urls import reverse


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.professor = Professor.objects.create(name="Prof. Xavier")
        self.disciplina = Disciplina.objects.create(nome="Mutant Ethics", carga_horaria=60)

    def test_create_valid_review(self):
        review = Review.objects.create(
            dificuldade=3,
            qualidade=4,
            descricao="Very detailed explanations",
            nota_obtida=95,
            presenca=True,
            periodo="2023/2",  # valid
            professor=self.professor,
            disciplina=self.disciplina,
            usuario=self.user
        )
        self.assertEqual(str(review), f"Review de {self.user} para {self.professor} em {self.disciplina}")

    def test_invalid_periodo_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        review = Review(
            dificuldade=3,
            qualidade=4,
            descricao="Test",
            nota_obtida=85,
            presenca=True,
            periodo="2023-X",  # invalid
            professor=self.professor,
            disciplina=self.disciplina,
            usuario=self.user
        )
        with self.assertRaises(ValidationError):
            review.full_clean()  # This will check if the validation works for invalid 'periodo'


class AllReviewsViewTest(TestCase):
    def test_all_reviews_status_code(self):
        response = self.client.get(reverse("reviews:all_reviews"))  # Ensure your `urls.py` has the name="all_reviews"
        self.assertEqual(response.status_code, 200)
