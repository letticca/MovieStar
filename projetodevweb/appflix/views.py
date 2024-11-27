import requests
from django.shortcuts import render, get_object_or_404, redirect
from .models import Filme, Review
from .forms import CustomUserCreationForm, EditProfileForm, ReviewForm
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q
from colorthief import ColorThief
from io import BytesIO
from django.contrib import messages
from django.http import JsonResponse
from .forms import ReviewForm



@login_required
def home(request):
    query = request.GET.get('q')  # captura o termo de busca
    if query:
        filmes = buscar_filmes_por_titulo(query)  # busca por título
        mensagem = "Filme encontrado"  # mensagem para quando há pesquisa
    else:
        filmes = buscar_filmes_recente()  # busca os filmes mais recentes, ordenados por data de lançamento
        mensagem = "Filmes recentes"  # mensagem padrão

    return render(request, 'index.html', {'filmes': filmes, 'mensagem': mensagem})

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')  # redireciona para a página inicial ou outra página
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'editar_perfil.html', {'form': form})

@login_required
def adicionar_review(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.usuario = request.user  # Associa o usuário atual
            review.filme = filme           # Associa o filme especificado
            review.save()
            messages.success(request, 'Review adicionada com sucesso!')
            return redirect('detalhes_filme', filme_id=filme.id)
        else:
            # Aqui, imprime os erros para facilitar o diagnóstico
            print(form.errors)
            messages.error(request, 'Erro ao adicionar a review. Verifique os dados e tente novamente.')
    else:
        form = ReviewForm()

    return render(request, 'adicionar_review.html', {'form': form, 'filme': filme})


@login_required
def minhas_reviews(request):
    # # filtra reviews feitas pelo usuário atual
    # reviews = Review.objects.filter(usuario=request.user)
    # return render(request, 'minhas_reviews.html', {'reviews': reviews})

    reviews = Review.objects.filter(usuario=request.user)
    form = ReviewForm()  # Cria um novo formulário para a review
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            nova_review = form.save(commit=False)
            nova_review.usuario = request.user  # Associar a review ao usuário
            nova_review.save()
            return redirect('minhas_reviews')  # Redireciona para a página de reviews

    return render(request, 'minhas_reviews.html', {'reviews': reviews, 'form': form})

def buscar_filmes_recente():
    API_KEY = '32d259ae80e552537d5a35d756ffd875'  
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=pt-BR&page=1'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        filmes = data.get('results', [])
        
        # ordena os filmes pela data de lançamento
        for filme in filmes:
            try:
                # converte do formato YYYY-MM-DD para datetime para ordenação
                release_date_str = filme.get('release_date', '')
                if release_date_str:
                    # converte para o formato DD/MM/YYYY para exibir
                    filme['release_year'] = datetime.strptime(release_date_str, '%Y-%m-%d').year
                    filme['Released'] = datetime.strptime(release_date_str, '%Y-%m-%d')
                else:
                    filme['Released'] = None
            except ValueError:
                filme['Released'] = None
        
        # ordenar os filmes com base na data de lançamento
        filmes_ordenados = sorted(filmes, key=lambda x: (x['Released'] is not None, x['Released']), reverse=True)
        
        return filmes_ordenados
    return []

def detalhes_filme(request, filme_id):
    API_KEY = '32d259ae80e552537d5a35d756ffd875'
    base_url = 'https://api.themoviedb.org/3'

    filme_url = f'{base_url}/movie/{filme_id}?api_key={API_KEY}&language=pt-BR'
    response = requests.get(filme_url)
    
    if response.status_code == 200:
        filme_info = response.json()

        poster_url = f"https://image.tmdb.org/t/p/w500{filme_info.get('poster_path', '')}"
        poster_response = requests.get(poster_url)

        dominant_color_hex = '#000000'
        contrast_class = ''

        if poster_response.status_code == 200:
            color_thief = ColorThief(BytesIO(poster_response.content))
            try:
                dominant_color = color_thief.get_color(quality=1)
                dominant_color_hex = '#%02x%02x%02x' % dominant_color
                dominant_color_hex = ajustar_contraste(dominant_color_hex)
                if dominant_color_hex == '#000000':
                    contrast_class = 'review-btn-high-contrast'
            except Exception as e:
                print(f"Erro ao extrair a cor: {e}")
        
        video_url = f'{base_url}/movie/{filme_id}/videos?api_key={API_KEY}&language=pt-BR'
        video_response = requests.get(video_url)
        video_info = video_response.json()

        trailers = [video for video in video_info.get('results', []) if video['site'] == 'YouTube' and video['type'] == 'Trailer']
        trailer_key = trailers[0]['key'] if trailers else None

        # verifica se `release_date` está presente e extrai apenas o ano
        release_date = filme_info.get('release_date')
        if release_date:
            release_year = datetime.strptime(release_date, '%Y-%m-%d').year
        else:
            release_year = "Ano não disponível"

        # prepara o contexto a ser enviado para o template
        contexto = {
            'filme': {
                'id': filme_info['id'],
                'title': filme_info['title'],
                'overview': filme_info['overview'],
                'release_year': release_year,  # apenas o ano
                'poster_path': filme_info.get('poster_path', ''),
                'backdrop_path': filme_info.get('backdrop_path', ''),
                'trailer_key': trailer_key
            },
            'dominant_color': dominant_color_hex,
            'contrast_class': contrast_class,
            'form': ReviewForm()  # Adiciona o formulário aqui
            }

        return render(request, 'detalhes_filme.html', contexto)
    
    return render(request, '404.html', status=404)



def ajustar_cor_solida(cor_hex):
    if cor_hex == 'transparent' or not cor_hex:
        return '#333333'  # retorna um cinza escuro como fallback
    return cor_hex

def ajustar_contraste(cor_hex):
    cor_hex = ajustar_cor_solida(cor_hex)  # certifique-se de que a cor não seja transparente
    r, g, b = int(cor_hex[1:3], 16), int(cor_hex[3:5], 16), int(cor_hex[5:7], 16)
    
    luminosidade = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    if luminosidade > 0.7:
        return '#333333'
    return cor_hex

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redireciona para login após registro bem-sucedido
        else:
            return render(request, 'register.html', {'form': form})  # renderiza o template de registro com erros
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})  # inicialmente, renderiza o formulário vazio




