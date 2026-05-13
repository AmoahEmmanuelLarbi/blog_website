from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DetailView,
    DeleteView,
)

# from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, ProfileEditForm, PostForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Post, Comment
from django.db.models import Q
from taggit.models import Tag

# implement pagination
from django.core.paginator import Paginator

# Create your views here.


# creating view for new to signup
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "account/register.html"
    success_url = reverse_lazy("login")  # redirection page


# view for profile management
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "account/profile.html"


class ProfileEditView(LoginRequiredMixin, UpdateView):
    # User = get_user_model()  # get current user model
    form_class = ProfileEditForm
    template_name = "account/profile_edit.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        return self.request.user


# create a new post
class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "blog/post_create.html"
    success_url = reverse_lazy("posts")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


# function based view to show all post
def show_all_post(request):
    posts = Post.objects.all()

    # get search query from imput
    query = request.GET.get("query")
    tag = request.GET.get("tag")

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).distinct()

    if tag:
        posts = posts.filter(tags__slug=tag)

    # get all tags and use for filtering
    all_tags = Tag.objects.order_by("?")[:5]  # get 5 ramdom tags

    # pagination
    paginator = Paginator(object_list=posts, per_page=10)
    total_pages = paginator.num_pages
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    current_page_number = page_obj.number

    context = {
        "posts": page_obj,
        "total_pages": total_pages,
        "current_page_number": current_page_number,
        "random_tags": all_tags,
    }

    return render(request, "blog/post_list.html", context)


# details view of each post
class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"


# view to update post
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_create.html"
    success_url = reverse_lazy("posts")

    # only authors of post can edit the post
    def test_func(self):
        obj = self.get_object()
        print(obj)
        return obj.author == self.request.user


# view to delete post
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("posts")
    template_name = "blog/post_confirm_delete.html"
    context_object_name = "post"

    # only authors of post can edit the post
    def test_func(self):
        obj = self.get_object()
        print(obj)
        return obj.author == self.request.user


# views to handle CRUD operations for comments
@login_required
def post_comments(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post)
    # pk = request.GET.get("post.pk")
    # print(pk)

    context = {"post": post, "comments": comments}

    return render(request, "comment/comment_list.html", context)


# create view for comments
@login_required
def create_comment(request, pk):
    # first get a post
    post = get_object_or_404(Post, pk=pk)

    # create a comment
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("posts")

    else:
        form = CommentForm()

    return render(request, "comment/comment_form.html", {"form": form, "post": post})


# update view for comment
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment/comment_form.html"

    # only authors of comment can edit the comment
    def test_func(self):
        obj = self.get_object()
        print(obj)
        return obj.author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object.post
        return context

    def get_success_url(self):
        print(self.object.post.pk)
        return reverse_lazy("comments", kwargs={"pk": self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "comment/comment_confirm_delete.html"
    context_object_name = "comment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object().post

    # only authors of comment can delete the post
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    # success url
    def get_success_url(self):
        return reverse_lazy("comments", kwargs={"pk": self.object.post.pk})


# view to show tagged post
class PostByTagListView(LoginRequiredMixin, ListView):
    model = Post
    paginate_by = 10
    template_name = "blog/tag_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.tag_slug = self.kwargs.get("tag_slug")
        queryset = Post.objects.filter(tags__slug__iexact=self.tag_slug).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["tag"] = get_object_or_404(Tag, slug__iexact=self.tag_slug)
        return context
