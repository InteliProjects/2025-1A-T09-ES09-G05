# tree.sh atualizado (versão mais limpa e robusta)
echo "📁 Estrutura de pastas"
echo '```'
find . -type d \( \
    -name '.git' -o \
    -name 'node_modules' -o \
    -name '.venv' -o \
    -name 'venv' -o \
    -name '__pycache__' -o \
    -name 'grafana_data' \
    \) -prune -false -o -print |
sed -e 's/[^-][^\/]*\//  |__/g' -e 's/__/|--/' -e 's/^/ /'
echo '```'
