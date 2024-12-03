para rodar o projeto, caso use um sistema linux, certifique-se de que o usuario esteja no grupo docker ou seja usuario root.

entre na pasta do projeto e rode o comando "docker-compose up -d --build"

após o container estar no ar e funcionando, no navegador, use o link "localhost:8080" para entrar no php my admin e logue com as credenciais: 
user:root
senha: senha123

depois do login ter sido realizado, clique em sql, copie e cole o codigo que esta no arquivo "insert.sql"

assim que o usuario admin foi cadastrado no banco, abra a aplicação com o link "localhost:5000" e realize o login com o usuario que foi 
cadastrado por meio da aba sql no php my admin

para testar todas as funcionalidades da aplicação, primeiro cadastre o professor ou a sala, depois adicione a aula e por fim, realize o cadastro de aluno 

para a orquestração dos containers usando o PORTAINER.IO, utilize o link "localhost:9000", para efetuar o login use as credenciais:
user: admin
senha: admin03032005

OBS: caso preferir, gere uma senha hash no arquivo "gerar_hash.py", substituindo o hash gerado pelo hash que esta no codigo do arquivo "insert.sql"

