import openai

openai.api_key = 'xxx'


def read_entities(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        entities = file.read().splitlines()
    return entities

# Entities are saved to 4 files
cat1_entities = read_entities('cat1.txt')
cat2_entities = read_entities('cat2.txt')
cat3_entities = read_entities('cat3.txt')
cat4_entities = read_entities('cat4.txt')

combined_entities = "\n".join(cat1_entities + cat2_entities + cat3_entities + cat4_entities)

prompt = f"""
This is an entity fusion task in the medical domain. I will provide you with a list of entity names, including entities related to hospitalization processes, diagnosis and treatment, nursing work, medical resources, and medical examination items. You need to clearly understand the meaning of each entity and determine whether different entities have the same meaning. For entities that have the same meaning but different expressions, you need to identify them.

I will provide you with four reasons for entity similarity:

Chinese-English synonyms: Some entities in the medical records appear in English form, while others appear in Chinese form. You need to understand the meaning of the English and Chinese terms in the medical records and convert them into Chinese to determine if there are entities with similar meanings.
Abbreviations: For convenience, hospital staff sometimes use abbreviations in medical records to replace complex expressions. You need to understand the clear meaning of the abbreviations and determine if there are synonyms.
Chinese homophones: Many Chinese terms are derived from loanwords and are constructed based on the pronunciation of foreign terms to form the names of medical entities.
Other expression variations: Many Chinese terms have slight differences in expression, but their meanings are the same.

For entities with the same meaning, you also need to choose the best entity expression to make it closer to the standardized terminology in the medical domain.

Please return two lists: one for entities that do not need fusion and another for entities that need fusion. For the list of entities that do not need fusion, just output them line by line, ensuring each entity appears only once. For the list of entities with similar meanings, return the entities in the same line, provide the best entity expression, and specify the reason for the expression differences according to my definition of similar entity reasons.

The format is as follows:
Entities that do not need to be merged:
[1]Entity1
[2]Entity2
[3]...

Entities that need to be merged:
(1) Entity1, Entity2, ... [Best expression:], expression difference reason:
(2) ...

entities lists are as follow：{combined_entities}
"""

response = openai.Completion.create(
    engine="gpt-4",
    prompt=prompt,
    max_tokens=4096,
    temperature=0.1,
    presence_penalty=0
)

disambiguated_entities = response.choices[0].text.strip()
print("list：")
print(disambiguated_entities)


