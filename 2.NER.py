import os
import openai
import pandas as pd
import time
from tqdm import tqdm

openai.api_key = ""  # API address

PROMPT = """
This is a named entity recognition task for the inpatient process of non-small cell lung cancer. You are an expert with deep understanding of hospital medical records. Based on the real electronic medical records I provide, you need to extract all entities related to the hospitalization process mentioned in the medical records.

The hospitalization process typically covers the entire process from a patient's admission to discharge. In the provided electronic medical records, the hospitalization process is a series of diagnostic and therapeutic activities arranged in chronological order, including examinations, diagnoses, treatments, nursing care, follow-ups, and post-discharge visits. These activities are all related to the patient's hospital stay. Additionally, the process includes the personnel, departments, and resources involved in the diagnostic and therapeutic process.

When completing this task, you need to understand my definition of the hospitalization process and use it as the recognition logic to determine the standards and boundaries for identifying entities. Any terms unrelated to the definition or not mentioned in the medical records should not be considered. After identifying the named entities, you need to explain the reason for their identification based on the given definition. The result should be returned in the following format: [Entity Name]-[Reason for Identification]. The reasons for identification are of five types:

- Hospital activities and results: The entity represents a real diagnostic or therapeutic activity that affects the patient's hospitalization process. It is an activity actually performed by the patient or carried out by other medical staff or family members for the treatment of the patient. And the entity represents all medical conclusions related to the patient.
- Medical resources: The entity represents all resources used during the patient's hospitalization process, such as medications, medical materials, etc.
- Medical staffs: The entity represents all personnel or departments related to the patient's hospitalization.
- Examinations: The entity refers to all the examinations performed on the patient.
- Variation: Refers to all activities during the patient's treatment process that do not align with the main clinical pathway treatment tasks. This includes additional medical activities performed due to the patient's complications, or treatment activities that were not completed on time within the prescribed period for the current stage, as well as activities that affect the general inpatient process, such as delays or termination of the treatment process caused by the patient or their family.

For example, in the following text: “After reviewing the patient's condition, the deputy chief physician instructed: the patient should complete the necessary examinations to rule out surgical contraindications, and undergo a thoracoscopic (open chest) left lower lung wedge resection or lobectomy tomorrow. The patient's family has been fully informed about the condition, and the patient expressed understanding and consent to the surgery, signing the surgical informed consent form, and agreeing to follow the instructions.” The identifiable inpatient process named entities in this case include: reviewing the condition, ruling out surgical contraindications, thoracoscopic (open chest) left lower lung wedge resection or lobectomy, patient’s family, informing about the condition, understanding and consenting to the surgery, signing the surgical informed consent form. For example, the entities "reviewing the condition" and "ruling out surgical contraindications" belong to the first category.
Results that do not need to be merged:
[entities]-[type].
"""

def extract_entities(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional medical named entity recognition assistant, strictly following user instructions."
                },
                {
                    "role": "user",
                    "content": f"{PROMPT}\n\nElectronic medical record content:\n{text}\n\nPlease return the result in JSON format, containing two fields: 'Entity Name' and 'Reason for Identification', where 'Reason for Identification' must be one of the following five types: Hospital Activities and Results, Medical Resources, Medical Staff, Examinations, Variation"
                }
            ],
            temperature=0.1,
            max_tokens=4096,
            presence_penalty=0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API call error: {e}")
        return None

def process_files(folder_path):
    results = {}
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    for filename in tqdm(txt_files, desc="Processing Progress"):
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            json_response = extract_entities(content)
            if not json_response:
                continue

            import json
            data = json.loads(json_response)

            if isinstance(data, dict) and "Entity Name" in data and "Reason for Identification" in data:
                entities = data["Entity Name"]
                reasons = data["Reason for Identification"]

                if isinstance(entities, list) and isinstance(reasons, list):
                    if len(entities) == len(reasons):
                        results[filename] = pd.DataFrame({
                            "Entity Name": entities,
                            "Reason for Identification": reasons
                        })
                    else:
                        print(f"Warning: {filename} has mismatched number of entities and reasons.")
                elif isinstance(entities, str) and isinstance(reasons, str):
                    results[filename] = pd.DataFrame([{
                        "Entity Name": entities,
                        "Reason for Identification": reasons
                    }])
                else:
                    print(f"Warning: {filename} returned unexpected data structure.")

        except Exception as e:
            print(f"Error processing file {filename}: {e}")
    return results

def save_to_excel(results, output_file):
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for filename, df in results.items():
            sheet_name = filename.replace(".txt", "")[:31]  # Max 31 characters for Excel sheet name
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        all_entities = []
        for df in results.values():
            all_entities.extend(df.to_dict("records"))

        if all_entities:
            summary_df = pd.DataFrame(all_entities)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
    print(f"Results have been saved to: {output_file}")

if __name__ == "__main__":
    FOLDER_PATH = "C:\\Users\\list"
    OUTPUT_FILE = "Named Entity Recognition Results.xlsx"
    results = process_files(FOLDER_PATH)
    save_to_excel(results, OUTPUT_FILE)

