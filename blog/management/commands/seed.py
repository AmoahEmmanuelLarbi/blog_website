from django.core.management.base import BaseCommand
from blog.models import Post, Comment
from django.contrib.auth import get_user_model
from faker import Faker
import random

fake = Faker()

TECH_TOPICS = [
    "Artificial Intelligence breakthrough",
    "OpenAI releases new model",
    "Cybersecurity vulnerability discovered",
    "New Python framework trending",
    "Cloud computing innovation",
    "Startup raises millions in funding",
    "Quantum computing milestone",
    "Tech layoffs in big companies",
    "Blockchain adoption grows",
    "New mobile app goes viral",
]

COMMENTS = [
    "This is really interesting!",
    "I saw this coming honestly.",
    "Tech is evolving so fast.",
    "Can someone explain this in simple terms?",
    "This will change everything.",
    "I’m not sure how I feel about this.",
    "Big implications for developers.",
    "This is scary but exciting.",
    "I need to read more about this.",
    "Wow, didn’t expect this news.",
]


class Command(BaseCommand):
    help = "Seed database with fake tech news posts and comments"

    def handle(self, *args, **kwargs):
        # user model
        User = get_user_model()

        user = User.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR("No user found. Create a user first."))
            return

        posts = []

        # 🔹 Create 30 posts
        for i in range(30):
            title = f"{random.choice(TECH_TOPICS)}: {fake.catch_phrase()}"
            content = "\n\n".join(fake.paragraphs(nb=3))

            post = Post.objects.create(title=title, content=content, author=user)

            posts.append(post)

        # 🔹 Create 50 comments
        for i in range(50):
            Comment.objects.create(
                post=random.choice(posts), author=user, content=random.choice(COMMENTS)
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded tech news data!"))
