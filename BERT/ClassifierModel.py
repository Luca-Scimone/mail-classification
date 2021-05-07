from Bert import Bert
import torch

# Initialization of Bert
bert = Bert ()
bert.__init_bert_tools__()

# Creating tensors from the padded matrix and the mask
input_ids = torch.tensor(bert.padded)  
attention_mask = torch.tensor(bert.attention_mask)

# Fetching the features
with torch.no_grad():
    last_hidden_states = bert.model(input_ids, attention_mask=attention_mask)
features = last_hidden_states[0][:,0,:].numpy()
