function showVideos(category) {
        // Esconde todos os grupos de vídeos
        document.querySelectorAll('.video-group').forEach(group => {
            group.style.display = 'none';
        });
        
        // Mostra o grupo selecionado
        document.getElementById(category).style.display = 'block';
        
        // Atualiza os botões ativos
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
    }