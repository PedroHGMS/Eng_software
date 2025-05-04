from django.test import TestCase
from universities.models import Professor, Universidade, Disciplina


class UniversidadeModelTest(TestCase):
    def test_create_universidade(self):
        uni = Universidade.objects.create(nome="UFOP")
        self.assertEqual(str(uni), "UFOP")


class ProfessorModelTest(TestCase):
    def setUp(self):
        self.uni = Universidade.objects.create(nome="UFMG")

    def test_create_professor_without_university(self):
        prof = Professor.objects.create(name="Dr. Smith", departamento="Matemática")
        self.assertEqual(str(prof), "Dr. Smith")
        self.assertIsNone(prof.universidade)

    def test_create_professor_with_university(self):
        prof = Professor.objects.create(name="Dr. Alice", universidade=self.uni)
        self.assertEqual(prof.universidade.nome, "UFMG")


class DisciplinaModelTest(TestCase):
    def setUp(self):
        self.uni1 = Universidade.objects.create(nome="USP")
        self.uni2 = Universidade.objects.create(nome="UNICAMP")

    def test_create_disciplina(self):
        disc = Disciplina.objects.create(nome="Física", carga_horaria=60)
        self.assertEqual(str(disc), "Física")
        self.assertEqual(disc.carga_horaria, 60)

    def test_add_universidades_to_disciplina(self):
        disc = Disciplina.objects.create(nome="Matemática", carga_horaria=90)
        disc.universidades.set([self.uni1, self.uni2])  # ManyToMany requires set/add
        self.assertEqual(disc.universidades.count(), 2)
        self.assertIn(self.uni1, disc.universidades.all())
        self.assertIn(self.uni2, disc.universidades.all())
