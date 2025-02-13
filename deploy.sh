#!/bin/bash

# Cria um diretório para o pacote
mkdir -p package

# Instala as dependências no diretório package
pip install -r requirements.txt -t package/

# Adiciona o código da Lambda ao pacote
cp lambda_function.py package/

# Compacta o pacote
cd package
zip -r ../lambda_function.zip .
cd ..