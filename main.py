#!/usr/bin/env python3
"""
OCR de Certidões de Imóveis usando Ollama Local via Docker
Extrai dados de imagens e converte para DataFrame estruturado
"""

import ollama
import pandas as pd
import json
import re
import argparse
import sys
import base64
from pathlib import Path


class OllamaReceiptOCR:
    """Classe para processar OCR de certidões imobiliárias usando Ollama local"""
    
    def __init__(self, host='http://localhost:11434'):
        """
        Inicializa o cliente Ollama
        
        Args:
            host: URL do servidor Ollama (default: http://localhost:11434)
        """
        self.client = ollama.Client(host=host)
        self.vision_model = "llama3.2-vision"
        self.text_model = "llama3"
    
    def extract_image_data(self, image_path):
        """
        Extrai dados da imagem usando modelo de visão
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            str: Texto extraído da imagem
        """
        print(f"Extraindo dados da imagem: {image_path}")
        
        try:
            # Lê a imagem e converte para base64
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            print(f"Imagem convertida para base64 ({len(image_data)} bytes)")
            
            response = self.client.chat(
                model=self.vision_model,
                messages=[{
                    "role": "user",
                    "content": "Extract all text from this Brazilian property registry document (certidão de imóvel). Read all visible text carefully, including registry numbers, names, addresses, CPF, dates, and property details.",
                    "images": [image_data]
                }],
                options={
                    "temperature": 0,
                    "num_ctx": 2048  # Reduz contexto para economizar memória
                }
            )
            
            extracted_text = response['message']['content'].strip()
            print(f"Dados extraídos com sucesso ({len(extracted_text)} caracteres)")
            return extracted_text
            
        except Exception as e:
            print(f"Erro ao extrair dados da imagem: {e}")
            raise
    
    def structure_to_json(self, text):
        """
        Converte texto extraído em JSON estruturado
        
        Args:
            text: Texto extraído da imagem
            
        Returns:
            str: Resposta do modelo (contém JSON)
        """
        print("Estruturando dados em JSON...")
        
        prompt = f"""Extract the following property registry details from the Brazilian certidão de imóvel text and return them as a structured JSON object.

Fields to extract:
- Matricula (Registry/Matricula Number)
- Proprietario (Owner name)
- CPF_Proprietario (Owner CPF)
- Endereco_Imovel (Property address - street, number, neighborhood)
- Municipio (City)
- Estado (State)
- Area_Terreno (Land area in m²)
- Registro_Anterior (Previous registry number if mentioned)
- Data_Registro (Registration date)
- Cartorio (Registry office name and location)
- Livro (Book number)
- Folha (Page number)
- Observacoes (Any important notes or remarks)

Input text:
{text}

Return ONLY a valid JSON object, no extra text or explanations. Use null for missing fields.
"""
        
        try:
            response = self.client.chat(
                model=self.text_model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                options={
                    "temperature": 0,
                    "num_ctx": 2048  # Reduz contexto para economizar memória
                }
            )
            
            result = response['message']['content'].strip()
            print("JSON estruturado com sucesso")
            return result
            
        except Exception as e:
            print(f"Erro ao estruturar JSON: {e}")
            raise
    
    def extract_json_from_response(self, response_text):
        """
        Extrai JSON usando regex da resposta do modelo
        
        Args:
            response_text: Texto da resposta contendo JSON
            
        Returns:
            dict: Dicionário Python com dados estruturados
        """
        print("Extraindo JSON da resposta...")
        
        # Tenta encontrar JSON entre ``` ou no texto direto
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # Tenta encontrar JSON direto
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("Não foi possível encontrar JSON na resposta")
        
        try:
            receipt_dict = json.loads(json_str)
            print("JSON parseado com sucesso")
            return receipt_dict
        except json.JSONDecodeError as e:
            print(f"Erro ao parsear JSON: {e}")
            print(f"JSON string: {json_str[:500]}...")
            raise
    
    def create_dataframe(self, receipt_dict):
        """
        Cria DataFrame pandas a partir do dicionário de certidão
        
        Args:
            receipt_dict: Dicionário com dados da certidão
            
        Returns:
            pd.DataFrame: DataFrame com informações da certidão
        """
        print("Criando DataFrame...")
        
        # Cria DataFrame com uma linha contendo todos os dados
        df = pd.DataFrame([{
            "Matricula": receipt_dict.get('Matricula'),
            "Proprietario": receipt_dict.get('Proprietario'),
            "CPF": receipt_dict.get('CPF_Proprietario'),
            "Endereco_Imovel": receipt_dict.get('Endereco_Imovel'),
            "Municipio": receipt_dict.get('Municipio'),
            "Estado": receipt_dict.get('Estado'),
            "Area_Terreno": receipt_dict.get('Area_Terreno'),
            "Registro_Anterior": receipt_dict.get('Registro_Anterior'),
            "Data_Registro": receipt_dict.get('Data_Registro'),
            "Cartorio": receipt_dict.get('Cartorio'),
            "Livro": receipt_dict.get('Livro'),
            "Folha": receipt_dict.get('Folha'),
            "Observacoes": receipt_dict.get('Observacoes')
        }])
        
        print(f"DataFrame criado com {len(df)} linha(s)")
        return df
    
    def process_receipt(self, image_path, output_csv=None):
        """
        Processa certidão completa: extração, estruturação e conversão
        
        Args:
            image_path: Caminho para imagem da certidão
            output_csv: Caminho para salvar CSV (opcional)
            
        Returns:
            tuple: (DataFrame, dict com JSON estruturado)
        """
        # Valida arquivo
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {image_path}")
        
        # Pipeline completo
        extracted_text = self.extract_image_data(image_path)
        json_response = self.structure_to_json(extracted_text)
        receipt_dict = self.extract_json_from_response(json_response)
        df = self.create_dataframe(receipt_dict)
        
        # Salva CSV se especificado
        if output_csv:
            df.to_csv(output_csv, index=False)
            print(f"DataFrame salvo em: {output_csv}")
        
        return df, receipt_dict


def main():
    """Função principal para execução via linha de comando"""
    parser = argparse.ArgumentParser(
        description='OCR de certidões de imóveis usando Ollama local via Docker'
    )
    parser.add_argument(
        'image_path',
        type=str,
        help='Caminho para a imagem da certidão'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='http://localhost:11434',
        help='URL do servidor Ollama (default: http://localhost:11434)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Caminho para salvar CSV de saída (opcional)'
    )
    parser.add_argument(
        '--show-json',
        action='store_true',
        help='Mostra JSON estruturado na saída'
    )
    
    args = parser.parse_args()
    
    try:
        # Processa certidão
        ocr = OllamaReceiptOCR(host=args.host)
        df, receipt_dict = ocr.process_receipt(args.image_path, args.output)
        
        # Exibe resultados
        print("\n" + "="*80)
        print("DATAFRAME RESULTANTE:")
        print("="*80)
        print(df.to_string())
        
        if args.show_json:
            print("\n" + "="*80)
            print("JSON ESTRUTURADO:")
            print("="*80)
            print(json.dumps(receipt_dict, indent=2, ensure_ascii=False))
        
        print("\n" + "="*80)
        print("Processamento concluído com sucesso!")
        print("="*80)
        
    except Exception as e:
        print(f"\nERRO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()