def buscar_filmes_por_titulo(titulo):
    API_KEY = '32d259ae80e552537d5a35d756ffd875'
    url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=pt-BR&query={titulo}&page=1'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        filmes = data.get('results', [])
        
        # extração do ano de lançamento
        for filme in filmes:
            release_date_str = filme.get('release_date', '')
            if release_date_str:
                filme['release_year'] = datetime.strptime(release_date_str, '%Y-%m-%d').year
            else:
                filme['release_year'] = None
        
        return filmes
    return []


def buscar_e_salvar_filme(filme_id):
    API_KEY = '32d259ae80e552537d5a35d756ffd875' 
    url = f'https://api.themoviedb.org/3/movie/{filme_id}?api_key={API_KEY}&language=pt-BR'
    response = requests.get(url)
    
    if response.status_code == 200:
        filme_info = response.json()
        data_lancamento_str = filme_info.get('release_date', None)

        if data_lancamento_str:
            try:
                # converte para o formato DD/MM/YYYY para exibição e manter para ordenação
                data_lancamento = datetime.strptime(data_lancamento_str, '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                data_lancamento = None  
        else:
            data_lancamento = None

        if not Filme.objects.filter(id=filme_id).exists():
            novo_filme = Filme(
                titulo=filme_info['title'],
                descricao=filme_info['overview'],
                data_lancamento=data_lancamento,
                id=filme_info['id'], 
                poster=filme_info.get('poster_path', '') 
            )
            novo_filme.save()
            return novo_filme
    return None
