import openai
import json

openai.api_key = 'xxx'


def load_documents(file_paths):
    documents = {}
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            documents[file_path] = file.read()
    return documents


def classify_entities(documents, categories):
    results = {}

    for doc_name, text in documents.items():
        prompt = f"""
                 Assume that you are an expert who is very familiar with all the treatment processes in a hospital. I need you to perform an entity classification task, which involves understanding the meaning of the category labels I provide, as well as understanding the meaning of the entities given to you, and then determining which category an entity belongs to. Please note that an entity can only belong to one category label, and if the entity fits the definition of multiple labels, you need to choose the most appropriate one.
                 The category labels include the following six types: {', '.join(categories)}.
                 I have provided a more detailed explanation for each of these six labels:

                 Admission Day: This refers to the first day of hospitalization, which is the time when the patient first enters the hospital and is recorded. The attending physician must initially assess the patient's condition and evaluate them, and based on the patient's condition, arrange subsequent examinations, diagnoses, treatments, and nursing activities. Typically, this includes taking the medical history, performing an admission examination, ward rounds, creating a treatment plan, and diagnosing the patient, along with establishing medical orders and nursing tasks. In the electronic medical record, the documentation for the admission day is titled "Initial Medical Record". Admission day is based on the admission time, and it typically involves activities such as admission diagnosis, admission examination, physical examination, and medical record documentation.
                 Preoperative Day: This is the time from the second day of hospitalization to the day before surgery. During this stage, the attending physician, chief physician, and nursing staff conduct rounds, engage in preoperative discussions, and make a preoperative summary. Based on the patient's lab tests, imaging studies, and other auxiliary examination reports, the final diagnosis is confirmed, and the surgical risk is assessed to ensure the indication for surgery is clear and that a reasonable surgical plan is formulated. Preoperative preparations are also carried out. Senior physicians need to write the medical record, have the patient's family sign the informed consent form for surgery, the self-payment items agreement, the blood transfusion consent, the authorization agreement, etc. During this phase, the patient's other surgical complications are also addressed, and if necessary, specialists from other departments are invited for consultations. In the electronic medical record, all rounds and activities between the admission day and the day of surgery are considered part of the preoperative day, which involves all diagnostic, evaluation, nursing, examination, and preparation activities after the admission day.
                 Surgery Day: This is the day the patient undergoes surgery, typically between the third and seventh day of hospitalization. On this day, the patient undergoes surgery. The surgeon records the surgery, the attending physician documents the postoperative progress, the senior physician conducts rounds, observes vital signs, and explains the patient's condition and postoperative precautions to the patient and their family. Close monitoring and necessary documentation are required, as well as observing changes in the patient's condition, postoperative psychological and lifestyle care, and ensuring the patient’s airway remains unobstructed. This stage involves the chief physician, associate chief physician, attending physician, and nurses. In the electronic medical record, the surgery day documentation is titled "First Postoperative Medical Record".
                 Postoperative Day1: This is the first day of hospitalization following surgery. It mainly involves focused nursing and monitoring of the patient. The care level is the highest during this stage, and monitoring is most intensive, with frequent documentation of the patient’s physiological indicators and wound status. In the electronic medical record, the medical activities on this day are recorded under "First Postoperative Medical Record", including all diagnostic and treatment activities on the patient's first postoperative day. It is a critical time point for observing the patient's condition and status.
                 Recovery Day: This refers to the time from the second day to the seventh day after surgery. During this phase, the patient's recovery is monitored, postoperative problems are addressed, and any postoperative complications are treated. In the electronic medical record, the removal of the patient's chest drainage tube marks the end of the postoperative recovery stage.
                 Discharge Day: This is from the eighth to the fourteenth day after surgery. After the chest drainage tube has been removed, all diagnostic and treatment activities until the last medical record are categorized as discharge day activities. This includes confirming the patient's postoperative status, determining if they meet discharge criteria, formulating a follow-up treatment plan, providing instructions for follow-up visits, and completing the final medical record.

                 The definitions of these six labels explain the essential features of entities that should fall under each label and the key medical activities that need to be performed. You need to clarify the boundaries between the different labels based on these definitions to ensure that the concepts of the labels do not overlap.
                 For example, for the medical activity "Multidisciplinary Consultation," it should be categorized under the "Preoperative Day" label. This is because a multidisciplinary consultation occurs when the patient has multiple complications before surgery, requiring various related departments to discuss and determine the best treatment plan. It takes place before the surgery day and is not part of the basic evaluation done when the patient is admitted. According to the definition of the "Preoperative Day": "During this phase, other complications that may affect the surgery must be addressed, and if necessary, other specialists are consulted or the patient is transferred to another department." Therefore, you should categorize it under the "Preoperative Day" label.

                 Output format:
                 [1] entity: Multidisciplinary Consultation, category: Preoperative Day
                 all entities are as follow：\n{text}\n\n"""

        try:
            response = openai.Completion.create(
                engine="gpt-4",
                prompt=prompt,
                max_tokens=4096,
                temperature=0.1,
                presence_penalty=0
            )

            classified_entities = response.choices[0].text.strip()
            results[doc_name] = classified_entities

        except Exception as e:
            print(f"wrong：{e}")

    return results


def save_results_to_json(results, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)


def main():

    # We randomly divided the entities into six documents to meet the token limit, and processed each of these six documents separately.
    file_paths = ['txt1.txt', 'txt2.txt', 'txt3.txt', 'txt4.txt', 'txt5.txt', 'txt6.txt']

    categories = ['Admission Day', 'Preoperative Day', 'Surgery Day', 'Postoperative Day1', 'Recovery Day', 'Discharge Day']

    documents = load_documents(file_paths)

    results = classify_entities(documents, categories)

    save_results_to_json(results, 'classification_results.json')
    print("saved to classification_results.json")


if __name__ == "__main__":
    main()

