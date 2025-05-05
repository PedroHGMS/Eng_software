// static/reviews/make_review.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('review-form');
    if (!form) {
        console.error('JS Error: Formulário (#review-form) não encontrado.');
        return;
    }

    const submitButton = form.querySelector('.submit-btn');
    const formMessages = document.getElementById('form-messages');

    // --- Helper Functions ---

    // Função para exibir mensagens (sucesso ou erro global)
    function displayMessage(message, type) {
        formMessages.textContent = message;
        // Remove classes de estado anteriores e adiciona a nova
        formMessages.classList.remove('success', 'error');
        formMessages.classList.add(type); // Adiciona a classe 'success' ou 'error'
        formMessages.style.display = 'block'; // Garante que a div está visível
        // Opcional: Rolar para a mensagem para garantir que o usuário a veja
        formMessages.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Função para limpar mensagens e erros de campo
    function clearMessages() {
        // Limpa mensagem global
        formMessages.textContent = '';
        formMessages.classList.remove('success', 'error'); // Remove classes de estado
        formMessages.style.display = 'none'; // Oculta a div

        // Limpa todos os erros de campo e remove classes visuais de erro
        form.querySelectorAll('.errorlist').forEach(ul => ul.innerHTML = ''); // Limpa o conteúdo das listas de erro
        // Remove a classe 'is-invalid' de todos os elementos que podem tê-la
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

        // Garante que os ratings visuais resetem para vazio (0)
        form.querySelectorAll('.rating-widget').forEach(widget => {
             const widgetInput = form.querySelector(`[name="${widget.dataset.fieldName}"]`);
             // Se o input resetar para vazio ou 0, atualiza o visual
             if (widgetInput && (!widgetInput.value || parseInt(widgetInput.value, 10) <= 0)) {
                  updateVisualRating(widget, 0); // Reseta o visual para 0 estrelas/círculos
             }
        });
         // Garante que o toggle visual reset para off
        const presencaCheckbox = form.querySelector('input[name="presenca"]');
        if (presencaCheckbox) {
             // O form.reset() já desmarca o checkbox. Se ele estiver desmarcado, o listener de 'change'
             // no próprio checkbox já deve cuidar do visual via CSS.
             // Nada mais precisa ser feito aqui, apenas garantir que o checkbox *está* desmarcado após reset.
        }
    }


    // Função para exibir erros de validação de campo
    // errors é um dicionário { field_name: ["Erro 1", "Erro 2"], ... }
    function displayFieldErrors(errors) {
        // Limpa erros anteriores antes de exibir os novos
        // Cuidado para não limpar a mensagem GLOBAL de 'corrija os erros'
        form.querySelectorAll('.errorlist').forEach(ul => ul.innerHTML = '');
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

        let firstInvalidField = null; // Para focar/rolar para o primeiro campo com erro

        // Itera sobre os erros recebidos do Django
        for (const fieldName in errors) {
            if (errors.hasOwnProperty(fieldName)) { // Garante que é uma propriedade própria
                const errorList = errors[fieldName]; // Array de strings de erro para este campo

                // Tenta encontrar o campo no DOM pelo nome.
                // Pode ser um input[name], select[name], textarea[name], ou até um input[type="hidden"]
                const fieldInput = form.querySelector(`[name="${fieldName}"]`);

                if (fieldInput) {
                     // Tenta encontrar o UL de erro associado ao campo.
                     // O template usa o ID do campo input/select/textarea + "_errors".
                     const errorUl = document.getElementById(`${fieldInput.id}_errors`);

                     if (errorUl) {
                        // Adiciona os erros à lista UL
                        errorList.forEach(errorText => {
                            const li = document.createElement('li');
                            li.textContent = errorText;
                            errorUl.appendChild(li);
                        });

                        // Adiciona classe de erro visual ao campo ou seu contêiner visual
                        const formGroup = fieldInput.closest('.form-group'); // Encontra o grupo pai

                        if (formGroup) { // Verifica se o campo está dentro de um .form-group
                            if (formGroup.classList.contains('form-group-rating')) { // Se for um grupo de rating
                                 const ratingWidget = formGroup.querySelector('.rating-widget');
                                 if (ratingWidget) {
                                     ratingWidget.classList.add('is-invalid');
                                     // O primeiro campo inválido para rolar/focar pode ser o widget container
                                     if (!firstInvalidField) firstInvalidField = ratingWidget;
                                 }
                            } else if (formGroup.classList.contains('form-group-toggle')) { // Se for um grupo de toggle
                                 formGroup.classList.add('is-invalid');
                                  // O primeiro campo inválido para rolar/focar pode ser o toggle group
                                 if (!firstInvalidField) firstInvalidField = formGroup;
                            } else {
                                 // Para inputs/selects/textareas padrão, adicione a classe .is-invalid diretamente
                                 fieldInput.classList.add('is-invalid');
                                  // O primeiro campo inválido para rolar/focar é o input/select/textarea
                                 if (!firstInvalidField) firstInvalidField = fieldInput;
                            }
                        } else {
                             // Fallback se o campo não estiver em um .form-group (menos comum)
                             fieldInput.classList.add('is-invalid');
                              if (!firstInvalidField) firstInvalidField = fieldInput;
                        }

                    } else {
                         // Fallback: Se não encontrar o UL de erro específico, logar
                         console.error(`Errolist UL não encontrado para o campo "${fieldName}". ID esperado: "${fieldInput.id}_errors"`);
                         // Ainda marca o campo como inválido visualmente se for um controle padrão
                         if (!fieldInput.closest('.form-group-rating') && !fieldInput.closest('.form-group-toggle')) {
                             fieldInput.classList.add('is-invalid');
                         }
                          if (!firstInvalidField) firstInvalidField = fieldInput; // Ainda tenta rolar/focar nele
                    }
                } else {
                     // Erro para um nome de campo que não existe no formulário DOM (menos comum, ex: non_field_errors)
                     console.error(`Campo DOM não encontrado para o nome: "${fieldName}".`);
                     // Se for 'non_field_errors', você pode exibir em uma div separada,
                     // mas o tratamento atual foca em erros por campo.
                     // A mensagem global "Por favor, corrija os erros" já cobre isso em parte.
                }
            }
        }

        // Opcional: Rolar para o primeiro campo com erro para melhor UX
         if (firstInvalidField) {
             // Use um pequeno delay para dar tempo da interface atualizar
             setTimeout(() => {
                 // Para inputs/selects/textareas, use focus()
                 // Para widgets visuais (container), use scrollIntoView
                 if (firstInvalidField.focus && typeof firstInvalidField.focus === 'function') {
                      firstInvalidField.focus();
                 } else {
                      // Rola para o elemento (pode ser o container do widget)
                      firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                 }
             }, 100);
         }
    }


    // --- Rating Widget Logic (Stars and Circles) ---
    const ratingWidgets = form.querySelectorAll('.rating-widget');

    // Função para atualizar a aparência dos ícones com base em um valor (para estado SELECIONADO)
    // Recebe o widget específico e o valor para atualizar
    function updateVisualRating(widget, value) {
        const icons = widget.querySelectorAll('.star-icon, .circle-icon');
        const iconType = widget.classList.contains('rating-stars') ? 'star' : 'circle';
        const filledFaClass = 'fas'; // Font Awesome Solid
        const emptyFaClass = 'far';  // Font Awesome Regular
        const iconNameClass = `fa-${iconType}`; // ex: fa-star, fa-circle
        const iconClass = `${iconType}-icon`; // Classe customizada: star-icon, circle-icon

        icons.forEach(icon => {
            const rating = parseInt(icon.dataset.rating, 10);

            // Remove classes de estado Font Awesome e customizadas de preenchimento/hover
            icon.classList.remove(emptyFaClass, filledFaClass, 'filled', 'hover-fill');
            // Garante que a classe base do ícone esteja presente (star-icon ou circle-icon)
            icon.classList.add(iconClass);
            // Garante que a classe do nome do ícone esteja presente (fa-star ou fa-circle)
            icon.classList.add(iconNameClass);


            if (rating <= value) {
                // Ícone deve estar preenchido (sólido)
                icon.classList.add(filledFaClass); // Adiciona 'fas'
                icon.classList.add('filled'); // Adiciona a classe customizada 'filled' para CSS de cor
            } else {
                // Ícone deve estar vazio (regular)
                icon.classList.add(emptyFaClass); // Adiciona 'far'
                icon.classList.remove('filled');
            }
        });
    }


    // Inicializa cada widget de rating
    ratingWidgets.forEach(widget => {
        const icons = widget.querySelectorAll('.star-icon, .circle-icon');
        // Encontra o input original associado ao widget pelo atributo data-field-name
        // Deve ser o input hidden ou select real do formulário
        const hiddenInput = form.querySelector(`[name="${widget.dataset.fieldName}"]`);
        const maxRating = parseInt(widget.dataset.maxRating, 10);
        const iconType = widget.classList.contains('rating-stars') ? 'star' : 'circle';
        const iconClass = `${iconType}-icon`; // Classe customizada: star-icon, circle-icon


        // Seta o valor inicial do widget (se o formulário foi renderizado com dados inválidos ou iniciais)
        // Verifica se o input existe e tem um valor numérico válido maior que 0
        // Se o valor for 0 ou menos, trata como não selecionado
        const initialValue = (hiddenInput && hiddenInput.value && !isNaN(parseInt(hiddenInput.value, 10))) ? parseInt(hiddenInput.value, 10) : 0;
        updateVisualRating(widget, initialValue);


        // --- Event Listeners para Hover (Preview) ---
        widget.addEventListener('mouseover', function(e) {
            const hoveredIcon = e.target.closest(`.${iconClass}`);
            if (hoveredIcon) {
                const hoverRating = parseInt(hoveredIcon.dataset.rating, 10);

                // Remove qualquer classe de hover-fill anterior *apenas para este widget*
                icons.forEach(icon => icon.classList.remove('hover-fill'));

                // Adiciona a classe hover-fill ao ícone sob o mouse e todos antes dele
                icons.forEach(icon => {
                    const rating = parseInt(icon.dataset.rating, 10);
                    if (rating <= hoverRating) {
                         icon.classList.add('hover-fill');
                    }
                });
                 // Adiciona classe no container (opcional para CSS)
                 widget.classList.add('hover-preview-active');
            }
        });

        widget.addEventListener('mouseout', function() {
             // Remove classe hover-fill de todos os ícones *apenas para este widget*
             icons.forEach(icon => icon.classList.remove('hover-fill'));
             // Remove classe do container (opcional)
             widget.classList.remove('hover-preview-active');

             // A aparência volta para o estado definido pelas classes 'filled' / 'fas' / 'far'
             // setadas no clique (updateVisualRating)
        });


        // --- Event Listener para Click (Seleção Final) ---
        widget.addEventListener('click', function(e) {
            const clickedIcon = e.target.closest(`.${iconClass}`);
            if (clickedIcon) {
                const clickedRating = parseInt(clickedIcon.dataset.rating, 10);

                // 1. Atualiza o valor do input original (CRUCIAL para submissão)
                if (hiddenInput) {
                     hiddenInput.value = clickedRating;
                     // Dispara um evento 'change' no input original (opcional, pode ser útil para frameworks)
                     // hiddenInput.dispatchEvent(new Event('change')); // Desativado por padrão para simplicidade
                }

                // 2. Atualiza a aparência visual para o estado SELECIONADO permanentemente
                updateVisualRating(widget, clickedRating); // Passa o widget e o valor

                // 3. Remove classe de erro visual do widget e UL de erro ao clicar
                 widget.classList.remove('is-invalid');
                 // Encontra o UL de erro usando o ID do hiddenInput
                 if(hiddenInput) { // Verifica se hiddenInput foi encontrado
                    const errorUl = document.getElementById(`${hiddenInput.id}_errors`);
                    if(errorUl) errorUl.innerHTML = ''; // Limpa o conteúdo da lista de erros
                 }
                 // clearMessages(); // Pode ser agressivo demais limpar mensagem global a cada clique de rating
            }
        });

         // Adiciona listener de foco ao widget container (para acessibilidade e erro visual)
         // Permite que a borda de erro `.is-invalid:focus-within` no container funcione
         widget.setAttribute('tabindex', '0'); // Torna o widget focusable
         widget.addEventListener('focus', function() {
             // Opcional: Ações ao focar o widget
         });
         widget.addEventListener('blur', function() {
             // Opcional: Ações ao perder o foco do widget
              // Remove classes de hover-fill caso o blur ocorra durante um hover (menos comum, mas seguro)
             icons.forEach(icon => icon.classList.remove('hover-fill'));
             widget.classList.remove('hover-preview-active');
         });

    });

    // --- Toggle Widget Logic (Presença) ---
    // Encontra o input checkbox de presença
    const presencaCheckbox = form.querySelector('input[name="presenca"]');
    if (presencaCheckbox) {
        // O CSS com :checked e + label .toggle-switch já manipula o visual
        // O JS só precisa garantir que a classe de erro seja removida ao interagir
        const toggleGroup = presencaCheckbox.closest('.form-group-toggle'); // Encontra o grupo pai

        if (toggleGroup) {
            // Adiciona listener de 'change' ao checkbox nativo
            presencaCheckbox.addEventListener('change', function() {
                 toggleGroup.classList.remove('is-invalid'); // Remove a classe de erro do grupo pai
                 // Encontra o UL de erro usando o ID do checkbox
                 const errorUl = document.getElementById(`${this.id}_errors`);
                 if(errorUl) errorUl.innerHTML = ''; // Limpa o conteúdo da lista de erros
                 // clearMessages(); // Pode ser agressivo demais limpar mensagem global a cada toggle
            });

             // Adiciona tabindex ao grupo para foco (para acessibilidade e erro visual)
             // Permite que a borda de erro `.is-group-toggle.is-invalid:focus-within` funcione
             toggleGroup.setAttribute('tabindex', '0');
             toggleGroup.addEventListener('focus', function() {
                 // Opcional: Ações ao focar o toggle group
             });
             toggleGroup.addEventListener('blur', function() {
                 // Opcional: Ações ao perder o foco do toggle group
             });
        } else {
             console.error('JS Error: Contêiner .form-group-toggle não encontrado para o checkbox de presença.');
             // Ainda adiciona um listener de 'change' ao checkbox nativo como fallback
             presencaCheckbox.addEventListener('change', function() {
                 // Encontra o UL de erro usando o ID do checkbox
                 const errorUl = document.getElementById(`${this.id}_errors`);
                 if(errorUl) errorUl.innerHTML = '';
             });
        }
    } else {
         console.warn('JS Warning: Checkbox de presença (input[name="presenca"]) não encontrado.');
    }


    // --- Form Submission Logic (AJAX) ---
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Previne a submissão tradicional

        clearMessages(); // Limpa mensagens e erros anteriores

        // Adiciona classe 'submitting' e desabilita o botão ANTES do fetch
        submitButton.classList.add('submitting');
        submitButton.disabled = true;

        const formData = new FormData(form);
        const formAction = form.getAttribute('action') || window.location.pathname;

        fetch(formAction, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // Identifica como AJAX
                // Não defina Content-Type: multipart/form-data manualmente com FormData,
                // fetch faz isso automaticamente e define o boundary correto.
                 'X-CSRFToken': formData.get('csrfmiddlewaretoken') // Inclui o token CSRF
            },
            body: formData // Envia os dados do formulário
        })
        .then(response => {
             // Processa a resposta HTTP
             // Clona a resposta para poder ler o corpo duas vezes (uma como texto, outra como json)
             const clonedResponse = response.clone();
             // Tenta ler o corpo da resposta como texto primeiro para debug em caso de erro JSON
            return response.text().then(text => {
                // Tenta parsear como JSON
                let json = null;
                try {
                    json = JSON.parse(text);
                } catch (e) {
                    // Se falhar ao parsear, json continua null
                }

                // Se a resposta for OK (2xx)
                if (response.ok) {
                    if (json && json.success !== undefined) {
                         // Resposta JSON esperada com chave 'success'
                        return json;
                    } else {
                         // Resposta OK, mas não JSON esperado (ex: HTML de erro 500 renderizado pelo Django)
                         const error = new Error(`Erro inesperado (resposta OK, mas não JSON válido): ${response.status}`);
                         error.status = response.status;
                         error.responseText = text; // Guarda o corpo da resposta como texto
                         throw error; // Lança erro
                    }
                } else {
                    // Se for um status de erro (4xx, 5xx)
                    // Assume que erros de validação estão em .errors para status 400
                    const error = new Error(json && json.message ? json.message : (response.statusText || 'Erro do servidor.'));
                    error.status = response.status;
                    // Anexa os erros de validação se existirem (esperado para status 400)
                    error.errors = json && json.errors ? json.errors : null;
                    error.responseJson = json; // Guarda o JSON completo se parseado
                    error.responseText = text; // Guarda o corpo da resposta como texto
                    throw error; // Lança o error tratado
                }
            });
        })
        .then(data => {
            // Processa a resposta de sucesso (data.success === true)
            submitButton.classList.remove('submitting'); // Remove classe do spinner
            submitButton.disabled = false; // Reabilita o botão

            if (data.success) {
                displayMessage(data.message || 'Operação realizada com sucesso!', 'success');
                // Opcional: Redirecionar ou limpar o formulário
                if (data.redirect_url) {
                    // Use um pequeno delay para o usuário ler a mensagem
                    setTimeout(() => {
                         window.location.href = data.redirect_url;
                    }, 1500); // Redireciona após 1.5 segundos
                } else {
                    // Limpa o formulário se não redirecionar
                    form.reset();
                    // O clearMessages já cuida do reset visual dos widgets não nativos
                     // Limpa a mensagem global após um tempo se o formulário for apenas resetado
                     setTimeout(clearMessages, 5000); // Mensagem some após 5 segundos
                }
            } else {
                // Caso a API retorne 2xx mas com success: false (menos comum, indica lógica de backend customizada)
                 displayMessage(data.message || 'Falha na operação.', 'error');
                 console.error('API returned success: false', data);
            }
        })
        .catch(error => {
            // Processa erros (status não-2xx ou erros de rede/parsing/lógica)
            submitButton.classList.remove('submitting'); // Remove classe do spinner
            submitButton.disabled = false; // Garante que o botão está reabilitado

            // Exibe mensagem de erro global
            let globalErrorMessage = 'Ocorreu um erro inesperado.';

            if (error.status === 400 && error.errors) {
                // Erros de validação do formulário (do Django, status 400, com chave 'errors')
                displayFieldErrors(error.errors); // Exibe erros específicos por campo
                globalErrorMessage = 'Por favor, corrija os erros no formulário.'; // Mensagem global para erros de validação
                console.error('Form Validation Errors:', error.errors);
            } else if (error.status) {
                 // Outros erros HTTP (ex: 403 Forbidden, 404 Not Found, 500 Internal Server Error)
                 globalErrorMessage = `Erro ${error.status}: ${error.message || error.statusText || 'Erro no servidor.'}`;
                 console.error('HTTP Error:', error.status, error.message);
                 // Logar o corpo da resposta se disponível para debug
                 if (error.responseText) {
                      console.error('Response Body:', error.responseText);
                 } else if (error.responseJson) {
                      console.error('Response JSON:', error.responseJson);
                 }
            } else {
                // Erros de rede ou outros erros do fetch (sem status HTTP)
                globalErrorMessage = 'Ocorreu um erro de rede ao enviar o formulário. Verifique sua conexão.';
                console.error('Fetch Error:', error);
            }
             displayMessage(globalErrorMessage, 'error'); // Exibe a mensagem global de erro
        });
    });

    // --- Limpar mensagens de erro ao interagir com campos ---
    // Adicionar listeners de limpeza para inputs, selects, textareas
    form.querySelectorAll('input:not([type="submit"]):not([type="checkbox"]), select, textarea').forEach(field => {
        // Listener para input (digitar em texto/number)
        field.addEventListener('input', function() {
            this.classList.remove('is-invalid');
             // Encontra o UL de erro usando o ID do campo
            const errorUl = document.getElementById(`${this.id}_errors`);
            if(errorUl) errorUl.innerHTML = '';
            // clearMessages(); // Pode ser agressivo demais limpar mensagem global a cada input
        });
         // Listener para change (select, checkbox - embora checkbox tenha seu listener)
        field.addEventListener('change', function() {
             this.classList.remove('is-invalid');
             // Encontra o UL de erro usando o ID do campo
             const errorUl = document.getElementById(`${this.id}_errors`);
             if(errorUl) errorUl.innerHTML = '';
             // clearMessages(); // Pode ser agressivo demais
        });
    });

    // Adicionar listeners de limpeza para os widgets de rating (no clique)
     form.querySelectorAll('.rating-widget').forEach(widget => {
         widget.addEventListener('click', function() {
             // Este listener já chama updateVisualRating que remove classes de hover/filled
             // Adicionamos a limpeza de erro específico e global aqui
             this.classList.remove('is-invalid'); // Remove erro do container do widget
             // Encontra o input original associado
             const hiddenInput = form.querySelector(`[name="${this.dataset.fieldName}"]`);
             if(hiddenInput) { // Verifica se hiddenInput foi encontrado
                  // Encontra o UL de error using the ID of the hiddenInput
                 const errorUl = document.getElementById(`${hiddenInput.id}_errors`);
                 if(errorUl) errorUl.innerHTML = ''; // Limpa o conteúdo da lista de erros
             }
             // clearMessages(); // Pode ser agressivo demais
         });
     });

    // Add cleanup listeners for the toggle widget (on change of the native checkbox)
     form.querySelectorAll('.form-group-toggle input[type="checkbox"]').forEach(checkbox => {
         checkbox.addEventListener('change', function() {
             const toggleGroup = this.closest('.form-group-toggle');
             if(toggleGroup) toggleGroup.classList.remove('is-invalid'); // Remove erro do grupo pai
              // Find the error UL using the ID of the checkbox
             const errorUl = document.getElementById(`${this.id}_errors`);
             if(errorUl) errorUl.innerHTML = ''; // Limpa o conteúdo da lista de erros
             // clearMessages(); // Could be too aggressive
         });
     });

    // Optional: A general listener to clear the global message when the user focuses on any field
    // Can be useful to clear the global error message when starting to correct the form
    form.querySelectorAll('input:not([type="submit"]), select, textarea, .rating-widget, .form-group-toggle').forEach(focusableElement => {
        // Check if the element is an input, select, or textarea before adding the 'focus' listener
         if (focusableElement.tagName === 'INPUT' || focusableElement.tagName === 'SELECT' || focusableElement.tagName === 'TEXTAREA') {
             focusableElement.addEventListener('focus', function() {
                 // clearMessages(); // Uncomment if you want to clear the global message on focus of any field
             });
         } else if (focusableElement.classList.contains('rating-widget') || focusableElement.classList.contains('form-group-toggle')) {
              // For visual widgets, use click instead of focus to clear the global message
              // The specific widget click/change listeners already handle clearing field errors
              // This is just for potentially clearing the global message on interaction
              focusableElement.addEventListener('click', function() {
                 // clearMessages(); // Uncomment if you want to clear the global message on click of a widget
              });
         }
    });

});