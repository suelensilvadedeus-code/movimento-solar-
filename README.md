
# ☀️ Movimento Solar - Irradiância Solar Interativa

Este aplicativo simula a variação da irradiância solar conforme o movimento do Sol,
com base em medições reais obtidas por sensores e calibradas por região. Para usar as suas medições 
insira os arquivos conforme o indicado abaixo: 

Configure o arquivo para o nome "medicoes_unificadas_corrigido.csv"
As medições precisam ter o nome da região, e valores medidos separados por virgulas.

## 🚀 Como executar localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o app:
   ```bash
   streamlit run movimento_solar_web.py
   ```

## 🌍 Deploy no Streamlit Cloud

1. Faça upload dos arquivos para um repositório GitHub (ex: `movimento-solar`).
2. Acesse [https://share.streamlit.io](https://share.streamlit.io)
3. Clique em **New App** e selecione o repositório.
4. Em **Main file path**, insira:
   ```
   movimento_solar_web.py
   ```
5. Clique em **Deploy**

O aplicativo ficará disponível em:
```
https://movimento-solar.streamlit.app
```

## 📦 Formato do CSV
O arquivo CSV deve conter as colunas:
```
Regiao,ADC,Tipo
Brasil,21000,Pais
Bahia,120.0,Estado
Salvador,154.0,Cidade
Cabula,75.0,Bairro
```
