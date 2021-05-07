from Bert import Bert

# Initialization of Bert
bert = Bert ()
bert.__init_tokenizer__()
bert.__init_padding__()
bert.__init_attention_mask__()

# Creating tensors from the padded matrix and the mask
input_ids = torch.tensor(bert.padded)  
attention_mask = torch.tensor(bert.attention_mask)

if not self.quiet:
    print ("Embedding the dataset... (this might take a while)")

# Fetching the features
with torch.no_grad():
    last_hidden_states = bert.model(input_ids, attention_mask=attention_mask)
features = last_hidden_states[0][:,0,:].numpy()
