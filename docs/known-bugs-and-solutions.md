# Known Bugs and Solutions

Este documento reúne problemas conhecidos, suas causas e possíveis soluções.

---

## Erro 404 (Not Found)

**Mensagem:**

```
HTTP Error 404: Not Found
```

### Possíveis causas

* A URL está incorreta ou incompleta.
* O vídeo foi removido.
* A playlist foi removida.
* O conteúdo é privado ou possui restrições de acesso.

### Solução

* Verifique se a URL foi copiada corretamente.
* Abra a URL no navegador para confirmar que ela ainda existe.
* Caso seja um conteúdo privado, certifique-se de possuir acesso.

---

## Avisos do YouTube (EJS / JavaScript Challenge)

**Mensagens como:**

```
n challenge solving failed
```

ou

```
Remote components challenge solver...
```

### O que significa?

O YouTube alterou seu sistema de proteção e o yt-dlp não conseguiu resolver automaticamente o desafio JavaScript.

### Solução

Ative o EJS pelo comando:

```
:ejs
```

Caso o problema continue, atualize o yt-dlp para a versão mais recente.

---

## Links do YouTube Music

O SimpleDL aceita links do YouTube Music.

Quando um link também pertence a uma playlist, será perguntado:

```
1. Baixar apenas este vídeo
2. Baixar a playlist inteira
```

Escolha a opção desejada.

---

## Playlists

Ao baixar uma playlist, você poderá escolher:

* baixar toda a playlist;
* baixar apenas um intervalo de vídeos;
* cancelar a operação.

---

## Download interrompido

Se um vídeo da playlist falhar durante o download, o SimpleDL continuará baixando os próximos vídeos e exibirá um resumo ao final.

---

## Problemas de conexão

Erros de conexão podem ocorrer por:

* Internet instável;
* indisponibilidade temporária do YouTube;
* bloqueios de firewall ou antivírus.

Tente novamente após alguns minutos.

---

## Ainda com problemas?

Se o erro persistir, envie o arquivo de log localizado na pasta `logs/` ao abrir um relatório de problema.
