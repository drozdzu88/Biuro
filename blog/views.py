from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.db.models import Count

from .models import Post, Comment 
from .forms import EmailPostForm, CommentForm

from taggit.models import Tag 

# Create your views here

def post_list(request, tag_slug=None):
	object_list = Post.published.all()
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		object_list = object_list.filter(tags__in=[tag])
	paginator = Paginator(object_list, 3) #Trzy posty na każdą stronę
	page = request.GET.get('page')
	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		posts = paginator.page(1)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)
	content = {
		'page': page,
		'posts': posts,
		'tag': tag,
	}
	return render(request, 'blog/post/list.html', content)

def post_detail(request, year, month, day, post):
	post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
	#Lista aktywnych komentarzy dla danego posta
	comments = post.comments.filter(active=True)
	if request.method =='POST':
		#Komentarz został opublikowany
		comment_form = CommentForm(data=request.POST)
		if comment_form.is_valid():
			#Utworzenie obiektu Comment, nie zapisany jeszcze w bazie
			new_comment = comment_form.save(commit=False)
			#Przypisanie komentarza do bieżącego posta
			new_comment.post = post
			#Zapisanie komentarza w bazie danych
			new_comment.save()
	else:
		comment_form = CommentForm()
	
	post_tags_ids = post.tags.values_list('id', flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
	
	content = {
		'post': post,
		'comments': comments,
		'comment_form': comment_form,
		'similar_posts': similar_posts,
		}

	return render (request, 'blog/post/detail.html', content)

class PostListView(ListView):
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'blog/post/list.html'

def post_share(request, post_id):
	#Pobieranie posta na podstawie jego identyfikatora
	post = get_object_or_404(Post, id=post_id, status='published')
	sent = False

	if request.method == 'POST':
		#Formularz został wysłany
		form  = EmailPostForm(request.POST)
		if form.is_valid():
			#Weryfikacja pół formularza zakończyła się powodzeniem...
			cd = form.cleaned_data
			post_url = request.build_absolute_uri(post.get_absolute_url())
			subject ='{} ({}) zachęca do przeczytania "{}"'.format(cd['name'], cd['email'], post.title)
			message = 'Przeczytaj post "{}" na stronie {}\n\n Komentarz dodany przez {}:{}'.format(post.title, post_url, cd['name'], cd['comments'])
			send_mail(subject, message, 'bp.lukaszdrozd@gmail.com', [cd['to']])
			sent=True
	else:
		form = EmailPostForm()
	content = {
		'post': post,
		'form': form,
		'sent': sent
	}

	return render(request, 'blog/post/share.html', content)

