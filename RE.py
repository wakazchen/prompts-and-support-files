import openai
import os
import json

openai.api_key = 'xxx'


def extract_relationships(text, entities):
    prompt = f"""
    This is a relationship extraction task for a non-small cell lung cancer inpatient process. I will provide you with an entity list and a segment of real electronic medical records. Based on the given entities, you need to understand and analyze the medical records to identify relationships between the specified entities.

    During the relationship extraction process, please note the following key points:

    Previous medical statistical studies have found that during the diagnostic phase, laboratory tests conducted before imaging tests can significantly improve diagnostic efficiency.
    Once the CT scan results, X-ray results, and preoperative infection test results are confirmed, the patient can proceed to the preoperative discussion phase. It is not necessary to wait for all test results to be confirmed before entering the preoperative discussion phase.
    During the patient recovery phase, both the attending physician and the deputy director physician have the same responsibilities. They are both responsible for determining the patient's follow-up examination items, postoperative treatment, and whether the patient is ready for discharge.
    The above content represents the practical experience and applications in the actual diagnostic and therapeutic process of hospitals. These points are not directly stated in the electronic medical records but should be considered when extracting relationships between entities based on the medical records. Additionally, when performing relationship extraction, you must strictly adhere to the content of the medical records and summarize the relevant evidence from the original text. You may also perform basic reasoning about implicit relationships between entities, but you must explain the reasoning logic and the evidence from the medical records. You must not use information outside the medical records or make assumptions. The final output format should be: [Entity1]-[Relationship]-[Entity2]-[Reason].

    For example, from the following electronic medical record text: "The deputy director physician checked the patient and instructed: Based on the patient's medical history, physical examination, and auxiliary examinations, the current diagnosis is...". The directly obtainable relationship is: [Deputy director physician]-[Checked]-[Patient]-[Original text content: Deputy director physician checked the patient and instructed]. The relationship that needs to be inferred is: [Medical history]-[Dependent on]-[Diagnosis result]-[Inferred from "Based on the patient's medical history, physical examination, and auxiliary examinations, the current diagnosis is..."]. This is because the medical history is one of the bases for the diagnosis result, even though it is not explicitly stated in the original text.

    The entity list is: {entities}; the specific electronic medical record text is as follows: {text}.

    """
    try:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=4096,
            temperature=0.1,
            presence_penalty=0,
            n=1,
            stop=["\n"]
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error extracting relationships: {e}")
        return ""


def process_document(corpus_path, ner_path, result_path):
    with open(corpus_path, 'r', encoding='utf-8') as f:
        corpus_content = f.read()

    with open(ner_path, 'r', encoding='utf-8') as f:
        ner_content = f.read()

    corpus_pages = corpus_content.split('---page break---')
    ner_sections = ner_content.split('--section break--')

    if len(corpus_pages) != len(ner_sections):
        print(f"Error: The number of pages in {corpus_path} does not match the sections in {ner_path}")
        return

    extracted_results = []

    for i in range(len(corpus_pages)):
        corpus_page = corpus_pages[i].strip()
        ner_section = ner_sections[i].strip()

        print(f"Processing section {i + 1} of {corpus_path} and {ner_path}...")

        relationships = extract_relationships(corpus_page, ner_section)
        extracted_results.append(relationships)

    with open(result_path, 'w', encoding='utf-8') as f:
        for i, result in enumerate(extracted_results):
            f.write(f"--section break--\n{result}\n")

    print(f"Processed {corpus_path} and {ner_path} and saved results to {result_path}")


def process_multiple_documents(corpus_folder, ner_folder, result_folder):
    for i in range(1, 101):
        corpus_file = os.path.join(corpus_folder, f"语料{i}.txt")
        ner_file = os.path.join(ner_folder, f"ner{i}.txt")
        result_file = os.path.join(result_folder, f"re{i}.txt")
        process_document(corpus_file, ner_file, result_file)


def save_results_to_json(result_folder):
    all_results = {}
    for i in range(1, 101):
        result_file = os.path.join(result_folder, f"re{i}.txt")
        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_results[f"re{i}"] = content

    with open(os.path.join(result_folder, 'relationships.json'), 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    print(f"All results saved to relationships.json")


corpus_folder = 'xxx'
ner_folder = 'xxx'
result_folder = 'xxx'

process_multiple_documents(corpus_folder, ner_folder, result_folder)

save_results_to_json(result_folder)
