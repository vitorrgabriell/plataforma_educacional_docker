/* usar este insert após rodar o banco */
USE plataforma_educacional;

INSERT INTO usuarios(nome, email, senha_hash, tipo) VALUES ('admin1', 'admin1@gmail.com', '$2b$12$MkEbBTiCPWSv5rlw0bcmg.QONCaYwhTUM0vFTY8.XEINYks2MfdaO', 'admin')

/* NO CAMPO DA SENHA, GERAR O HASH COM A SENHA DESEJADA, A SENHA QUE JA ESTÁ NO CODIGO É "admin123", MAS CASO DESEJE MUDAR, TROQUE A SENHA E RODE O CODIGO, COPIE O HASH APÓS RODAR O ARQUIVO
"gerar_hash.py" E COLE NO INSERT ACIMA