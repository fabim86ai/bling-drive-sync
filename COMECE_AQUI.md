## Passo 3: Deploy no Render com Gravity (3 min)

1. Abra Gravity (Claude em seu navegador)
2. 2. Diga: "Va para render.com e crie um novo Web Service"
   3. 3. Gravity abre https://dashboard.render.com
      4. 4. Clique **New +** -> **Web Service**
         5. 5. Clique **GitHub** (conecta se nao estiver)
            6. 6. Procura e seleciona `bling-drive-sync`
               7. 7. Clique **Connect**
                  8. 8. Em "Start Command" deixa em branco (pega do render.yml)
                     9. 9. Clique **Create Web Service**
                        10. 10. Aguarda uns 30 segundos o deploy comecar
                           
                            11. ## Passo 4: Adicionar Variaveis de Ambiente (3 min)
                           
                            12. Ainda no Render Dashboard, na sua app `bling-drive-sync`:
                           
                            13. 1. Clique na app -> Aba **Environment**
                               
                                2. 2. **Adicionar Variavel 1:**
                                   3.    - Key: `BLING_API_KEY`
                                         -    - Value: Sua chave API do Bling
                                              -    - Clique **Add**
                                               
                                                   - 3. **Adicionar Variavel 2:**
                                                     4.    - Key: `GOOGLE_DRIVE_ROOT_FOLDER`
                                                           -    - Value: `F&R Contabilidade`
                                                                -    - Clique **Add**
                                                                 
                                                                     - 4. **Adicionar Variavel 3 (Importante!):**
                                                                       5.    - Key: `GOOGLE_CREDENTIALS_JSON`
                                                                             -    - Value: Seu arquivo credentials.json do Google
                                                                              
                                                                                  -    ### Como pegar o credentials.json em base64:
                                                                              
                                                                                  -       **Se tiver no Windows:**
                                                                                  -      - Abra PowerShell
                                                                                  -     - Va ate a pasta do arquivo
                                                                                  -    - Cola: `[Convert]::ToBase64String([System.IO.File]::ReadAllBytes("credentials.json"))`
                                                                                       -    - Copia a saida (e uma string gigante)
                                                                                            -    - Cola no Value acima
                                                                                             
                                                                                                 -    **Se tiver no Mac/Linux:**
                                                                                                 -       - Abre Terminal
                                                                                                 -      - Va ate a pasta do arquivo
                                                                                                 -     - Cola: `cat credentials.json | base64`
                                                                                                 -    - Copia saida gigante
                                                                                                      -    - Cola no Value acima
                                                                                                       
                                                                                                           -    **Se nao quiser base64:**
                                                                                                           -       - Abre credentials.json com bloco de notas
                                                                                                           -      - Copia TODO o conteudo (e um JSON)
                                                                                                           -     - Cola no Value
                                                                                                       
                                                                                                           - 5. Clique **Add**
                                                                                                            
                                                                                                             6. ## Passo 5: Testar (1 min)
                                                                                                            
                                                                                                             7. 1. Volta aos Logs da app (aba **Logs**)
                                                                                                                2. 2. Espera aparecer:
                                                                                                                   3.    ```
                                                                                                                            [OK] Scheduler iniciado
                                                                                                                            ```
                                                                                                                         
                                                                                                                         3. Abre no navegador (copiar URL da app Render):
                                                                                                                         4.    ```
                                                                                                                                  https://sua-app-render.onrender.com/health
                                                                                                                                  ```
                                                                                                                                  Deve retornar: `{"status": "ok", ...}`
                                                                                                                           
                                                                                                                           4. Forca sincronizacao manual:
                                                                                                                           5.    ```
                                                                                                                                    https://sua-app-render.onrender.com/sync-now
                                                                                                                                    ```
                                                                                                                                    Deve retornar resultado (abra com POST via Postman ou use Gravity pra isso)
                                                                                                                             
                                                                                                                             ## Passo 6: Confirmar no Google Drive (1 min)
                                                                                                                     
                                                                                                                     1. Abre seu Google Drive
                                                                                                                     2. 2. Procura pasta "F&R Contabilidade"
                                                                                                                        3. 3. Deve ter 2 pastas dentro:
                                                                                                                           4.    - `Notas-Entrada/`
                                                                                                                                 -    - `Notas-Saida/`
                                                                                                                                      - 4. Se estiverem vazias e normal (se nao tem notas no mes anterior)
                                                                                                                                       
                                                                                                                                        5. ## Passo 7: Pronto!
                                                                                                                                       
                                                                                                                                        6. Seu sistema esta rodando. Todo 1o dia util de abril (e proximos meses), automaticamente as 8h:
                                                                                                                                       
                                                                                                                                        7. [OK] Render executa o script
                                                                                                                                        8. [OK] Busca notas do Bling
                                                                                                                                        9. [OK] Salva no Google Drive
                                                                                                                                        10. [OK] Voce nem sabe que rodou (esta la silencioso)
                                                                                                                                       
                                                                                                                                        11. ## Troubleshooting Rapido
                                                                                                                                       
                                                                                                                                        12. **Erro: "Variaveis faltando"**
                                                                                                                                        13. - Todas as 3 estao no Environment? Clica **Save** depois de adicionar
                                                                                                                                           
                                                                                                                                            - **Erro: "Invalid credentials"**
                                                                                                                                            - - Tenta colar o JSON direto (sem base64)
                                                                                                                                             
                                                                                                                                              - **Logs vazios ou app nao inicia**
                                                                                                                                              - - Clica **Restart** no Render Dashboard
                                                                                                                                                - - Aguarda 30 segundos
                                                                                                                                                  - - Checa Logs novamente
                                                                                                                                                   
                                                                                                                                                    - **Nao aparece nada no Drive**
                                                                                                                                                    - - Testa `/sync-now` manualmente
                                                                                                                                                      - - Ve os Logs completos
                                                                                                                                                        - - Verifica se passou o credentials.json correto
                                                                                                                                                         
                                                                                                                                                          - ## Se Quiser Forcar Sincronizacao Manualmente
                                                                                                                                                         
                                                                                                                                                          - (Sem esperar 1o do mes)
                                                                                                                                                         
                                                                                                                                                          - Opcao A: Linha de comando
                                                                                                                                                          - ```bash
                                                                                                                                                            curl -X POST https://sua-app-render.onrender.com/sync-now
                                                                                                                                                            ```
                                                                                                                                                            
                                                                                                                                                            Opcao B: Usar Gravity
                                                                                                                                                            "Abre https://sua-app-render.onrender.com/sync-now (POST)"
                                                                                                                                                            
                                                                                                                                                            ## Proximos Passos
                                                                                                                                                            
                                                                                                                                                            - [ ] GitHub repo criado com 4 arquivos
                                                                                                                                                            - [ ] - [ ] Deploy feito no Render
                                                                                                                                                            - [ ] - [ ] 3 variaveis de ambiente adicionadas
                                                                                                                                                            - [ ] - [ ] `/health` retorna OK
                                                                                                                                                            - [ ] - [ ] Folders criadas no Drive
                                                                                                                                                            - [ ] - [ ] Pronto! 1o de abril roda automatico
                                                                                                                                                           
                                                                                                                                                            - [ ] **Tempo total: ~20 minutos**
                                                                                                                                                           
                                                                                                                                                            - [ ] ---
                                                                                                                                                           
                                                                                                                                                            - [ ] ## Resumao Pra Voce Entender
                                                                                                                                                           
                                                                                                                                                            - [ ] Voce criou um robo:
                                                                                                                                                            - [ ] - Roda na nuvem (Render)
                                                                                                                                                            - [ ] - Todo 1o dia util as 8h
                                                                                                                                                            - [ ] - Busca notas do Bling (API)
                                                                                                                                                            - [ ] - Salva no Google Drive
                                                                                                                                                            - [ ] - Ninguem faz nada
                                                                                                                                                            - [ ] - Nenhum clique
                                                                                                                                                            - [ ] - Zero browser
                                                                                                                                                           
                                                                                                                                                            - [ ] E isso. FIM!
                                                                                                                                                            - [ ] 
