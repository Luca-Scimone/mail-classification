from transformers import BertModel, BertTokenizer
import tensorflow as tf
import torch

# pre train bert model
model = BertModel.from_pretrained('bert-base-uncased')

# on télécharge le tokeniser ed bert
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

sentence = 'I loving Paris'
tokens = tokenizer.tokenize(sentence)
print(tokens)

tokens = ['[CLS]'] + tokens + ['[SEP]']
tokens = tokens + ['[PAD]'] + ['[PAD]']
attention_mask = [1 if i!= '[PAD]' else 0 for i in tokens]

# on convertit les token en ids (token officiel on va dire)
token_ids = tokenizer.convert_tokens_to_ids(tokens)
print(token_ids)

# mnt on peut convertir nos vecteur en tenseur
token_ids = torch.tensor(token_ids).unsqueeze(0)
attention_mask = torch.tensor(attention_mask).unsqueeze(0)

# on récupère le embedding word
hidden_rep, cls_head = model(token_ids, attention_mask = attention_mask)
print(hidden_rep)


"""
text = "Here is the sentence I want embeddings for."
marked_text = "[CLS] " + text + " [SEP]"# Tokenize our sentence with the BERT tokenizer.
tokenized_text = tokenizer.tokenize(marked_text)# Print out the tokens.
print (tokenized_text)
"""