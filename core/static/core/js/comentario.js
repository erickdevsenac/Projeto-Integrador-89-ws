// Sistema de Comentários para Perfil de Loja
class CommentSystem {
    constructor() {
        this.currentSort = 'recent';
        this.init();
    }
 
    init() {
        this.bindEvents();
        this.setupCharacterCounters();
        this.loadComments();
    }
 
    bindEvents() {
        // Ordenação
        document.querySelectorAll('.sort-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleSort(e));
        });
 
        // Formulário de comentário
        const commentForm = document.getElementById('commentForm');
        if (commentForm) {
            commentForm.addEventListener('submit', (e) => this.handleCommentSubmit(e));
        }
 
        // Sistema de likes
        document.querySelectorAll('.like-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleLike(e));
        });
 
        // Sistema de denúncia
        document.querySelectorAll('.report-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleReport(e));
        });
 
        // Resposta do vendedor
        document.querySelectorAll('.respond-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleRespond(e));
        });
 
        // Moderação
        document.querySelectorAll('.moderation-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.handleModerationTab(e));
        });
 
        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleApprove(e));
        });
 
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleDelete(e));
        });
 
        document.querySelectorAll('.ignore-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleIgnore(e));
        });
 
        // Modal
        const modal = document.getElementById('responseModal');
        if (modal) {
            modal.querySelector('.close-modal').addEventListener('click', () => this.closeModal());
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.closeModal();
            });
 
            document.getElementById('responseForm').addEventListener('submit', (e) => this.handleResponseSubmit(e));
        }
 
        // Tecla Escape para fechar modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
        });
    }
 
    setupCharacterCounters() {
        // Contador de caracteres para comentário
        const commentText = document.getElementById('commentText');
        if (commentText) {
            commentText.addEventListener('input', (e) => {
                const count = e.target.value.length;
                document.getElementById('charCount').textContent = count;
               
                if (count > 450) {
                    e.target.style.borderColor = 'var(--warning-color)';
                } else {
                    e.target.style.borderColor = '';
                }
            });
        }
 
        // Contador de caracteres para resposta
        const responseText = document.getElementById('responseText');
        if (responseText) {
            responseText.addEventListener('input', (e) => {
                const count = e.target.value.length;
                document.getElementById('responseCharCount').textContent = count;
               
                if (count > 250) {
                    e.target.style.borderColor = 'var(--warning-color)';
                } else {
                    e.target.style.borderColor = '';
                }
            });
        }
    }
 
    handleSort(e) {
        e.preventDefault();
       
        // Remove active class de todos os botões
        document.querySelectorAll('.sort-btn').forEach(btn => {
            btn.classList.remove('active');
        });
       
        // Adiciona active class ao botão clicado
        e.target.classList.add('active');
        this.currentSort = e.target.dataset.sort;
       
        this.sortComments();
    }
 
    sortComments() {
        const comments = Array.from(document.querySelectorAll('.comment-item'));
        const container = document.getElementById('commentsList');
       
        comments.sort((a, b) => {
            const ratingA = parseInt(a.dataset.rating);
            const ratingB = parseInt(b.dataset.rating);
            const dateA = new Date(a.dataset.date);
            const dateB = new Date(b.dataset.date);
            const likesA = parseInt(a.dataset.likes);
            const likesB = parseInt(b.dataset.likes);
           
            switch(this.currentSort) {
                case 'recent':
                    return dateB - dateA;
                case 'highest':
                    return ratingB - ratingA;
                case 'lowest':
                    return ratingA - ratingB;
                case 'relevant':
                    // Fórmula de relevância: rating * 0.5 + likes * 0.3 + recente * 0.2
                    const scoreA = (ratingA * 0.5) + (likesA * 0.3) + (dateA.getTime() / 10000000000 * 0.2);
                    const scoreB = (ratingB * 0.5) + (likesB * 0.3) + (dateB.getTime() / 10000000000 * 0.2);
                    return scoreB - scoreA;
                default:
                    return 0;
            }
        });
       
        // Limpa e reordena os comentários
        container.innerHTML = '';
        comments.forEach(comment => {
            container.appendChild(comment);
        });
    }
 
    async handleCommentSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
       
        // Validação básica
        const rating = formData.get('rating');
    }
}