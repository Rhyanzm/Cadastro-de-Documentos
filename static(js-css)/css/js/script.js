document.addEventListener('DOMContentLoaded', function () {
    // ---- Lógica para o formulário de cadastro/edição de colaborador ----
    const formColaborador = document.querySelector('form');
    const nr10AplicavelCheckbox = document.getElementById('nr10_aplicavel');
    const nr10ValidadeInput = document.getElementById('nr10_validade');
    const codigoRegistroInput = document.getElementById('codigo_registro');

    // Função para controlar a visibilidade e obrigatoriedade do campo NR-10 Validade
    function toggleNr10Validade() {
        if (nr10AplicavelCheckbox.checked) {
            nr10ValidadeInput.style.display = 'block';
            nr10ValidadeInput.required = true; // Torna o campo obrigatório
            nr10ValidadeInput.parentElement.style.display = 'block'; // Mostra o label
        } else {
            nr10ValidadeInput.style.display = 'none';
            nr10ValidadeInput.required = false; // Torna o campo opcional
            nr10ValidadeInput.value = ''; // Limpa o valor quando não é aplicável
            nr10ValidadeInput.parentElement.style.display = 'none'; // Oculta o label 
            // === Função para salvar arquivos PDF ===
            function salvarPDFs(codigo, colaboradores) {
                const nrs = ['6', '10', '11', '12', '18', '20', '33', '35'];

                nrs.forEach(nr => {
                    const input = document.getElementById(`pdfNR${nr}`);
                    if (input && input.files.length > 0) {
                        const file = input.files[0];
                        const reader = new FileReader();
                        reader.onload = function (e) {
                            colaboradores[codigo][`pdfNR${nr}`] = e.target.result;
                            localStorage.setItem('colaboradores', JSON.stringify(colaboradores));
                        };
                        reader.readAsDataURL(file);
                    }
                });

                const asoInput = document.getElementById('pdfASO');
                if (asoInput && asoInput.files.length > 0) {
                    const file = asoInput.files[0];
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        colaboradores[codigo].pdfASO = e.target.result;
                        localStorage.setItem('colaboradores', JSON.stringify(colaboradores));
                    };
                    reader.readAsDataURL(file);
                }
            }

            // === Função para exibir link de PDF ao editar colaborador ===
            function preencherLinksPDF(codigo, colaboradores) {
                const colab = colaboradores[codigo];
                const nrs = ['6', '10', '11', '12', '18', '20', '33', '35'];
                preencherLinksPDF(codigo, colaboradores);

                nrs.forEach(nr => {
                    const link = document.getElementById(`verPDFNR${nr}`);
                    if (link && colab[`pdfNR${nr}`]) {
                        link.href = colab[`pdfNR${nr}`];
                        link.style.display = 'inline';
                    } else if (link) {
                        link.style.display = 'none';
                    }
                });

                const linkASO = document.getElementById('verPDFASO');
                if (linkASO && colab.pdfASO) {
                    linkASO.href = colab.pdfASO;
                    linkASO.style.display = 'inline';
                } else if (linkASO) {
                    linkASO.style.display = 'none';
                }
            }

        }
    }

    // Executa a função ao carregar a página (para o caso de edição onde o checkbox já vem marcado)
    if (nr10AplicavelCheckbox && nr10ValidadeInput) {
        toggleNr10Validade();
        // Adiciona um listener para o evento de mudança no checkbox
        nr10AplicavelCheckbox.addEventListener('change', toggleNr10Validade);
    }

    // Adicionar validação do código de registro ao enviar o formulário
    if (formColaborador && codigoRegistroInput) {
        formColaborador.addEventListener('submit', function (event) {
            const codigo = codigoRegistroInput.value;

            if (codigo.length !== 6 || !/^\d+$/.test(codigo)) {
                alert('O Código de Registro deve ter exatamente 6 dígitos numéricos.');
                event.preventDefault(); // Impede o envio do formulário
                return false;
            }
            const colaboradores = JSON.parse(localStorage.getItem('colaboradores')) || {};
            salvarPDFs(codigo, colaboradores);
            // Outras validações podem ser adicionadas aqui
            return true; // Permite o envio se tudo estiver ok
        });
    }

    // ---- Lógica para a tela inicial (index.html) ----
    const formConsulta = document.querySelector('form[action="/consultar_colaborador"]');
    const inputCodigoConsulta = document.getElementById('codigo_registro');

    if (formConsulta && inputCodigoConsulta) {
        formConsulta.addEventListener('submit', function (event) {
            const codigo = inputCodigoConsulta.value;
            if (codigo.length !== 6 || !/^\d+$/.test(codigo)) {
                alert('Por favor, insira um Código de Registro de 6 dígitos numéricos.');
                event.preventDefault(); // Impede o envio do formulário
                return false;
            }
            return true;
        });
    }
});
// script.js - Para mostrar o nome do arquivo selecionado
document.getElementById('arquivo_pdf').addEventListener('change', function () {
    const nomeArquivo = this.files.length > 0 ? this.files[0].name : '';
    document.getElementById('nome-arquivo').textContent = nomeArquivo;
});
