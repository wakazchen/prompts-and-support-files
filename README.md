# prompts-and-support-files
This is the code collection for the article "Method for Constructing Knowledge Graphs Using Domain Knowledge Constraints and Guidance in Large Language Models," which includes six files in total:

(1) ontology construction.py: This is the code for ontology construction. The ontology construction process does not call APIs but is instead done directly through the GPT-4 chat window. This file demonstrates two prompts for ontology construction.

(2) NER.py: The data used is electronic medical record texts. By combining with prompt words, it recognizes named entities contained in the texts. The final recognized results are Chinese named entities, which are output in tabular form.

(3) RE.py: The data used includes electronic medical record texts and the named entities recognized by the NER file. By combining with prompt words to understand the context, it identifies relationships between different entities, ultimately generating a JSON file containing entities and their inter-entity relationships.Due to the excessive number of characters in some medical record texts, a "---page break---" symbol is inserted between different parts of the record to serve as a marker for splitting the record. The record is segmented in this way to better accomplish the task.

(4) Knowledge filling.py: It uses the set of entities recognized by NER.py. By combining with prompt words, it classifies all entities into different ontology concepts.

(5) Entity disambiguation.py: It uses the set of entities recognized by NER.py. By combining with prompt words to determine the concept of each entity, it unifies the names of entities that share the same concept.

(6) Primary Lung Cancer Surgical Clinical Pathway Form.pdf: This is the form for the national standard clinical pathway for non-small cell lung cancer

# Instructions for Use
The code primarily calls OpenAI's API interface to interact with CHATGPT. Its main function is to accomplish the named entity recognition (NER) task by combining prompt words with different medical record texts. Therefore, the core content of the code lies in the design of prompt words—guiding GPT to output results through prompts, followed by simple result organization to obtain all usable medical named entities.  

The dataset consists of 100 real electronic medical records. The original data of these records are in an unreadable PDF format, containing hospital seals, numerous tables, medical imaging pictures, etc. To use this dataset, it must first be converted into a readable TXT format by removing certain non-textual information from the records, thereby forming coherent medical record text entries.  
    
Secondly, using this code requires a valid API interface; otherwise, you need to directly interact with CHATGPT using the prompt words. Since the core of the code is the prompt words, the results obtained from direct interaction with CHATGPT via prompts are consistent with those from interaction via the API interface. The role of the code is merely to organize the results.  
    
As both the experimental dataset and the prompt words are in Chinese, translating them into English may introduce linguistic differences. Prompt words expressed differently in Chinese and English may lead to deviations in the final results. In the attachment, we provide the original Chinese medical records in PDF format, Chinese medical records in TXT format, and English medical records translated into English for the editor’s reference.  

This dataset has been successfully used in the publication of a Chinese paper. Link: https://kns.cnki.net/kcms2/article/abstract?v=YtMUyApXHwbklhkedd6Q1mhQTUGRxIXIUaK9Sy4Dvorz9Xf3ZFqpMzB2DH5J7pMdXEHj1h_A0Z6HHHZ9oH2wKqjYonXRUjatYMxhkBz28GvuZ5F9Rh5aD5mbz_qSp-QFcmb5vwaD2oMU_q8IcEZSNQojDBcwRbH2F6Aely9T1aPppYMDV4ed8A==&uniplatform=NZKPT&language=CHS
