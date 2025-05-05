document.addEventListener('DOMContentLoaded', function() {
    // Obtém referências para o formulário de filtro/ordenação e o container de reviews
    const filterSortForm = document.querySelector('.interactivity-area form');
    const reviewsContainer = document.getElementById('reviews-container');

    // Verifica se os elementos essenciais existem na página
    if (!filterSortForm || !reviewsContainer) {
        console.error('JS Error: Formulário de filtro/ordenação ou container de reviews (#reviews-container) não encontrado.');
        return; // Sai se algo estiver faltando
    }

    // --- Função Principal para Buscar e Atualizar Reviews ---
    // Esta função será chamada tanto na submissão do formulário quanto no clique da paginação
    function fetchReviews(eventOrUrl) {
        let fetchUrl;

        // Determina a URL da requisição:
        // Se um evento de formulário foi passado, constrói a URL com base nos dados do formulário.
        // Se uma string de URL foi passada (dos links de paginação), usa essa URL.
        if (eventOrUrl instanceof Event) {
            eventOrUrl.preventDefault(); // Previne o comportamento padrão (recarregar a página)
            const formAction = filterSortForm.getAttribute('action');
            const formData = new FormData(filterSortForm);
            const searchParams = new URLSearchParams(formData).toString();
            fetchUrl = `${formAction}?${searchParams}`;
             // Opcional: Atualiza a URL no histórico do navegador sem recarregar (HTML5 History API)
             // window.history.pushState({ path: fetchUrl }, '', fetchUrl); // Pode causar problemas com paginação, use com cuidado
        } else if (typeof eventOrUrl === 'string') {
            fetchUrl = eventOrUrl; // É uma URL de paginação
             // Opcional: Atualiza a URL no histórico do navegador
             // window.history.pushState({ path: fetchUrl }, '', fetchUrl); // Pode causar problemas com submissão de form posterior
        } else {
             console.error("JS Error: Parâmetro inválido para fetchReviews:", eventOrUrl);
             return; // Sai se o parâmetro for inválido
        }

        // Adiciona um indicador visual de carregamento na área de reviews
        reviewsContainer.innerHTML = '<div class="loading-indicator"><i class="fas fa-spinner fa-spin fa-2x"></i> Carregando reviews...</div>';

        // Faz a requisição AJAX usando a Fetch API
        fetch(fetchUrl, {
            method: 'GET', // Requisições de filtro/ordenação/paginação são GET
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // Header para identificar como requisição AJAX no Django
            }
        })
        .then(response => {
            // Verifica se a resposta HTTP foi bem-sucedida (status 2xx)
            if (!response.ok) {
                console.error('Erro na requisição:', response.status, response.statusText);
                 // Exibe uma mensagem de erro na área de reviews
                reviewsContainer.innerHTML = '<p class="error-message"><i class="fas fa-exclamation-triangle"></i> Erro ao carregar reviews.</p>';
                throw new Error('Network response was not ok'); // Lança erro para ir para o catch
            }
            // Espera que a resposta seja JSON (conforme configurado na view)
            return response.json();
        })
        .then(data => {
            // Verifica se os dados recebidos contêm a chave 'html' (conforme configurado na view)
            if (data && data.html !== undefined) {
                // Substitui o conteúdo atual do container de reviews pelo HTML recebido
                reviewsContainer.innerHTML = data.html;
                // IMPORTANTE: Reanexa os listeners aos NOVOS links de paginação
                attachPaginationListeners();
            } else {
                 console.error('Resposta AJAX não contém HTML válido ou no formato esperado:', data);
                 // Exibe uma mensagem de erro se a resposta não estiver no formato esperado
                 reviewsContainer.innerHTML = '<p class="error-message"><i class="fas fa-exclamation-triangle"></i> Resposta inesperada do servidor.</p>';
            }
        })
        .catch(error => {
            console.error('Erro na operação fetch:', error);
             // O erro de rede já foi tratado no .then, mas este catch pega outros erros
             // Exibe uma mensagem de erro genérica se não foi tratada antes
             if (!reviewsContainer.querySelector('.error-message')) { // Evita duplicar a mensagem se já foi exibida
                  reviewsContainer.innerHTML = '<p class="error-message"><i class="fas fa-exclamation-triangle"></i> Ocorreu um erro na requisição.</p>';
             }
        });
    }

    // --- Função para Anexar Listeners aos Links de Paginação ---
    // Esta função precisa ser chamada:
    // 1. No carregamento inicial da página (para links renderizados pelo Django)
    // 2. Após CADA atualização bem-sucedida do reviewsContainer via AJAX
    function attachPaginationListeners() {
        // Encontra todos os links de paginação *dentro do container de reviews*
        const paginationLinks = reviewsContainer.querySelectorAll('.pagination a');

        paginationLinks.forEach(link => {
            // Adiciona um listener de clique a cada link de paginação
            link.addEventListener('click', function(event) {
                event.preventDefault(); // Previne o comportamento padrão do link (recarregar)
                const pageUrl = this.getAttribute('href'); // Obtém a URL do link (ex: ?page=2&ordenar=...)
                fetchReviews(pageUrl); // Chama a função principal passando a URL para buscar
            });
        });
    }

    // --- Event Listeners Iniciais ---

    // 1. Anexa o listener à submissão do formulário de filtro/ordenação
    // Quando o usuário clica no botão "Aplicar" (ou pressiona Enter no form)
    filterSortForm.addEventListener('submit', fetchReviews);

    // 2. Anexa os listeners aos links de paginação que estão presentes
    // na página quando ela carrega inicialmente (renderizada pelo Django)
    attachPaginationListeners();

    // Opcional: Disparar a busca AJAX imediatamente quando filtros/ordenação mudam (sem precisar clicar em Aplicar)
    // Isso pode ser mais responsivo, mas envia requisições a cada mudança.
    // Se ativado, o botão "Aplicar" pode ser mantido apenas como um indicador visual ou removido.
    // const filterSortSelects = filterSortForm.querySelectorAll('select');
    // filterSortSelects.forEach(select => {
    //     select.addEventListener('change', function() {
    //         // Dispara a submissão do formulário programaticamente
    //         filterSortForm.dispatchEvent(new Event('submit')); // Simula o evento 'submit'
    //         // Ou filterSortForm.requestSubmit(); // API mais moderna, verifica input válido
    //         // Ou fetchReviews(); // Chama a função diretamente (mas não garante que o form está submetido)
    //     });
    // });

});